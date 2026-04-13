from typing import TypedDict, List
from langchain_core.documents import Document


class State(TypedDict):
    complaint: str
    rewritten_complaint: str
    category: str
    answer: str
    retry_count: int
    docs: List[Document]
    completed: bool
