# FYP-1 workflow contracts

These are current implementation contracts, not future features.

## Exact-result binding

A later parameter in content, text, expected_content or query may be {"from_step": N}. N must be a positive integer referencing a strictly earlier step. Parameters otherwise follow the canonical tool schema. No forward reference, path/recipient binding, expression evaluation or interpolation is accepted. Only a successfully verified output enters the result map. At use time the bound value must pass the destination's string contract; then Python evaluates policy and obtains approval over the resolved values. Retrieval instructions remain literal data. This enables read-to-write and read-to-send, not an implicit summary generator.

## Browser state

One pipeline invocation owns one lazy Chromium session. The first browser call opens its URL. Further calls with that same requested URL act on the retained page, including state reached through clicks. A different requested URL navigates. Cookies and input state do not carry into another task. Standalone tool calls create their own session. A click must start with an absent/hidden unique expected postcondition and end with it visible. Network tools always cross the HIGH-risk gate.

## Communication limits

Production reservations are persisted in ignored .aura-private/communication_limits.db before UI effects. SQLite BEGIN IMMEDIATE serializes writers. Defaults: global 30/hour, exact application identity 100/rolling 24h, global 100/rolling 24h. Application names are normalized and hashed; message bodies and recipients are not stored in the limiter. The global ceiling also covers changing window titles. Backward clocks, corrupt/unavailable storage and exhausted quotas deny sending. Failed attempts retain reservations to avoid duplicate-send retries. These limits are conservative software defaults, not a platform-policy certification.

Restart, simultaneous callers, clock rollback, unavailable storage, independent identities and daily expiry are tested. Quota timestamps/hashes remain an at-rest encryption gap documented in ENCRYPTION_SCOPE.md.
