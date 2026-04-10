from typing import TypedDict


class State(TypedDict):
    complaint: str
    rewritten_complaint: str
    category: str
    answer: str
    retry_count: int
