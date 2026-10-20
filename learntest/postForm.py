from fastapi import FastAPI, Form
from pydantic import BaseModel
from typing import Annotated


app = FastAPI()

@app.post("/login1")
def login1(username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password": password}

class User1(BaseModel):
    username: str = Form(...)
    password: str = Form(...)

@app.post("/login2")
def login2(user: Annotated[User1, Form(...)]):
    return user



if __name__ == "__main__":
    import uvicorn
    uvicorn.run('postForm:app', host="127.0.0.1", port=8000, reload=True)