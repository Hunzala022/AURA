# At-rest encryption acceptance boundary

11 October 2026. This is an explicit gap analysis and migration design, not an approved waiver or a claim that AES-256 is implemented.

The roadmap requires AES-256 coverage of retained application data. Current Fernet uses AES-128-CBC plus HMAC-SHA256 for session task/result fields, audit parameters and memory document content. SQLite identifiers, timestamps, agent/tool/risk/status fields, Chroma vectors/identifiers, and communication quota timestamps/application hashes remain outside payload encryption. The key lives in an ignored local key file. Source files, explicitly user-created output documents and user-controlled external apps are not implicitly encrypted by AURA. Temporary screenshots are held in memory unless the user explicitly requests an output file.

Required protected set: complete session/audit records, memory content and embeddings with retrieval metadata, and communication-limit state. New runtime paths must remain ignored. Recovery copies of the previously exposed state are private forensic material and must remain separately controlled; new encryption cannot revoke historical exposure.

Proposed migration: use an authenticated AES-256 envelope with a dedicated versioned key, encrypt complete records and vector snapshots, and keep a plaintext vector index only in process memory. Use atomic replacement for encrypted snapshots, authenticated version/record identity, unique nonces, bounded decoding, strict corruption failure and serialized writers. Persist audit/limit decisions durably before effects. For larger datasets, evaluate a supported encrypted database instead of claiming payload encryption covers page/WAL/index metadata.

Before switching retained data: create a hash-verified private backup; export/decrypt into memory; write a separate encrypted target; compare record counts and decrypted payload hashes without printing contents; test restart/retrieval, wrong-key and tampering rejection, crash recovery, quota persistence and plaintext-canary absence in all files including journals; then explicitly approve cutover. Preserve the old stores for rollback until acceptance and owner-approved retirement. No irreversible migration or new secret was performed in this checkpoint.

Threat model: disk disclosure while AURA is stopped is in scope. An attacker running as the same account while the key is unlocked, a local administrator or operator-approved disclosure is not defeated by application encryption. Whole-volume encryption may supplement this design, but its presence/configuration has not been verified and is not assumed.

Exit disposition: **NOT COMPLETE**. Formal scope identifies exact work; it does not weaken or waive the encryption requirement. Retained-data cutover remains subject to the user's existing approval boundary.
