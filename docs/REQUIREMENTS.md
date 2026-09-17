# Requirement-by-requirement review

Sources: the supplied five-page `AI_Engineering_Intern_Take_Home_Project.pdf`, the matching Google Doc, the email's submission instructions, and the original candidate pack. Section 11 is absent in the supplied brief; it has not been invented. The additional hint allows CAG, but this implementation follows the explicit RAG pipeline.

| Requirement | Implementation / evidence |
|---|---|
| Python end-to-end application | Python 3.12, `src/`, Streamlit frontend |
| Streamlit Login / Register | Both forms in `streamlit_app.py`; registration/login UI test |
| Authenticated New Decision | Ticket form, action, confidence, reason, sources, questions, JSON download |
| Authenticated History and individual result | Paginated history, ticket selector, detail API call, full message and all submitted order fields visible above the recommendation |
| Frontend uses HTTP, not direct database access | `src/ui_client.py`; no database imports in the frontend |
| FastAPI | `src/api.py`, OpenAPI at `/docs` |
| POST /register | Unique normalized email, Argon2id password hash |
| POST /login | Password verification, JWT issuance |
| GET /me | Authenticated account lookup |
| POST /tickets | Retrieve, generate, validate, save, return |
| GET /tickets | Only the current user's tickets |
| GET /tickets/{id} | ID and owner predicates in the database query |
| No plaintext passwords | `pwdlib` Argon2id; verified hash test |
| Bearer JWT verification | Fixed HS256, exp, iat, sub, issuer, audience |
| Authorization test | `test_alice_cannot_read_bobs_ticket`: Alice receives 404 for Bob's saved ticket and cannot see it in her list |
| SQLite users schema | id, email, password_hash, created_at |
| SQLite tickets schema | id, user_id FK, message, created_at; metadata JSON added |
| SQLite decisions schema | id, ticket_id FK, action, reason, confidence, sources JSON, created_at; audit/evidence fields added |
| Database constraints / persistence | Foreign keys, unique ticket decision, bounded confidence, atomic writes, restart test |
| Load provided policies | All six original Markdown files; unchanged |
| Split documents | Complete numbered rules, repeated heading, one-rule overlap |
| Create embeddings | Gemini `gemini-embedding-001`, normalized 768-dimensional vectors |
| Store embeddings locally | `kb_chunks.embedding` BLOBs in SQLite |
| Embed new ticket | Same embedding model, `RETRIEVAL_QUERY` |
| Retrieve relevant chunks | NumPy cosine ranking plus bounded parent expansion |
| Pass context to LLM | Current ticket + retrieved chunks only |
| Gemini API | Official `google-genai` SDK, configurable model |
| Structured AI decision | Pydantic action enum, reason, finite confidence, sources, evidence, questions |
| Validate before storage | Pydantic plus chunk/quote/source checks, one repair attempt |
| Insufficient information | `NEEDS_MORE_INFORMATION` with specific questions; outage is separately 503 |
| Supplied sample evaluation | `python -m scripts.evaluate`; all five unchanged cases passed on final Gemini 3.5 Flash-Lite; `reports/evaluation-current.json` |
| Correct / incorrect / accuracy report | JSON and console, service errors separate and included in denominator |
| Do not copy historical answers | CSV not in retrieval; strict request allowlist excludes all answer/issue labels |
| Own API key; secrets excluded | Private setup script, `.env.example`, `.gitignore`, clean packaging |
| Git / repository source | [Public Teja2000-byte/policy-desk repository](https://github.com/Teja2000-byte/policy-desk), verified without authentication; clean ZIP retained as a backup |
| README setup / usage | `README.md`, launch commands, configuration, troubleshooting, evaluation |
| Database/schema deliverable | `src/database.py` plus generated `docs/schema.sql` |
| Tests for important functionality | Tests under `tests/`, verification record under `reports/` |
| Coding-agent disclosure | `DEVELOPMENT.md` |
| Keep scope small and understandable | One backend, one frontend, one SQLite database; no extra app architecture |
| Less than two-minute screen recording | Completed and reviewed; selected MP4 is 112.70 seconds |
| Verbal explanation while sharing screen | Candidate recorded narration about the architecture while demonstrating the app |
| Drive shareable recording link | Candidate will upload the completed recording and provide the link; access verification pending |
| Submission email subject | Template and checklist specify `ASSIGNMENT SUBMISSION: <Your Name>` |
| Deadline | Sunday, 20 September 2026, as stated in the email; timezone/time not specified |

## Actual verification boundary

The final **Gemini 3.5 Flash-Lite** configuration passed all five supplied cases over real authenticated HTTP: **5 correct, 0 incorrect, 0 service errors, 100% accuracy on this set**. The run used 11 of the authorized 30 API calls and saved all five tickets and validated decisions. Exact S05 returned `NEEDS_MORE_INFORMATION` with specific questions. See `reports/evaluation-current.json` and `reports/verification.md`.

The **110 passing offline tests** use provider doubles and establish engineering behavior, not Gemini accuracy. The historical five- and twelve-case live reports used Gemini 2.5 Flash and an earlier prompt; their scores are not attributed to the final model. The additional 12 cases were not rerun on the final model, and the other 28 additional cases were not executed. The narrated recording and public repository are complete. The candidate's Drive link and final email are the remaining delivery steps.
