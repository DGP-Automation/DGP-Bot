from operater import get_issue_with_label, make_issue_comment, remove_one_issue_label


async def notify_issuers(repo_name: str, release_name: str, html_url: str) -> str:
    return_result = ""
    all_ready_issue = get_issue_with_label(repo_name, "等待发布")
    for issue in all_ready_issue:
        issue_number = issue["number"]
        return_result += make_issue_comment(
            repo_name, issue_number, f"包含解决该问题的程序版本 {release_name} 已发布，[点击查看]({html_url})"
        )
        return_result += remove_one_issue_label(repo_name, issue_number, "等待发布")

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