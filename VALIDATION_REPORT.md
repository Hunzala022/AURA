# FYP-1 validation evidence

Consolidated 13 October 2026. The user's single Windows laptop is the complete target under SCOPE_DECISIONS.md.

| Check | Result | Evidence / boundary |
|---|---|---|
| Regression | 80/80 PASS | reports/regression.json; tested source hashes; six real loopback Chromium cases, files, SQLite/Chroma, policy and mocked agents |
| Deterministic system scenarios | 20/20 PASS | reports/stage4_system.json; expected failures and denials count as correct outcomes; fixture planner |
| Standalone red team | 18/18 PASS | test_red_team_4_3.py; overlaps regression |
| Isolated live execution | 2/2 PASS | reports/live_execution.json; real model, temporary files/audit, exact-action guard and approval fixtures |
| Native desktop | PASS | reports/desktop_acceptance.json; Notepad exact literal readback, title change, denied and approved audit paths |
| Native messaging | PASS, bounded | reports/messaging_acceptance.json; preselected Business WhatsApp self-chat, native input, durable quota, new visible message, denied/approved audit paths |
| Containment and rotation | PASS | reports/security_exit.json; known-key/path scans and retained-data decryption |
| Live planning | 19/25 required PASS | reports/model_exit_validation.json; no tools executed |

Native desktop and messaging use deterministic planner/approval fixtures with real adapters, policy and audit. They do not establish live model-to-messaging reliability. Browser observation additionally showed the new self-message marked Read and an empty composer. Four durable reservations include failed attempts. Only synthetic text was sent to the authorized self-chat; no Slack or unrelated WhatsApp session was used.

## Comparable planning results

The same corrected gold applies to both runs: optional exact-window verification after launch and an equivalent Save-target description are accepted. Wrong verification parameters still fail. Python policy is authoritative; advisory hints are diagnostic.

| Dimension | Checkpoint | Current |
|---|---:|---:|
| Schema/parameter contract | 18/25 | 22/25 |
| Decision, contract-gated | 17/25 | 20/25 |
| Tools | 16/25 | 20/25 |
| Parameters | 17/25 | 19/25 |
| Order | 16/25 | 20/25 |
| Deterministic policy expectation | 17/25 | 20/25 |
| Advisory hint agreement | 2/25 | 2/25 |
| All required checks | 16/25 | 19/25 |

The old 2/25 combined score included advisory hints. Removing hints gave 14/25 before gold correction; gold corrections gave 16/25. Only 16 to 19 is the comparable observed planning improvement. One sample per case is not a stable reliability estimate.

Six failures remain: deletion incorrectly clarifies; browser fill, browser click and UI-tree read remain invalid after bounded repair; screenshot repair clarifies instead of capturing; application launch verifies the title as document body text. PLANNING_FORENSICS.md and reports/planning_forensics.json separate all 25 cases into schema, decision, tools, parameters, ordering, policy, gold and advisory-hint findings. Schema gating is not eight independent failures.

Five cases attempted bounded contract repair without benchmark gold. A separate two-stage experiment completed two failing cases and was interrupted before four others completed; it is not used by production. Its malformed raw response was not captured, limiting diagnosis.

## Model, performance and acceptance limits

Qwen3.5-4B Q8_0, Ollama and the approved projector remain unchanged. Shared options: temperature 0, context 4096, generation limit 768. Current median total planning latency 38.36 s; first-generation TTFT 0.85 s; first-generation generation rate 5.35 tokens/s. Maximum sampled total GPU usage 4,344 MiB; system RAM 15,682.84 MiB; CPU 93.3%. Repair time is included in elapsed latency but not first-generation token metrics. System totals include other processes and are not isolated model allocations.

Earlier vision evidence remains scoped to two synthetic color probes and one normalized-coordinate grounding probe. Real desktop grounding remains open. Historical failed experiments are preserved.

Representative live multi-agent workflows, general recipient navigation, remaining communication interaction behavior, full at-rest AES-256 coverage, the live-system twelve-metric evaluation and final demo/sign-off remain open. See REQUIREMENT_TRACEABILITY.md and FYP1_EXIT_AUDIT.md.
