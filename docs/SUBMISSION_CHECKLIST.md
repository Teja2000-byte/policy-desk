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
- [x] Upload the [final recording](https://drive.google.com/file/d/1bqWFzBvWQtodxOo7bRhPpgmZ9RbMP87n/view?usp=sharing) to Drive. Permission metadata confirms anyone-with-link viewer access; the page returned HTTP 200 without authentication, and browser playback advanced with a displayed duration of 1:53.
- [x] Choose a public GitHub repository as the project delivery, under the candidate's `Teja2000-byte` account. Keep the ZIP as a backup.
- [x] Publish [Teja2000-byte/policy-desk](https://github.com/Teja2000-byte/policy-desk) and verify access without authentication. The public source tree matches the reviewed local project.
- [ ] Review the completed email below and send it as a reply to the original invitation.
- [ ] Reply to the original invitation before the deadline.

## Agreed order of work

**Record first → review the video → finish evaluation and packaging checks → verify the Drive link → prepare and send the email.**

The recording, its review, current-model evaluation, and public repository publication are complete. The Drive viewer link is verified. The remaining step is to review and send the submission email. Continue studying the architecture, JWT, database, RAG, validation, and limitations for the later technical discussion; the two-minute video does not need to teach all of those topics in detail.

## Packaging and credentials

Use your own Gemini key as requested by the brief, configured privately on your machine. Reviewers follow the README and supply their own credentials. Never attach a key or the local `.env`.

The source package includes the schema, which creates the runtime SQLite database during setup. It excludes local accounts, password hashes, saved user tickets, private keys, JWT secrets, virtual environments, caches, and logs.

```bash
python -m scripts.package
```

The public source is available at [Teja2000-byte/policy-desk](https://github.com/Teja2000-byte/policy-desk). The ZIP is retained locally as a backup. The candidate uploaded the recording; its viewer link and basic playback have been verified. No submission email has been sent.

## Submission email — ready for candidate review

Subject: ASSIGNMENT SUBMISSION: Teja Gopal

Hi Abhinav,

Thank you for the opportunity. Please find my completed submission for the AI & Backend Engineering Internship assignment.

GitHub repository: https://github.com/Teja2000-byte/policy-desk
Demo recording (1 minute 53 seconds): https://drive.google.com/file/d/1bqWFzBvWQtodxOo7bRhPpgmZ9RbMP87n/view?usp=sharing

Policy Desk includes the requested Streamlit interface, FastAPI backend, JWT authentication, SQLite persistence, and Gemini-powered recommendations grounded in the supplied policies.

The final model correctly handled all five supplied test cases, including the missing-information case. All 110 automated tests pass, and the repository includes setup instructions, evaluation results, and an AI-assisted development disclosure.

I look forward to discussing the implementation and design decisions.

Best regards,
Teja Gopal

No email has been sent. Reply to the original invitation using the subject above.
