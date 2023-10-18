import re
from operater import (make_issue_comment, add_issue_label, get_issue_label, get_issue_node_id, get_issue_language,
                      add_issue_to_project_board_with_number_and_column_name, remove_one_issue_label)

LABEL_TO_BE_REMOVED_ON_CLOSING = ["priority:high", "priority:low", "priority:medium", "需要社区帮助"]


async def find_fixed_issue(repo_name: str, commit_id: str, message: str) -> str:
    return_result = ""

    re_result = re.findall(r"#\d+", message)
    org_name = repo_name.split("/")[0]
    if len(re_result) == 0:
        return ""
    else:
        for issue in re_result:
            issue_number = issue.replace("#", "")
            print(f"Commit {commit_id} fixed issue {issue_number}")
            issue_node_id = get_issue_node_id(repo_name, issue_number)
            current_issue_labels = get_issue_label(repo_name, issue_number)
            if "已修复" in current_issue_labels:
                print(f"Issue {issue_number} already fixed, skip")
                continue
            issue_language = get_issue_language(repo_name, issue_number)
            if issue_language == "CHS":
                return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} 已修复此问题")
            elif issue_language == "ENG":
                return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} fixed this issue")
            else:
                pass
            return_result += add_issue_label(repo_name, issue_number, ["已修复", "等待发布"])
            return_result += add_issue_to_project_board_with_number_and_column_name(org_name=org_name,
                                                                                    issue_node_id=issue_node_id,
                                                                                    project_number=2,
                                                                                    column_name="完成")
            for label in current_issue_labels:
                if label in LABEL_TO_BE_REMOVED_ON_CLOSING:
                    return_result += remove_one_issue_label(repo_name, issue_number, label)
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
