from fastapi import FastAPI, Request
from issue import issue_handler
from push import push_handler
from release import release_handler
from issue_comment import comment_handler
from pull_request import pull_request_handler
from private_endpoints import private_send_issue_comment, add_discord_message, get_discord_message
import uvicorn

app = FastAPI(docs_url=None, redoc_url=None)


@app.get("/")
async def root():
    return {"message": "GitHub Webhook is running"}


@app.post("/payload")
async def payload(request: Request):
    result = None
    hook_type = request.headers.get("X-GitHub-Event")
    request_payload = await request.json()
    print(f"Receiving: Hook type: {hook_type}")

    try:
        if hook_type == "ping":
            result = {"message": "pong"}
        elif hook_type == "issues":
            result = await issue_handler(request_payload)
        elif hook_type == "push":
            result = await push_handler(request_payload)
        elif hook_type == "release":
            result = await release_handler(request_payload)
        elif hook_type == "issue_comment":
            result = await comment_handler(request_payload)
        elif hook_type == "pull_request":
            result = await pull_request_handler(request_payload)
        else:
            print("Unknown hook type")
    except Exception as e:
        result = await add_discord_message({"message": f"Error: {e}"})
        return {"message": str(result)}

    return {"message": str(result)}


@app.post("/private")
async def private_send(request: Request):
    request_payload = await request.json()
    hook_type = request_payload["type"]

    if hook_type == "send_issue_comment":
        result = await private_send_issue_comment(request_payload["data"])
    elif hook_type == "add_discord_message":
        result = await add_discord_message(request_payload["data"])
    elif hook_type == "get_discord_message":
        result = await get_discord_message()
    else:
        return {"message": "Unknown hook type"}

    return {"message": str(result)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
