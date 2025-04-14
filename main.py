import uvicorn
import sentry_sdk
from fastapi import FastAPI, Request
from issue import issue_handler
from issue_comment import comment_handler
from pull_request import pull_request_handler
from push import push_handler
from release import release_handler
import admin
from config import SENTRY_TOKEN_URL
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration


def before_send(event, hint):
    request = event.get("request", {})
    headers = request.get("headers", {})
    github_delivery = headers.get("X-GitHub-Delivery")
    if github_delivery:
        event.setdefault("tags", {})["github_delivery"] = github_delivery
    return event


sentry_sdk.init(
    dsn=f"https://{SENTRY_TOKEN_URL}",
    send_default_pii=True,
    integrations=[
        StarletteIntegration(
            transaction_style="url",
            failed_request_status_codes={403, *range(500, 599)},
        ),
        FastApiIntegration(
            transaction_style="url",
            failed_request_status_codes={403, *range(500, 599)},
        ),
    ],
    profiles_sample_rate=1.0,
    before_send=before_send
)

app = FastAPI(docs_url=None, redoc_url=None)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "GitHub Webhook is running"}


@app.post("/payload")
async def payload(request: Request):
    headers = request.headers
    result = "Something went wrong"
    hook_type = headers.get("X-GitHub-Event")
    request_payload = await request.json()
    print(f"Receiving: Hook type: {hook_type}")

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

    return {"message": str(result)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips="*")
