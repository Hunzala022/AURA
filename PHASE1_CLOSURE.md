# Phase 1 internal containment — CLOSED

Verified 2026-10-10. This supersedes the pending-rewrite status in the historical containment report; it does not claim external erasure.

- Clean development checkout: `D:\Project AURA\.aura-private\post-clean-check`, branch master. Never push from the original checkout.
- Rewritten remote master: `c4d1a5111835d265e0683accff6f8c0abceaeea2`.
- Rewritten remote main: `999bd8be304f46022fa4fc4bcf5b33f63f7f44cc`.
- Scanned every reachable object in the clean clone: neither old nor current key bytes present; `.keys/`, `aura_memory.db`, `aura_chroma/` absent from reachable paths.
- Copied current rotated key and stores without copying any old Git directory. All remain ignored and untracked. Ten SQLite encrypted fields decrypt with the current key and reject the compromised key. Chroma PersistentClient loads its one retained memory and its ciphertext decrypts.
- `python -B -m unittest test_key_management -v`: 4/4 pass in this clean checkout. No pytest dependency needed for these tests.
- Retained handover/audit documents copied from the original checkout into ignored private storage; no historical refs transferred.
- Recovery material remains private in the original checkout's `.aura-private/`: pre-rewrite bundles, pre-rotation backup and post-rotation backup. Never publish this folder.

## GitHub residual surfaces (read-only API inspection)

| Surface | Status | Evidence/action |
|---|---|---|
| Normal branches | CLEAN for known key/paths | main/master match rewritten refs and clean-clone object scan |
| Tags | NOT PRESENT | No advertised tags |
| Pull requests / exposed PR refs | NOT PRESENT | All-state PR list empty; no advertised PR refs |
| Actions runs | NOT PRESENT | total_count 0 |
| Actions artifacts | NOT PRESENT | total_count 0 |
| Releases/assets | NOT PRESENT | release list empty |
| Forks | NOT PRESENT | public fork list empty |
| Known old commit reference | AFFECTED | GitHub API still resolves 05047ed100253cd24d614b6b4c9400e828521290 |
| External/private copies | UNABLE TO VERIFY | Previously downloaded copies cannot be revoked |

Owner action: request GitHub Support removal of retained sensitive commit views/objects. Provide repository name, old exposed paths, history rewrite's First Changed Commit(s), changed PR refs (none found), and orphaned LFS report if produced. Retrieve filter-repo reports from the private history-clean mirror; do not attach keys or decrypted data. No support request, artifact deletion, visibility/security change, or further force push was performed here. The old ciphertext remains compromised wherever old copies survive.

Owner request draft: retained privately at .aura-private/retained-handovers/GITHUB_RESIDUAL_CLEANUP_DRAFT.md. It includes the exact seven exposed files (including the key), first-changed commit mapping and PR-ref result. GitHub decides whether the residual private-data risk qualifies for cleanup; no complete-erasure guarantee is made.
