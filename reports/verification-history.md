# Historical verification timeline

This is the development record before final submission preparation. Statuses such as “pending” describe that point in time. Use [verification.md](verification.md) and [evaluation-current.json](evaluation-current.json) for the final results.

# Verification record

Checked on **17 September 2026**, using Python 3.12 on macOS. Machine-readable summary: [verification.json](verification.json).

## Observed results

| Check | Result | Evidence |
|---|---|---|
| Offline engineering tests | **110 passed**, zero failures/errors | Automated test run; 99.01% `src/` statement coverage |
| Real Gemini ingestion | **6 policies, 12 indexed chunks** | Persistent local Gemini embedding index |
| Supplied live sample cases | **5/5 correct**, zero incorrect/errors | [evaluation.json](evaluation.json) |
| Preselected additional live cases | **12/12 correct**, zero incorrect/errors | [boundary-evaluation.json](boundary-evaluation.json) |
| Browser end-to-end check | Real damage decision generated, evidence displayed, saved result reopened from History | Streamlit → FastAPI → Gemini → SQLite → History |

Both live suites used **`gemini-2.5-flash`** and **`gemini-embedding-001`**. The policy fingerprint was `23f5194773eefe8def3b85efb773ed2fdc01b5eda20ab61610b7fe7f15e0cc3f`. Report files preserve run timestamps, dataset hashes, expected/actual actions, reasons, sources, and per-case elapsed times. These live outcomes preceded a later change to quota-error messages and retry handling; decision and retrieval logic remain unchanged. The error-handling change was then checked with all 93 offline tests.

The five supplied cases exercised damage evidence, eligible returns, delayed shipping, wrong items, and missing information. Their generated reasons and saved policy quotes were inspected. The browser check independently generated the ₹3,500 damage example, returned **REQUEST_PHOTOS**, displayed verified quotes, and retrieved the same saved result from History.

## Additional evaluation scope

The 12-case subset was selected **before its execution** from the 40 additional cases, to keep live request volume bounded. Selection: **E01, E02, E03, E08, E09, E10, E12, E13, E23, E26, E29, E37**. Inputs are saved unchanged in `data/boundary_smoke_cases.json`.

Coverage includes the ₹2,000 damage threshold and seven-day cutoff; the ₹3,000 defect threshold and fourteen-day cutoff; the return window; shipping after ten days; late wrong-item reports; cancellation while processing; and an instruction-injection attempt embedded in a damaged-item ticket.

**The other 28 additional cases were not executed.** The historical CSV diagnostic evaluation was also not run. Passing 5 supplied cases and 12 visible additional cases is evidence for these smoke tests, not a general accuracy estimate or a guarantee of resistance to prompt injection. Model confidence is self-reported and uncalibrated. Quote validation verifies that the evidence exists; it does not prove the interpretation is correct.

## Engineering checks

- **99.01% statement coverage of `src/`** (499 of 504 statements). The frontend file and scripts are outside this coverage denominator; separate tests exercise their behavior.
- Ruff static checks and Python compilation passed. A clean extraction of the initial source ZIP also passed all 86 tests and Ruff. The latest quota-handling change passed the complete 93-test suite and Ruff. It changes error reporting and suppresses immediate quota retries.
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

## Subsequent quota incident

After the successful suites and browser check, a real diagnostic request on 17 September 2026 received **429 RESOURCE_EXHAUSTED**, with `GenerateRequestsPerDayPerProjectPerModel-FreeTier` and quota value **20** for `gemini-2.5-flash`. Embedding access still succeeded. This identifies daily generation quota exhaustion rather than a missing key or general network failure. New decisions are blocked until quota becomes available; the next documented daily reset is 18 September 2026 at 12:30 PM IST.

The provider now shows a specific daily-quota/reset message, keeps raw provider details private, and skips immediate retries for HTTP 429. Seven regression cases were added; the full **93-test** suite and Ruff passed. Successful live reports were preserved rather than overwritten with this later service failure.

## Candidate steps still pending

The candidate has completed and selected the under-two-minute narrated screen recording. The current-model evaluation, public GitHub publication, verified Drive viewer link, and final email remain pending. Continue studying the implementation for the technical discussion. See [the demo script](../docs/DEMO_SCRIPT.md) and [submission checklist](../docs/SUBMISSION_CHECKLIST.md).

## Local launch recovery and alternative-model checks

Later on 17 September, neither local server was running, so the browser showed "site cannot be reached." The prepared Mac workspace now includes a double-click launcher outside the submission source tree. It starts `python run.py` in Terminal independently of the temporary development command session. Both health endpoints returned HTTP 200, and the sign-in screen was visibly verified in the browser. Keep the launcher Terminal open while using the app. The reviewer uses the portable README setup.

Two optional alternative-model checks were performed without changing the main app's configuration or billing. `gemini-2.5-flash-lite` metadata was accessible, but generation returned 404 NOT_FOUND; its five-case report records service errors rather than incorrect recommendations. `gemini-3.8-flash` answered an initial access probe but produced intermittent 503 UNAVAILABLE errors in the actual ticket pipeline. Its eight-case report includes the five supplied cases plus preselected E01, E09, and E37. The saved reports preserve unsuccessful attempts instead of presenting them as passing.

After those diagnostics the main application remained on the previously verified `gemini-2.5-flash`. The earlier 5/5 and 12/12 results apply to that model and those completed runs. The alternate model reports are diagnostics, not evidence of improved reliability. The same 28 extended cases remain unexecuted; the three selected for the alternate check were already among the 12 earlier boundaries.

## Replacement-key troubleshooting

After the candidate replaced the local key and reported another generic error, local inspection confirmed that Settings reads the configured file, the key is nonempty with no whitespace or duplicate declaration, and the private file permissions remain 0600. This does not establish whether Google accepts that key.

The provider now reports the failed operation and Google HTTP status, using fixed messages for authentication, permissions, missing resources/models, invalid setup/request, quota, and server errors. Diagnostic logs contain only operation and status. Thirteen regression cases brought the full offline suite to **106 passing tests**, with **99.00% `src/` statement coverage** (495/500), and Ruff passed. Both local services were restarted and their health endpoints returned 200.

The candidate's subsequent attempt reported **Google HTTP 404 at decision generation** for `gemini-2.5-flash`. The pipeline had passed the retrieval stage. This identifies a model/resource error in that request; it does not establish that the model is globally retired or that the replacement project has exhausted its quota.

The private local `.env` was then changed to `gemini-3.8-flash`, a supported model in [Google's documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), and the app restarted. Both local health endpoints returned HTTP 200 and the backend confirmed the new model setting. Subsequent user-initiated decision attempts returned **Google HTTP 503 at decision generation**. Re-entering the supplied key confirmed it already matched the saved value. Source defaults and historical evaluation reports remain unchanged; the private `.env` is excluded from the ZIP.

The candidate then explicitly authorized **one minimal diagnostic request, without retries**. That request succeeded using the configured key and Gemini 3.8 Flash: the response contained "Hello", elapsed time was 25.47 seconds, and reported usage was 91 total tokens (6 prompt, 1 response, 84 thinking). No policy or ticket data was sent. This establishes access for that request; it does not establish remaining quota, explain every prior 503, or prove the full decision pipeline works with the replacement key. See [the recorded diagnostic](replacement-key-access.json).

Inspection found the app still applied temperature 0 to Gemini 3.x. Following [Google's recommendation to retain default sampling for Gemini 3.x](https://ai.google.dev/gemini-api/docs/troubleshooting), the provider now omits that override for those models. The evaluated Gemini 2.5 setting remains unchanged. Both request configurations were checked offline against the installed SDK. **At that stage, the agent had made exactly one Gemini request with the replacement key; full decision generation was unverified.**

The sampling correction passed the complete **106-test offline suite** and Ruff. At that stage, `src/` statement coverage was **99.00% (496/501)**. No further live requests were made during that adjustment.

## Clarification generation adjustment

After the candidate reported that other examples worked while Missing information still returned Google HTTP 503, the system instructions were clarified: insufficient facts are a normal successful NEEDS_MORE_INFORMATION outcome, and questions should be ready for a support agent to send to the customer. Gemini 3.x now uses its supported low thinking level to reduce reasoning work. The existing retry cap and honest provider-failure behavior are unchanged. This is a mitigation, not a confirmed diagnosis of the 503.

The full **108-test offline suite** and Ruff passed. The clarification persistence test now uses the exact incomplete S05 input instead of inheriting facts from a damaged-order fixture. It verifies normal success, retained unknown fields, customer questions, and history. Model request tests verify both Gemini 2.5 settings and Gemini 3.8 settings, including prefixed model names. Coverage remains **99.00% (496/501)**. These tests use isolated doubles and do not establish live model behavior. The historical five- and twelve-case live reports preceded these prompt changes.

The candidate subsequently authorized the prepared diagnostic for real S05 retrieval and generation, capped at one query embedding plus one generation request, without retries or output repair.

## Confirmed S05 capacity error

At 2026-09-17T15:36:16Z the explicitly authorized diagnostic made **exactly two API calls**. Query embedding succeeded in **0.67 seconds**. Gemini 3.8 Flash generation failed after **9.62 seconds** with HTTP **503 UNAVAILABLE** and the message: "This model is currently experiencing high demand." Total elapsed time was **10.31 seconds**, below the configured 30-second request timeout. Google explicitly reported model capacity as the cause of this attempt. This does not prove the cause of every earlier failure or guarantee future availability.

The [redacted diagnostic report](missing-information-diagnostic.json) records the actual failure. No result was fabricated, no app account or ticket was created, no retries occurred, and no further requests were made after the two-call cap. Cumulative agent usage of the replacement key is **three calls**: the earlier approved Hello request plus these two calls.

The provider now maps this high-demand error to a specific fixed message, keeping raw provider text private in app responses. All **109 offline tests** and Ruff pass; coverage is **99.01% (499/504)**. This improves error reporting; it does not cure Google capacity shortages. Live S05 generation remains unsuccessful on the latest attempt.

## Lighter model configured for manual testing

The local private `.env` now selects `gemini-3.5-flash-lite`, listed as a stable model with structured-output support in [Google documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite). The application was restarted and local readiness confirmed. The key, embedding model, policy index, and source default are preserved. **No agent Gemini calls were made for this switch.** Model access, live S05 behavior, and capacity are unverified pending the candidate's own test. All prior live reports retain their actual model names and results.

## Flash-Lite user results and recording preparation

Read-only inspection confirmed three genuine saved decisions on Gemini 3.5 Flash-Lite. One is a damaged-item clarification asking how many days ago delivery occurred, generated in 4.785 seconds and saved at 2026-09-17T15:58:13Z. The candidate reports that this model is working well. This is evidence of real generation, validation, and persistence; it is not a formal accuracy benchmark. The saved clarification input is **not the exact supplied S05 return case**. See [the manual verification record](manual-flash-lite-check.json).

### History readability update

History now displays the full submitted customer message and all six order fields above the decision, without requiring an expander or reading JSON. A browser check reopened existing saved damage and clarification tickets and confirmed that a message longer than the selector preview is fully visible and wraps normally; absent numeric fields display as “Not provided.” The selector remains a short navigation preview. Customer text is escaped before rendering. The existing frontend and HTTP-client suites passed **9/9** tests; Ruff and syntax/diff checks passed. This verification used saved records and offline test doubles, with **zero Gemini requests**. No decision or evaluation logic changed.

The source default and `.env.example` now select Gemini 3.5 Flash-Lite to match the local app. The recording script and submission checklist have been revised for this state and omit historical accuracy claims from the video. The full supplied-case evaluation on the current model/prompt remains pending, along with the candidate's recording, Drive sharing, and final submission review. No Gemini calls were made for this check.

After aligning the default and example configuration, the complete **110-test offline suite** and Ruff passed. Coverage remains **99.01% (499/504)**. No additional Gemini requests were made.

## Repository preparation after recording

The candidate selected the second narrated demonstration, with an original duration of **112.63 seconds**. Review used sampled full-resolution screen frames, a complete local automatic narration transcript, and audio-level measurements. The selected MP4 raises narration volume while preserving the original video stream; its duration is **112.70 seconds**. The candidate confirmed that the video is ready. The recording was not uploaded during review.

The complete offline suite was rerun after the History display change: **110 tests passed**, with **99.01% `src/` statement coverage** (499/504). Ruff and Git whitespace checks passed. A scan of the 60 publishable files and 82 historical Git blobs found no current Gemini key or JWT secret and no matches for the checked common credential patterns. The private `.env`, local SQLite database, virtual environment, and private reports are excluded by Git rules. This is a targeted credential check, not a guarantee that every possible secret pattern was detected.

The selected GitHub account is `Teja2000-byte`; repository access was verified and the proposed `policy-desk` name was available at this check. No repository was created or published during these checks. The current-model five-case evaluation is still pending explicit authorization to use the candidate's API quota. **No Gemini requests were made during this repository preparation.**
