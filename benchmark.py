# HISTORICAL HARNESS: retained for provenance, not current validation.
# Current live inference evidence: validate_model.py. Do not use old scoring for sign-off.
"""
A.U.R.A Stage 1 — Milestone 1.2: Model Acquisition & Raw Validation
Uses Ollama API (localhost:11434) to benchmark the locally-imported Qwen 3.5 4B Q8 model.
Measures: Load/warmup time, first-token latency, generation speed (TPS), and schema validation.
"""
import time
import json
import subprocess
import requests
from core.schema import ToolCallSchema
from core.prompt import BASE_SYSTEM_PROMPT

OLLAMA_API = "http://localhost:11434"
MODEL_NAME = "aura-qwen:latest"


def get_vram_info():
    """Get VRAM usage from nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(", ")
            return {
                "vram_used_mb": int(parts[0]),
                "vram_total_mb": int(parts[1]),
                "vram_free_mb": int(parts[2])
            }
    except Exception:
        pass
    return None


def run_benchmark():
    print("=" * 60)
    print("A.U.R.A STAGE 1 — MODEL ACQUISITION & RAW VALIDATION")
    print("Engine: Ollama | Model: Qwen 3.5 4B Q8_0")
    print("=" * 60)

    # 0. Check Ollama is running
    try:
        r = requests.get(f"{OLLAMA_API}/api/version", timeout=3)
        print(f"[+] Ollama server detected: v{r.json().get('version', '?')}")
    except Exception:
        print("[!] Ollama server not reachable at localhost:11434.")
        print("    Run 'ollama serve' in another terminal first.")
        return

    # 1. VRAM at idle (before model load)
    vram_idle = get_vram_info()
    if vram_idle:
        print(f"[+] VRAM at idle: {vram_idle['vram_used_mb']} MB / {vram_idle['vram_total_mb']} MB")

    # 2. Warm up / load model (first call forces Ollama to load into VRAM)
    print("\n[*] Loading model into VRAM (warmup call)...")
    start_load = time.time()
    try:
        warmup = requests.post(f"{OLLAMA_API}/api/generate", json={
            "model": MODEL_NAME,
            "prompt": "Hello",
            "stream": False,
            "options": {"num_predict": 1, "num_ctx": 4096, "num_gpu": 99}
        }, timeout=120)
        warmup.raise_for_status()
    except Exception as e:
        print(f"[!] Model load/warmup failed: {e}")
        return
    load_time = time.time() - start_load
    print(f"[+] Model loaded in {load_time:.2f} seconds.")

    # VRAM after model load
    vram_loaded = get_vram_info()
    if vram_loaded:
        print(f"[+] VRAM under load: {vram_loaded['vram_used_mb']} MB / {vram_loaded['vram_total_mb']} MB")
        if vram_idle:
            model_vram = vram_loaded['vram_used_mb'] - vram_idle['vram_used_mb']
            print(f"[+] Model VRAM footprint: ~{model_vram} MB")

    # 3. Actual benchmark — streaming generation with tool-call prompt
    user_command = (
        "AURA, I want to delete the old project folder at "
        "C:\\Archive\\old_project. It's taking up too much space."
    )

    print(f"\n[*] Sending command: '{user_command}'")
    print("[*] Waiting for first token...")

    start_gen = time.time()
    first_token_time = None
    output = ""
    tokens_generated = 0

    try:
        resp = requests.post(f"{OLLAMA_API}/api/chat", json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user", "content": user_command}
            ],
            "stream": True,
            "format": ToolCallSchema.model_json_schema(),
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096,
                "num_gpu": 99
            }
        }, stream=True, timeout=300)
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            msg = chunk.get("message", {})
            content = msg.get("content", "")

            if content and first_token_time is None:
                first_token_time = time.time() - start_gen
                print(f"[+] First token latency: {first_token_time:.2f}s")

            if content:
                output += content
                tokens_generated += 1

            # Ollama sends done=true on last chunk
            if chunk.get("done"):
                # Extract eval metrics if available
                eval_count = chunk.get("eval_count", tokens_generated)
                eval_duration_ns = chunk.get("eval_duration", 0)
                prompt_eval_count = chunk.get("prompt_eval_count", 0)
                prompt_eval_duration_ns = chunk.get("prompt_eval_duration", 0)
                break

    except Exception as e:
        print(f"[!] Generation failed: {e}")
        return

    total_gen_time = time.time() - start_gen

    # Use Ollama's native TPS if available (more accurate than counting chunks)
    if eval_duration_ns > 0:
        ollama_tps = eval_count / (eval_duration_ns / 1e9)
    else:
        ollama_tps = tokens_generated / total_gen_time if total_gen_time > 0 else 0

    if prompt_eval_duration_ns > 0:
        prompt_tps = prompt_eval_count / (prompt_eval_duration_ns / 1e9)
    else:
        prompt_tps = 0

    print("\n[==== RAW MODEL OUTPUT ====]")
    print(output)
    print("[==========================]\n")

    # 4. Validate output against Pydantic schema
    try:
        parsed = json.loads(output)
        validated_call = ToolCallSchema(**parsed)
        schema_pass = True
        print("[+] SCHEMA VALIDATION: [PASS]")
        print(f"    Tool:      {validated_call.tool_name}")
        print(f"    Params:    {validated_call.parameters}")
        print(f"    Reasoning: {validated_call.reasoning}")
        print(f"    Risk:      {validated_call.risk_hint}")
    except json.JSONDecodeError as e:
        schema_pass = False
        print(f"[-] SCHEMA VALIDATION: [FAIL] (Invalid JSON)")
        print(f"    Error: {e}")
    except Exception as e:
        schema_pass = False
        print(f"[-] SCHEMA VALIDATION: [FAIL] (Schema Mismatch)")
        print(f"    Error: {e}")

    # 5. Final metrics report
    print("\n" + "=" * 60)
    print("           A.U.R.A STAGE 1 — BENCHMARK RESULTS")
    print("=" * 60)
    print(f"  Model              : Qwen 3.5 4B (Q8_0)")
    print(f"  Engine             : Ollama v{requests.get(f'{OLLAMA_API}/api/version').json().get('version', '?')}")
    print(f"  Load Time          : {load_time:.2f} s")
    if first_token_time:
        print(f"  First Token Latency: {first_token_time:.2f} s")
    print(f"  Generation Speed   : {ollama_tps:.2f} tokens/sec (eval)")
    if prompt_tps > 0:
        print(f"  Prompt Processing  : {prompt_tps:.2f} tokens/sec")
    print(f"  Tokens Generated   : {eval_count}")
    print(f"  Context Window     : 4096 tokens allocated")
    if vram_idle:
        print(f"  VRAM (idle)        : {vram_idle['vram_used_mb']} MB")
    if vram_loaded:
        print(f"  VRAM (under load)  : {vram_loaded['vram_used_mb']} MB")
    print(f"  Schema Validation  : {'[PASS]' if schema_pass else '[FAIL]'}")
    print("=" * 60)


if __name__ == "__main__":
    run_benchmark()
