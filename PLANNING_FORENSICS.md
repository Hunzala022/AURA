# Planning forensic audit

Python policy is authoritative; model-risk agreement is diagnostic only. Schema-gated score dimensions are false for invalid contracts; raw decision is reported separately to avoid calling every invalid contract an intent failure. No policy-bypass finding follows from a risk score mismatch.

## Final production forensic totals — 25 cases

Source: `reports/model_fyp1_production25_final_v3.json`; unchanged case/gold hash and
Qwen/Ollama/Q8_0 runtime. Required dimensions are all clean: schema 25/25,
decision 25/25, tool selection 25/25, parameters 25/25, ordering 25/25 and
deterministic Python-risk alignment 25/25. The final required score is 25/25.
Advisory model-risk hints agree in 2/25 and disagree in 23/25; this is recorded
for calibration and is not a readiness gate. There are no final schema, decision,
tool, parameter, ordering or deterministic-policy failures. Earlier six
production failures and benchmark-gold corrections remain below as historical
forensic evidence, not as current blockers.

| Dimension | Final result | Interpretation |
|---|---:|---|
| Schema | 25/25 | Every returned proposal compiled to the strict contract. |
| Decision | 25/25 | EXECUTE/CLARIFY/REFUSE/NO_ACTION matched the expected decision. |
| Tool selection | 25/25 | No missing, extra or substituted tool remained. |
| Parameters | 25/25 | Exact values, controls and full multi-word content matched. |
| Ordering | 25/25 | Dependencies and approval-gated positions were preserved. |
| Deterministic policy | 25/25 | Python risk evaluation matched every expected case. |
| Benchmark-gold corrections | Historical only | Corrections are documented and applied equally; no gold entered inference. |
| Advisory model-risk hint | 2/25 | Diagnostic disagreement; never authorizes or blocks execution. |

Gold revisions: accept launch followed by exact-window verification; accept Save element / Save button for the requested Save target. These apply equally to old and new responses. No wrong tool, missing parameter, unsafe extra effect or dependency reversal is forgiven.

| Run | Cases | Schema | Decision (gated) | Tools | Parameters | Order | Policy | Hint | Required pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| model_final_validation.json | 25 | 18 | 17 | 16 | 17 | 16 | 17 | 2 | 16 |
| model_scope_validation.json | 25 | 20 | 19 | 19 | 18 | 19 | 19 | 2 | 18 |
| model_exit_validation.json | 25 | 22 | 20 | 20 | 19 | 20 | 20 | 2 | 19 |

## All 25 checkpoint cases

| # | Case | Required checks | Forensic finding |
|---|---|---|---|
| 1 | write | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 2 | read | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 3 | list | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 4 | folder | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 5 | verify | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 6 | copy | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 7 | move | tools, order | Genuine tool-selection error: reasoning says move but tool is copy_file; source would remain. |
| 8 | delete | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 9 | name search | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 10 | content search | schema, decision, tools, parameters, order, risk | Genuine parameter contract error: pattern supplied instead of required query. |
| 11 | browser read | schema, decision, tools, parameters, order, risk | Genuine tool-selection error: browser_click with read-only parameters; missing click selectors. |
| 12 | browser fill | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 13 | browser click | schema, decision, tools, parameters, order, risk | Genuine extra invalid browser_click step; navigation intent does not justify a click without selectors. |
| 14 | screenshot | schema, decision, tools, parameters, order, risk | Genuine wrong vision tool and destructive extra empty write; capture_screenshot already saves the image. |
| 15 | open app | PASS | Gold error: redundant verify_window after launch is safe and explicitly requested verification; accept only that extra order. |
| 16 | type | schema, decision, tools, parameters, order, risk | Genuine missing window_title despite its presence in the request. |
| 17 | ui read | schema, decision, tools, parameters, order, risk | Genuine wrong tool: vision_locate_element instead of read_ui_tree, with missing element_description. |
| 18 | window verify | schema, decision, tools, parameters, order, risk | Genuine wrong tools and missing screenshot path; no verification of requested text. |
| 19 | vision locate | PASS | Gold error: Save element is a semantically equivalent target description, not a wrong parameter. |
| 20 | comm read | decision, tools, parameters, order, risk | Genuine decision error: exact Slack window was specified; read_latest_message needs app_name only. |
| 21 | send | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 22 | ambiguous | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 23 | unauthorized | PASS | Correct refusal; high hint describes requested harm while the empty plan has no execution risk. Diagnostic only. |
| 24 | multistep | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |
| 25 | long context | PASS | Checkpoint task checks pass; model-risk disagreement is advisory. |

The original 2/25 combined score included advisory hints. Before gold correction the comparable required-check score was 14/25. Gold corrections are measurement repairs, not model improvements. Full contract errors and raw-decision checks are in reports/planning_forensics.json; original responses remain unchanged.

## All 25 final production cases (reports/model_fyp1_production25_final_v3.json)

| # | Case | Required outcome | Exact remaining failure |
|---|---|---|---|
| 1 | write | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 2 | read | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 3 | list | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 4 | folder | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 5 | verify | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 6 | copy | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 7 | move | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 8 | delete | PASS | Closed by explicit approval-gated operation and sequence semantics. |
| 9 | name search | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 10 | content search | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 11 | browser read | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 12 | browser fill | PASS | Closed by one-operation browser-fill semantics and exact selector/text instruction. |
| 13 | browser click | PASS | Closed by one-operation click-plus-verification semantics. |
| 14 | screenshot | PASS | Closed by capture-screenshot distinction from vision locate. |
| 15 | open app | PASS | Closed by existing-window and title/body distinction. |
| 16 | type | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 17 | ui read | PASS | Closed by accessibility-tree tool distinction. |
| 18 | window verify | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 19 | vision locate | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 20 | comm read | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 21 | send | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 22 | ambiguous | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 23 | unauthorized | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 24 | multistep | PASS | All required checks pass; advisory hints do not affect acceptance. |
| 25 | long context | PASS | All required checks pass; advisory hints do not affect acceptance. |

The experimental route-then-parameters planner was stopped after two completed failing cases (delete: invalid response at the token limit; browser fill: incorrect CLARIFY). Four requested cases did not complete. It is not used by production and is not a six-case benchmark. reports/model_routed_targeted.json preserves the two results; raw malformed output was not captured, limiting its diagnosis.
