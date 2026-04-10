from graph import app

result = app.invoke({
    "complaint": "The app is not working again",
    "retry_count": 0
})

print(result)