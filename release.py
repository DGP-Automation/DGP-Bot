from operater import get_issue_with_label, make_issue_comment, remove_one_issue_label, get_issue_language, close_issue


async def notify_issuers(repo_name: str, release_name: str, html_url: str) -> str:
    return_result = ""
    all_ready_issue = get_issue_with_label(repo_name, "等待发布")
    for issue in all_ready_issue:
        issue_number = issue["number"]
        issue_language = get_issue_language(repo_name, issue_number)
        if issue_language == "CHS":
            return_result += make_issue_comment(
                repo_name, issue_number, f"包含解决该问题的程序版本 [{release_name}]({html_url}) 已发布。"
            )
        elif issue_language == "ENG":
            return_result += make_issue_comment(
                repo_name, issue_number, f"Program version [{release_name}]({html_url}) which contains the solution has been "
                                         f"released."
            )
        else:
            pass
        return_result += remove_one_issue_label(repo_name, issue_number, "等待发布")
        return_result += close_issue(repo_name, issue_number, "completed")

    return return_result


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
