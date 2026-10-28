"""POST /tickets：分类、按需检索 FAQ、生成带来源的建议回复。"""

from fastapi import APIRouter, Depends, HTTPException
from openai import APIError

from ticket_service import Ticket, TicketResult, create_client, process_ticket


router = APIRouter(tags=["tickets"])


def get_llm_client():
    try:
        client = create_client()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    with client:
        yield client


@router.post("/tickets", response_model=TicketResult)
def create_ticket(ticket: Ticket, client=Depends(get_llm_client)):
    try:
        return process_ticket(ticket, client)
    except (APIError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="模型请求失败或返回格式无效") from exc
    except (OSError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail="FAQ 检索服务暂不可用") from exc
