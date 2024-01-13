from operater import make_issue_comment


async def pull_request_handler(payload: dict) -> str:
    return_result = ""

    # open pr
    if payload["action"] == "opened":
        if payload["pull_request"]["user"]["type"].lower() == "bot":
            return_result += "PR opened by bot, skip actions"
            return return_result
        user_association = payload["pull_request"]["author_association"].lower()
        user_name = payload["pull_request"]["user"]["login"]
        if user_association != "first_time_contributor":
            return_result += "PR opened by recognized user, skip actions"
            return return_result
        new_issue_comment = f""""@{user_name} Thanks for your Pull Request! It is now pending for review. We invite you to join our community as a contributor via link below, so you get in touch with the development team in an easier way.
        
@{user_name} 感谢您的 Pull Request！您的 PR 已进入待审核状态。我们邀请您通过下方链接加入我们的社区，这将帮助您更方便地与开发团队取得联系。
        
[Discord](https://discord.gg/Yb8bykaUKp)
        
[QQ Group Chat: Snap Dev Community](https://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=XJPjE6ffuYPkZmXvujdP1ZDY2BqL8RDg&authKey=YHBYvW4KmPUpPjGwYwGduG7ZELhFIkd9QxLHuwBFmm4UvQH1ThWiv%2FKPgeckiqt4&noverify=0&group_code=982424236)
"""

        return_result += make_issue_comment(payload["repository"]["full_name"], payload["pull_request"]["number"],
                                            new_issue_comment)

    return return_result
