from typing import Literal

from pydantic import BaseModel


class AlertCreate(BaseModel):
    title: str
    level: Literal["info", "warning", "critical"]
