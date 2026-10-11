# FYP-1 remediation checkpoint â€” 11 October 2026

FYP-1 is **not signed off**. This checkpoint contains verified repairs, passing deterministic tests and explicit evidence of remaining live-planning failures. It is not a completed FYP-1 baseline.

## 1. What works

The canonical 22-tool contract, complete-plan preflight, caller agent boundaries, deterministic risk policy, approval denial, exception handling, observable file/browser postconditions and encrypted session/audit persistence are tested. The same Qwen3.5-4B Q8_0 weights now accept images with the approved matching projector. A guarded live write-and-verify task completed; a separate live deletion plan was denied and its fixture remained intact.

## 2. Original ten findings

| # | Finding and root cause | Resolution / evidence | Remaining limit |
|---|---|---|---|
| 1 | Public key and runtime files tracked | Rotated/migrated current data; cleaned reachable history; ignored stores; key/object scans and containment tests | Known old GitHub commit still resolves; private recovery copies intentionally retained |
| 2 | Prompt advertised 14 unimplemented names | core/tools.py catalog generates prompt and routing contracts; all 22 resolve, all 14 old names reject | Unsupported requests still need clarification |
| 3 | Stage 4.1 mismatches counted as passes | core/evaluation.py scores decision, tools, parameters, order and risk independently; runner exits nonzero on failure | Planning-only results do not establish execution success |
| 4 | Stage 4.2 ignored actual task outcome | 20 isolated cases compare expected status, execution semantics and observable postconditions | External agents/planner are mocked in this suite |
| 5 | Red team lacked assertions/failure exit | Standalone unittest runner; 18/18 assertions-based tests pass, process status recorded | Not exhaustive adversarial assurance |
| 6 | Air-gap claim contradicted network tools | Current README/status describe local inference plus online browser/communication capabilities | Air-gapped operation is not claimed |
| 7 | Tool exceptions escaped the execution loop | Structured failure boundary halts later steps and preserves prior effects/audits | General rollback is not implemented |
| 8 | Vision capability incorrectly dismissed | Missing-projector error reproduced; exact-weight-compatible F16 projector added with backup and approval | Synthetic image probes do not prove arbitrary desktop grounding |
| 9 | Fernet mislabeled AES-256 | Current docs accurately describe AES-128-CBC plus HMAC-SHA256 and plaintext metadata/vectors | Roadmap all-data AES-256 requirement remains unmet |
| 10 | Stale dependency list | Active runtime requirements plus validated direct versions and environment report | Python 3.11 and second hardware configuration are unverified |

Additional verified repairs cover independent copy/move endpoint policy, path normalization and Windows alternate data streams, executable-source protection, vision found:false/error handling, exact messaging recipient/text checks, empty-content verification and missing-file false-success handling. Detailed problem/change/test/limit mapping is in FYP1_STATUS.md.

## 3. Test evidence

- **61/61 regression tests** pass, including four real loopback Chromium checks, real temporary file operations, SQLite/Chroma persistence and four key-management tests.
- **18/18 red-team tests** pass; these overlap the regression suite.
- **20/20 deterministic system expectations** pass, including expected denial and failure cases. This does not mean 20 successful live-model tasks.
- **2/2 isolated live execution checks** pass with the shipped generic generation schema and strict Python validation. The test guard permits only exact synthetic operations; approvals are fixtures.
- Two synthetic color probes and one normalized-coordinate grounding probe passed after projector repair. Earlier failing probes are retained.

reports/regression.json records the tested source hashes. reports/live_execution*.json retain the failed schema experiments and corrected independent test setup.

## 4. Final live planning evidence

The final 25-case single-pass run uses the shipped prompt/schema, unchanged Q8_0 language weights and shared generation settings. It executes no tools.

| Dimension | Passing / 25 |
|---|---:|
| Full Python plan/parameter contract | 18 |
| Decision | 17 |
| Tool selection | 16 |
| Parameters | 16 |
| Deterministic policy risk | 17 |
| Model risk hint agreement | 2 |
| Strict expected tool order | 15 |
| All checks excluding advisory model hint | 14 |
| All strict checks | 2 |

These are separate planning dimensions, not a task-success rate. Expected ordering is strict, and model hints use the benchmark's risk convention. Python policy always remains authoritative.

Observed median latency: **32.66 s**; median TTFT: **0.75 s**; median generation: **6.07 tokens/s**. Maximum sampled GPU total usage: **5,245 MiB**; system RAM: **14,936 MiB**. One 6 GB machine, one sample per case and system-wide resource sampling do not establish a hardware-comparison result. See VALIDATION_REPORT.md and reports/model_final_summary.json.

A tested tool-specific generation constraint improved syntax in three targeted cases but repeatedly confused write and verification. It was reverted after the generic schema passed both live execution checks. Strict per-tool Python validation was never removed. No broad model-accuracy improvement is claimed.

## 5. Security posture

Internal containment is closed for the known exposed key and paths. Current private runtime stores remain local and ignored. No old or new key values are included in terminal output, documentation or this checkpoint.

Remaining HIGH findings concern live task reliability, incomplete at-rest coverage relative to the roadmap and retained historical GitHub exposure. The old commit API still returned HTTP 200 on 11 October. The owner cleanup draft and exact rewrite evidence are retained privately; no Support contact or destructive remote action occurred.

The application is not an OS sandbox. Same-user malware, path races, operator-approved exfiltration, incomplete prompt-injection filtering, GUI ambiguity, restart-reset communication limits and non-tamper-evident logging remain threat-model limits. No absolute security guarantee is made.

## 6. Architecture

Local model plan -> full Python contract/agent validation -> deterministic policy -> explicit approval when HIGH -> audited execution -> observable verification -> final encrypted session record. A failed or invalid plan never becomes a successful task merely because inference returned JSON or Python did not throw.

## 7. Documentation

Authoritative: README.md, FYP1_STATUS.md, MODEL_RUNTIME.md, TOOL_MAP.md, PHASE1_CLOSURE.md, VALIDATION_REPORT.md and REQUIREMENT_TRACEABILITY.md. Historical stage summaries are explicitly labeled. Original handovers/reference documents and the owner cleanup draft remain in ignored private storage.

The official roadmap's AS608 and WebSocket direction supersedes legacy R307/HTTP/serial suggestions. This reconciliation is not a FYP-2 implementation plan.

## 8. Git checkpoint

Authoritative checkout: D:\Project AURA\.aura-private\post-clean-check, master, descending from cleaned commit c4d1a5111835d265e0683accff6f8c0abceaeea2. main remains the cleaned historical branch at 999bd8be304f46022fa4fc4bcf5b33f63f7f44cc. The commit containing this report is an ordinary remediation checkpoint, not a release/completion tag. Publication identity is recorded privately after pushing and in the user-facing completion message.

No old Git directory or contaminated refs were transferred. No further rewrite, force push, branch deletion or backup deletion was performed.

## 9. Remaining blockers

1. Live planner contract/task reliability must improve and pass representative acceptance checks.
2. The user confirmed that no 12 GB GPU machine is available yet; its required comparison is pending, not waived.
3. Real desktop and messaging acceptance remains incomplete; no external message was sent in these tests.
4. Full at-rest encryption requires an approved design/scope decision before migration of retained user data.
5. Dynamic tool-result binding, stateful browser workflows and persistent per-platform daily communication limits remain incomplete.
6. Residual GitHub sensitive-object cleanup requires repository-owner review/action; external copies cannot be revoked.

## 10. FYP-2 readiness

FYP-2 cannot be signed off to begin on this evidence. No hardware implementation or formal FYP-2 milestone plan was started.

**FYP-1 NOT YET READY â€” REMAINING BLOCKERS: live planning reliability, unavailable second hardware, desktop/messaging acceptance, encryption and workflow gaps, and residual GitHub exposure.**
