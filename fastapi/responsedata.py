from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    price: float
    category: str

class Pagenation(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int

class ListResponse(BaseModel):
    status: str = "success"
    data: List[Item]
    pagenation: Pagenation

DB1 = [Item(id = i, name = f'item{i}', price = i * 100.0, category = 'iphone'if i % 2 ==0 else 'ipad') for i in range(1, 101)]

@app.get("/items1")
async def get_items1():
    return ["apple1", "banana1", "cherry1"]

@app.get("/items2")
async def get_items2():
    return DB1

@app.get("/items3")
async def get_items3(category: Optional[str] = Query(None, description="Filter by category")):
    # temp = []
    # temp = DB1
    # if category:
    #     temp.clear()
    #     for item in DB1:
    #         if item.category == category:
    #             temp.append(item)
    # if temp:
    #     return temp
    # return DB1
    filtered_items = DB1
    if category:
        filtered_items = [item for item in DB1 if item.category == category]
    return filtered_items

@app.get("/items4")
async def get_items4(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = Query(None, description="Filter by category")):
    
    #filter for data
    filtered_items = DB1
    if category:
        filtered_items = [item for item in DB1 if item.category == category]

    #pagination
    total = len(filtered_items)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    return filtered_items[start:end]


@app.get("/items5")
async def get_items5(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = Query(None, description="Filter by category")):
    
    #filter for data
    filtered_items = DB1
    if category:
        filtered_items = [item for item in DB1 if item.category == category]

    #pagination
    total = len(filtered_items)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    return ListResponse(data = filtered_items[start:end], 
                        pagenation = Pagenation( 
                            total=total, 
                            page=page, 
                            page_size=page_size, 
                            total_pages=total_pages)
                        )





if __name__ == "__main__":
    import uvicorn
    uvicorn.run('responsedata:app', host="127.0.0.1", port=8000, reload=True)