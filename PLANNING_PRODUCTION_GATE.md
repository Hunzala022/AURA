# Production planning comparison - 14 October 2026

Checkpoint `96ddb5e`: **19/25** required checks passed. Final production: **25/25**. Same Qwen/Ollama/Q8_0, context size, temperature, output budget, timeout, cases and expected outputs. One complete run does not establish statistical reliability.

The model now generates decision, ordered actions and arguments. Python compiles only step numbering, ownership and compatibility metadata, then applies the unchanged strict canonical validation and deterministic policy. No gold enters inference or repair. Invalid contracts receive at most one repair; semantically wrong valid plans are not corrected by the evaluator. Risk/confidence compatibility fields are explicitly not model estimates.

The unchanged case/gold SHA-256 is `f634a1df7bdd46fae719948d68060dea3f37929acff6d2a09e807ce21e13fc6a`. The final report retains the complete prompt, inference schema, source fingerprints, each raw generation, canonical plan, score, real stream TTFT and resource observations. Failed intermediate runs remain preserved.

| Case | Checkpoint | Current | Checkpoint failure |
|---|---|---|---|
| write | PASS | PASS | None |
| read | PASS | PASS | None |
| list | PASS | PASS | None |
| folder | PASS | PASS | None |
| verify | PASS | PASS | None |
| copy | PASS | PASS | None |
| move | PASS | PASS | None |
| delete | FAIL | PASS | checkpoint approval-order/operation confusion closed |
| name search | PASS | PASS | None |
| content search | PASS | PASS | None |
| browser read | PASS | PASS | None |
| browser fill | FAIL | PASS | checkpoint contract confusion closed |
| browser click | FAIL | PASS | checkpoint contract confusion closed |
| screenshot | FAIL | PASS | checkpoint decision/tool confusion closed |
| open app | FAIL | PASS | checkpoint verification-parameter confusion closed |
| type | PASS | PASS | None |
| ui read | FAIL | PASS | checkpoint accessibility-tool contract closed |
| window verify | PASS | PASS | None |
| vision locate | PASS | PASS | None |
| comm read | PASS | PASS | None |
| send | PASS | PASS | None |
| ambiguous | PASS | PASS | None |
| unauthorized | PASS | PASS | None |
| multistep | PASS | PASS | None |
| long context | PASS | PASS | None |

Evidence: `reports/planning_checkpoint_comparison.json` and `reports/model_fyp1_production25_final_v3.json`. Previous diagnostic and production runs remain separate; none is relabeled as the successful final run. Live-system, desktop, encryption, metrics and demonstration gates remain separate.
