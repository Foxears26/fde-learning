
from fastapi import Depends, FastAPI, HTTPException, Header
from routers.alerts import router as alerts_router
from routers.auth import router as auth_router
import logging, time, uuid, json
from dotenv import load_dotenv

load_dotenv()  # 从当前目录往上找，能找到根目录的 .env

app = FastAPI()

# alerts 路由在挂载时统一添加鉴权依赖。
API_KEY = "dev-secret-key"  # 先硬编码，再换环境变量later

def check_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


app.include_router(alerts_router, dependencies=[Depends(check_key)])
# 浏览器 OAuth 跳转不携带 X-API-Key，登录路由不绑定鉴权依赖。
app.include_router(auth_router)


@app.get("/hello")
def hello():
    return {"message": "Hello World"}

#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alerts")

@app.middleware("http")
async def log_requests(request, call_next):
    req_id = str(uuid.uuid4())[:8]
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(json.dumps({
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "level": "INFO",
        "request_id": req_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration,
    }))
    return response



if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
