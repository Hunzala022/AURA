# A.U.R.A. FYP-1 remediation baseline

A local-inference Python planner and deterministic tool executor. **FYP-1 sign-off is pending**; see `FYP1_STATUS.md` and the requirement traceability report. No FYP-2 implementation is started.

The development baseline is the cleaned master branch, not the historical contaminated checkout. The current local development directory is `D:\Project AURA\.aura-private\post-clean-check`.

## Setup

Python 3.11+ on Windows (this run uses Python 3.14). Direct versions used for this run are recorded in requirements-validated.txt. Use a virtual environment and `python -m pip install -r requirements.txt`. For browser tools also run `python -m playwright install chromium`. Core reasoning uses the already-installed local Ollama service and `aura-qwen:latest`; see `MODEL_RUNTIME.md` for the exact weights/projector and backup.

Start the console with `python run_aura.py`. Desktop tools need an interactive Windows session and exact window/control names. No test or runtime silently grants human approval.

## Authoritative documentation

Start with `REMEDIATION_REPORT.md` for the checkpoint, evidence and remaining gates. `SCOPE_DECISIONS.md` defines the single-laptop scope and authoritative Python-policy criterion.

- `PHASE1_CLOSURE.md`: clean-history and private-state verification; residual GitHub exposure.
- `MODEL_RUNTIME.md`: exact inference artifact, approved projector repair, limits.
- `TOOL_MAP.md`: canonical names, parameter contracts and agent ownership.
- `FYP1_STATUS.md`: current architecture, security boundaries, remaining requirements.
- `REQUIREMENT_TRACEABILITY.md`: roadmap milestone evidence and sign-off status.
- `VALIDATION_REPORT.md`: live versus fixture evidence, scoring dimensions and measurement limits.
- `PLANNING_FORENSICS.md`: all 25 checkpoint cases, audited gold corrections and comparable required-check results.
- `WORKFLOW_CONTRACTS.md`: explicit output bindings, browser state lifetime and persistent communication quotas.
- `ENCRYPTION_SCOPE.md`: exact at-rest gap and migration acceptance design; no waiver.
- `DESKTOP_MESSAGING_ACCEPTANCE.md`: passing native desktop/self-chat acceptance and remaining live workflow boundaries.
- `FYP1_EXIT_AUDIT.md`: final exit decision and remaining gates.
- `reports/`: corrected machine-readable evidence with mocked/live modes explicit.

Original stage summaries, office documents, forensic handovers and benchmark reports are historical evidence, not current completion claims. Original reference documents are retained privately in `.aura-private/reference-documents/`; annotated forensic handovers and the owner cleanup draft are in `.aura-private/retained-handovers/`.

## Validation

```powershell
$env:AURA_BROWSER_TEST='1'
python -B -m unittest discover -s tests -v
python -B test_red_team_4_3.py
python -B benchmark_system_4_2.py
python -u -B validate_model.py
python -u -B validate_live_execution.py
```

The regression suite includes containment tests, real temporary file/SQLite/Chroma operations, loopback Chromium when opted in, and mocked UI/messaging/model cases. The system suite has 20 deterministic scenarios; it is not a live model accuracy score. The live model benchmark plans 25 synthetic tasks and never executes tools. Legacy root test scripts may operate on a live desktop; they are excluded from pytest discovery.

## Security boundary

A model plan is untrusted. The whole plan is validated against canonical tool/parameter/agent contracts before any effect. Each execution step passes deterministic risk policy, explicit approval when HIGH, an audit attempt, execution, postcondition checking and outcome logging. Audit unavailability blocks execution. Earlier side effects are reported on failure; general rollback is not claimed.

Keys and runtime databases remain local, ignored and untracked. Do not copy old Git directories, merge pre-rewrite history, or force-add runtime data. Local inference does not imply an air gap: browser/communication actions can use the network; embedding setup may need a one-time model download.
