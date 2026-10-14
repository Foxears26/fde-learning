from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal

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




@app.post("/alerts", status_code=201)
def create_alert(alert: AlertCreate):
    new = {"id": len(alerts) + 1, **alert.model_dump()}
    alerts.append(new)
    return new

@app.put("/alerts/{alert_id}", status_code=201)
def update_alert(alert_id: int, alert: AlertCreate):
    for a in alerts:
        if a["id"] == alert_id:
            alerts.remove(a)
            new = {"id": alert_id, **alert.model_dump()}
            alerts.append(new)
            return new
    raise HTTPException(status_code=404, detail="Alert not found")

@app.delete("/alerts/{alert_id}", status_code=201)
def delete_alert(alert_id: int):
    for a in alerts:
        if a["id"] == alert_id:
            alerts.remove(a)
            return {"message": "Alert deleted"}
    raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/alerts")
def list_alerts(page: int = 1, page_size: int = 10):
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total": len(alerts),
        "page": page,
        "page_size": page_size,
        "items": alerts[start:end],
    }

@app.get("/alerts/by-id/{alert_id}")
def get_alert(alert_id: int):
    for a in alerts:
        if a["id"] == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alert not found")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)