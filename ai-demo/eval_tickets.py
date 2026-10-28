"""同一批 10 条工单对比有/无 RAG。真实调用 DeepSeek，最多 40 次 LLM 请求。

运行：python ai-demo/eval_tickets.py
分类与 RAG 无关；另评估期望 FAQ 命中率和关键信息覆盖率。
指标是规则匹配，不判断引用是否支持结论，也不衡量完整的回复质量。
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fastapi"))
from ticket_service import Ticket, create_client, process_ticket


# 期望引用只适用于技术类；关键信息点采用忽略大小写的子串匹配。
CASES = (
    {"id": "T01", "title": "重复扣款", "description": "本月订阅被扣款两次，请核对账单并退款。",
     "expected_category": "billing", "expected_citations": [], "expected_key_points": ["账单", "退款"]},
    {"id": "T02", "title": "需要发票", "description": "请问如何获取上个月付款的发票？",
     "expected_category": "billing", "expected_citations": [], "expected_key_points": ["发票"]},
    {"id": "T03", "title": "取消续费", "description": "我希望取消下月自动续费，已支付费用可以退吗？",
     "expected_category": "billing", "expected_citations": [], "expected_key_points": ["续费", "退款"]},
    {"id": "T04", "title": "生产 API 全部 401", "description": "所有 /alerts 请求均返回 Invalid API key，生产业务中断。",
     "expected_category": "technical", "expected_citations": ["FAQ-1"], "expected_key_points": ["X-API-Key", "401"]},
    {"id": "T05", "title": "分页为空", "description": "GET /alerts?page=20&page_size=10 返回空 items，如何排查？",
     "expected_category": "technical", "expected_citations": ["FAQ-4"], "expected_key_points": ["total", "page_size"]},
    {"id": "T06", "title": "429 重试", "description": "调用 API 被限流，Retry-After 应怎么处理？",
     "expected_category": "technical", "expected_citations": ["FAQ-12"], "expected_key_points": ["Retry-After", "响应"]},
    {"id": "T07", "title": "创建返回 422", "description": "POST /alerts 的 level 传 urgent 后失败，正确取值是什么？",
     "expected_category": "technical", "expected_citations": ["FAQ-7"], "expected_key_points": ["info", "warning", "critical"]},
    {"id": "T08", "title": "忘记密码", "description": "无法登录我的账户，请指导我重置密码。",
     "expected_category": "account", "expected_citations": [], "expected_key_points": ["重置", "密码"]},
    {"id": "T09", "title": "修改邮箱", "description": "需要将个人账户的登录邮箱更换为新邮箱。",
     "expected_category": "account", "expected_citations": [], "expected_key_points": ["邮箱", "验证"]},
    {"id": "T10", "title": "注销账户", "description": "我不再使用这个账户，请问如何申请注销？",
     "expected_category": "account", "expected_citations": [], "expected_key_points": ["注销", "账户"]},
)


def evaluate(client, *, processor=process_ticket, cases=CASES):
    results = {}
    for use_rag in (True, False):
        rows = []
        for case in cases:
            expected = case["expected_category"]
            technical = expected == "technical"
            row = {
                "id": case["id"], "expected": expected, "predicted": None,
                "correct": False, "error": None,
                "expected_citations": case["expected_citations"],
                "expected_key_points": case["expected_key_points"],
                "citation_hit": False if technical else None,
                "matched_key_points": [],
                "key_point_total": len(case["expected_key_points"]),
                "key_point_coverage": 0.0,
            }
            try:
                result = processor(
                    Ticket(title=case["title"], description=case["description"]),
                    client, use_rag=use_rag,
                )
                cited = {citation.id for citation in result.citations}
                text = result.suggested_reply.casefold()
                matched = [point for point in case["expected_key_points"]
                           if point.casefold() in text]
                row.update(
                    predicted=result.category, correct=result.category == expected,
                    citation_hit=bool(cited.intersection(case["expected_citations"]))
                    if technical else None,
                    matched_key_points=matched,
                    key_point_coverage=len(matched) / row["key_point_total"]
                    if row["key_point_total"] else 0.0,
                )
            except Exception as exc:
                # 失败也计入各指标的分母；不输出可能包含凭据的异常正文。
                row["error"] = type(exc).__name__
            rows.append(row)
        total = len(rows)
        correct = sum(row["correct"] for row in rows)
        technical_total = sum(row["expected"] == "technical" for row in rows)
        citation_hits = sum(row["citation_hit"] is True for row in rows)
        key_point_hits = sum(len(row["matched_key_points"]) for row in rows)
        key_point_total = sum(row["key_point_total"] for row in rows)
        results["rag" if use_rag else "no_rag"] = {
            "rows": rows, "total": total, "correct": correct,
            "errors": sum(row["error"] is not None for row in rows),
            "accuracy": correct / total if total else 0.0,
            "technical_total": technical_total, "citation_hits": citation_hits,
            "citation_accuracy": citation_hits / technical_total if technical_total else 0.0,
            "key_point_hits": key_point_hits, "key_point_total": key_point_total,
            "key_point_coverage": key_point_hits / key_point_total if key_point_total else 0.0,
        }
    return results


def print_report(results):
    print("| 模式 | 分类正确/总数 | 分类准确率（分类与 RAG 无关） | 引用准确率 | 关键信息覆盖率 | 失败数 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for mode, label in (("rag", "有 RAG"), ("no_rag", "无 RAG")):
        result = results[mode]
        print(f'| {label} | {result["correct"]}/{result["total"]} | '
              f'{result["accuracy"]:.1%} | {result["citation_accuracy"]:.1%} | '
              f'{result["key_point_coverage"]:.1%} | {result["errors"]} |')
    for mode, label in (("rag", "有 RAG"), ("no_rag", "无 RAG")):
        print(f"{label} 逐条结果：")
        for row in results[mode]["rows"]:
            citation = ("命中" if row["citation_hit"] else "未命中") if row["citation_hit"] is not None else "不适用"
            print(f'  {row["id"]}: expected={row["expected"]}, '
                  f'predicted={row["predicted"]}, 引用={citation}, '
                  f'信息覆盖={len(row["matched_key_points"])}/{row["key_point_total"]}, '
                  f'error={row["error"] or "-"}')
    delta = results["rag"]["accuracy"] - results["no_rag"]["accuracy"]
    print(f"有 RAG - 无 RAG：{delta:+.1%}（分类准确率差）")
    print("分类与 RAG 无关：分类在检索前完成，分类差异可能来自模型波动。")
    print("引用准确率 = 引用了至少一个期望 FAQ 的技术工单数 / 期望分类为 technical 的工单数；非技术类不参与。")
    print("关键信息覆盖率 = 命中的期望信息点总数 / 全部期望信息点总数；仅检查建议回复，忽略大小写。")
    print("失败工单保留在分母中；无适用样本或无期望信息点时记为 0%。规则匹配不判断引用是否支持结论。")


def main():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    try:
        client = create_client()
    except RuntimeError as exc:
        print(str(exc))
        return 1
    with client:
        results = evaluate(client)
    print_report(results)
    return int(any(result["errors"] for result in results.values()))


if __name__ == "__main__":
    raise SystemExit(main())
