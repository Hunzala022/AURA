import time
import json
import psutil
from llama_cpp import Llama
from core.schema import ToolCallSchema
from core.prompt import BASE_SYSTEM_PROMPT

def measure_vram_placeholder():
    # Accurately measuring VRAM in Python on Windows usually requires pynvml or nvidia-smi.
    # We will log system RAM and prompt user to check VRAM, or we can use a basic estimate.
    # For robust VRAM, one would use:
    # import subprocess; subprocess.run(['nvidia-smi'])
    pass

def run_benchmark():
    model_path = "models/Qwen_Qwen3.5-4B-Q8_0.gguf"
    
    print("="*50)
    print("A.U.R.A STAGE 1 - MODEL ACQUISITION & RAW VALIDATION")
    print("="*50)
    
    # 1. Measure load time
    start_load = time.time()
    try:
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,  
            n_ctx=4096, # Long context for orchestrator
            verbose=False
        )
    except Exception as e:
        print(f"[!] Model load failed. Please ensure the path is correct and llama-cpp-python is installed.")
        print(e)
        return
        
    load_time = time.time() - start_load
    print(f"[+] Model loaded in {load_time:.2f} seconds.")
    
    # User Command
    user_command = "AURA, I want to delete the old project folder at C:\\Archive\\old_project. It's taking up too much space."
    
    # 2. Generation & Metrics
    print(f"\n[*] Sending command: '{user_command}'")
    print("[*] Waiting for first token...")
    
    start_gen = time.time()
    
    # Stream the output to capture first-token latency
    stream_response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": BASE_SYSTEM_PROMPT},
            {"role": "user", "content": user_command}
        ],
        response_format={
            "type": "json_object",
            "schema": ToolCallSchema.model_json_schema()
        },
        temperature=0.1,
        stream=True
    )
    
    first_token_time = None
    output = ""
    tokens_generated = 0
    
    for chunk in stream_response:
        if first_token_time is None:
            first_token_time = time.time() - start_gen
            print(f"[+] First token latency: {first_token_time:.2f}s")
            
        delta = chunk["choices"][0]["delta"]
        if "content" in delta and delta["content"] is not None:
            output += delta["content"]
            tokens_generated += 1

    total_gen_time = time.time() - start_gen
    tps = tokens_generated / total_gen_time if total_gen_time > 0 else 0
    
    print("\n[==== RAW OUTPUT ====]")
    print(output)
    print("[====================]\n")
    
    # 3. Validate Output against Schema
    try:
        parsed = json.loads(output)
        validated_call = ToolCallSchema(**parsed)
        print("[+] SCHEMA VALIDATION: PASS")
        print(f"    Tool: {validated_call.tool_name}")
        print(f"    Reasoning: {validated_call.reasoning}")
        print(f"    Risk: {validated_call.risk_hint}")
    except Exception as e:
        print(f"[-] SCHEMA VALIDATION: FAIL")
        print(f"    Error: {e}")
        
    print("\n[==== RAW METRICS ====]")
    print(f"- Load Time         : {load_time:.2f} s")
    print(f"- First Token Latency: {first_token_time:.2f} s")
    print(f"- Generation Speed  : {tps:.2f} tokens/sec")
    print(f"- Tokens Generated  : {tokens_generated}")
    print(f"- Context Window    : 4096 tokens allocated")
    print("="*50)
    print("NOTE: Run 'nvidia-smi' in another terminal while this runs to record exact VRAM used at idle and under load.")

if __name__ == "__main__":
    run_benchmark()
