from .nodes import (
    categorize_node,
    rewrite_node,
    get_category,
    refund_node,
    other_node,
    technical_node,
    answer_node
)
from langgraph.graph import StateGraph, END
from .state import State
from langgraph.checkpoint.memory import MemorySaver

# Initialize graph
graph = StateGraph(State)

# Add nodes
graph.add_node("categorize", categorize_node)
graph.add_node("rewrite", rewrite_node)
graph.add_node("refund", refund_node)
graph.add_node("other", other_node)
graph.add_node("technical", technical_node)
graph.add_node("answer", answer_node)

# Create flow
graph.set_entry_point("rewrite")
graph.add_edge("rewrite", "categorize")
graph.add_conditional_edges(
    "categorize",
    get_category,
    {
        "refund": "refund",             # Explicit is better than implicit
        "technical": "technical",
        "other": "other"
    }
)
graph.add_edge("refund", END)
graph.add_edge("other", END)
graph.add_edge("technical", "answer")
graph.add_edge("answer", END)

# Prepare RAM db for app to compile
checkpointer = MemorySaver()

# Compile the app
graph_app = graph.compile(
    checkpointer=checkpointer,  # Save state to MemorySaver after every step
    interrupt_before=["refund"]    # Pause before node
)