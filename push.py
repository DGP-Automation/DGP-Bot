import re
from operater import make_issue_comment, add_issue_label


async def find_fixed_issue(repo_name: str, commit_id: str, message: str) -> str:
    return_result = ""

    re_result = re.findall(r"#\d+", message)
    if len(re_result) == 0:
        return ""
    else:
        for issue in re_result:
            issue_number = issue.replace("#", "")
            print(f"Commit {commit_id} fixed issue {issue_number}")
            return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} 已修复此问题")
            return_result += add_issue_label(repo_name, issue_number, ["已修复", "等待发布"])
    return return_result


async def push_handler(payload: dict) -> str:
    return_result = ""

    # issue commenter
    repo_name = payload["repository"]["full_name"]
    for commit in payload["commits"]:
        try:
            return_result += await find_fixed_issue(repo_name, commit["id"], commit["message"])
        except TypeError:
            return_result = ""
    return return_result
