from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from eval_tickets import CASES, evaluate, print_report


def reply(category, text="", citations=()):
    return SimpleNamespace(category=category, suggested_reply=text,
                           citations=[SimpleNamespace(id=id_) for id_ in citations])


def test_evaluation_runs_ten_cases_in_both_modes(capsys):
    by_title = {case["title"]: case for case in CASES}

    def process(ticket, client, use_rag):
        case = by_title[ticket.title]
        return reply(case["expected_category"], " ".join(case["expected_key_points"]),
                     case["expected_citations"] if use_rag else [])

    processor = Mock(side_effect=process)
    results = evaluate(Mock(), processor=processor)
    assert len(CASES) == 10
    assert {case["expected_category"] for case in CASES} == {"billing", "technical", "account"}
    assert all(case["expected_citations"] == [] for case in CASES
               if case["expected_category"] != "technical")
    assert processor.call_count == 20
    assert [call.kwargs["use_rag"] for call in processor.call_args_list] == [True] * 10 + [False] * 10
    for mode in ("rag", "no_rag"):
        assert results[mode]["accuracy"] == 1.0
        assert results[mode]["correct"] == results[mode]["total"] == 10
        assert results[mode]["key_point_coverage"] == 1.0
        assert results[mode]["technical_total"] == 4
    assert results["rag"]["citation_accuracy"] == 1.0
    assert results["no_rag"]["citation_accuracy"] == 0.0
    print_report(results)
    output = capsys.readouterr().out
    assert "分类与 RAG 无关" in output
    assert "引用准确率" in output and "关键信息覆盖率" in output
    assert "100.0%" in output


def test_incorrect_and_failed_cases_stay_in_denominator():
    processor = Mock(side_effect=[reply("account"), RuntimeError("secret")] * 10)
    results = evaluate(Mock(), processor=processor)
    for mode in ("rag", "no_rag"):
        result = results[mode]
        assert result["total"] == 10
        assert result["errors"] == 5
        correct = sum(row["predicted"] == row["expected"] for row in result["rows"])
        assert result["accuracy"] == correct / 10
        assert result["technical_total"] == 4
        assert result["citation_accuracy"] == 0.0
        assert result["key_point_total"] == sum(len(case["expected_key_points"]) for case in CASES)
        assert result["key_point_coverage"] == 0.0
        assert "secret" not in str(result)


def case(id_, category, citations, points):
    return {"id": id_, "title": id_, "description": "测试描述",
            "expected_category": category, "expected_citations": citations,
            "expected_key_points": points}


def test_partial_quality_scores_use_expected_category_and_weighted_points():
    cases = (
        case("a", "technical", ["FAQ-1", "FAQ-2"], ["X-API-Key", "401"]),
        case("b", "technical", ["FAQ-4"], ["total"]),
        case("c", "billing", [], ["退款"]),
    )

    def process(ticket, client, use_rag):
        if ticket.title == "a":
            # 故意错分，仍按期望 technical 计入引用分母；多个期望中命中一个就算命中。
            return reply("billing", "检查 x-api-key。", ["FAQ-2", "FAQ-2"] if use_rag else [])
        if ticket.title == "b":
            # FAQ-40 不能误当成 FAQ-4；引文原文含 total 也不计入建议回复覆盖。
            result = reply("technical", "请补充信息。", ["FAQ-40"])
            result.citations[0].document = "total"
            return result
        return reply("billing", "请申请退款。" if use_rag else "请补充资料。")

    results = evaluate(Mock(), processor=Mock(side_effect=process), cases=cases)
    rag, no_rag = results["rag"], results["no_rag"]
    assert rag["accuracy"] == pytest.approx(2 / 3)
    assert rag["technical_total"] == 2
    assert rag["citation_hits"] == 1
    assert rag["citation_accuracy"] == 0.5
    assert no_rag["citation_accuracy"] == 0.0
    assert rag["key_point_hits"] == 2
    assert rag["key_point_total"] == 4
    assert rag["key_point_coverage"] == 0.5
    assert no_rag["key_point_coverage"] == 0.25
    assert rag["rows"][0]["matched_key_points"] == ["X-API-Key"]
    assert rag["rows"][0]["key_point_coverage"] == 0.5
    assert rag["rows"][2]["citation_hit"] is None


def test_failed_technical_ticket_counts_against_both_quality_metrics():
    cases = (case("a", "technical", ["FAQ-1"], ["API"]),
             case("b", "technical", ["FAQ-2"], ["401", "key"]))
    processor = Mock(side_effect=[reply("technical", "api", ["FAQ-1"]), RuntimeError("secret")] * 2)
    results = evaluate(Mock(), processor=processor, cases=cases)
    for result in results.values():
        assert result["errors"] == 1
        assert result["citation_accuracy"] == 0.5
        assert result["key_point_coverage"] == pytest.approx(1 / 3)
        assert result["rows"][1]["citation_hit"] is False
        assert result["rows"][1]["key_point_coverage"] == 0.0


@pytest.mark.parametrize("cases", [(), (case("a", "account", [], []),)])
def test_empty_denominators_do_not_divide_by_zero(cases):
    processor = Mock(return_value=reply("account"))
    for result in evaluate(Mock(), processor=processor, cases=cases).values():
        assert result["technical_total"] == result["key_point_total"] == 0
        assert result["citation_accuracy"] == result["key_point_coverage"] == 0.0
