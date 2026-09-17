-- Canonical schema is defined in src/database.py. Generated snapshot.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    metadata TEXT NOT NULL CHECK(json_valid(metadata)),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS tickets_owner ON tickets(user_id, id DESC);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY,
    ticket_id INTEGER NOT NULL UNIQUE REFERENCES tickets(id),
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1),
    sources TEXT NOT NULL CHECK(json_valid(sources)),
    evidence TEXT NOT NULL CHECK(json_valid(evidence)),
    missing_information TEXT NOT NULL CHECK(json_valid(missing_information)),
    retrieved_context TEXT NOT NULL CHECK(json_valid(retrieved_context)),
    model TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS kb_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS kb_chunks (
    chunk_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding BLOB NOT NULL
);
