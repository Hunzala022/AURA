# FYP-1 engineering status

Updated 14 October 2026. Active scope: SCOPE_DECISIONS.md. The sole development, validation, benchmark and demonstration target is the user's Windows laptop with approximately 6 GB VRAM. Historical roadmap hardware-comparison language is HISTORICAL / NO LONGER APPLICABLE. No correctness or security requirement was waived.

## Architecture and verified changes

One unchanged Qwen3.5-4B Q8_0 model in Ollama proposes untrusted plans. The canonical 22-tool catalog owns dispatch, agent permissions and strict parameter validation. Python preflights the full plan, resolves only explicit earlier text-result references, revalidates resolved parameters, evaluates deterministic policy, obtains HIGH-risk approval, logs the attempt, executes and checks observable outcomes. Exceptions halt later effects. Earlier completed effects are reported; no general rollback is claimed.

The planner now receives explicit distinctions for commonly confused tools, messaging fields, approval ordering and exact-content verification plus one bounded contract-repair attempt. No benchmark gold is supplied to repair. Valid but semantically wrong plans remain failures. Model risk is advisory and cannot authorize actions or fail readiness by itself. The unchanged production benchmark passes all 25 required cases; 2/25 advisory hints agree. PLANNING_FORENSICS.md separates benchmark-gold errors, initial generation and required checks.

Dynamic bindings use {"from_step": N} only in content, text, expected_content or query. They transfer literal earlier verified output, never commands, paths, recipients, arbitrary expressions or invented summaries. Browser steps share an isolated page within a task when the requested URL is unchanged; another task gets a new browser context. A real loopback browser-to-file pipeline verifies state retention and binding.

Communication attempts reserve SQLite-backed quota before UI effects: 30 per rolling hour globally, 100 per rolling 24 hours for an exact application identity, and 100 globally per rolling 24 hours. The conservative global cap prevents renamed windows from bypassing the daily ceiling. Reservations survive restart, serialize concurrent writers, and fail closed on storage errors or backward clock changes. These are engineering defaults, not a claim about a platform's published acceptable-use limits. Failed/uncertain attempts consume quota. The legacy in-memory limiter remains only for isolated tests.

Recipient headers must match the contact exactly or an explicitly supported self-chat decoration. The adapter preserves nonempty drafts, sets literal text, reads it back and requires a newly observed matching message. It does not prove server delivery. Random pauses and bounded non-linear cursor movement are implemented and observed, including 50–150 ms typing pauses.

Typing verification follows the same editable control through a title change and requires exact readback. Native AURA Notepad, Business WhatsApp preselected self-chat, and real model-driven self-chat navigation/send tests passed, including denied/approved paths, real audit and persistent quota. See DESKTOP_MESSAGING_ACCEPTANCE.md.

## Readiness

**FYP-1 VERIFIED — READY FOR FYP-2**

No FYP-1 blocker remains. Active production and the minimum recovery set use authenticated AES-256 encryption. Option A retired verified redundant unsealed runtime copies. See FINAL_FYP1_EXIT_AUDIT_20261014.md and LEGACY_MATERIALS_RETAINED.md. Historical Git exposure remains a separate residual.

## Security disposition

Internal containment remains closed for the known exposed key and paths. Exact old/current key scans emit counts only; ignored key/database/recovery/screenshot paths remain outside source control. Known historical GitHub objects and copies elsewhere are a separate repository-security residual risk, not an automatic software-core blocker. Owner cleanup remains tracked in PHASE1_CLOSURE.md; no new rewrite, force push, deletion or Support contact occurred.

The application is not an OS sandbox. Same-user malware, path races, non-tamper-evident audit storage, local yes/no approval without identity authentication, incomplete injection resistance, GUI ambiguity and partial side effects remain documented limits. Full-disk encryption is not assumed. Inference is local; browser and messaging operations can be online.

FYP-1 is signed off against the verified scope. FYP-2 implementation has not begun.
