from fastapi import FastAPI

alerts = [
    {"id": 1, "level": "warning", "title": "CPU 高"},
    {"id": 2, "level": "critical", "title": "磁盘满"},
    {"id": 3, "level": "warning", "title": "内存高"},
    {"id": 4, "level": "info", "title": "备份完成"},
]


app = FastAPI()

@app.get("/alerts/{level}")
def get_alerts(level: str, limit: int = 10):
    result = [a for a in alerts if a["level"] == level]
    return result[:limit]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)