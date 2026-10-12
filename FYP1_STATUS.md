# FYP-1 engineering status

Updated 13 October 2026. Active scope: SCOPE_DECISIONS.md. The sole development, validation, benchmark and demonstration target is the user's Windows laptop with approximately 6 GB VRAM. Historical roadmap hardware-comparison language is HISTORICAL / NO LONGER APPLICABLE. No correctness or security requirement was waived.

## Architecture and verified changes

One unchanged Qwen3.5-4B Q8_0 model in Ollama proposes untrusted plans. The canonical 22-tool catalog owns dispatch, agent permissions and strict parameter validation. Python preflights the full plan, resolves only explicit earlier text-result references, revalidates resolved parameters, evaluates deterministic policy, obtains HIGH-risk approval, logs the attempt, executes and checks observable outcomes. Exceptions halt later effects. Earlier completed effects are reported; no general rollback is claimed.

The planner now receives explicit distinctions for commonly confused tools and one bounded contract-repair attempt. No benchmark gold is supplied to repair. Valid but semantically wrong plans remain failures. Model risk is advisory and cannot authorize actions or fail readiness by itself. PLANNING_FORENSICS.md separates original-gold errors, initial generation and required checks.

Dynamic bindings use {"from_step": N} only in content, text, expected_content or query. They transfer literal earlier verified output, never commands, paths, recipients, arbitrary expressions or invented summaries. Browser steps share an isolated page within a task when the requested URL is unchanged; another task gets a new browser context. A real loopback browser-to-file pipeline verifies state retention and binding.

Communication attempts reserve SQLite-backed quota before UI effects: 30 per rolling hour globally, 100 per rolling 24 hours for an exact application identity, and 100 globally per rolling 24 hours. The conservative global cap prevents renamed windows from bypassing the daily ceiling. Reservations survive restart, serialize concurrent writers, and fail closed on storage errors or backward clock changes. These are engineering defaults, not a claim about a platform's published acceptable-use limits. Failed/uncertain attempts consume quota. The legacy in-memory limiter remains only for isolated tests.

Recipient headers must match the contact exactly or an explicitly supported self-chat decoration. The adapter preserves nonempty drafts, sets literal text, reads it back and requires a newly observed matching message. It does not prove server delivery. Random pauses exist; the roadmap's complete human-interaction behavior, including non-linear cursor motion, is not yet demonstrated.

Typing verification follows the same editable control through a title change and requires exact readback. Subsequent native AURA Notepad and Business WhatsApp self-chat tests passed, including denied/approved paths and real audit. They use planner/approval fixtures and are distinct from earlier external UI probes. The successful message test covers a preselected self-chat; general recipient navigation remains open. See DESKTOP_MESSAGING_ACCEPTANCE.md.

## Readiness blockers

1. Representative live planning still has task-contract/semantic failures. See the complete per-case results and final comparison in PLANNING_FORENSICS.md and the exit audit.
2. Controlled native desktop/self-chat adapter acceptance passed. Live-model desktop/messaging workflows, general recipient navigation, desktop vision, complete communication interaction behavior and representative multi-agent live workflows remain open.
3. Roadmap AES-256/all-at-rest coverage is incomplete. ENCRYPTION_SCOPE.md identifies plaintext metadata/vectors/quota state and a non-destructive migration design. Formal scope is not a waiver.
4. Final system-level twelve-metric evidence and a complete reproducible demo/sign-off depend on those outcomes. Exact-result binding and task-scoped browser state are implemented, but arbitrary summarization and PDF-summary workflows are not established by those primitives.

## Security disposition

Internal containment remains closed for the known exposed key and paths. Exact old/current key scans emit counts only; ignored key/database/recovery/screenshot paths remain outside source control. Known historical GitHub objects and copies elsewhere are a separate repository-security residual risk, not an automatic software-core blocker. Owner cleanup remains tracked in PHASE1_CLOSURE.md; no new rewrite, force push, deletion or Support contact occurred.

The application is not an OS sandbox. Same-user malware, path races, non-tamper-evident audit storage, local yes/no approval without identity authentication, incomplete injection resistance, GUI ambiguity and partial side effects remain documented limits. Full-disk encryption is not assumed. Inference is local; browser and messaging operations can be online.

FYP-1 is not signed off and FYP-2 has not begun. No completion tag is justified by this checkpoint.
