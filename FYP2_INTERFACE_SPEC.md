# FYP-2 interface handoff — 14 October 2026

This specifies future integration points; it does not start FYP-2 or sign off
FYP-1. The exit decision is in FYP1_EXIT_AUDIT.md. FYP_2_HANDOFF.md is historical.
The supported target is the single Windows laptop.

## Approval interface

`core.policy.authorize_high_risk_action(action_details) -> bool` is the software
operator interface. The control plane calls it after deterministic policy and an
ATTEMPTED audit, before any tool effect. Only the literal boolean True approves.
False, timeout, exceptions or unavailable audit must not grant permission.
Denied actions stop subsequent steps. No biometric identity check exists today.

A later hardware integration can replace that function with an authenticated,
bounded request for the exact reviewed action. Bind the response to the action
and session, reject replay and late responses, and retain the existing before/
after audit and postcondition checks. No hardware transport is implemented here.

## Application interface

`core.control_plane.execute_pipeline(user_prompt, *, memory_factory=None,
allowed_agents=None) -> dict` owns planning, validation, permission scope, Python
policy, approval, execution, verification and audit. The caller supplies agent
permissions, never the model. A future UI must call this boundary rather than
dispatch tools directly. Do not expose dependency injection to untrusted clients.

The result includes decision, status, success, steps, error, warnings and latency.
Each step records tool, agent, risk, execution/verification flags and status.
Successful earlier effects may remain after failure; there is no general rollback.
Do not present a nonexception return as successful completion. Success is true
only for COMPLETED. Approval blocking currently uses a local console interface;
web sessions will require an explicit asynchronous approval design, not a claim
that progress already streams through WebSockets.

## Model and vision

Keep the verified Qwen3.5-4B Q8_0 model and compatible projector. No model-family
switch is required for the demonstrated desktop vision path. Accessibility lookup
comes first; fallback captures the verified foreground target window and checks
focus again before model grounding. Returned coordinates identify a location;
they do not authorize or execute a click. Preserve absence/focus-loss handling
and test target-window offsets if adding displays or changing DPI.

## Persistence and communication

Memory methods are log_session, log_audit_trail, store_memory and retrieve_memory.
The selected AES-256-GCM backend encrypts complete SQLite/vector/quota snapshots
and keeps the Chroma index
ephemeral. Do not bypass storage selection or silently recreate a missing key.

Communication reservations persist and precede UI effects. A failed or uncertain
send consumes quota. Never automatically resend an ambiguous result. Exact
recipient identity, empty composer, literal text readback and new-message evidence
remain required. Current real-app acceptance covers the authorized Business
WhatsApp preselected self-chat; general navigation is a separate limitation.

## Defense rehearsal

`python -B validate_fyp1_demo.py` runs bounded synthetic fixtures through the real
model and tools: simple read, Research-to-OS output, frozen/approved write,
denied deletion and malicious-page containment. Its explicit mock operator is
FYP-1 software approval, not identity authentication. Consult the generated
`reports/fyp1_demo.json` for the actual pass/fail result, not this script description.
