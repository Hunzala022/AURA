# FYP-1 requirement traceability

Updated 13 October 2026. Original roadmap plus the user's explicit amendments in SCOPE_DECISIONS.md. All development and acceptance target the single Windows laptop. Original multi-machine language is HISTORICAL / NO LONGER APPLICABLE. The roadmap states Python 3.11+, not an exact 3.11 pin; Python 3.14.3 satisfies that version range. Q8_0 is preserved by explicit instruction. No engineering gate is waived.

| Milestone | Status | Evidence / remaining boundary |
|---|---|---|
| 1.1 Environment | VERIFIED COMPLETE | reports/environment.json; Windows, Python 3.14.3 and tested dependency versions |
| 1.2 Qwen installation | VERIFIED COMPLETE | MODEL_RUNTIME.md; same weights, approved projector; target-laptop measurements |
| 1.3 Structured contracts | VERIFIED COMPLETE | Full-plan validation, canonical tools, reference validation; contract tests |
| 1.4 Planner instructions | COMPLETE WITH LIMITATION | Canonical catalog, untrusted memory, semantic distinctions; failures remain measurable |
| 1.5 20–30 planning prompts and metrics | COMPLETE WITH LIMITATION | All 25 cases audited; latency/TTFT/TPS/system resource measures; one sample per case is not statistical reliability |
| 1.6 Go/no-go | NOT COMPLETE | Live semantic failures and full-pipeline acceptance remain |
| 2.1 State and agent permissions | COMPLETE WITH LIMITATION | Explicit prior-result text bindings, no forward/path/recipient binding; scoped agents |
| 2.2 Deterministic policy | COMPLETE WITH LIMITATION | Endpoint/path checks and denial tests; not a kernel sandbox |
| 2.3 Human approval | COMPLETE WITH LIMITATION | Strict True authorization and deny tests; no biometric/identity claim |
| 2.4 OS/files/accessibility | COMPLETE WITH LIMITATION | Real files and native Notepad adapter acceptance with exact readback/audit; planner/approval fixtures; broader live desktop workflows open |
| 2.5 End-to-end workflows | PARTIALLY COMPLETE | Real loopback browser fill/click/read-to-file binding; deterministic planner fixture; live file checks separate |
| 2.6 Postconditions | COMPLETE WITH LIMITATION | File digests/readback, browser transitions, exact editable-control readback; delivery ambiguity remains |
| 3.1 Logical profiles | VERIFIED COMPLETE | Five tool profiles and deterministic security boundary, shared model |
| 3.2 Browser | COMPLETE WITH LIMITATION | Task-scoped state and cross-task isolation; loopback integration; authenticated existing user tabs not attached automatically |
| 3.3 Communication behavior and limits | PARTIALLY COMPLETE | Durable atomic reservations/global ceiling; native self-chat send with policy/audit and denial accepted; general recipient navigation and full interaction behavior open |
| 3.4 Research | COMPLETE WITH LIMITATION | Real local filename/content search; no web search or PDF summarization claim |
| 3.5 SQLite/Chroma memory | COMPLETE WITH LIMITATION | Restart/retrieval/persistence tested; memory is untrusted context |
| 3.6 Sanitization | COMPLETE WITH LIMITATION | HTML and instruction-data tests; no complete injection-defense claim |
| 3.7 Vision fallback | PARTIALLY COMPLETE | Approved projector and synthetic grounding; real desktop grounding acceptance open |
| 3.8 Encryption | NOT COMPLETE | ENCRYPTION_SCOPE.md; selected-payload Fernet is not AES-256/all-at-rest |
| 3.9 Tool security gate | VERIFIED COMPLETE | Canonical tools cross Python policy, approval and audit; unknown tools reject |
| 4.1 Cross-agent scenarios | PARTIALLY COMPLETE | 20 deterministic scenario outcomes plus browser binding integration; not 20 real multi-agent model executions |
| 4.2 Twelve system metrics | PARTIALLY COMPLETE | Planning metrics and isolated live execution; full live system task/long-context/injection coverage incomplete |
| 4.3 Red team | COMPLETE WITH LIMITATION | Assertions/nonzero failures; expanded binding, quota and recipient tests; not exhaustive |
| 4.4 Target-laptop validation | COMPLETE WITH LIMITATION | Measured and tested on the sole approved laptop; system resource totals are not isolated allocations |
| 4.5 Audit | COMPLETE WITH LIMITATION | Attempts, approval/denial and outcomes; fail closed; not tamper-evident |
| 4.6 Defect closure | PARTIALLY COMPLETE | Current remaining failures explicitly recorded in exit audit |
| 4.7 Documentation/demo/handoff | PARTIALLY COMPLETE | Current technical truth documented; full software acceptance and demo sign-off not complete |

Repository-security residual: historical GitHub exposure is tracked separately; internal containment and prevention of new leakage remain mandatory. No FYP-2 implementation starts before a justified verified status.
