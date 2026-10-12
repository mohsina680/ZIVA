from src.agentic_studio.prompts import build_agent_user_message
from src.agentic_studio import rag


class _FakeDoc:
    def __init__(self, text, metadata):
        self.page_content = text
        self.metadata = metadata


class _FakeStore:
    def __init__(self, docs):
        self._docs = docs

    def similarity_search(self, query, k):
        return self._docs[:k]


def test_build_agent_user_message_handles_empty_context():
    content = build_agent_user_message("TASK", "Do something", "")
    assert "No relevant context was retrieved." in content
    assert "TASK:\nDo something" in content


def test_retrieve_context_respects_character_limit(monkeypatch):
    docs = [
        _FakeDoc("A" * 100, {"source": "doc1.md", "chunk_id": 1, "chunk_total": 2}),
        _FakeDoc("B" * 100, {"source": "doc2.md", "chunk_id": 2, "chunk_total": 2}),
    ]
    monkeypatch.setattr(rag, "load_vector_db", lambda: _FakeStore(docs))

    class _Settings:
        rag_retrieval_k = 5
        rag_max_context_chars = 80

    monkeypatch.setattr(rag, "get_settings", lambda: _Settings())

    context = rag.retrieve_context("test query")
    assert "[Context 1 | Source: doc1.md | Chunk 1/2]" in context
    assert len(context) <= 80
