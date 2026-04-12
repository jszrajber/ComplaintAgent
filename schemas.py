from pydantic import BaseModel
from typing import Literal


class ComplaintRequest(BaseModel):
    complaint: str


class RefundDecision(BaseModel):
    decision: Literal['approve', "reject"]
    