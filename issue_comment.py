from dgp_tools import *
from operater import make_issue_comment
from issue import log_dump


async def comment_handler(payload: dict) -> str:
    AUTHORIZED_LEVEL = ["owner", "member"]
    return_result = ""

    # issue commenter
    repo_name = payload["repository"]["full_name"]
    issue_number = payload["issue"]["number"]
    comment_sender = payload["comment"]["user"]["login"]
    authority = payload["comment"]["author_association"]
    comment_body = payload["comment"]["body"]
    if not comment_body.startswith("@dgp-bot"):
        return ""
    if authority.lower() not in AUTHORIZED_LEVEL:
        return "Not authorized"
    comment_body = comment_body.split(" ")
    command = comment_body[1]
    if command == "拉取日志":
        print("Pulling log")
        if len(comment_body) == 3:
            dumped_log = get_log(comment_body[2])
            if dumped_log["data"]:
                data = f"device_id: {comment_body[2]} \n```\n{dumped_log['data'][0]['info']}\n```"
                return_result += make_issue_comment(repo_name, issue_number, data)
            else:
                return_result += make_issue_comment(repo_name, issue_number, "空日志")
        elif len(comment_body) == 2:
            issue_body = payload["issue"]["body"]
            dumped_log = log_dump(issue_body)
            if dumped_log["code"] != 0:
                print("Find device log, post it")
                return_result += make_issue_comment(repo_name, issue_number, dumped_log["data"])
            else:
                return_result += make_issue_comment(repo_name, issue_number, "未找到设备 ID")
        else:
            print("Invalid command format when pulling log")
    return return_result
