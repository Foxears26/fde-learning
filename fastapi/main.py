
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Literal
import logging, time, uuid, json

app = FastAPI()

alerts = [
    {"id": 1, "level": "warning", "title": "CPU 高"},
    {"id": 2, "level": "critical", "title": "磁盘满"},
    {"id": 3, "level": "warning", "title": "内存高"},
    {"id": 4, "level": "info", "title": "备份完成"},
]

class AlertCreate(BaseModel):
    title: str
    level: Literal["info", "warning", "critical"]

#Update : 101526 每个需要保护的接口加上 _: None = Depends(check_key)
API_KEY = "dev-secret-key"  # 先硬编码，再换环境变量later

def check_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/alerts", status_code=201)
def create_alert(alert: AlertCreate, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    new = {"id": len(alerts) + 1, **alert.model_dump()}
    alerts.append(new)
    return new

@app.put("/alerts/{alert_id}", status_code=201)
def update_alert(alert_id: int, alert: AlertCreate, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    for a in alerts:
        if a["id"] == alert_id:
            alerts.remove(a)
            new = {"id": alert_id, **alert.model_dump()}
            alerts.append(new)
            return new
    raise HTTPException(status_code=404, detail="Alert not found")

@app.delete("/alerts/{alert_id}", status_code=201)
def delete_alert(alert_id: int, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    for a in alerts:
        if a["id"] == alert_id:
            alerts.remove(a)
            return {"message": "Alert deleted"}
    raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/alerts")
def list_alerts(page: int = 1, page_size: int = 10, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total": len(alerts),
        "page": page,
        "page_size": page_size,
        "items": alerts[start:end],
    }

@app.get("/alerts/by-id/{alert_id}")
def get_alert(alert_id: int, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    for a in alerts:
        if a["id"] == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/alerts/{level}")
def get_alerts(level: str, limit: int = 10, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    result = [a for a in alerts if a["level"] == level]
    return result[:limit]

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