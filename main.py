from fastapi import FastAPI
from agent_components.graph import graph_app
from schemas import ComplaintRequest, RefundDecision
from uuid import uuid4

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/complaint")
async def get_solution(req: ComplaintRequest):
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}  # Cannot be global, otherwise all endpoints would share the same ID

    result = graph_app.invoke({
        "complaint": req.complaint,
        "retry_count": 0
    }, config=config)

    state = graph_app.get_state(config)

    if "refund" in state.next:
        return {
            "status": "pending_approval",
            "thread_id": thread_id
        }

    else:
        return {"answer": result["answer"]}


@app.post("/refund/{thread_id}")
async def handle_refund(thread_id: str, body: RefundDecision):
    if body.decision == "approve":
        config = {"configurable": {"thread_id": thread_id}}
        result = graph_app.invoke(None, config=config)
        return {"answer": result["answer"]}
    else:
        return {"answer": "Refund rejected"}

