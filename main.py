from fastapi import FastAPI, HTTPException, status
from agent_components.graph import graph_app
from schemas import ComplaintRequest, RefundDecision
from uuid import uuid4
from fastapi.responses import StreamingResponse
import json

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "ok"}


# @app.post("/complaint")
# async def get_solution(req: ComplaintRequest):
#     thread_id = str(uuid4())
#     config = {"configurable": {"thread_id": thread_id}}  # Cannot be global, otherwise all endpoints would share the same ID

#     result = graph_app.invoke({
#         "complaint": req.complaint,
#         "retry_count": 0,
#         "completed": False
#     }, config=config)

#     state = graph_app.get_state(config)

#     if "refund" in state.next:
#         return {
#             "status": "pending_approval",
#             "thread_id": thread_id
#         }

#     else:
#         return {"answer": result["answer"]}

@app.post("/complaint")
async def get_solution(req: ComplaintRequest):
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}  # Cannot be global, otherwise all endpoints would share the same ID

    async def generate():   # async because of async events inside
        # Iteration must bye async
        async for event in graph_app.astream_events({   # Method gets every action in graph as dicts
            "complaint": req.complaint,
            "retry_count": 0,
            "completed": False
        }, config=config, version="v2"):    # v2 gives more info, new version of event formattting

            # Check if it is refund
            if event['event'] == "on_chain_end":    # on_chain_end is at the end of every node
                output = event["data"].get("output", {})
                if isinstance(output, dict) and output.get("category") == "refund":
                    yield json.dumps({
                        "status": "pending_approval",
                        "thread_id": thread_id
                    })

                    return      # For generators value must be yield first, then return

            # Else stream answer
            if event["event"] == "on_chat_model_stream":    # tokens only
                if event['metadata']['langgraph_node'] == "answer":     # answer_node only
                    chunk = event['data']['chunk']
                    if chunk:
                        yield chunk.content

    return StreamingResponse(generate(), media_type="text/event-stream")    # Explicit info that this is streaming, str must be sent

# Command to test streaming
# curl -X POST http://localhost:8000/complaint \
#   -H "Content-Type: application/json" \
#   -d '{"complaint": "My app is not working"}' \
#   --no-buffer


@app.post("/refund/{thread_id}")
async def handle_refund(thread_id: str, body: RefundDecision):
    config = {"configurable": {"thread_id": thread_id}}     # Cannot be global, otherwise all endpoints would share the same ID
    state = graph_app.get_state(config)     # Get the current state of a graph

    if state.values.get("completed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This request has been already processed")

    if body.decision == "approve":
        result = await graph_app.ainvoke(None, config=config)
        print(f"NEXT: {state.next}")
        print(f"VALUES: {state.values}")
        graph_app.update_state(config, {"completed": True})     # Update state without using nodes
        return {"answer": result}
    else:
        graph_app.update_state(config, {"completed": True})
        return {"answer": "Refund rejected"}
