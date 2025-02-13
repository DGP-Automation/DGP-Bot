import re
from datetime import datetime, timezone, timedelta
from gemini import create_pull_request_summary
from config import AUTHORIZED_LEVEL
from dgp_utils.dgp_tools import *
from issue import log_dump
from operater import make_issue_comment


async def comment_handler(payload: dict) -> str:
    return_result = ""

    # issue commenter
    full_repo_name = payload["repository"]["full_name"]
    issue_number = payload["issue"]["number"]
    comment_sender = payload["comment"]["user"]["login"]
    authority = payload["comment"]["author_association"]
    comment_body = payload["comment"]["body"]
    pull_log_command = re.search(r"(/log) (?P<device_id>\w{32})", comment_body)
    if not pull_log_command:
        pull_log_command = re.search(r"(^/log$)", comment_body)
    if pull_log_command:
        if authority.lower() not in AUTHORIZED_LEVEL:
            print(f"Unauthorized user: {comment_sender} was trying to pull log, authority: {authority}")
            return ""
        comment_body_list = comment_body.split(" ")
        if len(comment_body_list) == 2:
            device_id = pull_log_command.group("device_id")
            print("Pulling log for device: ", device_id)
            dumped_log = get_log(device_id)
            if dumped_log["data"]:
                log_data = ""
                for this_log in dumped_log["data"]:
                    this_log_data = this_log["Info"].replace(r'\n', '\n').replace(r'\r', '\r')
                    log_time = datetime.fromtimestamp(this_log["Time"] / 1000, tz=timezone.utc) + timedelta(hours=8)
                    log_time = log_time.strftime('%Y-%m-%d %H:%M:%S') + " (UTC+8)"
                    this_log_data = f"\n**{log_time}**\n```\n{this_log_data}\n```\n"
                    log_data += this_log_data
                data = f"device_id: {device_id} \n{log_data}"
                return_result += make_issue_comment(full_repo_name, issue_number, data)
            else:
                return_result += make_issue_comment(full_repo_name, issue_number, f"> {comment_body}\n\n无已捕获的错误日志")
        elif len(comment_body_list) == 1:
            issue_body = payload["issue"]["body"]
            dumped_log = log_dump(issue_body)
            if dumped_log["code"] != 0:
                print("Find device log, post it")
                return_result += make_issue_comment(full_repo_name, issue_number, dumped_log["data"])
            else:
                return_result += make_issue_comment(full_repo_name, issue_number, f"> {comment_body}\n\n未找到设备 ID")
        else:
            print("Invalid command format when pulling log")
    if comment_body.strip().startswith("/pr-summary"):
        org_name, repository_name = full_repo_name.split("/")
        print(f"Generating PR summary for {full_repo_name}#{issue_number}")
        summary_text = await create_pull_request_summary(org_name, repository_name, issue_number)
        return_result += make_issue_comment(
            full_repo_name,
            issue_number,
            summary_text
        )
    return return_result
