# AI-assisted development disclosure

This project was developed with substantial assistance from OpenAI Codex, including requirements analysis, code generation, test creation, debugging, interface implementation, and documentation. It should not be presented as unaided work. The assignment explicitly encourages coding-agent use while evaluating the candidate's understanding and validation of the result.

## How the agent was used

1. Read the full five-page assignment PDF, compared it with the linked Google Doc, and inspected every supplied policy and dataset field.
2. Converted requirements into a traceable checklist before completing the implementation.
3. Built the FastAPI/Streamlit/SQLite application with the official Gemini SDK, without a multi-agent architecture or a historical-answer lookup.
4. Added isolated tests for authentication, account isolation, persistence, retrieval mechanics, model validation, provider failures, and UI-to-API integration.
5. Ran the tests, fixed observed failures, checked the application in a browser, and recorded the scope of verification.
6. Prepared a study guide and demonstration script for the candidate's independent review and practice.

## Decisions requiring engineering judgment

- `sqlite3` instead of an ORM: the small schema and explicit owner predicates are easy to inspect.
- Rule-preserving chunks with parent expansion: retrieving an isolated eligibility clause could omit an important exception.
- Persistent Gemini embeddings and NumPy cosine similarity: a small local index is adequate for six short documents.
- Separate schema validation and evidence validation: structured JSON does not prove that citations are real.
- One repair attempt for invalid model output and bounded retries for transient provider errors; no silent fake fallback.
- Strict exclusion of historical labels and diagnostic `issue_type` from model inputs.
- Clear distinction between deterministic engineering tests and live Gemini evaluation.

## Issues found and corrected during validation

- The historical dataset includes `processing` as an order status. The initial input vocabulary omitted it; the schema and UI now support it with documented pre-dispatch semantics.
- A deterministic retrieval test initially used misleading simulated vectors. The test double was corrected, and the real ranking/parent-expansion code was exercised separately from any claim about Gemini's semantic quality.
- Invalid non-string email values needed to reach request validation rather than raise an unexpected normalization error.
- Browser review found heading spacing obscured by Streamlit's header; the layout was adjusted.
- A full UI-to-API result test found a checkmark that Streamlit did not accept as an emoji. It was replaced with a supported icon, and result/history rendering was retested.

After the candidate privately configured their key, the agent ran real Gemini ingestion and evaluation: all five supplied cases and all 12 preselected additional cases passed, with no service errors. A browser check generated the damage example through Streamlit and reopened the saved result from History. No expected labels were supplied to the model. A subsequent daily-quota incident exposed an overly generic error message: the provider now identifies daily quota exhaustion from structured metadata and avoids immediate HTTP 429 retries. Seven regression cases were added, and all 93 tests passed. Decision and retrieval logic did not change.

See `reports/verification.md` for the executed checks and their limits. The remaining 28 additional cases were not executed. Test doubles live exclusively under `tests/`; they are not a production mode.

## Candidate ownership before submission

The candidate should read the code, run the app with their own Gemini key, review actual evaluation failures, and practice explaining a full request without reading the script. The study guide is preparation material, not evidence that this review has already happened.

Do not claim a measured Gemini accuracy, manual review, elapsed development effort, or personal authorship that has not actually occurred. If asked how AI was used, describe the assistance and then explain the design, tests, and limitations in your own words.
