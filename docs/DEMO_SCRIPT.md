# Screen recording plan: aim for 1 minute 45 seconds

Record your own screen and voice. Use the real Gemini-backed application after live verification. Do not substitute test-double output or claim an unmeasured accuracy.

## Prepare before recording

1. Add your own Gemini key with `python scripts/setup.py` or edit the existing private `.env`, then restart.
2. Run `python -m scripts.ingest` to avoid cold index creation during the recording.
3. Run `python run.py` if the services are not already running.
4. Run `python -m scripts.evaluate`. Review the actual report; resolve failures before claiming completion.
5. Create your own demo account and prepare one saved damage result and one missing-information result. Keep the page on Sign in when you start.
6. Use a browser window with readable text. Close secret files, hide notifications, and record only the application window. Keep the terminal test summary available in a second tab/window if desired.
7. On macOS, use Shift–Command–5, choose the application/window region, and enable your microphone. Check a short audio sample first. These are preparation instructions; no recording has been created by this project.

## Timing and narration

| Time | On screen | Speak in your own words |
|---|---|---|
| 0:00–0:15 | Show Sign in / Create account, then sign in | “This is Policy Desk, a support-ticket assistant built with Streamlit and FastAPI. Users register and sign in with JWT authentication, and passwords are stored as Argon2 hashes.” |
| 0:15–0:35 | Select the ₹3,500 damage example and click Generate decision | “I’m submitting a damaged order delivered yesterday. The frontend calls the backend over HTTP. The backend embeds this ticket and retrieves relevant chunks from the supplied policies.” |
| 0:35–1:00 | Show REQUEST_PHOTOS, reason, and expanded policy evidence | “Gemini returns a structured recommendation. This case needs photographs because the order exceeds ₹2,000 and the report is within seven days. The server validates the fields and checks that the quoted evidence exists before saving anything.” |
| 1:00–1:20 | Open the saved missing-information example from History, or generate it if response time permits | “If necessary details are missing, the assistant asks specific questions instead of inventing an answer. Confidence is the model’s estimate, not a measured probability.” |
| 1:20–1:45 | Show History, reopen the damage ticket, optionally show test/report summary | “Tickets and decisions are saved together in SQLite. Every history query checks the owner. Automated tests cover account isolation, token validation, persistence, retrieval, and failure handling. A separate runner evaluates actual Gemini decisions against the supplied cases.” |

If you have a verified result, add one short factual sentence: “The live sample run returned **[actual correct] of [actual total]** correct.” Replace those values from the report. Otherwise omit the accuracy claim.

Model response times vary. If a live call takes longer than expected, explain retrieval while waiting, then shorten the final section. You may show a previously generated, genuinely saved result in History; say that it is a saved result. Do not hide a failed call by pretending that another result belongs to it.

## Recording and sharing checklist

- Total duration is strictly less than two minutes; aim for 1:45–1:55.
- The Streamlit application is visibly running.
- Your voice explains the build in summarized points while sharing the screen.
- Action, reason, confidence, source evidence, and saved history are readable.
- No `.env`, password, API key, JWT, or personal browser tab appears.
- Play the recording from start to finish and verify microphone audio.
- Upload to Google Drive, set the intended viewing access, and test the shareable link in a signed-out/private browser window.
- Add the actual recording URL to the submission email. Do not use a local file path or a placeholder link.
