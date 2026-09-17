# AI-assisted development disclosure

Policy Desk was developed with substantial assistance from **OpenAI Codex**: requirements analysis, implementation, tests, debugging, interface improvements, and documentation. It is not presented as unaided work. The assignment encourages coding agents while evaluating the candidate's understanding and validation of their output.

## How the agent was used

1. Read the supplied five-page brief and candidate pack, then mapped each requirement to implementation and evidence in [the requirement review](docs/REQUIREMENTS.md).
2. Built the Streamlit → HTTP → FastAPI → Gemini → SQLite pipeline, including JWT authentication and account-scoped history.
3. Added isolated tests for authentication, ownership, validation, persistence, retrieval, provider failures, and frontend/API integration.
4. Used test results, browser checks, and real provider diagnostics to investigate failures and revise the implementation.
5. Ran the final supplied-case evaluation with the candidate's explicit permission and a 30-request cap, and recorded the actual outcomes.
6. Prepared a study guide and demo script, then checked the candidate's recording using screen frames, a local automatic transcript, timing, and audio-level measurements.

The candidate tested the running app, reported provider failures, identified the History readability problem, discussed the technical design, and recorded the narrated demonstration. The agent does not claim that the candidate independently authored every line or has completed every suggested study exercise.

## Design decisions

- **Explicit SQLite queries:** a small schema and visible owner predicates make authorization and transactions easy to inspect without an ORM.
- **Rule-preserving chunks with parent expansion:** preserve policy thresholds and exceptions while demonstrating real embedding-based retrieval.
- **Local vectors and NumPy:** sufficient for six short policy documents; no hosted vector database or orchestration framework is needed.
- **Separate schema and citation checks:** valid JSON alone cannot establish that evidence exists.
- **Bounded failures:** one retry for transient provider failures and one output-repair attempt; no immediate 429 retry and no fabricated offline decision.
- **No answer leakage:** expected labels, historical outcomes, customer identifiers, and diagnostic issue categories do not enter model requests.
- **Explicit evaluation scope:** offline test coverage, supplied-case accuracy, and model confidence are different measurements.

## Observed issues and corrections

- The supplied CSV uses `processing`; the request vocabulary and documentation were aligned with its pre-dispatch meaning.
- Tests exposed invalid email-type handling and a misleading simulated retrieval fixture; both were corrected.
- Browser checks exposed heading spacing and an unsupported result icon; the interface was corrected and retested.
- Real quota and provider failures showed that the original generic error was unhelpful. Safe messages now identify the operation and HTTP category without returning credentials or raw provider bodies.
- Gemini 3.x request settings were aligned with the selected model, and the prompt explicitly treats missing facts as a normal clarification outcome. Earlier high-demand errors were preserved as failures, not described as solved by wording alone.
- The candidate found that History shortened the original message and hid submitted facts. It now displays the complete escaped message and all six order fields above the saved decision.

Historical diagnostics and intermediate checks remain in [the verification timeline](reports/verification-history.md). The final source default and example configuration use **Gemini 3.5 Flash-Lite**.

## Final verification

- **110 offline tests passed**; `src/` statement coverage was **99.01% (499/504)**, and Ruff passed.
- The real final-model run passed **all five supplied cases**, including exact S05: **5 correct, 0 incorrect, 0 service errors**. It used **11 API requests**, within the approved maximum of 30.
- All five validated decisions were persisted. The supplied policy and data files were unchanged.
- The recording demonstrates the running app, a real decision with policy evidence, and saved history including a clarification result.

See [the current evaluation](reports/evaluation-current.json) and [verification record](reports/verification.md). Historical 5/5 and 12/12 results used Gemini 2.5 Flash and are not attributed to the final model. Five visible cases do not establish accuracy on unseen tickets, confidence calibration, or universal prompt-injection resistance.

## Candidate preparation

The [study guide](docs/STUDY_GUIDE.md) explains the request flow, JWTs, ownership checks, database transactions, retrieval, validation, evaluation, and limitations. The candidate should be ready to trace a request through the code and discuss these tradeoffs in their own words. This documentation does not claim a particular development duration or guarantee selection.
