"""mock SDK 和检索初始化：无需密钥、网络、embedding 模型或 PostgreSQL。"""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from main import app
from routers import tickets
import ticket_service


def completion(payload):
    content = payload if isinstance(payload, str) else json.dumps(payload)
    return SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=content))])


@pytest.fixture
def setup(monkeypatch):
    llm = Mock()
    retriever = Mock()
    monkeypatch.setattr(ticket_service, "get_retriever", retriever)
    app.dependency_overrides[tickets.get_llm_client] = lambda: llm
    with TestClient(app) as client:
        yield client, llm, retriever
    app.dependency_overrides.pop(tickets.get_llm_client, None)


@pytest.mark.parametrize("category,urgency", [
    ("billing", "low"), ("account", "medium"), ("technical", "high"),
])
def test_three_categories_and_conditional_top3_rag(setup, category, urgency):
    client, llm, factory = setup
    chunks = [{"id": f"FAQ-{i}", "document": f"资料 {i}", "distance": i / 10}
              for i in (1, 2, 3)]
    factory.return_value.search.return_value = chunks
    reply = "请检查请求。" + ("[来源：FAQ-1]" if category == "technical" else "")
    llm.chat.completions.create.side_effect = [
        completion({"category": category, "urgency": urgency}),
        completion({"suggested_reply": reply,
                    "citation_ids": ["FAQ-1"] if category == "technical" else []}),
    ]
    response = client.post("/tickets", json={"title": "测试标题", "description": "测试描述"})
    assert response.status_code == 200
    assert response.json() == {
        "category": category, "urgency": urgency, "suggested_reply": reply,
        "citations": [{"id": "FAQ-1", "document": "资料 1"}]
        if category == "technical" else [],
    }
    calls = llm.chat.completions.create.call_args_list
    assert len(calls) == 2
    assert calls[0].kwargs["response_format"] == {"type": "json_object"}
    prompt = calls[1].kwargs["messages"][1]["content"]
    assert "测试标题" in prompt and "测试描述" in prompt
    if category == "technical":
        factory.assert_called_once_with()
        factory.return_value.search.assert_called_once_with("测试标题\n测试描述", top_k=3)
        assert all(chunk["document"] in prompt for chunk in chunks)
    else:
        factory.assert_not_called()
        assert "资料 1" not in prompt


def test_no_rag_mode_skips_retriever_even_for_technical(setup):
    _, llm, factory = setup
    llm.chat.completions.create.side_effect = [
        completion({"category": "technical", "urgency": "high"}),
        completion({"suggested_reply": "请提供脱敏日志。", "citation_ids": []}),
    ]
    result = ticket_service.process_ticket(
        ticket_service.Ticket(title="故障", description="生产 API 失败"), llm, use_rag=False
    )
    assert result.citations == []
    factory.assert_not_called()


@pytest.mark.parametrize("payload", [
    {}, {"title": " ", "description": "内容"}, {"title": "标题", "description": ""},
])
def test_invalid_ticket_rejected(setup, payload):
    client, llm, factory = setup
    assert client.post("/tickets", json=payload).status_code == 422
    llm.chat.completions.create.assert_not_called()
    factory.assert_not_called()


@pytest.mark.parametrize("payload", [
    "not json", {"category": "unknown", "urgency": "high"},
    {"category": "billing", "urgency": "urgent"},
])
def test_invalid_classification_returns_502(setup, payload):
    client, llm, factory = setup
    llm.chat.completions.create.return_value = completion(payload)
    assert client.post("/tickets", json={"title": "标题", "description": "描述"}).status_code == 502
    factory.assert_not_called()


@pytest.mark.parametrize("ids,reply", [
    (["FAQ-999"], "方案[来源：FAQ-999]"),
    (["FAQ-1"], "方案[来源：FAQ-2]"),
])
def test_fabricated_or_mismatched_citation_rejected(setup, ids, reply):
    client, llm, factory = setup
    factory.return_value.search.return_value = [{"id": "FAQ-1", "document": "真实原文"}]
    llm.chat.completions.create.side_effect = [
        completion({"category": "technical", "urgency": "medium"}),
        completion({"suggested_reply": reply, "citation_ids": ids}),
    ]
    assert client.post("/tickets", json={"title": "故障", "description": "详情"}).status_code == 502


def test_empty_search_does_not_invent_sources(setup):
    client, llm, factory = setup
    factory.return_value.search.return_value = []
    llm.chat.completions.create.side_effect = [
        completion({"category": "technical", "urgency": "low"}),
        completion({"suggested_reply": "知识库信息不足，请提供脱敏日志。", "citation_ids": []}),
    ]
    response = client.post("/tickets", json={"title": "故障", "description": "详情"})
    assert response.status_code == 200
    assert response.json()["citations"] == []


def test_missing_key_returns_503(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with TestClient(app) as client:
        response = client.post("/tickets", json={"title": "标题", "description": "描述"})
    assert response.status_code == 503


def test_sdk_error_is_sanitized(setup):
    from openai import APIConnectionError
    import httpx

    client, llm, _ = setup
    llm.chat.completions.create.side_effect = APIConnectionError(
        request=httpx.Request("POST", "https://api.deepseek.com/chat/completions")
    )
    response = client.post("/tickets", json={"title": "标题", "description": "描述"})
    assert response.status_code == 502
    assert response.json()["detail"] == "模型请求失败或返回格式无效"
