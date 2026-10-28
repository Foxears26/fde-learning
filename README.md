# fde-learning

学习仓库包含天气查询、告警 API + 智能工单 API。
智能工单使用 DeepSeek 分类和生成回复，技术类工单通过 Chroma 检索 D3 的 20 条 FAQ。
本页以 Windows PowerShell 为例，所有命令从仓库根目录执行。

 eval 对比结果表：
   - 分类准确率：有 RAG 100% vs 无 RAG 100%（注明：分类在检索前完成，与 RAG 无关）
   - 引用准确率：有 RAG 75% vs 无 RAG 0%
   - 关键信息覆盖率：有 RAG 85% vs 无 RAG 75%

## 1. 准备环境和代码

准备 Git、Python 3.11，以及有可用额度的 DeepSeek API key。选择容器方式时还需
安装并启动 Docker Desktop（Linux containers）；本地跑 `/tickets` 无需 Docker 或 PostgreSQL。
首次安装依赖和下载 embedding 模型需要网络。

先从团队仓库获取地址，在新目录克隆；已有代码则直接进入该目录：

```powershell
git clone <团队提供的仓库地址> fde-learning
Set-Location fde-learning
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

这里直接使用虚拟环境中的 Python，无需执行激活脚本。依赖包含 PyTorch 相关包，首次安装可能较慢。

## 2. 创建本地环境文件

用编辑器在仓库根目录创建 `.env`。若已存在，保留其他配置，只补充缺少的字段。
用自己的 key 替换占位符，每行一个 `名称=值`，不加 PowerShell 的 `$env:` 前缀：

```dotenv
DEEPSEEK_API_KEY=replace-with-your-key
DEEPSEEK_MODEL=deepseek-flash
```

`.env` 已被 `.gitignore` 和 `.dockerignore` 排除。不要提交 key，也不要将它写入
Dockerfile 的 `ENV`、`ARG` 或源码。Docker 在启动时用 `--env-file .env` 注入配置，
无需把文件复制进镜像。环境变量明细见 [runbook](docs/runbook.md#环境变量)。

## 3. 先跑不依赖外部服务的测试

```powershell
.\.venv\Scripts\python.exe -m pytest fastapi/test_tickets.py ai-demo/test_rag_demo.py ai-demo/test_eval_tickets.py -q
```

这些测试 mock LLM，不消费额度，也不下载 embedding 模型；其中 RAG 测试使用临时
Chroma 库和确定性 embedding 替身。完整 `fastapi/` 测试还需要独立 PostgreSQL 测试库，
参见 [FastAPI README](fastapi/README.md#测试)。

## 4. 启动 API

在当前终端启动本地服务：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir fastapi --env-file .env --reload --host 127.0.0.1 --port 8000
```

打开 [接口文档](http://127.0.0.1:8000/docs)。保持服务终端运行，在第二个 PowerShell
窗口进行以下检查。也可选择 [Docker 启动方式](docs/runbook.md#docker-启动)，同一个
宿主机端口只运行一个服务。

## 5. 检查服务和两条处理路径

先确认服务响应，再通过 Swagger 的 `POST /tickets` → Try it out 发送示例：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/hello
```

预期返回 `message: Hello World`。这个检查不验证 LLM、RAG 或数据库。

非技术类工单：

```json
{"title":"申请发票","description":"请问如何获取上个月付款的发票？"}
```

技术类工单：

```json
{"title":"API 返回 401","description":"所有 /alerts 请求均提示 Invalid API key，请指导排查。"}
```

预期 HTTP 200，返回 `category`、`urgency`、`suggested_reply`、`citations`。
非技术类 `citations` 应为空数组；技术类检索 top-3，并返回实际引用的 FAQ ID 和原文。
若资料不足，技术类也可能返回空引用及补充信息请求，不能把 HTTP 200 当作答案质量保证。
`/tickets` 无需 `X-API-Key`；首次技术请求会加载或下载 embedding 模型，查看服务端日志等待完成。

## 6. 跑真实评估

在仓库根目录的第二个终端执行：

```powershell
.\.venv\Scripts\python.exe ai-demo/eval_tickets.py
```

这会对 10 条工单运行有 RAG / 无 RAG 两种模式，最多调用 LLM 40 次，会消耗额度。
不需要先启动 HTTP 服务；脚本直接调用同一套工单处理流程。输出含分类、引用和信息覆盖
指标及逐条结果；存在失败时退出码非零。数值可能随模型和代码变化。

阅读 [已记录的评估对比与 T07 待查问题](fastapi/README.md#eval-对比结果)。分类在检索前
完成，与 RAG 无关；回复质量应结合引用和关键信息指标以及人工检查来评估。

## 7. 按需启用项目 1

`/alerts` 依赖 PostgreSQL，并要求 `X-API-Key: dev-secret-key`。已有学习数据库容器
可执行 `docker start pg-alerts`；从零创建数据库、建表与容器联网步骤见
[runbook](docs/runbook.md#可选启用-alerts-数据库)。数据库停止影响 `/alerts`，
不影响 `/tickets` 的处理流程；`/tickets` 仍需要 DeepSeek 与技术类的本地 FAQ 模型。

## 后续阅读

- [FastAPI 接口、评估结果与测试](fastapi/README.md)
- [运行与排障手册](docs/runbook.md)
- [项目 2 复盘](docs/postmortem-tickets.md)
- [AI 练习目录](ai-demo/Readme.md)
- [天气查询项目](weathercheck/README.md)
