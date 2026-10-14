# Final legacy disposition — 14 October 2026

Option A is complete. Authenticated encrypted recovery archives were created,
extracted, hash-checked and used for recovery before any source retirement.
No secure physical SSD erasure is claimed.

## Inventory and classification

Paths are relative to `D:/Project AURA/.aura-private/post-clean-check/` unless
an absolute prefix is shown. Exact retired file manifests and all 20 target paths
are in reports/legacy_disposition.json. Semantic comparisons are in
reports/legacy_semantic_inventory.json.

| Item | Classification | Final disposition |
|---|---|---|
| Cutover legacy-backup: 8 files, including Fernet key, SQLite, Chroma and quota | REQUIRED RECOVERY MATERIAL | Sealed once as pre-cutover.aes, with two migration manifests; unsealed source retired |
| Current AES memory/quota, wrapped key, selection marker | ACTIVE PRODUCTION DATA | Unchanged; .aura-private/encryption-cutover-20261014 and storage-selection.json |
| Snapshot of current AES stores, wrapped key and selector | REQUIRED RECOVERY MATERIAL | Sealed once as post-cutover.aes |
| Current checkout aura_memory.db, aura_chroma, .keys and old communication_limits.db | REDUNDANT LEGACY COPY | Retired |
| D:/Project AURA/aura_memory.db, aura_chroma and .keys | REDUNDANT LEGACY COPY | Retired |
| D:/Project AURA/.aura-private/containment-20261010 runtime stores/key and empty staged directory | REDUNDANT LEGACY COPY | Retired; unrelated parent/script material untouched |
| D:/Project AURA/.aura-private/post-rotation-backup-20261010 runtime stores/key | REDUNDANT LEGACY COPY | Retired |
| encryption-preparation-20261014 and encryption-preparation-20261014-final, including backup/read-copy pairs, older AES targets and keys | REDUNDANT LEGACY COPY | Retired after both plaintext and AES record-subset comparisons |
| Current target legacy-read-copy and postcutover-recovery | REDUNDANT LEGACY COPY | Retired |
| Current target tamper-probes | TAMPER/TEST ARTIFACT | Retired |
| Isolated disposition-verification extraction | TAMPER/TEST ARTIFACT | Removed after successful recovery checks, including offline recovery rehearsal |
| D:/Project AURA/.git | GIT/REPOSITORY RECOVERY MATERIAL | Retained untouched |
| D:/Project AURA/.aura-private/history-clean.git | GIT/REPOSITORY RECOVERY MATERIAL | Retained untouched |
| D:/Project AURA/.aura-private/pre-rewrite.bundle and pre-rewrite-full.bundle | GIT/REPOSITORY RECOVERY MATERIAL | Both verified as complete valid bundles and retained untouched |
| Unknown runtime retirement candidate | UNKNOWN | None; no unknown file was selected for retirement |

All older sessions, audits, documents, stored vectors and quota entries were
contained in the chosen pre-cutover snapshot. No unique older runtime record
was discarded. The pre-cutover snapshot has 3 sessions, 4 audits, 1 memory/vector
and 4 quota reservations. The post-cutover snapshot has 12 sessions, 39 audits,
1 memory/vector and 5 reservations.

## Minimum retained recovery set

Private directory:
`D:/Project AURA/.aura-private/post-clean-check/.aura-private/fyp1-sealed-recovery/`

- `pre-cutover.aes`: 10 files; legacy snapshot plus integrity/migration manifests.
- `post-cutover.aes`: 4 files; current memory/quota snapshots, DPAPI-wrapped production key and selector.
- `recovery-key.dpapi`: dedicated AES-256 key protected by current-user Windows DPAPI.
- A constant-byte lock file is synchronization metadata, not an additional backup.

These containers reuse the approved AES-256-GCM EncryptedSQLite envelope with
purpose-bound authentication. File paths, contents, hashes and manifests are
inside the authenticated container. Outer checksums and counts are recorded in
reports/legacy_disposition.json; no plaintext payload/key is in Git.

## Recovery procedure

Retain this source commit, both archives, recovery-key.dpapi and access to the
same Windows account/profile credentials. DPAPI is not a portable independent
off-device recovery key.

1. Stop AURA writers. Work in the authoritative checkout with its documented dependencies.
2. Run `python -B seal_legacy_recovery.py verify --offline`. It rejects an existing extraction, authenticates both containers, extracts only safe contained paths into `.aura-private/disposition-verification/`, checks every hash, and verifies both recovery backends. It never selects or overwrites production.
3. For current recovery, preserve any newer production state first. Restore the extracted post-cutover memory.aes, quota.aes and aes256-key.dpapi together to a new private directory. Select that directory only after its decrypted counts/digests and quota are verified. The embedded selector records the original path mapping; do not blindly replace a live selector.
4. The pre-cutover directory restores the historical Fernet/SQLite/Chroma state for migration investigation. Do not downgrade production or lose newer sessions/quota. Reconcile newer state before a rollback.
5. After recovery review, remove the isolated extraction by its verified absolute path. Never leave unsealed recovery copies behind. Keep both archives and the wrapped recovery key.

## Claim and limitations

Known unsealed runtime copies were removed from the filesystem; retained runtime
recovery data is stored only in authenticated encrypted form. Physical SSD
erasure, OS pagefile cleanup, revocation of past disclosure and remote/fork/cache
erasure are not claimed. Git recovery objects are separately retained historical
repository evidence under the user's explicit instruction and may contain old
compromised material; they are not active runtime backups.
