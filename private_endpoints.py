from operater import make_issue_comment

discord_message_queue = []


async def private_send_issue_comment(payload_data: dict) -> str:
    return_result = ""

    # issue commenter
    repo_name = payload_data["repository_name"]
    issue_number = payload_data["issue_number"]
    comment_body = payload_data["comment"]
    return_result += make_issue_comment(repo_name, issue_number, comment_body)
    return return_result


async def add_discord_message(payload_data: dict) -> str:
    global discord_message_queue
    new_queue = discord_message_queue.copy()
    if len(new_queue) > 5:
        return "queue full"
    message = payload_data["message"]
    new_queue.append(message)
    discord_message_queue = list(tuple(new_queue))
    return "ok"


async def get_discord_message() -> str:
    global discord_message_queue
    if len(discord_message_queue) > 0:
        return discord_message_queue.pop(0)
    else:
        return ""
