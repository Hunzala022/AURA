# FYP-1 engineering status â€” sign-off pending

Updated 11 October 2026. This is the current source of truth. The original stage reports and office documents describe historical intentions/results and are not acceptance evidence.

## Working architecture

One local Qwen3.5-4B Q8_0 model produces an untrusted plan. Python validates the entire plan against the 22-tool catalog and tool ownership before any action. Each step crosses deterministic path/tool policy, explicit HIGH-risk approval, attempt logging, execution, independent file/UI postconditions where supported, and outcome logging. Exceptions halt subsequent steps and preserve the record of earlier effects. General rollback is not implemented.

Logical profiles are OS, browser, communication, research and vision. The security profile has no model-dispatched tools; policy is deterministic Python. A caller may restrict allowed agents. Default console scope includes all supported agents. This is an application boundary, not an OS sandbox or defense against a malicious same-user Python process.

SQLite holds session/audit state. Chroma holds vector retrieval state. Retrieved content is marked untrusted before planning. Fernet encrypts selected payloads using AES-128-CBC with HMAC-SHA256; vectors, identifiers, timestamps and other metadata are not fully encrypted. A local key beside the data does not protect against a same-user account compromise. The roadmap's AES-256/all-at-rest requirement is not met by this implementation.

Browser tools use fresh Chromium pages and live HTTP(S); stateful multi-step form workflows are not supported across calls. Communication uses desktop accessibility and may rely on internet-connected apps. Inference is local; the product is not air-gapped. Embedding initialization may require a download. Screenshot grounding now accepts images using the approved compatible projector, with strict normalized coordinates; a location is never reported as an executed click.

## Verified repairs and evidence

| Problem / root cause | Change | Verification | Remaining limit |
|---|---|---|---|
| Exposed key and tracked runtime stores | Rotation, migrated ciphertext, cleaned history and ignored current stores | PHASE1_CLOSURE.md; containment tests; exact-key object scans | Old commit still resolves on GitHub; external copies cannot be revoked |
| Fourteen advertised ghost tools; independent catalogs drifted | core/tools.py is canonical; prompt, parameter validation and dispatch derive from it | tests/test_contracts.py covers all 22 and rejects all 14 old names | Unsupported capabilities return clarification |
| Copy/move checked only one endpoint | core/policy.py independently normalizes/checks every path | tests/test_policy.py and executor denial tests | Junction/TOCTOU races and same-user process interference remain |
| Unhandled tool errors and false completion | Structured statuses, full-plan preflight, exception boundary, postconditions | tests/test_pipeline.py; tests/test_file_operations.py | Partial effects remain; no transactional rollback |
| Vision found:false counted as success | Strict found/coordinate/error handling; accessibility first | tests/test_vision.py; synthetic live reports | General desktop/DPI reliability not established |
| Imported model lacked projector | Same Q8_0 weights plus checksum-matched F16 projector | MODEL_RUNTIME.md and image probe reports | Synthetic image success is not desktop task accuracy |
| Benchmark warnings counted as passes | Strict independent dimensions; explicit outcomes; nonzero failures | tests/test_evaluation.py; 20 system scenarios | Deterministic fixtures are not live model accuracy |
| Weak messaging recipient/text checks | Exact recipient header, literal text readback, new-message observation | tests/test_comm.py | Mocked UI tests; not delivery confirmation |
| Stale dependencies and claims | Active requirements and authoritative documentation | reports/environment.json | Python 3.11 and second machine not tested |

A tool-specific constrained-generation schema was tested after the initial planning failures. It improved syntactic validity in three targeted cases but repeatedly selected the read-only verifier for a write request. A controlled comparison with the generic generation schema passed both isolated live execution cases. The shipped generation schema therefore constrains the plan shape and exact tool names; strict per-tool parameter and ownership validation remains in Python before any effect. The unsuccessful schema experiment and earlier failures remain in reports.

## Acceptance blockers and remaining work

- Live model planning must meet an agreed acceptance threshold on representative tasks; failures and risk-estimation errors cannot be hidden behind valid JSON.
- Real desktop and messaging acceptance is incomplete. No external messages were sent during this remediation. Local Chromium tests and mocked messaging tests do not establish real communication reliability.
- The user confirmed that a 12 GB GPU machine is not available yet; this requirement is pending, not waived. The roadmap's Python 3.11 environment is also unverified. Current measurements are from the 6 GB RTX 3060 Laptop GPU and Python 3.14.3. Runtime environment versions are recorded in reports/environment.json. Q8_0 was preserved as instructed.
- The all-data AES-256 requirement needs an approved design/scope decision before any migration of retained user data. Current selected-payload Fernet works but is not equivalent.
- Dynamic transfer of tool output into subsequent tool parameters is unsupported; compound summarize-and-send requests cannot be honestly claimed complete.
- Communication uses a process-local hourly limiter and randomized pauses. Persistent per-platform daily limits and the roadmap's full interaction behavior are incomplete.
- Owner action is required for GitHub residual sensitive-object cleanup. No Support contact or further history rewrite was performed.

These gaps are not approved deferrals. See REQUIREMENT_TRACEABILITY.md. No completion tag or FYP-2 implementation plan is authorized by this status.

## Security review

Verified mitigations: unknown tools/parameters and agent mismatches fail before effects; forged model risk cannot bypass Python policy; both copy/move paths, executable source files and Windows alternate data streams require appropriate review; high-risk denial prevents dispatch; unavailable audit initialization prevents execution; invalid vision responses fail; known private runtime paths are ignored.

Residual HIGH: incomplete at-rest coverage relative to the roadmap; retained old sensitive GitHub object; unreliable live planning undermines task-completion claims. Residual MEDIUM: no OS/process sandbox, path-check races, non-tamper-evident audit storage, local confirmation without identity authentication, regex sanitization is incomplete against prompt injection, GUI false matches/delivery ambiguity, no rollback, and rate limits reset on restart. Local administrator/same-user malware and exfiltration explicitly approved by an operator are outside the implemented boundary.

## FYP-2 documentation reconciliation

The official build roadmap specifies AS608 and Pi-to-PC WebSocket communication. Historical R307 and HTTP/serial suggestions are superseded design notes, not an approved implementation choice. Current software HITL is a local yes/no confirmation, not biometric identity verification. Hardware implementation and the formal FYP-2 milestone plan remain gated on FYP-1 sign-off.
