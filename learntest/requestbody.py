from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    age: int
    pwd: str | None
    sex: str = "男"

@app.post('/users')
def create_user(user: User):
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('requestbody:app', host="127.0.0.1", port=8000, reload=True)
