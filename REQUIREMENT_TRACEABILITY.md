# FYP-1 requirement traceability

Source: A.U.R.A. â€” Full Build Roadmap (FYP-1 + FYP-2), all nine pages. Audited 11 October 2026. Status concerns demonstrated implementation, not intended features. No requirement below is DEFERRED WITH APPROVAL; approval to preserve Q8_0/add its projector is not approval to waive acceptance gaps.

| Milestone / requirement | Status | Evidence and limit |
|---|---|---|
| 1.1 Environment on both target PCs | PARTIALLY COMPLETE | reports/environment.json; current Windows/Python 3.14.3 only; Python 3.11 and second PC unverified |
| 1.2 Qwen installation and hardware comparison | PARTIALLY COMPLETE | MODEL_RUNTIME.md; exact Q8_0 retained per explicit user constraint, superseding the original Q4_K_M proposal; 6 GB measured, second device pending |
| 1.3 Structured plan/schema and hand examples | VERIFIED COMPLETE | core/schema.py; tests/test_contracts.py; runtime rejects invalid full plans |
| 1.4 Planner prompt/tool instructions | COMPLETE WITH DOCUMENTED LIMITATION | Generated canonical catalog, untrusted-data separation; live task accuracy separate |
| 1.5 20â€“30 prompts and metric collection | PARTIALLY COMPLETE | validate_model.py has 25 cases, TTFT/TPS/latency/system resource samples; correctness separately scored; second machine absent |
| 1.6 Formal go/no-go | NOT COMPLETE | Live failures and other exit blockers remain; no go decision issued |
| 2.1 State manager/agent permissions | COMPLETE WITH DOCUMENTED LIMITATION | Caller agent scope, step records, contract tests; no dynamic result binding |
| 2.2 Deterministic policy | COMPLETE WITH DOCUMENTED LIMITATION | Both endpoints, traversal/case/sensitive/outside paths, caller scope tested; no kernel sandbox/TOCTOU guarantee |
| 2.3 Human approval | COMPLETE WITH DOCUMENTED LIMITATION | Explicit yes/no, strict True check, deny tests; not identity authentication |
| 2.4 OS/file/accessibility tools | PARTIALLY COMPLETE | Real file tests; accessibility mocked, live desktop acceptance incomplete |
| 2.5 End-to-end planning/execution | PARTIALLY COMPLETE | Deterministic full-pipeline cases; live-model reliability and output binding incomplete |
| 2.6 Post-action verification | COMPLETE WITH DOCUMENTED LIMITATION | File readback/hashes, browser observations, UI checks; message server delivery not independently verified |
| 3.1 Agent profiles/shared model | VERIFIED COMPLETE | One alias, five tool profiles, separate deterministic security policy |
| 3.2 Browser agent | COMPLETE WITH DOCUMENTED LIMITATION | Four real loopback Chromium tests; fresh-page semantics, internet sites not covered |
| 3.3 Communication/human interaction/limits | PARTIALLY COMPLETE | Recipient/text validation, hourly limiter, randomized pause; real apps, daily platform limits and full behavior incomplete |
| 3.4 Research/search | COMPLETE WITH DOCUMENTED LIMITATION | Real filename glob/content searches; recursive search requires approval; no web search tool |
| 3.5 SQLite/Chroma persistent contextual memory | COMPLETE WITH DOCUMENTED LIMITATION | Real restart/readback test, context supplied as untrusted data; learning/improved behavior not measured |
| 3.6 Sanitization/instruction-data boundary | COMPLETE WITH DOCUMENTED LIMITATION | HTML/script stripping and memory role tests; regex is not a complete injection defense |
| 3.7 Accessibility-first vision fallback | PARTIALLY COMPLETE | Mocked routing and live synthetic color/grounding tests; real desktop task acceptance incomplete |
| 3.8 AES-256/all-at-rest encryption | PARTIALLY COMPLETE | Selected payload Fernet and rotation verified; AES-128-CBC and plaintext vectors/metadata differ from requirement |
| 3.9 Gate all new tools | VERIFIED COMPLETE | All 22 cross actual risk policy; high-risk denials prevent mocked executor calls |
| 4.1 15â€“25 cross-agent/failure scenarios | COMPLETE WITH DOCUMENTED LIMITATION | 20 deterministic full-pipeline outcomes; planner/external effects are fixtures; live cross-agent acceptance remains |
| 4.2 Twelve-metric system benchmark | PARTIALLY COMPLETE | Observable deterministic results plus live planning metrics; live task success/failure/resource attribution not complete |
| 4.3 Red-team assertions | COMPLETE WITH DOCUMENTED LIMITATION | Executable unittest assertions and nonzero exit, full-pipeline attacks; no exhaustive adversarial guarantee |
| 4.4 Both hardware configurations | NOT COMPLETE | Only 6 GB GPU available; user explicitly confirmed 12 GB machine is not available yet |
| 4.5 High-risk audit logging | COMPLETE WITH DOCUMENTED LIMITATION | Attempt/approval/denial/outcome persisted; fail-closed tests; not tamper-evident |
| 4.6 Defect closure | PARTIALLY COMPLETE | Audit defects repaired; acceptance and residual security findings in FYP1_STATUS.md |
| 4.7 Documentation/demo/handoff | PARTIALLY COMPLETE | Current truth documented; real demo acceptance and FYP-2 sign-off not complete |

FYP-1 is not signed off. Additional hardware evidence, desktop acceptance and encryption/scope decisions cannot be inferred from passing unit tests.
