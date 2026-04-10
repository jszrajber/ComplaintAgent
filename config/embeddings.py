from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from data import text
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


# Creating chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,     # character size of chunk
    chunk_overlap=50    # how many characters are overlapping
)
chunks = splitter.split_text(text)


# Create Document type with metadata
documents = [
    Document(page_content=chunk, metadata={"source": "TechFlow", "chunk_id": i})
    for i, chunk in enumerate(chunks)
]


# Create vectorstore from embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text-v2-moe")
vectorstore = FAISS.from_documents(documents, embeddings)