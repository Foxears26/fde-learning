[English](#english) | [中文](#中文)

<a id="english"></a>

# AI Demo: AI Exercises and Intelligent Ticket Evaluation

## Project overview

This directory contains DeepSeek multi-turn chat, weather tool calling, FAQ RAG question answering,
and the Project 2 intelligent ticket evaluation comparing RAG with no RAG. Chat and weather scripts
run independently. RAG question answering and ticket evaluation reuse modules in `fastapi/`.

- [Repository setup and project navigation](../README.md#english)
- [FastAPI: alerts and intelligent ticket endpoints](../fastapi/README.md#english)
- [Operations and troubleshooting runbook](../docs/runbook.md)
- [Project 2 postmortem](../docs/postmortem-tickets.md)

## Architecture

| File / module | Responsibility and workflow |
| --- | --- |
| `deepseek_chat.py` | DeepSeek multi-turn chat, adjustable temperature, streaming output, and token usage |
| `weather_agent.py` | Model selects `get_weather` → Open-Meteo city lookup and current weather → model generates a reply |
| `rag_demo.py` | Question → shared FAQ top-three retrieval → DeepSeek answer → source ID validation |
| `eval_tickets.py` | Scores the same 10 tickets through `ticket_service.process_ticket` with and without RAG |
| `../fastapi/rag.py` | Single source for 20 FAQ entries, embeddings, Chroma indexing, and retrieval |
| `test_rag_demo.py` / `test_eval_tickets.py` | Automated tests for FAQ answers and evaluation rules |

Technical tickets are classified first, then retrieve the top three FAQ entries and generate a reply.
Nontechnical tickets do not initialize the retriever. Local FAQ indexes and model caches are stored
in `ai-demo/.chroma/`.

## How to run

All commands use Windows PowerShell and run from the repository root. Prepare Python 3.11,
create a virtual environment, and install the root dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configure `.env` in the repository root:

```dotenv
DEEPSEEK_API_KEY=replace-with-your-key
DEEPSEEK_MODEL=deepseek-flash
```

`DEEPSEEK_MODEL` applies to RAG question answering and the ticket workflow. The chat and weather
scripts currently use the fixed model `deepseek-flash`. Run the script you need:

```powershell
# Multi-turn chat; --stream enables streaming output
.\.venv\Scripts\python.exe ai-demo/deepseek_chat.py --temperature 0.2 --stream

# Weather tool calling
.\.venv\Scripts\python.exe ai-demo/weather_agent.py

# FAQ RAG question answering; the first run downloads the embedding model
.\.venv\Scripts\python.exe ai-demo/rag_demo.py
```

Enter `Q/q` to exit any of these three interactive scripts. Real model calls consume API credit.
For the Project 2 HTTP service, see [FastAPI startup instructions](../fastapi/README.md#how-to-run).

## Tests

Run the RAG and evaluation rule tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

To also check the ticket endpoint:

```powershell
.\.venv\Scripts\python.exe -m pytest fastapi/test_tickets.py ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

These tests mock the LLM, use a temporary Chroma database and deterministic embedding substitutes,
and need no network, API key, model download, or PostgreSQL. They consume no API credit and do not
represent real model evaluation results.

## Eval results

Project 2 compares the same 10 tickets with and without RAG. No HTTP service or database is needed:

```powershell
.\.venv\Scripts\python.exe ai-demo/eval_tickets.py
```

The script reads the root `.env` and makes up to 40 LLM calls, consuming API credit. It prints aggregate
and individual results and exits with a nonzero code if any calls fail. The following figures were
provided by the user in existing project records; no model evaluation was rerun for this documentation update.

| Metric | With RAG | Without RAG | Definition / note |
| --- | --- | --- | --- |
| Classification accuracy | 100% | 100% | Classification happens before retrieval and is independent of RAG |
| Citation accuracy | 75% | 0% | Fraction of expected technical tickets citing at least one expected FAQ |
| Key information coverage | 85% | 75% | Expected key points matched in suggested replies / total expected key points |

Citation scoring includes only tickets expected to be technical. Key points use case-insensitive
substring matching. Failed cases remain in the denominators. Rule matching does not determine whether
a citation supports a conclusion; manual review is still needed. Raw output, runtime model, and code
version were not supplied with the recorded figures. When rerunning, save the full output, model name,
commit, and time to avoid comparing different versions directly.

## Known issues

- T07 (creation returns 422) received a reply quality score of 0 in both modes in the recorded evaluation.
  The cause remains unconfirmed. FAQ-6 / FAQ-7 already contain `info / warning / critical`. Check the
  actual top-three retrieval, reply, expected FAQ, and matching rules. A quality score of 0 does not mean misclassification.
- The evaluation has only 10 cases. Improved citation and information coverage metrics do not prove all replies are better.
- The first RAG run downloads the embedding model. Local and Docker caches are separate.
- The weather tool supports current weather only, not future forecasts. Network or city matching problems can cause failures.
- Chat history stays in the current process's memory and is lost on exit.

---

<a id="中文"></a>

# AI Demo：AI 练习与智能工单评估

## 项目简介

本目录包含 DeepSeek 多轮聊天、天气工具调用、FAQ RAG 问答，以及项目 2 智能工单的
有 / 无 RAG 对比评估。聊天和天气脚本可独立运行；RAG 问答及工单评估复用 `fastapi/` 的模块。

- [仓库入门与项目导航](../README.md#中文)
- [FastAPI：告警与智能工单接口](../fastapi/README.md#中文)
- [运行与排障手册](../docs/runbook.md)
- [项目 2 复盘](../docs/postmortem-tickets.md)

## 架构

| 文件 / 模块 | 职责与调用关系 |
| --- | --- |
| `deepseek_chat.py` | DeepSeek 多轮聊天、可调 temperature、流式输出与 token 用量 |
| `weather_agent.py` | 模型选择 `get_weather` → Open-Meteo 城市与当前天气查询 → 模型生成回答 |
| `rag_demo.py` | 问题 → 共享 FAQ top-3 检索 → DeepSeek 回答 → 来源 ID 校验 |
| `eval_tickets.py` | 同一批 10 条工单分别调用 `ticket_service.process_ticket` 的有 / 无 RAG 模式并计分 |
| `../fastapi/rag.py` | 唯一一份 20 条 FAQ、embedding、Chroma 索引与检索逻辑 |
| `test_rag_demo.py` / `test_eval_tickets.py` | FAQ 问答与评估规则的自动化测试 |

技术工单先分类，再检索 top-3 FAQ 并生成回复；非技术类不初始化检索器。
本地 FAQ 索引和模型缓存位于 `ai-demo/.chroma/`。

## 如何运行

以下命令以 Windows PowerShell 为例，均从仓库根目录执行。准备 Python 3.11，
创建虚拟环境并安装根目录依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

在根目录 `.env` 配置：

```dotenv
DEEPSEEK_API_KEY=replace-with-your-key
DEEPSEEK_MODEL=deepseek-flash
```

`DEEPSEEK_MODEL` 用于 RAG 问答与工单流程；聊天和天气脚本当前固定使用 `deepseek-flash`。
运行所需的脚本：

```powershell
# 多轮聊天；可选 --stream 流式输出
.\.venv\Scripts\python.exe ai-demo/deepseek_chat.py --temperature 0.2 --stream

# 天气工具调用
.\.venv\Scripts\python.exe ai-demo/weather_agent.py

# FAQ RAG 问答；首次需要下载 embedding 模型
.\.venv\Scripts\python.exe ai-demo/rag_demo.py
```

以上三个交互脚本均输入 `Q/q` 退出，真实模型请求会消耗 API 额度。
项目 2 HTTP 接口启动方式见 [FastAPI 如何运行](../fastapi/README.md#如何运行)。

## 测试

在仓库根目录运行 RAG 与 eval 规则测试：

```powershell
.\.venv\Scripts\python.exe -m pytest ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

同时验证工单接口：

```powershell
.\.venv\Scripts\python.exe -m pytest fastapi/test_tickets.py ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

这些测试 mock LLM，使用临时 Chroma 库和确定性 embedding 替身，不需要网络、API key、
模型下载或 PostgreSQL，也不消耗 API 额度。它们不代表真实模型评估结果。

## Eval 结果

项目 2 使用同一批 10 条工单对比有 / 无 RAG，无需先启动 HTTP 服务或数据库：

```powershell
.\.venv\Scripts\python.exe ai-demo/eval_tickets.py
```

脚本读取根目录 `.env`，最多发起 40 次 LLM 请求，会消耗 API 额度；输出汇总及逐条结果，
出现失败时以非零退出码结束。以下为已有项目记录中用户提供的结果，本次文档更新未重新调用模型。

| 指标 | 有 RAG | 无 RAG | 说明 |
| --- | --- | --- | --- |
| 分类准确率 | 100% | 100% | 分类在检索前完成，与 RAG 无关 |
| 引用准确率 | 75% | 0% | 期望技术类工单中，引用至少一个期望 FAQ 的比例 |
| 关键信息覆盖率 | 85% | 75% | 建议回复命中的期望信息点总数 / 期望信息点总数 |

引用指标仅统计期望技术类工单；信息点使用忽略大小写的子串匹配；失败样本保留在分母内。
规则匹配不判断引用是否支持结论，仍需人工检查。原始输出、运行时模型和代码版本未随
已有数字提供；复跑时应保留完整输出、模型名、commit 和时间，避免跨版本直接比较。

## 已知问题

- T07（创建返回 422）在已记录评估中两种模式的回复质量得分均为 0，根因尚未确认。
  当前 FAQ-6 / FAQ-7 已含 `info / warning / critical`，仍需检查实际 top-3、回复、期望 FAQ
  和匹配规则；质量 0 分不代表分类错误。
- 评估只有 10 条样本，引用与信息覆盖指标提高不足以证明所有回复质量都提高。
- 首次 RAG 运行需要下载 embedding 模型；本地与 Docker 缓存独立。
- 天气工具只支持当前天气，不支持未来预报；网络或城市匹配问题可能导致查询失败。
- 聊天历史只保存在本次进程内存中，退出后不保留。
