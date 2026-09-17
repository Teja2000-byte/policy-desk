# Submission checklist

Deadline in the invitation: **Sunday, 20 September 2026**. No exact cutoff time or timezone was provided; leave a comfortable margin.

## What to send

Reply to the original email with:

1. **One project delivery:** a public GitHub repository link **or** the project ZIP attached. The PDF asks for a repository; the submission email explicitly permits a ZIP as an alternative.
2. **A Google Drive viewer link** to a screen recording strictly under two minutes, showing the running Streamlit application and your own brief verbal explanation.
3. Subject: **`ASSIGNMENT SUBMISSION: <Your Full Name>`**.

No public deployment, slide deck, separate study-guide attachment, or API key is requested. The localhost URL is not a shareable project link.

## Current readiness

- [x] Implement the required Streamlit, FastAPI, JWT, SQLite, RAG, and structured-decision flow.
- [x] Include source, pinned dependencies, README, `.env.example`, schema, policies/data, tests, an evaluation runner, and `DEVELOPMENT.md`.
- [x] Complete historical live evaluations on Gemini 2.5 Flash: 5/5 supplied cases and 12/12 preselected additional cases. Preserve those reports with their model names.
- [x] Confirm genuine user-created results on the current Gemini 3.5 Flash-Lite model, including a missing-delivery-date clarification. These manual results are not a full supplied-case benchmark.
- [x] Align the source default and example configuration with the working local Flash-Lite model.
- [x] Record the video with your own voice. The candidate selected the second recording, approximately 1 minute 53 seconds long.
- [x] Review sampled screen frames, a local narration transcript, audio levels, and duration. A louder MP4 preserves the original screen footage; the candidate has confirmed the video is ready.
- [x] Complete the final model/evaluation review: all five supplied cases passed on Gemini 3.5 Flash-Lite, including exact S05; 0 incorrect and 0 service errors. The approved run used 11 API requests. Actual results are in `reports/evaluation-current.json`.
- [x] Check source/README/configuration consistency, compare all supplied files, verify the schema, scan publishable source and Git history for credentials, and validate a clean source package. Its fresh setup and all 110 offline tests passed; Ruff passed.
- [ ] Upload the recording to Drive, set viewer access, and verify the link while signed out or in a private browser.
- [x] Choose a public GitHub repository as the project delivery, under the candidate's `Teja2000-byte` account. Keep the ZIP as a backup.
- [ ] Publish the finished project and verify that the public repository is accessible while signed out.
- [ ] Confirm the candidate's full name and final email contents.
- [ ] Reply to the original invitation before the deadline.

## Agreed order of work

**Record first → review the video → finish evaluation and packaging checks → verify the Drive link → prepare and send the email.**

The recording, its review, and the current-model evaluation are complete. The remaining work is final repository publication, Drive-link verification, and the submission email. Continue studying the architecture, JWT, database, RAG, validation, and limitations for the later technical discussion; the two-minute video does not need to teach all of those topics in detail.

## Packaging and credentials

Use your own Gemini key as requested by the brief, configured privately on your machine. Reviewers follow the README and supply their own credentials. Never attach a key or the local `.env`.

The source package includes the schema, which creates the runtime SQLite database during setup. It excludes local accounts, password hashes, saved user tickets, private keys, JWT secrets, virtual environments, caches, and logs.

```bash
python -m scripts.package
```

The provided ZIP is a local artifact. No public repository has been published, no recording uploaded, and no submission email sent automatically.

## Email draft — fill in only after final review

Subject: `ASSIGNMENT SUBMISSION: <Your Full Name>`

Hi Abhinav,

Thank you for the opportunity. Please find my submission for the AI & Backend Engineering Internship assignment.

Project: <Public GitHub URL, or state that the project ZIP is attached>

Demo recording: <Verified Google Drive viewer link>

Policy Desk implements a Streamlit interface, FastAPI endpoints, JWT authentication, SQLite persistence, and Gemini-based policy retrieval and structured recommendations. The project includes setup instructions, tests, an evaluation runner, and an AI-assisted development disclosure.

I look forward to discussing the implementation and design decisions.

Best regards,
<Your Full Name>

Replace every placeholder before sending. No email has been sent.
