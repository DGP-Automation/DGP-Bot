import json

from operater import (get_issue_with_label, make_issue_comment, remove_one_issue_label, get_issue_language, close_issue,
                      list_repo_milestones, update_milestone)


async def notify_issuers(repo_name: str, release_name: str, html_url: str) -> str:
    return_result = ""
    all_ready_issue = get_issue_with_label(repo_name, "等待发布")
    for issue in all_ready_issue:
        # Verify milestone
        if issue["milestone"] is None:
            continue
        elif type(issue["milestone"]) is list:
            if release_name not in [i["title"] for i in issue["milestone"]]:
                continue
        elif type(issue["milestone"]) is dict:
            if release_name != issue["milestone"]["title"]:
                continue
        else:
            raise Exception("Unknown milestone type")

        issue_number = issue["number"]
        issue_language = get_issue_language(repo_name, issue_number)
        if issue_language == "CHS":
            return_result += make_issue_comment(
                repo_name, issue_number, f"包含解决该问题的程序版本 [{release_name}]({html_url}) 已发布。"
            )
        elif issue_language == "ENG":
            return_result += make_issue_comment(
                repo_name, issue_number,
                f"Program version [{release_name}]({html_url}) which contains the solution has been "
                f"released."
            )
        else:
            pass
        return_result += remove_one_issue_label(repo_name, issue_number, "等待发布")
        return_result += close_issue(repo_name, issue_number, "completed")

    return return_result


async def close_version_milestone(repo_name: str, release_name: str) -> str:
    all_milestones = json.loads(list_repo_milestones(repo_name))
    version_milestone_num = None
    for milestone in all_milestones:
        if milestone["title"] == release_name:
            version_milestone_num = milestone["number"]
    if version_milestone_num is None:
        return "No milestone found"
    else:
        result = update_milestone(repo_name, version_milestone_num, {"state": "closed"})
    return result


async def release_handler(payload: dict) -> str:
    return_result = ""
    # Quick return
    if payload["action"] != "published":
        return "pass for not a published release"
    if payload["release"]["prerelease"]:
        return "pass for a prerelease"

    # Release Info
    release_name = payload["release"]["tag_name"]
    html_url = payload["release"]["html_url"]
    repo_name = payload["repository"]["full_name"]

    # Notify issuers
    return_result += await notify_issuers(repo_name, release_name, html_url)
    return_result += await close_version_milestone(repo_name, release_name)
    return return_result
