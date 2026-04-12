from .state import State
from langchain_core.prompts import ChatPromptTemplate
from .config.model import model
from langchain_core.output_parsers import StrOutputParser
from .config.retriever import retriever, format_docs

# Prompt for better adjusting the question
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", """
     Rewrite the question to be more specific and detailed. 
     Use ONLY the information you have, do NOT ask any questions. 
     """),
    ("user", "{question}")
])

rewriter_chain = rewrite_prompt | model | StrOutputParser()


def rewrite_node(state: State) -> dict:
    question = state["complaint"]
    answer = rewriter_chain.invoke({
        "question": question
    })
    return {"rewritten_complaint": answer}


# Prompt for categorization of complaing
prompt = ChatPromptTemplate.from_messages([
    ("system", """Select the most relevant category for the question ONLY out of those three:
     - refund
     - technical
     - other
     
     If the question is related to money, refunds or anything with currency - answer 'refund'
     If the question is related to application, services - answer 'techincal'
     If any other - answer "other"
     """),
    ("user", "Question:\n{question}")
])

cat_chain = prompt | model | StrOutputParser()


def categorize_node(state: State) -> dict:
    question = state["rewritten_complaint"]
    category = cat_chain.invoke({
        "question": question
    })
    if category not in ["refund", "technical"]:
        category = "other"

    return {"category": category}


def get_category(state: State) -> dict:
    category = state["category"]
    return category


def refund_node(state: State) -> dict:
    return {"answer": "Refund approved for order #XYZ"}


def other_node(state: State) -> dict:
    return {"answer": "Please contact support@company.com"}


def technical_node(state: State) -> dict:
    question = state["rewritten_complaint"]
    docs = retriever.invoke(question)
    return {"docs": docs}


answer_prompt = ChatPromptTemplate.from_messages([
    ("system", """
     Answer the question using ONLY context.

     Try to get as much informations as possible.

     Do NOT as questions.
     """),
    ("user", "Context:\n{context}\nQuestion:\n{question}")
])

answer_chain = answer_prompt | model | StrOutputParser()


def answer_node(state: State) -> dict:
    documents = format_docs(state["docs"])
    question = state["rewritten_complaint"]
    answer = answer_chain.invoke({
        "context": documents,
        "question": question
    })
    return {"answer": answer}
