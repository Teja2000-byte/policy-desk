# Before submitting

Deadline stated in the invitation: **Sunday, 20 September 2026**. No cutoff time or timezone was provided; submit with a comfortable margin.

## Progress and remaining personal steps

- [x] Configure your own Gemini API key locally and restart the backend.
- [x] Run the real Gemini sample evaluation: **5/5 correct**, zero errors; saved in `reports/evaluation.json`.
- [x] Run preselected additional boundaries: **12/12 correct**, zero errors; saved in `reports/boundary-evaluation.json`. The other 28 additional cases were not run.
- [x] Generate a real result in Streamlit and reopen it from History.
- [x] Restore local app startup and verify the browser sign-in screen after the servers stopped.
- [ ] Read the study guide and explain the code without relying on memorized text.
- [ ] Record your own under-two-minute narrated screen demonstration.
- [ ] Upload the recording to Google Drive and verify the shareable viewer link.
- [ ] Confirm your preferred full name for the email subject/signature.
- [ ] Reply to the original email with the public GitHub link or project ZIP and the recording link.

## Finish in this order

1. Study `docs/STUDY_GUIDE.md`, then rehearse `docs/DEMO_SCRIPT.md` in your own words.
2. Once the main model's quota resets, sign in to your demo account and prepare the damage and missing-information examples. Avoid rerunning the full evaluation suites before recording.
3. Record a 1:45–1:55 screen demonstration with your microphone enabled. Play it back and check that the interface and your explanation are clear.
4. Upload the recording to Google Drive and test its viewer link in a signed-out/private browser.
5. Attach `policy-desk-submission.zip` to your reply, add the recording link, replace the name placeholders, and send before the stated deadline. Do not send the localhost URL as the project submission; it only works on the computer running the app.

## Project packaging

The email explicitly accepts a **public GitHub repository or a ZIP**. The source folder is ready for Git, and a source ZIP is provided. No repository has been published or email sent automatically.

The package should include source code, pinned dependencies, `.env.example`, original data and policies, tests, the evaluation runner, README, schema, and `DEVELOPMENT.md`. Exclude `.env`, credentials, local account databases, downloaded decision records, virtual environments, caches, and logs.

To regenerate a clean ZIP after making changes:

```bash
python -m scripts.package
```

For GitHub, create your public repository only after checking the staged files and ignored secrets. If you publish the ZIP contents, the required synthetic dataset is included. The original data notes explicitly say it contains no real customer information. Do not include any real customer tickets you later enter.

## Email draft to adapt after validation

Subject: `ASSIGNMENT SUBMISSION: <Your Full Name>`

Hi Abhinav,

Thank you for the opportunity. Please find my submission for the AI & Backend Engineering Internship assignment.

Project: <Public GitHub URL, or state that the project ZIP is attached>

Demo recording: <Verified Google Drive viewer link>

The project implements a Streamlit interface, FastAPI endpoints, JWT authentication, SQLite persistence, and Gemini-based policy retrieval and structured decisions. The repository includes setup instructions, tests, an evaluation runner, and an AI-assisted development disclosure.

I look forward to walking you through the implementation and design decisions.

Best regards,
<Your Full Name>

Replace every placeholder before sending. Include an evaluation statistic only if it matches the saved live report. This draft has not been sent.
