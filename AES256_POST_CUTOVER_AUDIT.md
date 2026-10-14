# AES-256 production cutover audit — 14 October 2026

**Production AES-256-GCM is active and post-cutover validation passed.**
Option A has now closed the retained-runtime-material disposition boundary.
At cutover no legacy material was disposed of. Subsequent approved Option A retired only verified runtime/test copies; Git recovery, branches, tags and remote data remain untouched.

## Activation and selection

The approved original target failed its dry review because three Chroma index
files had changed; its backup was unchanged. A fresh non-destructive preparation
at `.aura-private/encryption-cutover-20261014/` preserved exactly the same record
and quota digests. Dry review established writer quiescence and source/backup
integrity; activation succeeded. No writer needed forced termination.

The private `.aura-private/storage-selection.json` selects complete encrypted
memory and quota snapshots in that directory. The key is AES-256 and wrapped by
Windows current-user DPAPI. Plaintext SQLite and Chroma retrieval indexes remain
in process memory. The model, Ollama runtime, Q8_0 and single-laptop scope did not
change. Evidence: reports/aes256_activation.json and
reports/encryption_cutover_preparation.json.

## Results and correction found during validation

| Validation | Result / evidence |
|---|---|
| Migration | Exact records, vectors, metadata and quota preserved |
| Fresh-process production restart | PASS; selected backend and quota confirmed |
| Retained-vector and actual text retrieval | PASS |
| Production canary | Persists after restart; absent from active encrypted files |
| Tamper handling | Modified memory copy rejects with InvalidTag; quota copy fails closed |
| Wrong-key, crash, concurrent writers, audit ordering | PASS in full regression |
| Browser-enabled regression | 110/110 PASS; six real Chromium cases and 20 deterministic outcomes |
| Red team | 18/18 PASS; also included in final regression |
| Live workflows, first AES run | 19/20; reports/live_workflows_aes256.json |
| Affected live rechecks | 2/2; reports/live_workflows_aes256_memory_recheck.json |
| Final default-selector production demo | 4/4, no retrieval warnings; reports/fyp1_demo_aes256_final.json |
| Known-key/path containment | PASS; reports/security_exit.json |

The first AES live run exposed a real query-adapter defect: default embeddings
returned NumPy float32 values, which Chroma rejected in a list query. Storage
already converted vector values to Python floats; retrieval now does the same.
A NumPy query/restart regression test reproduces the defect and passes after the
fix. The remembered-codeword and untrusted-memory scenarios both pass after
repair, with no retrieval warnings. Their earlier results remain preserved.
This provides passing coverage of all 20 distinct cases, not a claimed single
post-fix 20/20 run. Eighteen unaffected cases were not repeated.

The first post-cutover demo passed its four effects but had the retrieval warning;
its report remains separate. The final demo reran all four through the default
production selector after repair, with real selected-store auditing and no
warnings. No expected output, model or benchmark gold changed. The existing
25-case planner result remains 25/25; this storage change did not alter planning
prompts. Prior desktop/Business WhatsApp/vision evidence remains valid and was
not unnecessarily repeated; no message was sent during this cutover.

The initial full AES live run measured mean 6.25 tok/s, pipeline TTFT 2.24 s,
peak total GPU usage 5,181 MB, system RAM 14,353 MB and CPU 84.3%. Its original
95% planning/outcome figures remain recorded honestly. The two repaired cases
measured 6.14 tok/s and 1.97 s pipeline TTFT, peaking at 5,207 MB GPU. These are
separate runs and system-wide measurements, not isolated allocations or a merged
performance score.

## Data counts and rollback

| Store | Migrated | Current | Explained difference |
|---|---:|---:|---|
| Sessions | 3 | 12 | +1 canary session; +8 sessions from two four-part demo runs |
| Audit records | 4 | 39 | +1 canary audit; +34 demo audit events |
| Memories/vectors | 1 | 1 | None |
| Quota reservations | 4 | 5 | +1 validation reservation; no message sent |

All original rows remain present. Source and cutover-backup hashes still match
the private eight-file manifest. Fresh-process validation is recorded in
reports/aes256_cutover_validation.json.

Recovery material is ready, but rollback is not a blind selector reset: new AES
writes must first be preserved and reconciled into any restored state, including
quota. The original legacy files, hash-verified backup and pre-validation encrypted
recovery snapshot remain. DPAPI recovery requires the Windows account/profile.
No rollback or disposal was performed.

## Final disposition closure

Option A is complete. One pre-cutover and one post-cutover recovery snapshot were
sealed using the approved AES-256-GCM envelope and a DPAPI-protected recovery key.
All 14 archived files passed extraction/hash verification; both recovery paths
passed. Twenty inventoried redundant runtime/test targets were removed only after
verification. The extraction was removed afterward. Active records remain
12 sessions, 39 audits, 1 memory/vector and 5 quota reservations.

Targeted fresh-process validation confirms active selection, unchanged record and
quota digests, retrieval, archive authentication, absence of known unsealed runtime
stores, ignored private paths and zero known-key/private-path Git leakage. No
unrelated model, planner, desktop, messaging or vision tests were rerun.

LEGACY_MATERIALS_RETAINED.md enumerates every disposition category and the recovery
procedure. Historical Git repositories/bundles remain separately preserved. SSD
physical erasure, remote/cache erasure and portable cross-account DPAPI recovery
are not claimed. Requirement 3.8 is complete for active and retained runtime data.

**FYP-1 VERIFIED — READY FOR FYP-2**
