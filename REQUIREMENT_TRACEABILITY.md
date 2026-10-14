# FYP-1 requirement traceability

Updated 14 October 2026. Original roadmap plus the user's explicit amendments in SCOPE_DECISIONS.md. All development and acceptance target the single Windows laptop. Original multi-machine language is HISTORICAL / NO LONGER APPLICABLE. The roadmap states Python 3.11+, not an exact 3.11 pin; Python 3.14.3 satisfies that version range. Q8_0 is preserved by explicit instruction. No engineering gate is waived.

| Milestone | Status | Evidence / remaining boundary |
|---|---|---|
| 1.1 Environment | VERIFIED COMPLETE | reports/environment.json; Windows, Python 3.14.3 and tested dependency versions |
| 1.2 Qwen installation | VERIFIED COMPLETE | MODEL_RUNTIME.md; same weights, approved projector; target-laptop measurements |
| 1.3 Structured contracts | VERIFIED COMPLETE | Full-plan validation, canonical tools, reference validation; contract tests |
| 1.4 Planner instructions | COMPLETE WITH LIMITATION | Canonical catalog, untrusted memory, semantic distinctions; failures remain measurable |
| 1.5 20–30 planning prompts and metrics | COMPLETE WITH LIMITATION | All 25 cases audited; latency/TTFT/TPS/system resource measures; one sample per case is not statistical reliability |
| 1.6 Go/no-go | VERIFIED COMPLETE | Planning 25/25; production AES-256 and Option A recovery disposition verified. FYP-1 exit approved by evidence. |
| 2.1 State and agent permissions | COMPLETE WITH LIMITATION | Explicit prior-result text bindings, no forward/path/recipient binding; scoped agents |
| 2.2 Deterministic policy | COMPLETE WITH LIMITATION | Endpoint/path checks and denial tests; not a kernel sandbox |
| 2.3 Human approval | COMPLETE WITH LIMITATION | Strict True authorization and deny tests; no biometric/identity claim |
| 2.4 OS/files/accessibility | VERIFIED WITH LIMITATION | Real files, native Notepad acceptance, exact readback/audit and final real model-driven desktop workflow evidence; no OS-sandbox claim |
| 2.5 End-to-end workflows | VERIFIED WITH LIMITATION | 20/20 real model-driven isolated multi-agent workflows with observable file/browser postconditions; no arbitrary summarization claim |
| 2.6 Postconditions | COMPLETE WITH LIMITATION | File digests/readback, browser transitions, exact editable-control readback; delivery ambiguity remains |
| 3.1 Logical profiles | VERIFIED COMPLETE | Five tool profiles and deterministic security boundary, shared model |
| 3.2 Browser | COMPLETE WITH LIMITATION | Task-scoped state and cross-task isolation; loopback integration; authenticated existing user tabs not attached automatically |
| 3.3 Communication behavior and limits | VERIFIED WITH LIMITATION | Real model-driven authorized self-chat search/send, persistent quota, exact recipient/composer checks, curved pointer and typing pauses pass; no server-delivery API claim |
| 3.4 Research | COMPLETE WITH LIMITATION | Real local filename/content search; no web search or PDF summarization claim |
| 3.5 SQLite/Chroma memory | COMPLETE WITH LIMITATION | Restart/retrieval/persistence tested; memory is untrusted context |
| 3.6 Sanitization | COMPLETE WITH LIMITATION | HTML and instruction-data tests; no complete injection-defense claim |
| 3.7 Vision fallback | VERIFIED WITH LIMITATION | Approved projector, bounded foreground capture, real orange-target grounding and absent-purple rejection pass; no arbitrary-screen accuracy claim |
| 3.8 Encryption | VERIFIED COMPLETE | Complete production records/vectors/quota and minimum recovery snapshots use authenticated AES-256. DPAPI keys protected; archive extraction/recovery verified before unsealed runtime retirement. No SSD erasure claim. |
| 3.9 Tool security gate | VERIFIED COMPLETE | Canonical tools cross Python policy, approval and audit; unknown tools reject |
| 4.1 Cross-agent scenarios | VERIFIED WITH LIMITATION | AES initial run 19/20; numeric query adapter fixed; both memory-dependent cases rechecked 2/2 with no warnings. Passing coverage of all 20 cases, not a single post-fix full run. Deterministic outcomes 20/20. |
| 4.2 Twelve system metrics | VERIFIED WITH LIMITATION | Pre-cutover and AES live reports record all twelve metric families. Initial AES failure and affected recheck metrics remain separate; see AES256_POST_CUTOVER_AUDIT.md. |
| 4.3 Red team | COMPLETE WITH LIMITATION | Assertions/nonzero failures; expanded binding, quota and recipient tests; not exhaustive |
| 4.4 Target-laptop validation | COMPLETE WITH LIMITATION | Measured and tested on the sole approved laptop; system resource totals are not isolated allocations |
| 4.5 Audit | COMPLETE WITH LIMITATION | Attempts, approval/denial and outcomes; fail closed; not tamper-evident |
| 4.6 Defect closure | VERIFIED COMPLETE | Six planning failures and AES query-conversion defect closed with evidence; Option A disposition complete; no expected outputs changed. |
| 4.7 Documentation/demo/handoff | VERIFIED COMPLETE | Selected-production demo 4/4; final audit, traceability, sealed recovery procedure and residual limitations documented. No FYP-2 implementation. |

Repository-security residual: historical GitHub exposure is tracked separately; internal containment and prevention of new leakage remain mandatory. No FYP-2 implementation starts before a justified verified status.
