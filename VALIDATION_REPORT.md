# Final validation evidence — 14 October 2026

**FYP-1 VERIFIED — READY FOR FYP-2**

| Check | Result | Evidence |
|---|---|---|
| Production planning | 25/25 required; checkpoint 96ddb5e was 19/25 | reports/model_fyp1_production25_final_v3.json |
| Regression | 110/110, browser enabled | reports/regression.json |
| Deterministic outcomes | 20/20 | reports/stage4_system.json |
| Red team | 18/18, overlaps regression | test_red_team_4_3.py and regression evidence |
| Pre-cutover live workflows | 20/20 | reports/live_workflows_gate_v7.json |
| Initial AES live workflows | 19/20, retrieval defect found | reports/live_workflows_aes256.json |
| Repaired affected live cases | 2/2, no retrieval warnings | reports/live_workflows_aes256_memory_recheck.json |
| Native model-driven desktop | 4/4 | reports/live_desktop_v2.json |
| Real desktop vision | 2/2 | reports/desktop_vision_live_v3.json |
| Authorized self-chat | Denial/send 2/2; search/send PASS | reports/live_messaging.json; reports/live_message_navigation_v6.json |
| Final selected-production demo | 4/4, no retrieval warnings | reports/fyp1_demo_aes256_final.json |
| Production AES restart/recovery | PASS | reports/aes256_cutover_validation.json |
| Option A archive extraction/recovery | 14 file hashes and both recovery paths PASS | reports/legacy_disposition.json |
| Final targeted disposition validation | PASS; 12 sessions, 39 audits, 1 memory, 5 quota unchanged | reports/legacy_disposition_validation.json |

The NumPy query-adapter defect is fixed and covered by regression. All 20 live
cases have passing evidence; the initial full AES run and targeted rechecks are
separate runs, not a claimed single post-fix 20/20 run.

No production/core/agent/test source changed after the 110-test run. Disposition
added recovery utilities and documentation only. No unrelated model, planner,
desktop, WhatsApp, vision or benchmark suite was repeated.

Prior Stage 4 metrics remain in their original reports. The full initial AES run
measured 6.25 tok/s mean generation, 2.24 s pipeline TTFT, 5,181 MB total GPU peak,
14,353 MB system RAM and 84.3% CPU. Its 19/20 outcome is preserved. The two affected
rechecks measured 6.14 tok/s and 1.97 s pipeline TTFT. System totals include other
processes; these are not a combined performance estimate.

Twenty verified redundant runtime/test targets were retired after authenticated
archive extraction. No known unsealed runtime store remains in the intended
project/recovery locations. Active and recovery stores are ignored and untracked.
Historical Git repositories/bundles remain separately retained under instruction;
remote exposure and SSD remnants are not claimed erased. See
FINAL_FYP1_EXIT_AUDIT_20261014.md and LEGACY_MATERIALS_RETAINED.md.
