# Literature-review implementation addendum — 14 October 2026

This addendum updates the implementation claims associated with the retained AURA
SLR and proposal. It introduces no new literature claims or citations. Original
office/PDF references are historical; current empirical claims are governed by
the machine-readable reports and REQUIREMENT_TRACEABILITY.md.

| Proposed capability | Implemented boundary | Evidence / qualification |
|---|---|---|
| Local multi-agent reasoning | One shared Qwen3.5-4B Q8_0 model; logical tool profiles | Model chooses ordered tools/arguments; Python owns authority. No independent model per agent. |
| Reliable structured planning | Compact proposal compiled into strict canonical contract | 25-case reports retain raw outputs and failures; finite test success is not a universal reliability proof. |
| Deterministic safety | Full-plan validation, scope, policy, explicit approval, audit and postconditions | Not an OS sandbox; does not eliminate path races or same-user attacks. |
| Stateful workflows | Earlier verified text bindings and task-scoped browser page state | No arbitrary expression evaluation, path/recipient binding, or automatic summarization. |
| Human approval | Local software yes/no boundary and bounded mock operator in tests | No fingerprint identity verification in FYP-1. |
| Communication | Exact UIA recipient/draft checks, durable quotas, literal input, randomized pauses and bounded curved pointer motion | Real self-chat send accepted; general contact search is not signed off. No anti-detection or platform-compliance guarantee. |
| Vision | Accessibility-first, same-model projector fallback on real window capture | Positive and absent-target desktop cases; no arbitrary-screen accuracy claim. |
| Persistent memory | SQLite records and Chroma retrieval wired into planning | Actual remembered-codeword workflow tests memory influence. |
| AES-256 at rest | Active complete-snapshot AES-256-GCM backend and DPAPI key | Minimum recovery snapshots sealed and verified; redundant unsealed runtime copies retired under Option A. Historical Git artifacts remain separately preserved. |
| Prompt-injection resistance | Sanitization plus data/instruction separation and Python execution boundaries | Measure containment separately from requested-task completion; two live adversarial cases are not exhaustive. |
| Offline operation | Inference stays local | Browser and messaging can require network access; not air-gapped. |
| Hardware evaluation | Sole Windows laptop, approximately 6 GB VRAM | System/GPU totals include other software; no isolated-allocation claim. |

The final empirical numbers belong in VALIDATION_REPORT.md and the exit audit.
Historical scores that counted decision mismatches as passes, inferred success
from exception absence, or treated advisory risk hints as hard criteria are not
used for current readiness.
