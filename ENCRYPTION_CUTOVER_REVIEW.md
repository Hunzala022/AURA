# Final disposition update

Option A is complete; see LEGACY_MATERIALS_RETAINED.md and FINAL_FYP1_EXIT_AUDIT_20261014.md. The review below records the historical approval boundary before that separate authorization.

# AES-256 cutover review — 14 October 2026

**Approved and activated on 14 October 2026. Full retained-data encryption is not yet signed off because legacy material remains.**

The approved dry review detected changed Chroma index bytes. A fresh target at
`.aura-private/encryption-cutover-20261014/` preserved identical decrypted record
and quota digests, passed dry review, and was activated using the commands below
with that refreshed target. Earlier preparation directories remain intact.
The active private selection points to this fresh target. See
`reports/encryption_cutover_preparation.json`, `reports/aes256_cutover_validation.json`
and `LEGACY_MATERIALS_RETAINED.md`. Historical preparation details below are retained.

Commands actually executed successfully after refreshing preparation:

```powershell
python -B activate_encrypted_storage.py --target .aura-private/encryption-cutover-20261014
python -B activate_encrypted_storage.py --target .aura-private/encryption-cutover-20261014 --activate
```

Post-activation results and the final decision are in `AES256_POST_CUTOVER_AUDIT.md`.

This changes persistence from field-level Fernet plus persistent Chroma to complete
AES-256-GCM SQLite snapshots and an ephemeral Chroma retrieval index. It preserves
the public memory methods, stored embeddings, identifiers, timestamps, audit
records and quota decisions. It does not change Qwen, Ollama, Q8_0 or the laptop
scope. Current-user Windows DPAPI protects the new, dedicated 256-bit key.

## Concrete prepared state

Private directory: `.aura-private/encryption-preparation-20261014-final/`.

- `legacy-backup/`: hash-verified recovery copy of eight legacy files, including
  the local legacy key. Original files and this backup remain unchanged.
- `legacy-read-copy/`: disposable private copy opened by Chroma during export.
- `memory.aes`: complete 3 session records, 4 audit records and 1 memory/vector.
- `quota.aes`: 4 retained communication reservations.
- `aes256-key.dpapi`: dedicated key wrapped by this Windows user's DPAPI.
- `source-manifest.json` and `preparation-report.json`: counts and hashes only.

The export/import digests match exactly after restart, including metadata and
vectors. Retained-vector retrieval through ephemeral Chroma passed. See
`reports/encryption_preparation_final.json`. No key value is printed or documented.

## Proposed activation

The refreshed rehearsal includes all four current quota records. The dry review
passed on 14 October 2026 with `preconditions_passed: true`, `activated: false`
and `legacy_retirement_performed: false`. No production selection was written.

After explicit approval, stop AURA writers gracefully and perform the dry review:

```powershell
python -B activate_encrypted_storage.py --target .aura-private/encryption-preparation-20261014-final
```

Then the exact activation command is:

```powershell
python -B activate_encrypted_storage.py --target .aura-private/encryption-preparation-20261014-final --activate
```

Both commands reject changed source/backup contents, altered target records,
another Python process using the checkout, or an existing selection marker.
Activation creates only `.aura-private/storage-selection.json`, selecting both
encrypted stores together. A fresh AURA process loads this selection. Incomplete
state or invalid authentication fails closed. No legacy source, backup, branch,
tag or remote is deleted or rewritten by this command.

Before activation, repeat the rehearsal if source state changes. After activation,
rerun regression, live workflows, quota restart and the demo against the selected
backend. Existing legacy-backend evidence is not relabeled as AES-256 evidence.

## Recovery and legacy retirement

Before any new encrypted-backend write, disabling the new private selection and
restarting restores the untouched legacy backend. After new writes, stop AURA and
preserve both stores; reconcile/export new records before any rollback so sessions
and quota reservations are not lost. Never reset quota simply to recover service.
The legacy backup is a recovery artifact, not a claim of complete encryption.

DPAPI recovery depends on the Windows account and its profile credentials. Copying
only the wrapped key to a different account is not an independent recovery plan.
Keep a protected recovery copy of the account/key material under owner control.

Old active stores, the legacy read copy and recovery material still contain
unencrypted metadata/vectors. They must be sealed into authenticated encrypted
archives and their unsealed copies retired under separately reviewed approval,
or explicitly retained as controlled historical forensic material with a stated
exception. No retirement, deletion or waiver has been performed. Full historical
disk erasure cannot be claimed merely by deleting files, particularly on an SSD.

## Decision boundary

The user explicitly approved the persistence cutover and post-activation validation.
This approval does not authorize disposal of any legacy or recovery material.

**DO NOT CLAIM COMPLETE RETAINED-DATA ENCRYPTION:** legacy-material disposition
still requires separate explicit approval. Production selection is now AES-256-GCM.
