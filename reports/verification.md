# Verification record

Checked on **17 September 2026**, using Python 3.12 on macOS. Machine-readable summary: [verification.json](verification.json).

## Observed results

| Check | Result | Evidence |
|---|---|---|
| Offline engineering tests | **86 passed**, zero failures/errors | Automated test run; 98.91% `src/` statement coverage |
| Real Gemini ingestion | **6 policies, 12 indexed chunks** | Persistent local Gemini embedding index |
| Supplied live sample cases | **5/5 correct**, zero incorrect/errors | [evaluation.json](evaluation.json) |
| Preselected additional live cases | **12/12 correct**, zero incorrect/errors | [boundary-evaluation.json](boundary-evaluation.json) |
| Browser end-to-end check | Real damage decision generated, evidence displayed, saved result reopened from History | Streamlit → FastAPI → Gemini → SQLite → History |

Both live suites used **`gemini-2.5-flash`** and **`gemini-embedding-001`**. The policy fingerprint was `23f5194773eefe8def3b85efb773ed2fdc01b5eda20ab61610b7fe7f15e0cc3f`. Report files preserve run timestamps, dataset hashes, expected/actual actions, reasons, sources, and per-case elapsed times. No production code was changed after observing these live outcomes.

The five supplied cases exercised damage evidence, eligible returns, delayed shipping, wrong items, and missing information. Their generated reasons and saved policy quotes were inspected. The browser check independently generated the ₹3,500 damage example, returned **REQUEST_PHOTOS**, displayed verified quotes, and retrieved the same saved result from History.

## Additional evaluation scope

The 12-case subset was selected **before its execution** from the 40 additional cases, to keep live request volume bounded. Selection: **E01, E02, E03, E08, E09, E10, E12, E13, E23, E26, E29, E37**. Inputs are saved unchanged in `data/boundary_smoke_cases.json`.

Coverage includes the ₹2,000 damage threshold and seven-day cutoff; the ₹3,000 defect threshold and fourteen-day cutoff; the return window; shipping after ten days; late wrong-item reports; cancellation while processing; and an instruction-injection attempt embedded in a damaged-item ticket.

**The other 28 additional cases were not executed.** The historical CSV diagnostic evaluation was also not run. Passing 5 supplied cases and 12 visible additional cases is evidence for these smoke tests, not a general accuracy estimate or a guarantee of resistance to prompt injection. Model confidence is self-reported and uncalibrated. Quote validation verifies that the evidence exists; it does not prove the interpretation is correct.

## Engineering checks

- **98.91% statement coverage of `src/`** (454 of 459 statements). The frontend file and scripts are outside this coverage denominator; separate tests exercise their behavior.
- Ruff static checks and Python compilation passed. A clean extraction of the initial source ZIP also passed all 86 tests and Ruff. Subsequent live verification added reports, the selected-case data, and documentation; it did not change the application code.
- All six original policy files, the 214-row historical CSV, data notes, and five supplied sample cases match the candidate pack byte for byte.
- Browser checks verified registration/sign-in, populated examples, navigation, the missing-key error before configuration, and the real result/history after configuration.
- Isolated automated UI-to-API tests also cover confidence/evidence rendering, history, and sign-out. Those test-provider results are separate from the real Gemini results above.
- The private key helper preserved the JWT secret and private file permissions. No credentials or local account database are included in the source ZIP.
- Before key configuration, the evaluator preflight correctly returned **NOT RUN**. After configuration, the actual live results replaced that earlier unverified status.

The suite covers password hashing and normalization; required routes; expired, malformed, wrongly signed, wrong-audience, and unsigned tokens; Alice/Bob ownership isolation; request validation; history pagination; persistence across restart; transaction rollback; clarification questions; invalid output and repair; invented citations; provider timeout/retry behavior and sanitized errors; SDK configuration; embedding shape and normalization; policy chunk coverage; index reuse/invalidation; ranking and parent expansion; HTTP client behavior; frontend forms/results/history/logout; input label exclusion; and honest evaluation metrics.

Two upstream test-framework deprecation warnings were emitted (Starlette/httpx and an AnyIO alias); they did not fail the checks. Direct dependencies are pinned in `requirements.txt` and `requirements-dev.txt`.

## Reproduce live evaluation

After configuring your own key and starting the backend, run from the project directory in an activated environment:

```bash
python -m scripts.ingest
python -m scripts.evaluate --delay 15
python -m scripts.evaluate --cases data/boundary_smoke_cases.json --output reports/boundary-evaluation.json --delay 20
```

Each run uses your Gemini quota and creates a separate local evaluation account. Results may vary with the provider/model. The evaluator sends only declared ticket input fields, excluding expected actions, historical labels, and issue categories.

## Candidate steps still pending

Study and explain the implementation, create the under-two-minute narrated screen recording, upload it to Drive with a verified viewer link, and send the final email. The source ZIP is a local deliverable, not a published GitHub repository. See [the demo script](../docs/DEMO_SCRIPT.md) and [submission checklist](../docs/SUBMISSION_CHECKLIST.md).
