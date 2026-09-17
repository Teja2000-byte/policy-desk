# Verification record

The final configuration uses **Gemini 3.5 Flash-Lite**, Python 3.12, and Gemini `gemini-embedding-001`. Checks completed on **17 September 2026**. See [verification.json](verification.json) for the machine-readable summary.

## Final results

| Check | Result | Evidence |
|---|---|---|
| Real Gemini, all five supplied cases | **5 correct, 0 incorrect, 0 errors; 100% accuracy on this set** | [Current evaluation](evaluation-current.json) |
| Exact supplied missing-information case S05 | **NEEDS_MORE_INFORMATION**, with specific questions | Same evaluation, case S05 |
| Persistence during the live run | **5 tickets and 5 validated decisions saved** | Evaluation persistence check |
| Offline engineering tests | **110 passed**, no failures or errors | Full suite rerun after the final application changes |
| Statement coverage of `src/` | **99.01% (499/504 statements)** | pytest-cov; frontend and scripts are outside this denominator |
| Code checks | Ruff and Git whitespace checks passed | Local checks |
| GitHub Actions on Linux | Fresh dependency installation, Ruff, and the offline suite **passed** | [Successful workflow run](https://github.com/Teja2000-byte/policy-desk/actions/runs/35258635098) |
| Supplied data | All **9 files unchanged**, including **6 policies** and the **214-row CSV** | Byte-for-byte comparison |
| Schema | `docs/schema.sql` matches the canonical schema | Direct comparison with `src/database.py` |
| Clean source package | Fresh no-key setup succeeded; **110 tests** and Ruff passed after extraction | Reviewer-style copy with no local account database or Gemini key |
| Local policy index | **12 chunks**, 768-dimensional real Gemini vectors | Persistent SQLite index; matching policy fingerprint |
| Narrated Streamlit demonstration | Selected video **112.70 seconds**, under two minutes | Candidate-confirmed final MP4 |

## Live evaluation method

The unmodified `scripts.evaluate` runner registered and logged in through a real local HTTP server, then submitted the five original cases to the production FastAPI application. The real Gemini provider used the final model, current prompt, schema checks, citation checks, and normal bounded retry/repair behavior. Expected actions and historical labels were excluded from every request payload.

A separate evaluation database contained only a copy of the unchanged policy embedding index before the run. This preserved the candidate's demonstration history while exercising real user creation, JWT issuance, retrieval, generation, validation, and SQLite persistence. An external request guard enforced the candidate's **30-call maximum**. The completed run used **11 calls: 5 query embeddings and 6 generation attempts**. No further Gemini calls were made after the suite. All five outcomes were correct; six generation attempts means this was not necessarily a single-attempt generation for every case.

For exact S05, “I want to return this.”, Gemini asked for the reason for return, days since delivery, whether the product was opened, and the product type. The persisted output cited relevant clauses from the provided policies. Its sources, quotes, and questions were inspected after the run.

To reproduce with your own key and a running backend:

```bash
python -m scripts.evaluate --output reports/evaluation-local.json --delay 15
```

The first run on a clean installation builds the policy index and therefore uses additional embedding requests. The recorded run reused its matching index. Results and provider availability can vary; this command is not a guarantee of the same number of requests.

## What the offline checks cover

The suite verifies registration and password hashing; required routes; valid, expired, malformed, wrongly signed, wrong-audience, and unsigned JWTs; Alice/Bob ownership isolation; input validation; pagination; persistence across restarts; transactional rollback; normal clarification output; invalid JSON and repair; invented citations; provider failure classification and bounded retries; SDK settings; embedding dimensions and normalization; chunk coverage; index reuse/invalidation; ranking and parent expansion; frontend HTTP calls; result/history rendering; logout; label exclusion; and honest evaluation metrics.

These tests use isolated provider doubles. They test engineering behavior and do not establish Gemini accuracy. GitHub Actions runs this same offline suite without a Gemini key. Two local framework deprecation warnings did not fail the tests.

The packaged source was extracted into a new folder and configured with the documented setup helper using `--no-key`. All 110 tests and Ruff passed there as well. The local checks reused the installed Python environment. GitHub Actions independently installed the pinned dependencies on a Linux runner and passed Ruff and the offline suite. Local Markdown links were checked, the ZIP matched all 64 publishable source/documentation files at this stage, and the credential scan found no current secrets or checked common credential patterns. Ignored `.env`, databases, and runtime files were absent from the source package.

The [public repository](https://github.com/Teja2000-byte/policy-desk) returned HTTP 200 without authentication. Its published source tree and commit matched the reviewed local project. The [Google Drive recording](https://drive.google.com/file/d/1bqWFzBvWQtodxOo7bRhPpgmZ9RbMP87n/view?usp=sharing) is shared as anyone-with-link viewer. Its page returned HTTP 200 without authentication; the expected file name appeared without a login redirect or access-request message. The browser player displayed 1:53 and its seek timer advanced during the playback check. This verifies basic preview playback, not a new complete listening review.

## Historical results and failures

Earlier **Gemini 2.5 Flash** runs passed [5/5 supplied cases](evaluation.json) and [12/12 preselected additional cases](boundary-evaluation.json). Those results used an earlier model and prompt. They are preserved as historical evidence and are not included in the final model's five-case score.

Unsuccessful alternate-model checks are retained in [the 2.5 Flash-Lite report](evaluation-flash-lite.json) and [the 3.8 Flash report](evaluation-gemini-3.8-flash.json). An earlier exact-S05 request to Gemini 3.8 Flash failed with Google HTTP 503 and a high-demand message; see [the diagnostic](missing-information-diagnostic.json). The final 3.5 Flash-Lite run succeeded on that same supplied case. Prior failures are not relabeled as successful runs.

The [historical timeline](verification-history.md) records the development checks and provider incidents. Its intermediate statuses are historical; this page and `evaluation-current.json` describe the final configuration.

## Limits of the evidence

- Five visible supplied cases are a smoke test, not an estimate of accuracy on unseen support tickets.
- The 12 additional cases were not rerun on the final model. The other 28 additional cases and the historical CSV diagnostic were not executed.
- Valid quotations demonstrate that cited text exists, not that every interpretation is correct.
- Model confidence is self-reported and uncalibrated. Prompt-injection resistance is not guaranteed.
- The source excludes `.env`, API keys, JWT secrets, local accounts/tickets, virtual environments, and logs. Reviewers supply their own credentials.

The recording review used sampled screen frames, a local automatic transcript, duration, and audio-level measurements; it was not a direct listening assessment. The candidate confirmed the recording is ready. The source repository and the Google Drive recording are separate submission deliverables.
