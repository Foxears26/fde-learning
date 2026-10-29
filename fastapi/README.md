[English](#english) | [中文](#中文)

<a id="english"></a>

# FastAPI: Alerts API and Intelligent Ticket API

## Project overview

Project 1 provides a REST API for alert management, including CRUD, pagination, and API Key
authentication. Project 2 classifies tickets, assigns urgency, and suggests replies. Technical tickets
use FAQ retrieval to generate answers with citations. A GitHub OAuth login demo is also included.

- [Repository setup and project navigation](../README.md#english)
- [AI exercises and Project 2 evaluation](../ai-demo/Readme.md#english)
- [Operations and troubleshooting runbook](../docs/runbook.md)
- [Project 2 postmortem](../docs/postmortem-tickets.md)

## Architecture

- `main.py` mounts alert, OAuth, and ticket routes and logs requests.
- Alert routes access PostgreSQL through SQLAlchemy ORM; `/alerts` routes share API Key validation.
- Ticket routes call `ticket_service.py`: classify first, then retrieve and generate a reply based on the category. Pydantic validates the output.
- `rag.py` shares the FAQ, embeddings, Chroma index, and retrieval logic between the ticket service and AI exercises.

### Intelligent ticket workflow and endpoint

`POST /tickets` accepts:

```json
{"title":"Production API returns 401","description":"Calls to /alerts always return Invalid API key. How should I troubleshoot this?"}
```

Example response (classification, urgency, and wording may vary):

```json
{
  "category": "technical",
  "urgency": "high",
  "suggested_reply": "Check that the request includes the correct X-API-Key. [来源：FAQ-1]",
  "citations": [{"id": "FAQ-1", "document": "Full original text of the retrieved FAQ"}]
}
```

The citation marker `[来源：FAQ-1]` is kept in its required source format.
DeepSeek first classifies tickets as `billing / technical / account` and assigns urgency
`high / medium / low`. Technical tickets retrieve the top three D3 FAQ entries before reply generation.
`citations` contains only entries actually cited, with original text filled in by the server from
retrieval results. Nontechnical tickets generate replies without initializing retrieval and return
empty `citations`. `/tickets` currently requires no alerts API Key and does not store tickets.
A missing DeepSeek key returns 503; model request or output format failures return 502.
Model calls use DeepSeek [JSON Output](https://api-docs.deepseek.com/guides/json_mode/), and the
server validates category, urgency, and reply structure with Pydantic.

The shared `rag.py` module holds the single set of 20 FAQ entries, indexing, and retrieval logic.
`ai-demo/rag_demo.py` imports it too. It reuses `ai-demo/.chroma/` and the D3 embedding model cache.
The first technical request loads or downloads the multilingual embedding model; later requests reuse
the instance in the process. Run `python ai-demo/rag_demo.py` to prepare the cache before working offline.
Containers also need an initial model download. Mount `/app/ai-demo/.chroma` to persist the cache.

### Alert endpoints

Every `/alerts` request needs the header `X-API-Key: dev-secret-key`.

| Method | Path | Description |
| --- | --- | --- |
| GET | /alerts | List alerts with page / page_size pagination |
| GET | /alerts/{level} | Filter by level: info / warning / critical |
| POST | /alerts | Create an alert (201) |
| PUT | /alerts/{id} | Update an alert |
| DELETE | /alerts/{id} | Delete an alert |

After starting the service, open the [interactive API documentation](http://127.0.0.1:8000/docs).

## How to run

Run all commands from the repository root. Follow the [setup instructions](../README.md#english)
to install dependencies and configure `.env`. Project 2 requires `DEEPSEEK_API_KEY`.
`DEEPSEEK_MODEL` is optional and defaults to `deepseek-flash`.

### Local startup

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir fastapi --env-file .env --reload --host 127.0.0.1 --port 8000
```

### Docker startup

Start Docker Desktop, then run:

```powershell
docker build -t alert-api:project2 .
docker run -d --name alert-api -p 127.0.0.1:8000:8000 --env-file .env --mount type=volume,source=tickets-chroma,target=/app/ai-demo/.chroma alert-api:project2
```

The key is supplied at runtime through `--env-file`, not stored in the Dockerfile or image.
After changing code, rebuild and create a new container; see the [runbook](../docs/runbook.md).
`/tickets` needs no PostgreSQL. Configure and start the database when using `/alerts`.

### PostgreSQL for alerts

Alerts are stored in PostgreSQL's `alerts` table through SQLAlchemy ORM. The connection string
comes from `DATABASE_URL`, defaulting to:
`postgresql+psycopg2://postgres:devpassword@localhost:5432/alertsdb`.
Locally, use the existing `alertsdb` database and `alerts` table. Start `pg-alerts` before uvicorn.

For creating a database and tables from scratch, see the [database setup guide](../docs/runbook.md#可选启用-alerts-数据库).

### GitHub OAuth login demo

Set the callback URL in your GitHub OAuth App to `http://localhost:8000/auth/callback`.
Before starting the service, set the environment variables in the current PowerShell session:

```powershell
$env:GITHUB_CLIENT_ID = "<your-client-id>"
$env:GITHUB_CLIENT_SECRET = "<your-client-secret>"
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir fastapi --env-file .env --reload --host localhost --port 8000
```

Visit `http://localhost:8000/login` and authorize the app. The response contains the username and a
Chinese welcome message, for example `{"login": "username", "message": "欢迎 username"}`.
`/login` and `/auth/callback` require no API Key. Credentials are read from environment variables at
request time. This demo shows authorization and username lookup only; it does not create a login session.

## Tests

Run all commands from the repository root. First run ticket and RAG tests that need no network,
key, model download, or database:

```powershell
.\.venv\Scripts\python.exe -m pytest fastapi/test_tickets.py ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

The full FastAPI suite requires PostgreSQL. Start the existing container and create the test database
only if it does not already exist:

```powershell
docker start pg-alerts
docker exec pg-alerts psql -U postgres -c "CREATE DATABASE alertsdb_test"
.\.venv\Scripts\python.exe -m pytest fastapi -v
```

Tests use the connection settings in `DATABASE_URL` but force the database name to `alertsdb_test`;
they do not clear the development database. Set `TEST_DATABASE_URL` to use another test server;
the database name is still fixed to `alertsdb_test`. Tests create tables automatically. Before each
test they clear alerts, reset IDs, and insert the original four seed records; after each test they
clear the data again. CI uses a PostgreSQL 16 service to create the test database automatically.

## Eval results

Project 2's real evaluation reads `DEEPSEEK_API_KEY`, consumes API credit, and makes up to 40 LLM
calls. Run it from the repository root without starting an HTTP service:

```powershell
.\.venv\Scripts\python.exe ai-demo/eval_tickets.py
```

The script contains 10 tickets with expected categories, FAQ citations, and key information points.
Both modes use the same processing workflow as the endpoint. Output includes classification accuracy,
citation accuracy, key information coverage, and failure counts. Citation accuracy is the fraction
of all expected technical tickets citing at least one expected FAQ; nontechnical cases are excluded.
Key information coverage is the total expected points matched in suggested replies divided by all
expected points, using case-insensitive substring matching. Failed cases stay in the denominators
and cause a nonzero exit code. Classification is independent of RAG because it happens before
retrieval; differences may reflect model variability. These rule metrics do not determine whether
citations support conclusions, so manual review is still needed.

The following 10-ticket results were provided by the user in existing project records.
No model evaluation was rerun for this documentation update.

| Metric | With RAG | Without RAG | Definition / note |
| --- | --- | --- | --- |
| Classification accuracy | 100% | 100% | Classification happens before retrieval and is independent of RAG |
| Citation accuracy | 75% | 0% | Fraction of expected technical tickets citing at least one expected FAQ |
| Key information coverage | 85% | 75% | Expected key points matched in suggested replies / total expected key points |

The record shows improved citation and information coverage metrics, but 10 cases and rule matching
do not prove that every reply improves. Raw output, runtime model, and code version were not supplied
with these figures. Save them when rerunning to avoid comparing different versions directly.

## Known issues

T07 (creation returns 422) received a reply quality score of 0 in both modes. A knowledge gap or an
expected-answer issue is suspected, but the cause remains unconfirmed. FAQ-6 / FAQ-7 already include
`info / warning / critical`. Check the actual top-three retrieval, suggested reply, expected FAQ, and
substring matching rules before concluding that the knowledge base lacks the answer. Classification
is scored separately; a T07 quality score of 0 does not mean misclassification.

- `/tickets` does not store tickets. The GitHub OAuth demo retrieves a username but creates no login session.
- The first technical request downloads or loads the embedding model. Local and Docker caches are separate.
- The alerts API Key is still the fixed development value `dev-secret-key` in the code.
- See the [runbook](../docs/runbook.md#常见问题) for startup, old-image 404 errors, database schema issues, and 502/503 troubleshooting.

---

<a id="中文"></a>

# FastAPI：告警 API 与智能工单 API

## 项目简介

项目 1 提供告警管理 REST API，支持增删改查、分页和 API Key 鉴权；项目 2 提供
智能工单分类、紧急度判断及建议回复，技术类工单结合 FAQ 检索生成带引用的回答。
另附 GitHub OAuth 登录 demo。

- [仓库入门与项目导航](../README.md#中文)
- [AI 练习与项目 2 评估](../ai-demo/Readme.md#中文)
- [运行与排障手册](../docs/runbook.md)
- [项目 2 复盘](../docs/postmortem-tickets.md)

## 架构

- `main.py` 挂载告警、OAuth 和工单路由，并记录请求日志。
- 告警路由通过 SQLAlchemy ORM 访问 PostgreSQL；`/alerts` 统一校验 API Key。
- 工单路由调用 `ticket_service.py`：先分类，再按类别检索和生成回复，用 Pydantic 校验输出。
- `rag.py` 共享 FAQ、embedding、Chroma 索引及检索逻辑，供工单服务和 AI 练习复用。

### 智能工单流程与接口

`POST /tickets` 接收：

```json
{"title":"生产 API 返回 401","description":"调用 /alerts 总是提示 Invalid API key，如何排查？"}
```

返回示例（模型分类、紧急度和建议文字可能变化）：

```json
{
  "category": "technical",
  "urgency": "high",
  "suggested_reply": "请检查请求是否携带正确的 X-API-Key。[来源：FAQ-1]",
  "citations": [{"id": "FAQ-1", "document": "检索所得 FAQ 完整原文"}]
}
```

先用 DeepSeek 将工单分为 `billing / technical / account`，并判断
`high / medium / low`。技术类检索 D3 FAQ 的 top-3 后生成回复；`citations`
仅包含实际引用的片段，由服务端从检索结果回填原文。非技术类不初始化检索器，
直接生成回复并返回空 `citations`。`/tickets` 当前无需 alerts 的 API Key，
不保存工单。缺少 DeepSeek key 返回 503，模型请求或输出格式失败返回 502。
模型调用采用 DeepSeek 的 [JSON Output](https://api-docs.deepseek.com/guides/json_mode/)，
并在服务端用 Pydantic 校验分类、紧急度和回复结构。

`rag.py` 是共享检索模块，保存唯一一份 20 条 FAQ、索引与检索逻辑；
`ai-demo/rag_demo.py` 也从这里导入。沿用 `ai-demo/.chroma/` 和 D3 的 embedding
模型缓存。首次技术类请求需加载或下载多语言 embedding 模型，之后复用进程内实例。
离线运行前请先用 `python ai-demo/rag_demo.py` 准备缓存。容器首次运行也需要下载模型；
需要持久化缓存时挂载 `/app/ai-demo/.chroma`。

### 告警接口

所有 `/alerts` 请求带 header：`X-API-Key: dev-secret-key`。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /alerts | 列表（支持 page / page_size 分页） |
| GET | /alerts/{level} | 按 level 查（info / warning / critical） |
| POST | /alerts | 新建（201） |
| PUT | /alerts/{id} | 更新 |
| DELETE | /alerts/{id} | 删除 |

交互式文档：服务启动后打开 http://127.0.0.1:8000/docs

## 如何运行

以下命令在仓库根目录执行；先按 [入门步骤](../README.md#中文) 安装依赖并配置 `.env`。
项目 2 需要 `DEEPSEEK_API_KEY`；可选 `DEEPSEEK_MODEL`，默认 `deepseek-flash`。

### 本地启动

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir fastapi --env-file .env --reload --host 127.0.0.1 --port 8000
```

### Docker 启动

先启动 Docker Desktop，再执行：

```powershell
docker build -t alert-api:project2 .
docker run -d --name alert-api -p 127.0.0.1:8000:8000 --env-file .env --mount type=volume,source=tickets-chroma,target=/app/ai-demo/.chroma alert-api:project2
```

Key 在运行时通过 `--env-file` 传入，不写进 Dockerfile 或镜像。
改代码后必须重新 build 并创建新容器；完整操作见 [runbook](../docs/runbook.md)。
`/tickets` 无需启动 PostgreSQL；使用 `/alerts` 时再配置并启动数据库。

### PostgreSQL（告警功能）

告警通过 SQLAlchemy ORM 存入 PostgreSQL 的 `alerts` 表。连接串从环境变量
`DATABASE_URL` 读取，默认值为
`postgresql+psycopg2://postgres:devpassword@localhost:5432/alertsdb`。
本地使用已有的 `alertsdb` 和 `alerts` 表；运行 uvicorn 前先启动 `pg-alerts`。

从零创建数据库及建表步骤见 [数据库运行说明](../docs/runbook.md#可选启用-alerts-数据库)。

### GitHub OAuth 登录 demo

在 GitHub OAuth App 中将回调地址设为 `http://localhost:8000/auth/callback`。
启动服务前，在当前 PowerShell 设置环境变量（填入自己的值）：

```powershell
$env:GITHUB_CLIENT_ID = "<你的 Client ID>"
$env:GITHUB_CLIENT_SECRET = "<你的 Client Secret>"
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir fastapi --env-file .env --reload --host localhost --port 8000
```

浏览器访问 `http://localhost:8000/login`，授权后返回
`{"login": "用户名", "message": "欢迎 用户名"}`。
`/login` 和 `/auth/callback` 无需 API Key；凭据仅在请求时从环境变量读取。
此 demo 只演示授权及获取用户名，不创建登录会话。

## 测试

以下命令均在仓库根目录执行。先运行无需网络、密钥、模型下载或数据库的工单与 RAG 测试：

```powershell
.\.venv\Scripts\python.exe -m pytest fastapi/test_tickets.py ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

完整 FastAPI 测试需要 PostgreSQL。先启动已有容器，仅在测试库尚不存在时创建：

```powershell
docker start pg-alerts
docker exec pg-alerts psql -U postgres -c "CREATE DATABASE alertsdb_test"
.\.venv\Scripts\python.exe -m pytest fastapi -v
```

测试使用 `DATABASE_URL` 的连接信息，但固定数据库名为 `alertsdb_test`，
不会清理开发库。需要其他测试服务器时可设置 `TEST_DATABASE_URL`，库名仍固定为
`alertsdb_test`。测试自动建表，每个测试前清空告警表、重置 ID 并插入原有四条
种子数据，测试后再次清空。CI 使用 PostgreSQL 16 service 自动创建测试库。

## Eval 结果

<a id="eval-对比结果"></a>

项目 2 真实评估会读取 `DEEPSEEK_API_KEY` 并消耗 API 额度，最多 40 次 LLM 请求。
在仓库根目录运行，无需先启动 HTTP 服务：

```powershell
.\.venv\Scripts\python.exe ai-demo/eval_tickets.py
```

脚本包含 10 条附期望分类、期望 FAQ 引用和期望关键信息点的工单。两种模式都走与
接口相同的处理流程，输出分类准确率、引用准确率、关键信息覆盖率和失败数。
引用准确率是引用至少一个期望 FAQ 的技术工单数占全部期望技术工单数的比例；
非技术类不参与。关键信息覆盖率是建议回复命中的信息点总数占期望信息点总数的比例，
采用忽略大小写的子串匹配。失败样本保留在各指标分母内，并以非零退出码报告失败。
分类与 RAG 无关：分类发生在检索前，准确率差异可能来自模型波动。
这两项规则指标不判断引用是否支持结论，仍需人工检查。

以下为已有项目记录中用户提供的 10 条工单评估结果，本次文档更新未重新调用模型。

| 指标 | 有 RAG | 无 RAG | 说明 |
| --- | --- | --- | --- |
| 分类准确率 | 100% | 100% | 分类在检索前完成，与 RAG 无关 |
| 引用准确率 | 75% | 0% | 期望技术类工单中，引用至少一个期望 FAQ 的比例 |
| 关键信息覆盖率 | 85% | 75% | 建议回复命中的期望信息点总数 / 期望信息点总数 |

本次记录显示引用与信息覆盖指标提高，但 10 条样本及规则匹配不足以证明所有回复质量
都提高。原始输出、运行时模型和代码版本未随本次数字提供，复跑时应一并保留，避免跨版本直接比较。

## 已知问题

T07（创建返回 422）两种模式的回复质量得分均为 0，疑为知识库缺口或期望答案问题，
尚未确定根因。当前 FAQ-6 / FAQ-7 已包含 `info / warning / critical`，
后续应检查实际 top-3、建议回复、期望 FAQ 与子串匹配规则，不能仅凭 0 分确认知识库缺失。
分类得分仍单独统计，T07 的质量 0 分不代表分类错误。

- `/tickets` 当前不保存工单；GitHub OAuth demo 仅获取用户名，不创建登录会话。
- 首次技术工单请求需下载或加载 embedding 模型；本地和 Docker 缓存独立。
- 告警 API Key 仍为代码内的开发固定值 `dev-secret-key`。
- 服务启动、旧镜像 404、数据库结构及 502/503 排查见 [运行手册](../docs/runbook.md#常见问题)。
