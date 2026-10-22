from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from db_models import Alert
from models import AlertCreate


router = APIRouter(prefix="/alerts")


def alert_data(alert: Alert):
    return {"id": alert.id, "level": alert.level, "title": alert.title}


@router.post("", status_code=201)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    new = Alert(**alert.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return alert_data(new)


@router.put("/{alert_id}", status_code=201)
def update_alert(alert_id: int, alert: AlertCreate, db: Session = Depends(get_db)):
    existing = db.get(Alert, alert_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    existing.title = alert.title
    existing.level = alert.level
    db.commit()
    db.refresh(existing)
    return alert_data(existing)


@router.delete("/{alert_id}", status_code=201)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    existing = db.get(Alert, alert_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(existing)
    db.commit()
    return {"message": "Alert deleted"}


@router.get("")
def list_alerts(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Alert))
    start = (page - 1) * page_size
    # Preserve list slicing behavior for zero and negative parameters too.
    start, end, _ = slice(start, start + page_size).indices(total)
    items = db.scalars(
        select(Alert).order_by(Alert.id).offset(start).limit(max(0, end - start))
    ).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [alert_data(alert) for alert in items],
    }


@router.get("/by-id/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert_data(alert)


@router.get("/{level}")
def get_alerts(level: str, limit: int = 10, db: Session = Depends(get_db)):
    query = select(Alert).where(Alert.level == level).order_by(Alert.id)
    if limit < 0:
        total = db.scalar(select(func.count()).select_from(Alert).where(Alert.level == level))
        limit = max(0, total + limit)
    return [alert_data(alert) for alert in db.scalars(query.limit(limit)).all()]
