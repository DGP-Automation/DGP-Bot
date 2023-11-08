from operater import make_issue_comment


async def private_send_issue_comment(payload_data: dict) -> str:
    return_result = ""

    # issue commenter
    repo_name = payload_data["repository_name"]
    issue_number = payload_data["issue_number"]
    comment_body = payload_data["comment"]
    return_result += make_issue_comment(repo_name, issue_number, comment_body)
    return return_result
