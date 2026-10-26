# Alert API
一个告警管理的 REST API（FastAPI），支持增删改查、分页、API Key 鉴权。

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
