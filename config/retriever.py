from .embeddings import vectorstore
from sentence_transformers import CrossEncoder

# Retrieve data from vector database
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Reranling model config
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def format_docs(documents) -> str:
    """
    Function for formatting retieved docs into string
    """
    return "\n\n".join(doc.page_content for doc in documents)
