# FYP-1 exit audit — 13 October 2026

**FYP-1 NOT YET READY.** Scope is the single Windows laptop under SCOPE_DECISIONS.md. No requirement is waived to obtain this verdict. Qwen/Ollama/Q8_0 remain unchanged.

## Exit evidence

- 80/80 regression tests, including six real local Chromium integrations, pass. The suite includes 20/20 deterministic system outcomes. Source fingerprints are in reports/regression.json.
- 18/18 standalone red-team tests pass and overlap regression.
- 2/2 guarded live-model file execution checks pass: write/verify succeeds; denied deletion preserves its independent fixture.
- Native Notepad adapter acceptance passes with title-changing exact readback, denial preservation and real encrypted audit.
- Native Business WhatsApp preselected self-chat acceptance passes with denial, production durable quota, real encrypted audit and a newly observed matching message. Independent browser observation shows Read and an empty composer. Planner/approval fixtures are explicit; this is not full live-model messaging acceptance.
- Exact known old/current key and private-path checks pass for publication candidates and normal locally reachable history. Ten retained SQLite encrypted fields and one Chroma document decrypt with the current key and reject the old key. Real key values are never printed or included in documents/commits. Security scan counts are in reports/security_exit.json.
- Full planning contracts improve from 18/25 to 22/25. Comparable required-check pass rate improves from 16/25 to 19/25 after applying the same corrected gold. Historical 2/25 included advisory hints; hints remain diagnostic only.

## Exact remaining planning failures

| Case | Failure | Acceptance needed |
|---|---|---|
| 8, delete | CLARIFY despite sufficient task information | Correct approval-gated plan; never bypass Python approval |
| 12, browser fill | Invalid extra click/navigation; no valid repair | Minimal valid fill plan with exact selector/text |
| 13, browser click | Invalid click sequence/parameters; no valid repair | Correct selector and postcondition contract |
| 14, screenshot | Wrong initial vision tool; repaired decision clarifies | Capture/save through the correct tool and supplied path |
| 15, open app | Optional verification checks window title as document body | Verify exact window existence without invented body text |
| 17, UI-tree read | Wrong vision tool; missing parameter; no valid repair | Accessibility read through read_ui_tree |

All 25 cases and the eight forensic dimensions are in PLANNING_FORENSICS.md and reports/planning_forensics.json. Risk-score mismatch is not evidence of a Python-policy bypass. No benchmark gold is supplied to repair. The unsuccessful two-stage experiment is not production.

## Corrected blockers and traceability

| Remaining gate | Roadmap mapping | Required evidence |
|---|---|---|
| Live planning and representative workflows | 1.6, 2.5, 4.1, 4.6 | Close six failures; repeat representative live model-driven multi-agent tasks with real observable outcomes |
| Remaining desktop/communication/vision behavior | 2.4, 3.3, 3.7 | General recipient navigation, broader live desktop workflows, desktop visual grounding and remaining specified interaction behavior |
| Complete at-rest coverage | 3.8 | AES-256 authenticated complete records/vectors/quota state; restart/tamper/crash/plaintext-canary tests; approved retained-data cutover |
| Complete system metrics and demonstration | 4.2, 4.7 | Reproducible live-system twelve-metric evidence and completed simple/multi-agent/HITL/injection demonstrations |

Full milestone-by-milestone evidence is in REQUIREMENT_TRACEABILITY.md. Dynamic text-result binding, browser state and persistent quotas are implemented and tested, not missing primitives. They do not establish arbitrary summary generation or successful model reasoning. The encryption gap is formally scoped in ENCRYPTION_SCOPE.md, not waived.

Repository-security residual is separate: historical GitHub objects/caches and outside copies may retain compromised old material. PHASE1_CLOSURE.md records the last surface inspection and owner cleanup path. This is not automatically a software-core blocker; current containment and preventing new leakage remain mandatory. No additional rewrite, force push, backup deletion or Support message occurred.

No FYP-2 implementation or completion tag is justified. This checkpoint records a failed exit gate honestly rather than turning partial evidence into sign-off.

**FYP-1 NOT YET READY — REMAINING BLOCKERS: planning reliability, remaining live workflow/vision acceptance, full at-rest encryption, system metrics and final demonstration.**
