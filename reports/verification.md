# Verification record

Checked on **17 September 2026**, using Python 3.12 on macOS. Machine-readable summary: `verification.json`.

## Executed successfully

- **86 offline automated tests passed**, with no failures or errors.
- **98.91% statement coverage of `src/`** (454 of 459 statements). This excludes the frontend file and scripts from the coverage denominator; Streamlit and evaluator behavior are exercised by separate tests.
- Ruff static checks and Python compilation passed.
- All six original policy files, the 214-row historical CSV, data notes, and five supplied sample cases match the candidate pack byte for byte.
- The real FastAPI and Streamlit processes started locally. Browser checks verified registration/sign-in, populated example facts, workspace navigation, and the explicit missing-Gemini-key error.
- An automated Streamlit-to-FastAPI integration check generated a validated result using the isolated test provider, rendered its confidence and evidence, retrieved it from history, and signed out. This is an engineering integration test, not a Gemini accuracy result.
- The safe key-setup helper was checked in a temporary directory: key updates preserved the JWT secret and maintained private file permissions.
- The live evaluator's preflight was run against the local API. It correctly stopped with **“Evaluation NOT RUN”** because the Gemini key was not configured.

## What the automated suite covers

Password hashing and normalization; all required routes; expired, malformed, wrongly signed, wrong-audience, and unsigned tokens; Alice/Bob ownership isolation; request validation; history pagination; persistence across application restart; transaction rollback; required clarification questions; invalid model output and repair; invented citations; provider timeout/retry behavior and sanitized errors; Gemini SDK configuration; embedding response shape and normalization; policy chunk coverage; local index reuse and invalidation; vector ranking and parent expansion; HTTP client behavior; frontend forms/results/history/logout; evaluation input label exclusion and honest metrics.

Two upstream test-framework deprecation warnings were emitted (Starlette/httpx and an AnyIO alias). They did not fail the checks. The direct dependency versions are recorded in `requirements.txt` and `requirements-dev.txt`.

## Not yet verified

**Live Gemini embedding quality, policy reasoning, and end-to-end sample accuracy remain unverified.** No usable Gemini API key was supplied or available in the environment. No actual Gemini calls or fabricated accuracy numbers are reported.

The five original sample cases and **40 additional cases** are ready to evaluate. Merely adding those cases is not evidence that they pass. The historical CSV diagnostic run is also optional and unexecuted.

The under-two-minute narrated recording, Google Drive upload/viewer link, and final email submission remain pending candidate action. The source ZIP is a local deliverable, not a published GitHub repository.

## Complete live verification

From the project directory and an activated environment:

```bash
python scripts/setup.py --set-key
# Stop the existing app, then restart it:
python run.py
```

In a second terminal with the same environment:

```bash
python -m scripts.ingest
python -m scripts.evaluate
python -m scripts.evaluate --cases data/extended_test_cases.json --output reports/extended-evaluation.json
```

Review returned actions and evidence. Record the real numbers and any limitations, then regenerate the source ZIP if the reports or code change. Read `docs/DEMO_SCRIPT.md` before recording.
