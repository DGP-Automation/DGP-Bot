import re

from config import LABEL_TO_BE_REMOVED_ON_CLOSING, VALID_PUSH_REF
from operater import (make_issue_comment, add_issue_label, get_issue_label, get_issue_node_id, get_issue_language,
                      add_issue_to_project_board_with_number_and_column_name, remove_one_issue_label, get_issue_type)


async def find_fixed_issue(repo_name: str, commit_id: str, message: str) -> str:
    return_result = ""

    re_result = re.findall(r"#\d+", message)
    org_name = repo_name.split("/")[0]
    if len(re_result) == 0:
        return ""
    else:
        for issue in re_result:
            issue_number = issue.replace("#", "")
            if get_issue_type(repo_name, issue_number) == "pull_request":
                print(f"issue {issue_number} is a pr, skip.")
                continue
            print(f"Commit {commit_id} fixed issue {issue_number}")
            issue_node_id = get_issue_node_id(repo_name, issue_number)
            current_issue_labels = get_issue_label(repo_name, issue_number)
            if "已修复" in current_issue_labels or "已完成" in current_issue_labels:
                print(f"Issue {issue_number} already fixed, skip")
                continue
            is_bug = True if "BUG" in current_issue_labels else False
            is_feat = True if "功能" in current_issue_labels else False
            issue_language = get_issue_language(repo_name, issue_number)
            if issue_language == "CHS":
                if is_bug:
                    return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} 已修复此问题")
                elif is_feat:
                    return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} 已实现此议题")
                else:
                    return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} 已完成此议题")
            elif issue_language == "ENG":
                if is_bug:
                    return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} fixed this bug")
                elif is_feat:
                    return_result += make_issue_comment(repo_name, issue_number,
                                                        f"{commit_id} implemented this feature")
                else:
                    return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} finished this issue")
            else:
                return_result += make_issue_comment(repo_name, issue_number, f"{commit_id} finished this issue")
            return_result += add_issue_label(repo_name, issue_number, ["已完成", "等待发布"])
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
    if payload["ref"] in VALID_PUSH_REF:
        for commit in payload["commits"]:
            try:
                return_result += await find_fixed_issue(repo_name, commit["id"], commit["message"])
            except TypeError:
                return_result = ""
    return return_result
