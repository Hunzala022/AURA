# Corrected validation evidence

Verified 11 October 2026. Results distinguish deterministic execution, live planning, synthetic vision and live execution.

## Regression and execution fixtures

- 61/61 unittest tests passed with real loopback Chromium enabled; reports/regression.json includes source hashes and the captured result.
- 18/18 red-team tests passed through the standalone entry point; reports/red_team.json records exit status 0. These overlap the regression suite and are not additional independent coverage.
- 20/20 deterministic system scenarios met explicit expected status and observable postconditions. The planner and external agents were fixtures; file operations used real temporary directories.
- Four regression cases used real Chromium against a local HTTP fixture. Messaging/accessibility tests used mocks. No external messages were sent.
- Real SQLite/Chroma persistence, ciphertext readback and four key-management tests are included.

## Live model planning: original 25-case run

All 25 requests used the approved projector-equipped alias and unchanged Q8_0 weights. No tools executed. This run began before the later tool-specific generation schema and prompt refinements; do not call it a full validation of the final prompt.

| Dimension | Passing cases / 25 |
|---|---:|
| Full Python schema/parameter contract | 20 |
| Decision matches expected | 17 |
| Tool selection | 16 |
| Parameters | 16 |
| Deterministic policy risk for the plan | 17 |
| Model risk hint matches the scoring convention | 1 |
| Required tool order | 15 |
| All dimensions including model risk hint | 1 |

Fifteen cases meet all dimensions except the advisory model-risk comparison. Model-risk hints never authorize execution. The prompt states broad risk rules but does not enumerate the exact trusted workspace path or every protected filename; hint agreement is therefore a diagnostic calibration measure, not a proof of policy enforcement. The strict combined score is not an observed task-completion rate.

The original raw results are preserved in reports/model_validation.json. reports/model_validation_rescored.json recomputes their scores using current path normalization and an explicit, separate model-risk comparison; no new model responses are fabricated. For empty plans the scoring convention expects a low model hint and no execution risk. The original prompt did not specify that convention, so this is a stricter diagnostic rescore, not a retroactive claim about original test instructions.

Observed median latency was 44.47 s, median TTFT 0.81 s and median generation rate 5.99 tokens/s. Maximum observed GPU total usage was 5,820 MiB and system RAM usage 15,588 MiB. Some later requests overlapped targeted inference checks; queue contention affects latency/TTFT. CPU/RAM/VRAM are system totals, not isolated model allocations. These are not clean hardware-comparison measurements.

## Targeted contract repair

Three subsequent live requests used tool-specific parameter constraints in the generation schema. All three produced schema-valid plans, but none passed every strict dimension:
- Deletion: clarified instead of producing an approval-gated plan.
- Browser read: correct tool and parameters, but model risk was medium rather than policy high.
- Browser fill: added an extra page read and underestimated risk.

reports/model_targeted_contract_repair.json contains raw evidence and prompt/schema hashes. Later prompt clarifications cover approval-gated paths and write/verify semantics. The typed generation schema repeatedly failed a live write task; the generic generation schema passed both isolated live checks and was restored. Strict Python per-tool validation remains mandatory. A separate final 25-case report records the shipped configuration. Generation options in the runtime and benchmark now share temperature 0, context 4096 and a 768-token limit.

## Vision

The original custom import rejected images because its projector was missing. With the checksum-matched projector, red/blue recognition passed 2/2; normalized-coordinate grounding returned a point inside the synthetic green target. The earlier pixel-coordinate failure remains in its report. These are minimal synthetic probes, not a desktop grounding benchmark.

## Acceptance

Live execution evidence is in reports/live_execution.json: 2/2 checks passed with the restored generic generation schema. Earlier failures are preserved in live_execution_initial.json, live_execution_before_semantics.json and live_execution_typed_schema.json. The first report coupled deletion setup to the failed write; subsequent runs use independent fixtures. It uses a real planner, temporary files and encrypted audit stores, with an exact-operation test guard and explicit approval fixtures. It does not validate external messaging, arbitrary desktop actions or an unguarded production workflow.

Live task reliability, second-machine metrics and real desktop acceptance remain incomplete. No single aggregate pass percentage establishes FYP-1 completion.

## Final shipped-configuration run

reports/model_final_validation.json contains all 25 responses with prompt/schema hashes. Summary: schema 18/25, decision 17/25, tools 16/25, parameters 16/25, policy risk 17/25, model-risk hint 2/25, strict order 15/25, all non-advisory checks 14/25, all strict dimensions 2/25. Median latency 32.66 s, TTFT 0.75 s, generation 6.07 tokens/s; maximum observed GPU total 5,245 MiB and system RAM 14,936 MiB. This run had no concurrent inference benchmark. It remains a single-pass planning-only measurement on one machine, not live task accuracy.
