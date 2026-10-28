# Runbook：告警与智能工单 API

命令以 Windows PowerShell 为例，从仓库根目录执行。首次安装和 key 配置见
[入门 README](../README.md)。本手册描述当前代码；旧版“告警数据存内存、重启清空”已不适用，
告警现存 PostgreSQL，工单接口不保存工单。

## 环境变量

| 变量 | 用途 | 默认或要求 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | `/tickets` 和真实 eval 调用 DeepSeek | 必填；缺少时 `/tickets` 返回 503 |
| `DEEPSEEK_MODEL` | 分类与生成模型 | 默认 `deepseek-flash` |
| `DATABASE_URL` | `/alerts` 的 PostgreSQL 连接 | 默认 `postgresql+psycopg2://postgres:devpassword@localhost:5432/alertsdb` |
| `TEST_DATABASE_URL` | 告警集成测试连接 | 可选；测试固定使用 `alertsdb_test` 库 |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | GitHub OAuth 示例 | 仅使用登录功能时配置 |

在根目录 `.env` 中使用 `KEY=value` 格式。`/alerts` 的 `dev-secret-key` 是当前代码中的
开发用 API Key，不是 DeepSeek key，也不由 `DEEPSEEK_API_KEY` 配置。

本地用 `uvicorn --env-file .env` 在导入应用前加载环境，确保 `DATABASE_URL` 生效。
Docker 用 `docker run --env-file .env` 注入；key 不进镜像，不写进 Dockerfile 的 `ENV`、
`ARG` 或构建参数。当前 `.dockerignore` 排除 `.env`，Dockerfile 仅复制依赖文件和 `fastapi/`。
修改 `.env` 后，本地重新启动服务；Docker 重新创建容器，`docker restart` 不会重新读取该文件。

参考：[Docker run 环境变量与 env-file](https://docs.docker.com/reference/cli/docker/container/run/#env)。

## 本地 uvicorn 启动

完成虚拟环境与依赖安装后执行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir fastapi --env-file .env --reload --host 127.0.0.1 --port 8000
```

`Ctrl+C` 停止。`--reload` 用于本地开发。本地 FAQ 和模型缓存位于 `ai-demo/.chroma/`。
项目 2 单独运行不需要 `pg-alerts`；需要 `/alerts` 再启用数据库。

## Docker 启动

先启动 Docker Desktop，`docker version` 应能显示 Server。构建上下文必须是仓库根目录：

```powershell
docker build -t alert-api:project2 .
docker run -d --name alert-api -p 127.0.0.1:8000:8000 --env-file .env --mount type=volume,source=tickets-chroma,target=/app/ai-demo/.chroma alert-api:project2
docker logs -f alert-api
```

`Ctrl+C` 只退出日志跟踪。`docker stop alert-api` 才停止服务。
命名卷 `tickets-chroma` 保存容器自己的模型缓存和索引；不会自动复用 Windows 本地
`ai-demo/.chroma/`。首次技术请求仍可能下载模型。Dockerfile 不包含 `ai-demo/` 脚本，
真实 eval 在宿主机的虚拟环境运行。

代码改动后重新构建并替换应用容器（移除的是名为 `alert-api` 的应用容器，保留命名卷）：

```powershell
docker build -t alert-api:project2 .
docker stop alert-api
docker rm alert-api
docker run -d --name alert-api -p 127.0.0.1:8000:8000 --env-file .env --mount type=volume,source=tickets-chroma,target=/app/ai-demo/.chroma alert-api:project2
```

没有旧容器时跳过 stop/rm。重 build 后仍必须创建新容器；同名 tag 更新不会改变现有
容器使用的镜像。不要用 `docker start` 或 `docker restart` 代替更新流程。

## 冒烟检查与日志

```powershell
Invoke-RestMethod http://127.0.0.1:8000/hello
$schema = Invoke-RestMethod http://127.0.0.1:8000/openapi.json
$schema.paths.PSObject.Properties.Name
```

`/hello` 应返回 `Hello World`，路径列表应含 `/tickets`。这个检查无需 key，
也不验证 LLM、检索或 PostgreSQL。到 [Swagger](http://127.0.0.1:8000/docs) 发送
[README 示例](../README.md#5-检查服务和两条处理路径)，检查实际返回的分类、建议和引用。

本地看 uvicorn 终端；需要落盘时，将启动命令输出重定向到 `app.log`。
容器使用 `docker logs --tail 100 alert-api`。应用日志包含 `request_id`、请求方法、
路径、状态码和耗时；当前 `request_id` 未通过响应头返回，可按时间和路径定位。
记录问题时保留脱敏请求和状态码，不记录 key 或数据库密码。

## 常见问题

| 现象 | 检查与处理 |
| --- | --- |
| 8000 端口冲突 | 检查是否同时运行本地 uvicorn 和容器；停止自己启动的旧实例，或本地改 `--port 8001`，Docker 改 `-p 127.0.0.1:8001:8000`，并同步修改访问 URL |
| Docker 无法连接 daemon | 启动 Docker Desktop 并等待 Engine 就绪，再用 `docker version` 检查 Server |
| 容器名已被占用 | `docker ps -a` 确认 `alert-api`；代码更新按上面的 build、stop、rm、run 流程处理 |
| `/tickets` 返回 404 | 查当前端口与 `/openapi.json`，确认请求打到新服务；容器可能仍使用未加入路由的旧镜像，重新 build 并创建容器 |
| 首次技术工单很慢 | 首次下载多语言 embedding 模型及初始化 20 条 FAQ；看日志、检查模型下载网络和磁盘，等待完成，保留缓存后再请求 |
| 本地已下载，Docker 仍很慢 | 两者缓存独立；Docker 使用 `tickets-chroma` 卷，首次需单独准备 |
| `/tickets` 返回 503 | 缺少 `DEEPSEEK_API_KEY`，或 FAQ 模型/存储初始化不可用；检查配置、下载网络、缓存目录权限和日志 |
| `/tickets` 返回 502 | DeepSeek 网络、凭据、额度、模型名或输出结构/引用校验失败；核对配置及脱敏错误，不反复盲重试 |
| 422 | `/tickets` 检查 title/description 必填且非空；`/alerts` 检查 level 仅为 info、warning、critical，并读取 detail 中的字段位置 |
| `/alerts` 返回 401 | 检查 `X-API-Key: dev-secret-key` 的值；header 名大小写不敏感 |
| `pg-alerts` 停止，`/alerts` 报数据库连接错误 | 启动 `pg-alerts`，核对连接串和表结构；这不影响 `/tickets`，其流程不访问数据库 |
| 容器立即退出 | 先查 `docker logs alert-api` 的导入、依赖或配置错误，再修改；不要只看宿主机代码推断容器内容 |

端口占用可用 `Get-NetTCPConnection -LocalPort 8000 -State Listen` 查看 PID，再用
`Get-Process -Id <PID>` 确认进程；只停止已经确认属于本项目的实例。

## 可选启用 alerts 数据库

已有 `pg-alerts` 容器时：

```powershell
docker start pg-alerts
```

全新环境且不存在同名容器时，创建学习用 PostgreSQL（下列凭据只用于本地练习）：

```powershell
docker run -d --name pg-alerts -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=devpassword -e POSTGRES_DB=alertsdb -p 5432:5432 --mount type=volume,source=alerts-pgdata,target=/var/lib/postgresql/data postgres:16
docker exec pg-alerts pg_isready -U postgres -d alertsdb
```

等待就绪后，用当前 ORM 在新库创建表。在仓库根目录执行一次；已有库不会自动升级表结构：

```powershell
.\.venv\Scripts\python.exe -c "import sys; from dotenv import load_dotenv; load_dotenv('.env'); sys.path.insert(0, 'fastapi'); from db_models import Base; from database import engine; Base.metadata.create_all(engine)"
```

本地 uvicorn 使用 `.env` 中的 `DATABASE_URL` 或默认 localhost 连接。API 运行在
Docker Desktop 容器时，`localhost` 指 API 容器自身；重新创建 API 容器时在 run 命令中
额外加 `-e DATABASE_URL=postgresql+psycopg2://postgres:devpassword@host.docker.internal:5432/alertsdb`，
使用宿主机发布的 PostgreSQL 端口（此参数会覆盖 env-file 中的同名变量）。

验证 `/alerts`：

```powershell
Invoke-RestMethod -Headers @{"X-API-Key"="dev-secret-key"} http://127.0.0.1:8000/alerts
```

完整告警测试首次需要创建独立库；只在库尚不存在时执行：

```powershell
docker exec pg-alerts psql -U postgres -c "CREATE DATABASE alertsdb_test"
.\.venv\Scripts\python.exe -m pytest fastapi -q
```

测试会清理 `alertsdb_test` 的告警数据，保留开发库。已有测试库若出现列缺失或空值约束
错误，应先核对与当前 ORM 的结构（含 nullable `assignee`），不要直接视为工单路由回归。

## 评估与交接

按 [入门步骤](../README.md#6-跑真实评估) 运行 eval，保存完整 stdout、运行时模型名、
代码 commit 和时间。对比表及 T07 待查项见 [项目 README](../fastapi/README.md#eval-对比结果)。
两次运行应使用相同样本和期望字段；人工检查引用是否支持回复，不能只看分类准确率。
