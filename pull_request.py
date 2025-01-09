from operater import make_issue_comment
from gemini import create_pull_request_summary

WHITELIST = [
    "DGP-Studio/Generic-API",
    "DGP-Studio/Snap.Hutao"
]


async def pull_request_handler(payload: dict) -> str:
    return_result = ""
    skip_invitation = False

    # only handle PR "opened" events
    if payload["action"] == "opened" or payload["action"] == "reopened":
        # skip if opened by another bot
        if payload["pull_request"]["user"]["type"].lower() == "bot":
            return_result += "PR opened by bot, skip actions"
            skip_invitation = True

        # check if it's a first-time contributor
        user_association = payload["pull_request"]["author_association"].lower()
        user_name = payload["pull_request"]["user"]["login"]
        if user_association != "first_time_contributor":
            return_result += "PR opened by recognized user, skip actions"
            skip_invitation = True

        # STEP 1: Greet the user & invite them to the community
        new_issue_comment = f""""@{user_name} Thanks for your Pull Request! It is now pending review. 
We invite you to join our community as a contributor via the links below, so you can get in touch with the development team in an easier way.

@{user_name} 感谢您的 Pull Request！您的 PR 已进入待审核状态。我们邀请您通过下方链接加入我们的社区，这将帮助您更方便地与开发团队取得联系。

[Discord](https://discord.gg/Yb8bykaUKp)

[QQ Group Chat: Snap Dev Community](https://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=XJPjE6ffuYPkZmXvujdP1ZDY2BqL8RDg&authKey=YHBYvW4KmPUpPjGwYwGduG7ZELhFIkd9QxLHuwBFmm4UvQH1ThWiv%2FKPgeckiqt4&noverify=0&group_code=982424236)
"""
        if not skip_invitation:
            return_result += make_issue_comment(
                payload["repository"]["full_name"],
                payload["pull_request"]["number"],
                new_issue_comment
            )

        # STEP 2: Check if this repository is in our whitelist
        repo_full_name = payload["repository"]["full_name"]
        if repo_full_name in WHITELIST:
            # PR title
            pr_title = payload["pull_request"]["title"]
            if "Crowdin" in pr_title:
                return_result += "\n\nPR title contains `Crowdin`, skip AI summary generation."

            # Prepare the parameters for summary generation
            org_name = payload["repository"]["owner"]["login"]
            repo_name = payload["repository"]["name"]
            pr_number = payload["pull_request"]["number"]

            # STEP 3: Generate the AI summary
            try:
                summary_text = await create_pull_request_summary(org_name, repo_name, pr_number)
                if summary_text:
                    # Post the summary as an issue comment
                    return_result += "\n\nAI Summary Generated.\n"
                    return_result += make_issue_comment(
                        repo_full_name,
                        pr_number,
                        summary_text
                    )
            except Exception as e:
                return_result += f"\n\nFailed to generate AI summary: {e}"

    return return_result
