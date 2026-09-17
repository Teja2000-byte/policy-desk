import hashlib
import json
import re
import threading

import numpy as np

from src.config import Settings
from src.database import Database
from src.provider import ProviderUnavailable
from src.schemas import RetrievedChunk, TicketInput

CHUNK_LIMIT = 420
CHUNK_VERSION = "rules-overlap-v1"


def split_document(source: str, text: str) -> list[dict]:
    """Keep numbered rules intact, repeat the heading, overlap one complete rule."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    heading, rules = lines[0], lines[1:]
    groups, current = [], []
    for rule in rules:
        if current and len("\n".join([heading, *current, rule])) > CHUNK_LIMIT:
            groups.append(current)
            current = current[-1:] if len(current) > 1 else []
        current.append(rule)
    if current:
        groups.append(current)
    elif not groups:
        groups.append([])
    return [
        {"chunk_id": f"{source}:{i + 1}", "source": source, "text": "\n".join([heading, *group])}
        for i, group in enumerate(groups)
    ]


class Retriever:
    def __init__(self, db: Database, provider, settings: Settings):
        self.db, self.provider, self.settings = db, provider, settings
        self._lock = threading.Lock()

    def _documents(self):
        files = sorted(self.settings.knowledge_base_path.glob("*.md"))
        if not files:
            raise ProviderUnavailable("No policy documents were found in knowledge_base.")
        return [(file.name, file.read_text(encoding="utf-8")) for file in files]

    def _fingerprint(self, docs):
        manifest = [
            CHUNK_VERSION,
            CHUNK_LIMIT,
            self.settings.embedding_model,
            self.settings.embedding_dimensions,
            docs,
        ]
        return hashlib.sha256(json.dumps(manifest, ensure_ascii=False).encode()).hexdigest()

    def ensure_index(self, force: bool = False) -> str:
        with self._lock:
            docs = self._documents()
            version = self._fingerprint(docs)
            with self.db.connect() as conn:
                old = conn.execute("SELECT value FROM kb_meta WHERE key='version'").fetchone()
                count = conn.execute("SELECT COUNT(*) FROM kb_chunks").fetchone()[0]
            if old and old[0] == version and count and not force:
                return version
            chunks = [chunk for name, text in docs for chunk in split_document(name, text)]
            vectors = self.provider.embed([chunk["text"] for chunk in chunks], "RETRIEVAL_DOCUMENT")
            # Build first, then atomically replace. A failed provider call preserves the old index.
            with self.db.connect() as conn:
                conn.execute("DELETE FROM kb_chunks")
                conn.executemany(
                    "INSERT INTO kb_chunks(chunk_id,source,text,embedding) VALUES(?,?,?,?)",
                    [
                        (
                            chunk["chunk_id"],
                            chunk["source"],
                            chunk["text"],
                            vector.astype(np.float32).tobytes(),
                        )
                        for chunk, vector in zip(chunks, vectors, strict=True)
                    ],
                )
                conn.execute("INSERT OR REPLACE INTO kb_meta(key,value) VALUES('version',?)", (version,))
            return version

    def retrieve(self, ticket: TicketInput) -> tuple[list[RetrievedChunk], str]:
        version = self.ensure_index()
        # Neither issue_type nor historical resolved_action is accepted by TicketInput.
        query = (
            "Support ticket: "
            + ticket.message
            + "\nKnown order facts: "
            + ticket.model_dump_json(exclude={"message"}, exclude_none=True)
        )
        vector = self.provider.embed([query], "RETRIEVAL_QUERY")[0]
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM kb_chunks ORDER BY chunk_id").fetchall()
        matrix = np.stack([np.frombuffer(row["embedding"], dtype=np.float32) for row in rows])
        if matrix.shape[1] != len(vector):
            raise ProviderUnavailable("The policy index dimensions changed. Rebuild the index.")
        scores = np.clip(matrix @ vector, -1, 1)
        ranked = sorted(range(len(rows)), key=lambda i: (-float(scores[i]), rows[i]["chunk_id"]))
        sources = list(dict.fromkeys(rows[i]["source"] for i in ranked))[: self.settings.retrieval_documents]
        # Expand selected parents to all their chunks so exceptions/windows are not lost.
        context = [
            RetrievedChunk(
                chunk_id=row["chunk_id"],
                source=row["source"],
                text=row["text"],
                similarity=round(float(scores[i]), 5),
            )
            for source in sources
            for i, row in enumerate(rows)
            if row["source"] == source
        ]
        return context, version

    def status(self):
        with self.db.connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM kb_chunks").fetchone()[0]
            version = conn.execute("SELECT value FROM kb_meta WHERE key='version'").fetchone()
        return {"indexed_chunks": count, "policy_version": version[0] if version else None}


def normalize_quote(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
