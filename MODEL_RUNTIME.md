# Current local inference runtime

Updated 11 October 2026. Current runtime: Ollama 0.34.3; reasoning alias `aura-qwen:latest`; Qwen3.5-4B Q8_0 language weights unchanged.

## Approved projector repair

The original custom import lacked a vision projector. A synthetic image request returned HTTP 500 with an explicit image-not-supported/mmproj error. Family metadata was not used as proof of runtime capability.

The user approved repairing the projector for the same model and quantization. Publisher metadata matched the installed language blob exactly:

- Language SHA256: `5c74c0ede371924357dff0cb6ba145bd67208b9b2389ded681adfff3f7608db7` (4,622,131,168 bytes).
- Matching F16 projector SHA256: `659b59dd44b73b1cd34af6cc424669484b06dc80f4340adf8ea84ad776eef813` (672,423,488 bytes).
- Publisher: [bartowski/Qwen_Qwen3.5-4B-GGUF](https://huggingface.co/bartowski/Qwen_Qwen3.5-4B-GGUF/tree/main).
- New alias digest: `6992631ea5c6e3bec0a3c68aee984674efe563d742be9297ef0f89dab3934bac`.
- Original alias retained as `aura-qwen-prevision-20261010:latest`; original show/config response is in ignored `.aura-private/ollama-prevision.json`.

The F16 projector does not change the Q8_0 language weights. No Ollama upgrade, language-model replacement, or alternate reasoning model was introduced. Ollama's native import configuration handles the model renderer.

## Reproduction

The original `Modelfile` is a **legacy text-only import recipe**. Do not use it to reconstruct the repaired multimodal alias. With the original language blob already present, obtain the named projector from the publisher and run:

```powershell
python configure_projector.py models/mmproj-Qwen_Qwen3.5-4B-f16.gguf
```

This checks the projector checksum and creates only `aura-qwen-vision-candidate`. Test the candidate before explicitly copying it onto the active alias. The development installation has already passed the synthetic tests and been activated with user authorization. Rollback, if required, is `ollama cp aura-qwen-prevision-20261010:latest aura-qwen:latest`; it restores the known image-incompatible configuration.

## Evidence and limits

Reports preserve the original failing image request, two passing color tests, the failed pixel-coordinate assumption, and the subsequent passing normalized-coordinate grounding test. The client now explicitly requests normalized 0â€“1000 coordinates, validates them, and converts to image pixels. A location response never claims a click or verified action. Screenshots are not saved implicitly.

These synthetic cases establish functioning image input and a basic location case, not general desktop grounding accuracy. Live desktop interaction, varied screenshot sizes/DPI, and task-level vision reliability require separate acceptance tests. The accessibility route remains primary.

## Planner limits

Current control-plane and benchmark generation options are temperature 0, context 4096 and maximum 768 generated tokens, with thinking disabled. Each request has a 180-second timeout. A parsed invalid contract permits one additional request containing validation errors; the replacement must pass the complete Python contract. Malformed JSON, unavailable inference and unsuccessful repair fail closed. No effect is retried. Benchmark elapsed time includes repair; TTFT/TPS refer to the initial generation. Earlier reports retain their original configurations.
