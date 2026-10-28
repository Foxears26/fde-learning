"""真实 Chroma + 确定性 embedding 替身 + mock LLM；不需要网络或密钥。"""

from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from rag_demo import (
    FAQS, NO_CONTEXT, answer_question, build_index, open_collection, retrieve,
)


class FakeEmbedder:
    """按主题给出固定向量，仅验证检索管道，不衡量真实模型的语义质量。"""

    def encode(self, texts, normalize_embeddings=True):
        vectors = []
        for text in texts:
            vector = [text.count(word) for word in ("401", "page_size", "429", "Retry-After")]
            vector.append(1.0)
            vectors.append(vector)
        embeddings = np.array(vectors, dtype=np.float32)
        if normalize_embeddings:
            embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings


@pytest.fixture
def store(tmp_path):
    collection = open_collection(tmp_path / "chroma")
    embedder = FakeEmbedder()
    build_index(collection, embedder)
    return collection, embedder


def test_index_has_20_chunks_and_persists_without_duplicates(tmp_path):
    path = tmp_path / "persistent"
    collection = open_collection(path)
    embedder = FakeEmbedder()
    build_index(collection, embedder)
    build_index(collection, embedder)
    reopened = open_collection(path)
    assert len(FAQS) == reopened.count() == 20
    stored = reopened.get(ids=["FAQ-3"], include=["documents", "metadatas"])
    assert stored["documents"] == [FAQS[2].document]
    assert stored["metadatas"] == [{"source": "FAQ-3"}]


def test_retrieve_top3_hits_auth_pagination_and_retry(store):
    collection, embedder = store
    for question, expected_id in [
        ("401 怎么办？", "FAQ-1"),
        ("分页 page_size 怎么传？", "FAQ-3"),
        ("429 Retry-After 怎么重试？", "FAQ-12"),
    ]:
        chunks = retrieve(question, collection, embedder)
        assert len(chunks) == 3
        assert expected_id in {chunk["id"] for chunk in chunks}
        distances = [chunk["distance"] for chunk in chunks]
        assert distances == sorted(distances)


def test_llm_prompt_contains_question_and_all_three_cited_chunks(store):
    collection, embedder = store
    question = "401 怎么办？"
    chunks = retrieve(question, collection, embedder)
    client = Mock()
    expected = "请检查 X-API-Key。[来源：FAQ-1]"
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=expected))]
    )
    assert answer_question(question, collection, embedder, client) == expected
    client.chat.completions.create.assert_called_once()
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert question in messages[1]["content"]
    for chunk in chunks:
        assert f'[来源：{chunk["id"]}]\n{chunk["document"]}' in messages[1]["content"]
    assert "不编造引用" in messages[0]["content"]


def test_empty_collection_returns_fallback_without_embedding_or_llm(tmp_path):
    collection = open_collection(tmp_path / "empty")
    embedder, client = Mock(), Mock()
    assert answer_question("401 怎么办？", collection, embedder, client) == NO_CONTEXT
    embedder.encode.assert_not_called()
    client.chat.completions.create.assert_not_called()


def test_blank_question_and_invalid_citations_do_not_produce_supported_answer(store):
    collection, embedder = store
    client = Mock()
    with pytest.raises(ValueError, match="问题不能为空"):
        answer_question("   ", collection, embedder, client)
    client.chat.completions.create.assert_not_called()
    for invalid_answer in ["直接反复重试即可。", "请重试。[来源：FAQ-999]"]:
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=invalid_answer))]
        )
        assert "模型未返回有效来源引用" in answer_question(
            "401 怎么办？", collection, embedder, client
        )
