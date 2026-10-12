# AURA remediation checkpoint — 13 October 2026

**FYP-1 NOT YET READY.** This report supersedes checkpoint 8980a05; the earlier report remains historical evidence in Git.

## Scope and verified changes

The user's single Windows laptop with approximately 6 GB VRAM is the complete development, benchmark, validation and demonstration target. SCOPE_DECISIONS.md supersedes historical comparison language. Python policy is authoritative; model risk hints are advisory. Historical GitHub exposure is a separate repository-security residual.

Qwen3.5-4B Q8_0, Ollama and the approved projector remain unchanged. Production now includes explicit tool semantics and one bounded contract repair; semantically wrong valid plans are not silently corrected. Canonical 22-tool validation, agent scope, approval, audit, failure handling and postconditions remain mandatory.

Validated prior-step text bindings, isolated stateful browser sessions and durable atomic hourly/daily communication reservations are implemented. Notepad typing follows its editable control through title changes. Messaging uses typed controls at Chromium's actual accessibility depth, preserves drafts, verifies literal input and recipient identity, and requires a new matching message. An already verified conversation is retained instead of unnecessarily searching again. Literal Unicode fallback does not interpret text as shortcuts; focus changes, control characters, unsupported supplementary codepoints and incomplete readback stop before send.

## Results

| Check | Result |
|---|---:|
| Regression, including six real Chromium cases | 80/80 |
| Deterministic system outcomes | 20/20 |
| Standalone red team, overlapping regression | 18/18 |
| Isolated live-model execution | 2/2 |
| Native Notepad, denied/approved paths | PASS |
| Native Business WhatsApp self-chat, denied/approved paths | PASS |
| Known-key/history/private-state containment | PASS |
| Live planning contracts | 22/25 |
| All required planning checks | 19/25 |

Equivalent corrected-gold planning is **16/25 old versus 19/25 current**. The old 2/25 combined score included advisory hints; excluding them originally gave 14/25, and gold corrections raised the comparable baseline to 16/25. Hint agreement remains 2/25 and is not a gate. Current median planning latency is 38.36 s; VALIDATION_REPORT.md defines metrics and limitations.

All 25 cases are decomposed in PLANNING_FORENSICS.md and reports/planning_forensics.json. Six failures remain: deletion decision, browser-fill contract, browser-click contract, screenshot decision/tool, launch-verification parameters and UI-tree-read contract. The two-stage planning experiment failed its two completed cases and was not promoted.

Native acceptance uses planner/approval fixtures with real policy, audit and UI effects. Separate isolated live checks use the actual model. These do not establish unguarded model-to-messaging reliability. One external-control self-send preceded one successful native self-send. Failed native attempts stopped before sending; synthetic partial drafts were explicitly cleared after inspection. Only synthetic acceptance text went to the authorized Business WhatsApp self-chat.

## Original ten findings

| Finding | Current disposition |
|---|---|
| Exposed key/runtime files | Current key rotated and retained data migrated previously; normal reachable history/candidates scan clean; external historical copies remain a separate risk |
| Ghost tools | Canonical catalog owns prompt/schema/dispatch; old unimplemented names reject |
| Planning mismatches passed | Independent required dimensions, corrected gold, advisory separation and nonzero failure exit |
| Outcomes not evaluated | Explicit expected statuses and observable postconditions in 20 deterministic scenarios |
| Red team always succeeded | Assertions/nonzero failure exit; 18 pass |
| Air-gap claim | Corrected: local inference plus potentially online tools |
| Unhandled exceptions | Structured failure halts later steps and records prior effects; no general rollback |
| Missing vision capability | Approved compatible projector works on unchanged weights; desktop grounding acceptance open |
| Fernet mislabeled AES-256 | Accurate AES-128-CBC/HMAC description; full-at-rest gap scoped, not waived |
| Stale dependencies | Tested direct versions documented; Python 3.14.3 satisfies roadmap Python 3.11+ |

## Corrected remaining software blockers

1. Resolve six live-planning failures and validate representative model-driven workflows.
2. Complete desktop-vision acceptance, general recipient-navigation acceptance, remaining roadmap communication interaction behavior and representative live multi-agent scenarios. Controlled native desktop/self-chat acceptance is closed within its documented scope.
3. Implement and verify full-record/vector/quota at-rest encryption. ENCRYPTION_SCOPE.md defines the protected set and non-destructive migration gates. Formal scope is not a waiver or retained-data cutover approval.
4. Complete the live-system twelve-metric evaluation and reproducible demonstration/sign-off.

Result binding, browser state and persistent quotas are no longer missing primitives. They do not imply arbitrary PDF summarization or successful general multi-agent reasoning.

## Security and publication

Real old/current encryption key values are never printed, committed or documented. Private keys, databases, recovery copies and screenshots remain ignored. Retained ciphertext decrypts with the current key and rejects the old key. Known historical GitHub objects/external copies remain a repository-security residual tracked in PHASE1_CLOSURE.md, not an automatic software-core blocker.

Authoritative checkout: D:\Project AURA\.aura-private\post-clean-check, cleaned master descending from 8980a05. This is an ordinary checkpoint, not a completion/release tag. No new rewrite, force push, branch/backup deletion, model switch, Support contact or FYP-2 implementation occurred. Publication identity is recorded after the ordinary push.

Final milestone evidence is in REQUIREMENT_TRACEABILITY.md and FYP1_EXIT_AUDIT.md. Current contracts and limitations are in FYP1_STATUS.md, VALIDATION_REPORT.md, PLANNING_FORENSICS.md, DESKTOP_MESSAGING_ACCEPTANCE.md, ENCRYPTION_SCOPE.md, WORKFLOW_CONTRACTS.md, MODEL_RUNTIME.md and TOOL_MAP.md.

**FYP-1 NOT YET READY — REMAINING BLOCKERS: planning reliability, remaining live workflow/vision acceptance, full at-rest encryption, system metrics and final demonstration.**
