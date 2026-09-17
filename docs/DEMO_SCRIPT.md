# Screen recording: aim for 1 minute 45 seconds to 1 minute 55 seconds

The email asks for a recording **under two minutes**, showing the running Streamlit application, its key functionality and output, and your own brief spoken explanation of how you built it. A full code walkthrough is not needed in this recording; prepare the study guide for the later 30-minute technical discussion.

**Completed:** the selected recording is 1 minute 53 seconds. The subsequent final-model evaluation passed all five supplied cases; results are in `reports/evaluation-current.json` and the README. The spoken script remains valid without adding accuracy numbers or re-recording. The sequence below is retained as the demonstration plan.

## Before pressing Record

1. Read this script and rehearse the click sequence and narration once or twice. Speak naturally; do not read the whole study guide on camera.
2. Keep the app's Terminal open and open http://127.0.0.1:8501/. The current configured model is **Gemini 3.5 Flash-Lite**. The backend, SQLite database, and embedding index are already prepared locally.
3. Use an account whose History contains a genuine saved clarification result. The candidate has successfully generated a Flash-Lite result asking for the missing delivery date. This can demonstrate the missing-information behavior without an extra live request during the video.
4. Start on **Sign in**. Briefly click **Create account**, return to **Sign in**, then sign in to your prepared account. Keep the password masked. Avoid spending time creating another account during the recording.
5. Plan one new live generation: **Damaged delivery · ₹3,500**, one day since delivery. Its expected action is **REQUEST_PHOTOS**. Keep the submitted details and result visible at a readable size.
6. Record the application window/region with your microphone enabled. On this Mac, Shift–Command–5 opens recording controls. Close `.env` and other secret files, and hide notifications. Check a short microphone sample first.

No extra API calls were made to prepare this script. Use saved History while rehearsing the narration to conserve quota.

## On-screen sequence and spoken script

Speak only the narration in the last column. The times are a guide: rehearse the actual clicks and aim to finish between 1:45 and 1:55. Stay in the Streamlit application throughout; there is no need to open code, a terminal, the README, or test results during the closing explanation.

| Time | Show | Say in your own words |
|---|---|---|
| 0:00–0:15 | Briefly show **Create account**, return to **Sign in**, then sign in. | “This is Policy Desk, an AI support-ticket decision assistant. I built the interface with Streamlit and the backend with FastAPI. Users register and log in, and protected requests use JWT authentication.” |
| 0:15–0:35 | Open **New decision**. Under **Try an example**, select **Damaged delivery · ₹3,500**. Show the populated message and order details, then click **Generate decision →** once. | “Here I’m submitting a ₹3,500 order that arrived damaged yesterday. Streamlit sends the ticket over HTTP. The backend uses embeddings to retrieve relevant passages from the supplied policies.” |
| 0:35–1:00 | Wait for the result. Show the action, **Model confidence**, and reason. Scroll to **Policy evidence** and keep a supporting quote expanded. | “Gemini returns a structured recommendation. This result requests photographs because of the order value and the damage policy. You can inspect the explanation, confidence, and exact supporting policy quote. Confidence is the model’s estimate.” |
| 1:00–1:20 | Open **History**. Use **Choose a ticket** to show the new ticket. Briefly show its **Submitted ticket** panel with the full message and order details, then select your previously saved clarification result and scroll to **Ask the customer**. | “The ticket and validated decision are saved together in SQLite. History shows only this account’s records. This previously saved example shows how the assistant asks for missing details when it cannot decide yet.” |
| 1:20–1:45 | Still in **History**, select the new damaged-delivery ticket again. Scroll past **Submitted ticket** to the decision and expanded **Policy evidence**. Point to the supporting quote during the first sentence, then leave this result on screen while finishing the narration. | “The backend checks the response structure and verifies cited quotes before saving. Tests cover authentication, ownership isolation, validation, and persistence. The project also includes an evaluation runner that compares recommendations with the supplied test cases’ expected answers, plus documented setup instructions.” |

This is roughly 170 spoken words. Your pace and model response time determine the actual duration. Leave a few seconds for clicks and finish before 2:00.

## Keep the demonstration accurate

- The earlier **5/5 supplied-case** and **12/12 additional-case** evaluations used **Gemini 2.5 Flash** and an earlier prompt. They are preserved historical results, not measured scores for the current Flash-Lite setup. Do not quote those scores as current-model accuracy in this video. The final submission will still include the evaluation runner and the actual results of the current-model evaluation.
- The final Gemini 3.5 Flash-Lite evaluation, completed after recording with the candidate's approval, passed all five supplied cases including exact S05. It used 11 API requests. This is a small supplied-case result, not a general accuracy claim; see `reports/evaluation-current.json`.
- Showing **Model confidence** is fine. It is the model's estimate for one decision, not the measured accuracy across test cases.
- Generate once and wait. If the provider fails or the recording runs long, stop and make a clean recording later. If you show a prior result, identify it as previously saved; do not present it as the outcome of a failed current request.
- The application recommends an action. It does not execute refunds, send emails, or contact customers automatically.
- “User” means the authenticated account using the app. The brief does not require separate customer and support-agent roles.

## Check the finished video

- Duration is strictly **less than two minutes**.
- The running Streamlit application and your spoken explanation are both present.
- Login/Register, New Decision, and History are demonstrated.
- Action, confidence, reasoning, policy sources, and an individual saved result are readable.
- Your voice is audible; no API key, JWT, password, `.env`, or unrelated personal tab is exposed.
- Watch the whole video before sharing it.

The recording review, current-model evaluation, repository publication, and package checks are complete. Upload the selected video to Google Drive, verify its viewer link, and prepare the submission email. The video does not need to be re-recorded to add evaluation numbers.
