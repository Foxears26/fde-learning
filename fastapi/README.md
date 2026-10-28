# Alert API
一个告警管理的 REST API（FastAPI），支持增删改查、分页、API Key 鉴权。

## 项目 2：智能工单

在仓库根目录安装 `python -m pip install -r requirements.txt`，在环境变量或根目录
`.env` 设置 `DEEPSEEK_API_KEY`。可选 `DEEPSEEK_MODEL`，默认 `deepseek-flash`。
启动方式仍为在 `fastapi/` 下运行 `uvicorn main:app --reload`。

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

在仓库根目录运行无需网络、密钥、模型下载或数据库的测试：

```powershell
python -m pytest fastapi/test_tickets.py ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

真实评估（读取 key，会消耗 API 额度，最多 40 次 LLM 请求）：

```powershell
python ai-demo/eval_tickets.py
```

脚本包含 10 条附期望分类、期望 FAQ 引用和期望关键信息点的工单。两种模式都走与
接口相同的处理流程，输出分类准确率、引用准确率、关键信息覆盖率和失败数。
引用准确率是引用至少一个期望 FAQ 的技术工单数占全部期望技术工单数的比例；
非技术类不参与。关键信息覆盖率是建议回复命中的信息点总数占期望信息点总数的比例，
采用忽略大小写的子串匹配。失败样本保留在各指标分母内，并以非零退出码报告失败。
分类与 RAG 无关：分类发生在检索前，准确率差异可能来自模型波动。
这两项规则指标不判断引用是否支持结论，仍需人工检查。

## 快速开始
### 本地运行
pip install -r ../requirements.txt  # 在 fastapi/ 目录下
docker start pg-alerts
uvicorn main:app --reload   # 在 fastapi/ 目录下
### Docker 运行
docker build -t alert-api .
docker run -d -p 8000:8000 --name alert-api alert-api

## 鉴权
所有 /alerts 请求带 header：X-API-Key: dev-secret-key

## GitHub OAuth 登录 demo

在 GitHub OAuth App 中将回调地址设为 `http://localhost:8000/auth/callback`。
启动服务前，在当前 PowerShell 设置环境变量（填入自己的值）：

```powershell
$env:GITHUB_CLIENT_ID = "<你的 Client ID>"
$env:GITHUB_CLIENT_SECRET = "<你的 Client Secret>"
uvicorn main:app --reload
```

浏览器访问 `http://localhost:8000/login`，授权后返回
`{"login": "用户名", "message": "欢迎 用户名"}`。
`/login` 和 `/auth/callback` 无需 API Key；凭据仅在请求时从环境变量读取。
此 demo 只演示授权及获取用户名，不创建登录会话。

## 接口列表
| 方法 | 路径 | 说明 |
| GET | /alerts | 列表（支持 page / page_size 分页） |
| GET | /alerts/{level} | 按 level 查（info / warning / critical） |
| POST | /alerts | 新建（201） |
| PUT | /alerts/{id} | 更新 |
| DELETE | /alerts/{id} | 删除 |
交互式文档：服务启动后打开 http://127.0.0.1:8000/docs

## PostgreSQL

告警通过 SQLAlchemy ORM 存入 PostgreSQL 的 `alerts` 表。连接串从环境变量
`DATABASE_URL` 读取，默认值为
`postgresql+psycopg2://postgres:devpassword@localhost:5432/alertsdb`。
本地使用已有的 `alertsdb` 和 `alerts` 表；运行 uvicorn 前先启动 `pg-alerts`。

## 测试

首次运行前创建独立测试库：

```powershell
docker start pg-alerts
docker exec pg-alerts psql -U postgres -c "CREATE DATABASE alertsdb_test"
python -m pytest -v
```

测试使用 `DATABASE_URL` 的连接信息，但固定数据库名为 `alertsdb_test`，
不会清理开发库。需要其他测试服务器时可设置 `TEST_DATABASE_URL`，库名仍固定为
`alertsdb_test`。测试自动建表，每个测试前清空告警表、重置 ID 并插入原有四条
种子数据，测试后再次清空。CI 使用 PostgreSQL 16 service 自动创建测试库。
