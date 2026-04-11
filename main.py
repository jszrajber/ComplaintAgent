from graph import app

config = {"configurable": {"thread_id": 1}}  # Values for db to retrieve the same thread after pausing

result = app.invoke({
    "complaint": "Where is the love",
    "retry_count": 0
}, config=config)

state = app.get_state(config)   # Checkpointer snapshot

if "refund" in state.next:
    print("REFUND - PAUSED")
    print("DO YOU WANT TO PROCEED WITH THE REFUND?")
    decision = input("Type 'yes' or 'no: ").strip().lower()

    if decision == "yes":
        result = app.invoke(None, config=config)
        print(result['answer'])
    else:
        print("Refund rejected")
else:
    print(result['answer'])