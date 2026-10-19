from fastapi import APIRouter, HTTPException

from models import AlertCreate


router = APIRouter(prefix="/alerts")

alerts = [
    {"id": 1, "level": "warning", "title": "CPU 高"},
    {"id": 2, "level": "critical", "title": "磁盘满"},
    {"id": 3, "level": "warning", "title": "内存高"},
    {"id": 4, "level": "info", "title": "备份完成"},
]


@router.post("", status_code=201)
def create_alert(alert: AlertCreate):
    new = {"id": len(alerts) + 1, **alert.model_dump()}
    alerts.append(new)
    return new


@router.put("/{alert_id}", status_code=201)
def update_alert(alert_id: int, alert: AlertCreate):
    for a in alerts:
        if a["id"] == alert_id:
            alerts.remove(a)
            new = {"id": alert_id, **alert.model_dump()}
            alerts.append(new)
            return new
    raise HTTPException(status_code=404, detail="Alert not found")


@router.delete("/{alert_id}", status_code=201)
def delete_alert(alert_id: int):
    for a in alerts:
        if a["id"] == alert_id:
            alerts.remove(a)
            return {"message": "Alert deleted"}
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("")
def list_alerts(page: int = 1, page_size: int = 10):
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total": len(alerts),
        "page": page,
        "page_size": page_size,
        "items": alerts[start:end],
    }


@router.get("/by-id/{alert_id}")
def get_alert(alert_id: int):
    for a in alerts:
        if a["id"] == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/{level}")
def get_alerts(level: str, limit: int = 10):
    result = [a for a in alerts if a["level"] == level]
    return result[:limit]
