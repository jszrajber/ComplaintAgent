from state import State
from langchain_core.prompts import ChatPromptTemplate
from config.model import model
from langchain_core.output_parsers import StrOutputParser

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

    return {"category": category}

    