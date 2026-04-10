from nodes import categorize_node, rewrite_node
from langgraph.graph import StateGraph
from state import State

# Initialize graph
graph = StateGraph(State)

# Add nodes
graph.add_node("categorize", categorize_node)
graph.add_node("rewrite", rewrite_node)


# Create flow
graph.set_entry_point("rewrite")
graph.add_edge("rewrite", "categorize")


# Compile the app
app = graph.compile()