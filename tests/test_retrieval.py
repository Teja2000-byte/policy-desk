import numpy as np
import pytest

from src.database import Database
from src.provider import ProviderUnavailable
from src.retrieval import Retriever, split_document
from src.schemas import TicketInput


def test_every_policy_rule_survives_chunking(settings):
    for path in settings.knowledge_base_path.glob("*.md"):
        chunks = split_document(path.name, path.read_text())
        assert len(chunks) >= 1
        assert len({c["chunk_id"] for c in chunks}) == len(chunks)
        for line in path.read_text().splitlines():
            if line.strip():
                assert any(line.strip() in chunk["text"] for chunk in chunks)
        assert all(chunk["text"].startswith("#") for chunk in chunks)


def test_semantic_vector_ranking_and_parent_expansion(settings, provider, ticket):
    db = Database(settings.database_path)
    retriever = Retriever(db, provider, settings)
    context, version = retriever.retrieve(TicketInput(**ticket))
    assert context[0].source == "damaged_goods.md"
    assert len({chunk.source for chunk in context}) == 3
    combined = "\n".join(chunk.text for chunk in context if chunk.source == "damaged_goods.md")
    assert "above ₹2,000" in combined and "within 7 calendar days" in combined
    assert len(version) == 64
    assert [call[1] for call in provider.embedded] == ["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]
    with db.connect() as conn:
        vector = np.frombuffer(
            conn.execute("SELECT embedding FROM kb_chunks LIMIT 1").fetchone()[0], dtype=np.float32
        )
        assert np.isclose(np.linalg.norm(vector), 1)


def test_index_cache_survives_restart_and_invalidates_on_policy_change(settings, provider):
    db = Database(settings.database_path)
    first = Retriever(db, provider, settings).ensure_index()
    assert len(provider.embedded) == 1
    assert Retriever(db, provider, settings).ensure_index() == first
    assert len(provider.embedded) == 1
    path = settings.knowledge_base_path / "shipping.md"
    path.write_text(path.read_text() + "\n6. New rule for the cache invalidation test.\n")
    assert Retriever(db, provider, settings).ensure_index() != first
    assert len(provider.embedded) == 2


def test_index_invalidates_when_embedding_configuration_changes(settings, provider):
    db = Database(settings.database_path)
    first = Retriever(db, provider, settings).ensure_index()
    settings.embedding_dimensions = 256
    provider.dimensions = 256
    assert Retriever(db, provider, settings).ensure_index() != first


def test_failed_rebuild_preserves_existing_index(settings, provider, monkeypatch):
    retriever = Retriever(Database(settings.database_path), provider, settings)
    retriever.ensure_index()
    before = retriever.status()

    def fail(*args):
        raise ProviderUnavailable("Test outage")

    monkeypatch.setattr(provider, "embed", fail)
    with pytest.raises(ProviderUnavailable):
        retriever.ensure_index(force=True)
    assert retriever.status() == before


def test_empty_knowledge_base_has_clear_error(settings, provider, tmp_path):
    settings.knowledge_base_path = tmp_path / "empty"
    settings.knowledge_base_path.mkdir()
    with pytest.raises(ProviderUnavailable, match="No policy documents"):
        Retriever(Database(settings.database_path), provider, settings).ensure_index()
