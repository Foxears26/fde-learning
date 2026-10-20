# Alert API
一个告警管理的 REST API（FastAPI），支持增删改查、分页、API Key 鉴权。

## 快速开始
### 本地运行
pip install -r requirements.txt
uvicorn main:app --reload   # 在 fastapi/ 目录下
### Docker 运行
docker build -t alert-api .
docker run -d -p 8000:8000 --name alert-api alert-api

## 鉴权
所有请求带 header：X-API-Key: dev-secret-key

## 接口列表
| 方法 | 路径 | 说明 |
| GET | /alerts | 列表（支持 page / page_size 分页） |
| GET | /alerts/{level} | 按 level 查（info / warning / critical） |
| POST | /alerts | 新建（201） |
| PUT | /alerts/{id} | 更新 |
| DELETE | /alerts/{id} | 删除 |
交互式文档：服务启动后打开 http://127.0.0.1:8000/docs
