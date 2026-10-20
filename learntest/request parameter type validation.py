from fastapi import FastAPI
from typing import List, Optional, Union



app = FastAPI()



@app.get('/items1/{item_id}')
def read_item1(item_id: int):
    return {"item_id": item_id}

@app.get('/items2/{item_id}')
def read_item2(item_id: Union[int, str]):
    return {"item_id": item_id}

@app.get('/items3/')
def read_item3(item_id: Union[int, None] = None):
    return {"item_id": item_id}

@app.get('/items4/')
def read_item4(item_id: Optional[int] = None):
    return {"item_id": item_id}

@app.get('/items5/')
def read_item5(item_ids: List):
    return {"item_ids": item_ids}

if __name__ == "__main__": 
    import uvicorn
    uvicorn.run('request parameter type validation:app', host="127.0.0.1", port=8000, reload=True)