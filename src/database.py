import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from src.schemas import DecisionOutput, TicketInput

SCHEMA = """
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
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_user(self, email: str, password_hash: str) -> dict:
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",
                (email, password_hash, utc_now()),
            )
            return dict(
                conn.execute("SELECT id,email,created_at FROM users WHERE id=?", (cur.lastrowid,)).fetchone()
            )

    def user_by_email(self, email: str):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    def user_by_id(self, user_id: int):
        with self.connect() as conn:
            return conn.execute("SELECT id,email,created_at FROM users WHERE id=?", (user_id,)).fetchone()

    def save_ticket(
        self,
        user_id: int,
        ticket: TicketInput,
        decision: DecisionOutput,
        context: list,
        model: str,
        version: str,
        latency_ms: int,
    ) -> int:
        # Both inserts share one transaction; failed decisions never leave partial rows.
        with self.connect() as conn:
            now = utc_now()
            cur = conn.execute(
                "INSERT INTO tickets(user_id,message,metadata,created_at) VALUES(?,?,?,?)",
                (user_id, ticket.message, json.dumps(ticket.model_dump(exclude={"message"})), now),
            )
            ticket_id = cur.lastrowid
            conn.execute(
                """INSERT INTO decisions(ticket_id,action,reason,confidence,sources,evidence,missing_information,retrieved_context,model,policy_version,latency_ms,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    ticket_id,
                    decision.action.value,
                    decision.reason,
                    decision.confidence,
                    json.dumps(decision.sources),
                    json.dumps([x.model_dump() for x in decision.evidence]),
                    json.dumps(decision.missing_information),
                    json.dumps([x.model_dump() for x in context]),
                    model,
                    version,
                    latency_ms,
                    now,
                ),
            )
            return ticket_id

    @staticmethod
    def _ticket(conn, row):
        if row is None:
            return None
        ticket = dict(row)
        ticket.update(json.loads(ticket.pop("metadata")))
        decision = dict(conn.execute("SELECT * FROM decisions WHERE ticket_id=?", (ticket["id"],)).fetchone())
        for key in ("sources", "evidence", "missing_information", "retrieved_context"):
            decision[key] = json.loads(decision[key])
        ticket["decision"] = decision
        return ticket

    def get_ticket(self, user_id: int, ticket_id: int):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM tickets WHERE id=? AND user_id=?", (ticket_id, user_id)
            ).fetchone()
            return self._ticket(conn, row)

    def list_tickets(self, user_id: int, limit: int, offset: int):
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM tickets WHERE user_id=?", (user_id,)).fetchone()[0]
            rows = conn.execute(
                "SELECT * FROM tickets WHERE user_id=? ORDER BY id DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset),
            ).fetchall()
            return {
                "items": [self._ticket(conn, row) for row in rows],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
