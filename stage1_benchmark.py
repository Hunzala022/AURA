# HISTORICAL HARNESS: retained for provenance, not current validation.
# Current live inference evidence: validate_model.py. Do not use old scoring for sign-off.
import time
import json
from llama_cpp import Llama
from pydantic import BaseModel, Field

# 1. Define strict A.U.R.A structured tool schema
class OSAction(BaseModel):
    action_type: str = Field(description="The type of OS action, e.g., 'read_file', 'open_browser'")
    target_path: str = Field(description="The absolute path or URL to target")
    reasoning: str = Field(description="Brief reason why this action is being taken")

def run_stage1_benchmark():
    model_path = "models/Qwen_Qwen3.5-4B-Q8_0.gguf"
    print(f"[*] Starting A.U.R.A Stage 1 Local Validation...")
    print(f"[*] Loading model: {model_path} into VRAM...")
    
    start_load = time.time()
    try:
        # We offload all layers to GPU (n_gpu_layers=-1) since 4.6GB fits in 6GB VRAM.
        # n_ctx=2048 is a safe starting context window.
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,  
            n_ctx=2048,
            verbose=False # Set true if you want to see detailed C++ logs
        )
    except Exception as e:
        print(f"[!] Failed to load model: {e}")
        return

    load_time = time.time() - start_load
    print(f"[+] Model successfully loaded in {load_time:.2f} seconds.")

    # 2. Prepare the task
    system_prompt = "You are A.U.R.A, a secure local OS agent. You MUST output ONLY valid JSON matching the requested schema. No conversational filler."
    user_prompt = "User Command: 'AURA, I need you to read the SLR document located at D:\\Project AURA\\AURA Resources\\SLR - Project AURA.pdf'."

    print("\n[*] Sending command to model for structured tool-call generation...")
    start_gen = time.time()
    
    # 3. Execute with JSON schema enforcement
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={
            "type": "json_object",
            "schema": OSAction.model_json_schema()
        },
        temperature=0.1,
        max_tokens=256
    )
    
    gen_time = time.time() - start_gen
    
    raw_output = response["choices"][0]["message"]["content"]
    completion_tokens = response["usage"]["completion_tokens"]
    tps = completion_tokens / gen_time if gen_time > 0 else 0

    print("\n" + "="*50)
    print("A.U.R.A STAGE 1 BENCHMARK RESULTS")
    print("="*50)
    print(f"RAW OUTPUT:\n{raw_output}\n")
    
    # 4. Verification Step
    print("[*] Verifying JSON structure...")
    try:
        parsed_data = json.loads(raw_output)
        print("[+] VERIFICATION PASSED: Output is strictly valid JSON.")
        print(f"    Action: {parsed_data.get('action_type')}")
        print(f"    Target: {parsed_data.get('target_path')}")
        print(f"    Reasoning: {parsed_data.get('reasoning')}")
    except json.JSONDecodeError:
        print("[-] VERIFICATION FAILED: Model produced malformed JSON.")

    print(f"\n[Performance Metrics]")
    print(f"- Load Time: {load_time:.2f}s")
    print(f"- Generation Time: {gen_time:.2f}s")
    print(f"- Generation Speed: {tps:.2f} Tokens/Second")
    print("="*50)
    print("NOTE: Please check your Windows Task Manager (Performance -> GPU) to observe VRAM usage.")

if __name__ == "__main__":
    run_stage1_benchmark()
