# Desktop and messaging acceptance evidence

Updated 14 October 2026; actual interactive Windows laptop. Synthetic text only. Private screenshot evidence stays in ignored `.aura-private/acceptance/`.

## Observed real UI behavior

- Launched Notepad and selected the unique empty `Untitled - Notepad` window, preserving the unrelated existing window.
- Its editable document supported literal set-value. `AURA acceptance fixture alpha {Enter}` read back exactly, with braces preserved. The title changed immediately after entry.
- Fixed AURA's typing implementation and independent verifier to compare exact text on the same editable control rather than rediscovering the obsolete title. The regression reproduces a changed title and rejects substring-only readback. This was the historical fixture state; the user may subsequently close it.
- The user authorized only Business WhatsApp in the current designated Chrome profile and excluded Slack and the other WhatsApp session. The connected tab identified itself as WhatsApp Business; its open conversation explicitly showed `(You)` and `Message yourself`.
- Entered the synthetic `AURA acceptance test` into an empty composer, verified its text and self-chat destination, sent once, and observed the new message with `Read` plus an empty composer. No unrelated recipient received a message. No other message was edited or deleted.

## What this proves and what it does not

The initial interactions above used Codex computer/browser controls. They are separate from the subsequent native AURA acceptance below and cannot alone establish a native adapter pass.

AURA's communication adapter now supports an explicit recipient-control label distinct from the contact search string, refuses to overwrite a nonempty draft, requires exact text readback, observes a newly visible matching message, and reserves durable quota before UI effects. Missing ValuePattern support still fails closed. Message delivery must not be retried automatically after an uncertain outcome.

## Subsequent native acceptance

- `validate_desktop_acceptance.py` guarded the exact observed Notepad window handle/title and synthetic fixture content before effects. The denied pipeline preserved the fixture. The approved pipeline used the production typing adapter and independent verifier; exact text survived the title change. Real temporary SQLite/Chroma audit recorded ATTEMPTED, DENIED_BY_HITL, ATTEMPTED, APPROVED_BY_HITL and VERIFIED. `reports/desktop_acceptance.json` passed. That historical synthetic document contained `AURA native adapter verified {Enter}`.
- `validate_messaging_acceptance.py` guarded the exact Business WhatsApp window, explicit self-chat header and empty composer. Denial did not enter the adapter. Approved execution used AURA's native adapter, production persistent quota and real temporary encrypted audit. It sent one `AURA acceptance test`, observed a new matching message and recorded VERIFIED. `reports/messaging_acceptance.json` passed. `validate_live_message_navigation.py` separately passed with the real production model, authorized search navigation, message-count transition 4→5, empty composer, one quota reservation, two bounded pointer moves and twenty 50–150 ms typing pauses. Browser observation showed Read; this is UI evidence, not an independent server API receipt.
- Native attempts exposed generic-versus-editable UIA control selection, insufficient traversal depth, Chromium's empty-composer newline marker and ignored SetValue behavior. These were corrected. Literal Unicode fallback bypasses key-expression parsing, checks focused control identity during input, and requires exact readback before send. The installed library returns the last event count rather than a combined down/up count; final readback remains authoritative. Partial drafts and ambiguous outcomes stop execution. Only known synthetic partial drafts were cleared during test setup; no user draft was overwritten.
- Existing verified conversations are retained rather than searching again. Search navigation is signed off only for the uniquely identified authorized self-chat; arbitrary recipient search is not claimed. Four production quota reservations persisted, including unsuccessful attempts; denied control-plane calls do not reserve quota. Earlier readback failure is retained in `reports/messaging_acceptance_before_literal_input.json`.

The two historical native tests above use explicit deterministic planner and approval fixtures; interactive approval UX and model-to-desktop planning are not tested by them. This is real adapter/policy/audit acceptance, not full unguarded model workflow acceptance. No unrelated recipient received a test message, and no Slack or other WhatsApp session was used.

Remaining acceptance boundary: arbitrary recipient navigation and server-delivery confirmation are outside this authorized self-chat test. Native input fallback rejects control characters and supplementary Unicode codepoints; unsupported inputs fail closed. Private screenshot: `.aura-private/acceptance/native-self-message.png`.


Subsequent model-driven evidence: reports/live_desktop_v2.json (4/4), reports/live_messaging.json (2/2), reports/live_message_navigation_v6.json (search/send PASS), and reports/desktop_vision_live_v3.json (2/2). Each retains its actual prompt fingerprint. The Read observation belongs to the earlier preselected send, not an independent receipt for the navigation run. A later read-only acceptance attempt stopped at its foreground precondition and is not counted as passing.
