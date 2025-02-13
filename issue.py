import re
from datetime import datetime, timezone, timedelta
from dgp_utils.dgp_tools import *
from operater import *


def bad_title_checker(title: str) -> bool:
    bad_title_list = ["合适的标题", "请在这里填写角色名称", "Issue Title Here"]
    for bad_title in bad_title_list:
        if bad_title in title:
            return True
    return False


def log_dump(body: str) -> dict:
    is_eng = False
    device_id = re.search(r"(设备 ID\n\n)(\w|\d){32}(\n\n)", body)
    if not device_id:
        device_id = re.search(r"(Device ID\n\n)(\w|\d){32}(\n\n)", body)
        if device_id:
            is_eng = True
    if device_id:
        if is_eng:
            device_id = device_id.group(0).replace("Device ID\n\n", "")
        else:
            device_id = device_id.group(0).replace("设备 ID\n\n", "")
        device_id = device_id.replace("\n\n", "")
        print("find device_id: {}".format(device_id))
        log_dict = get_log(device_id)
        if log_dict["data"]:
            log_data = ""
            for this_log in log_dict["data"]:
                this_log_data = this_log["Info"].replace(r'\n', '\n').replace(r'\r', '\r')
                log_time = datetime.fromtimestamp(this_log["Time"] / 1000, tz=timezone.utc) + timedelta(hours=8)
                log_time = log_time.strftime('%Y-%m-%d %H:%M:%S') + " (UTC+8)"
                this_log_data = f"\n**{log_time}**\n```\n{this_log_data}\n```\n"
                log_data += this_log_data
            data = f"device_id: {device_id} \n{log_data}"
            return {"code": 1, "device_id": device_id, "data": data}
        else:
            if is_eng:
                data = f"device_id: {device_id} \nNo captured error log"
            else:
                data = f"device_id: {device_id} \n无已捕获的错误日志"
            return {"code": 2, "device_id": device_id, "data": data}
    else:
        return {"code": 0, "device_id": None, "data": "未找到设备 ID"}


def category_tag(body: str) -> str | None:
    is_eng = False
    category_str = re.search(r"(问题分类\n\n)(.*?)(\n\n)", body)
    if not category_str:
        category_str = re.search(r"(Issue Category\n\n)(.*?)(\n\n)", body)
        if category_str:
            is_eng = True
    if category_str:
        if is_eng:
            category_str = category_str.group(0).replace("Issue Category\n\n", "")
        else:
            category_str = category_str.group(0).replace("问题分类\n\n", "")
        category_str = category_str.replace("\n\n", "")
        try:
            return CATEGORY_MATCHER[category_str]
        except KeyError:
            try:
                return CATEGORY_MATCHER_ENG[category_str]
            except KeyError:
                return None


def app_version_checker(body: str) -> dict:
    is_eng = False
    app_version = re.search(r"(Snap Hutao 版本)(\n\n)(.)+(\n\n)(### 设备 ID)", body)
    if not app_version:
        app_version = re.search(r"(Snap Hutao Version)(\n\n)(.)+(\n\n)(### Device ID)", body)
        if app_version:
            is_eng = True
    if app_version:
        if is_eng:
            app_version = app_version.group(0).replace("Snap Hutao Version\n\n", "")
            app_version = app_version.replace("### Device ID", "")
        else:
            app_version = app_version.group(0).replace("Snap Hutao 版本\n\n", "")
            app_version = app_version.replace("### 设备 ID", "")
        stable_version = json.loads(requests.get("https://api.github.com/repos/DGP-Studio/Snap.Hutao/"
                                                 "releases/latest").text)["tag_name"]
        beta_metadata = json.loads(
            requests.get("https://api.github.com"
                         "/repos/DGP-Studio/Snap.Hutao/actions/artifacts?per_page=1").text)["artifacts"][0]
        beta_version = beta_metadata["name"].split("-")[1]
        beta_download_url = (f"https://github.com/DGP-Studio/Snap.Hutao/actions/runs"
                             f"/{beta_metadata['workflow_run']['id']}/artifacts/{beta_metadata['id']}")
        if app_version.startswith(stable_version):
            return {"code": 2, "data": app_version, "is_alpha": False}
        elif app_version.startswith(beta_version):
            return {"code": 2, "data": app_version, "is_alpha": True}
        else:
            if is_eng:
                return {"code": 1,
                        "data": f"Due to resource constraints, we will not consider issues related to older versions "
                                f"of the client. If you believe this is not a right judgement, please reopen the "
                                f"issue manually \n"
                                f" Please update to the latest version: \n"
                                f" Stable: [{stable_version}](https://api.snapgenshin.com/patch/hutao/download) \n"
                                f" Beta: [{beta_version}]({beta_download_url})"}
            else:
                return {"code": 1,
                        "data": f"由于资源有限，我们将不会考虑与旧版本客户端相关的问题。如果你认为该判定有误，请手动重新打开议题。 \n"
                                f" 请更新至最新版本: \n"
                                f" 稳定版: [{stable_version}](https://api.snapgenshin.com/patch/hutao/download) \n"
                                f" 测试版: [{beta_version}]({beta_download_url})"}
    else:
        return {"code": 0, "data": "未找到版本号", "is_alpha": False}


def windows_version_checker(body: str) -> dict:
    is_eng = False
    windows_version = re.search(r"(Windows 版本)(\n\n)(.)+(\n\n)(### Snap Hutao 版本)", body)
    if not windows_version:
        windows_version = re.search(r"(Windows Version)(\n\n)(.)+(\n\n)(### Snap Hutao Version)", body)
        if windows_version:
            is_eng = True
    if windows_version:
        if is_eng:
            windows_version = windows_version.group(0).replace("Windows Version\n\n", "")
            windows_version = windows_version.replace("\n\n### Snap Hutao Version", "")
        else:
            windows_version = windows_version.group(0).replace("Windows 版本\n\n", "")
            windows_version = windows_version.replace("\n\n### Snap Hutao 版本", "")
        if any(version in windows_version for version in OUTDATED_WINDOWS_VERSION):
            return {"code": 1, "data": windows_version}
        else:
            return {"code": 2, "data": windows_version}
    else:
        return {"code": 0, "data": "未找到版本号"}


async def issue_handler(payload: dict):
    # Check Issue Status
    result = ""
    is_eng = False
    action = payload["action"]
    issue_number = payload["issue"]["number"]
    repo_name = payload["repository"]["full_name"]
    sender_name = payload["sender"]["login"]
    issue_title = payload["issue"]["title"]
    if r"[ENG]" in issue_title:
        is_eng = True
    if action == "opened":
        current_issue_labels = get_issue_label(repo_name, issue_number)
        # Publish Checker
        if "[Publish]" in issue_title and "Publish" in current_issue_labels:
            author_association = payload["issue"]["author_association"]
            if author_association.lower() not in AUTHORIZED_LEVEL:
                result += close_issue(repo_name, issue_number, "not_planned")
                result += block_user_from_organization(payload["repository"]["owner"]["login"], sender_name)
                return result
            else:
                # Start pre-publish process
                print("Publish issue found")
                upcoming_version_number = re.search(r"(?<=\[Publish]: Version )(?P<V>\d+\.\d+\.\d+)", issue_title)
                upcoming_version_number = upcoming_version_number.group("V")
                print("Upcoming version number: ", upcoming_version_number)
                new_ms_return = create_new_milestone(repo_name, upcoming_version_number,
                                                     f"milestone for version {upcoming_version_number}")
                new_ms_number = json.loads(new_ms_return)["number"]
                print("New milestone created, number: ", new_ms_number)
                publishing_issues = get_issue_with_label(repo_name, "等待发布")
                print(f"{len(publishing_issues)} publishing issues found, start processing")
                for issue in publishing_issues:
                    this_issue_number = issue["number"]
                    result += update_issue_milestone(repo_name, this_issue_number, new_ms_number)
                update_issue_milestone(repo_name, issue_number, new_ms_number)

        # Bad title issue processor
        if bad_title_checker(issue_title):
            print("Bad title issue found")
            if is_eng:
                result += make_issue_comment(repo_name, issue_number, f"@{sender_name} Please edit the issue to set a "
                                                                      f"proper title")
            else:
                result += make_issue_comment(repo_name, issue_number,
                                             f"@{sender_name} 请通过编辑功能设置一个合适的标题")
            result += close_issue(repo_name, issue_number, "not_planned")
            result += add_issue_label(repo_name, issue_number, ["需要更多信息"])
            # result += lock_issue_conversation(repo_name, issue_number)
        # Log dump issue processor
        dumped_log = log_dump(payload["issue"]["body"])
        if dumped_log["code"] != 0:
            print("Find device log, post it")
            result += make_issue_comment(repo_name, issue_number, dumped_log["data"])
        # Category tag issue processor
        category = category_tag(payload["issue"]["body"])
        if category:
            print(f"Find category tag: {category}, add it")
            result += add_issue_label(repo_name, issue_number, [category])
        # Check Windows version
        windows_version_checker_return = windows_version_checker(payload["issue"]["body"])
        if windows_version_checker_return["code"] == 1:
            print("Windows version outdated. Closing issue.")
            this_windows_version = windows_version_checker_return["data"]
            if this_windows_version.startswith("18362"):
                this_windows_version = "Windows 10 Build 1903"
            elif this_windows_version.startswith("18363"):
                this_windows_version = "Windows 10 Build 1909"
            elif this_windows_version.startswith("19041"):
                this_windows_version = "Windows 10 Build 2004"
            elif this_windows_version.startswith("19042"):
                this_windows_version = "Windows 10 Build 20H2"
            elif this_windows_version.startswith("19043"):
                this_windows_version = "Windows 10 Build 21H1"
            elif this_windows_version.startswith("19044"):
                this_windows_version = "Windows 10 Build 21H2"
            elif this_windows_version.startswith("22000"):
                this_windows_version = "Windows 11 Build 21H2"
            if is_eng:
                this_issue_comment = this_windows_version + " is an outdated Windows version. \n## Windows 10 " \
                                                            "Lifecycle\n![image](" \
                                                            "https://user-images.githubusercontent.com/10614984/220493442-cad6b7e9-3e06-4184-8e42-950ee8587e11.png)\n\n" \
                                                            "## Snap Hutao Minimum System Requirement \n" \
                                                            "- Windows 10Build 19045 (22H2)\n" \
                                                            "  - Build 19045 (22H2)\n" \
                                                            "- Windows 11 Build 22621 (22H2)\n" \
                                                            "  - Build 22621 (22H2)\n" \
                                                            "- Lower versions may cause unexpected error"
            else:
                this_issue_comment = this_windows_version + " 是一个过时的 Windows 版本。 \n## Windows 10 " \
                                                            "生命周期\n![image](" \
                                                            "https://user-images.githubusercontent.com/10614984/220493442-cad6b7e9-3e06-4184-8e42-950ee8587e11.png)\n\n" \
                                                            "## Snap Hutao 最低系统要求 \n" \
                                                            "- Windows 10Build 19045 (22H2)\n" \
                                                            "  - Build 19045 (22H2)\n" \
                                                            "- Windows 11 Build 22621 (22H2)\n" \
                                                            "  - Build 22621 (22H2)\n" \
                                                            "- 低于上述版本可能会导致程序会有不可预知的错误"
            result += make_issue_comment(repo_name, issue_number, this_issue_comment)
        else:
            print("Windows version check pass")
        # Check app version
        app_version_checker_return = app_version_checker(payload["issue"]["body"])
        if app_version_checker_return["code"] == 1:
            print("App version outdated. Closing issue.")
            result += make_issue_comment(repo_name, issue_number, app_version_checker_return["data"])
            result += close_issue(repo_name, issue_number, "not_planned")
            result += add_issue_label(repo_name, issue_number, ["过时的版本"])
        else:
            if app_version_checker_return["is_alpha"]:
                result += add_issue_label(repo_name, issue_number, ["测试版本"])
            print("App version check pass")

    elif action == "edited":
        # Bad title issue processor
        had_bad_title = False
        bad_title_fixed_before = False
        had_legacy_version = False
        action_made_by_bot = False
        # Get Metadata
        bot_comments = get_bot_comment_in_issue(repo_name, issue_number)
        issue_labels = get_issue_label(repo_name, issue_number)
        # Condition Checker
        for bot_comment in bot_comments:
            if ("请通过编辑功能设置一个合适的标题" in bot_comment[
                "body"] or "Please edit the issue is set a proper title"
                    in bot_comment["body"]):
                had_bad_title = True
            if "标题已经修改" in bot_comment["body"] or "Title is fixed" in bot_comment["body"]:
                bad_title_fixed_before = True
        if "过时的版本" in issue_labels:
            had_legacy_version = True
        # Action
        if had_bad_title and not bad_title_fixed_before:
            if not bad_title_checker(payload["issue"]["title"]):
                # result += unlock_issue_conversation(repo_name, issue_number)
                result += reopen_issue(repo_name, issue_number)
                if is_eng:
                    result += make_issue_comment(repo_name, issue_number, "Title is fixed")
                else:
                    result += make_issue_comment(repo_name, issue_number, "标题已经修改")
                result += remove_one_issue_label(repo_name, issue_number, "需要更多信息")
                previous_bot_comments = get_bot_comment_in_issue(repo_name, issue_number)
                for comment in previous_bot_comments:
                    if ("请通过编辑功能设置一个合适的标题" in comment["body"] or
                            "Please edit the issue is set a proper title" in comment["body"]):
                        result += hide_issue_comment(comment["node_id"], "OUTDATED")
                    if "标题已修改" in comment["body"] or "Title is fixed" in comment["body"]:
                        result += hide_issue_comment(comment["node_id"], "OUTDATED")
                action_made_by_bot = True
        if had_legacy_version:
            app_version_checker_return = app_version_checker(payload["issue"]["body"])
            if app_version_checker_return["code"] != 1:
                result += remove_one_issue_label(repo_name, issue_number, "过时的版本")
                action_made_by_bot = True
        # Re-open issue if all conditions are fixed
        issue_labels = get_issue_label(repo_name, issue_number)
        if "过时的版本" not in issue_labels and "需要更多信息" not in issue_labels and action_made_by_bot:
            result += reopen_issue(repo_name, issue_number)

    elif action == "labeled":
        # If label with BUG or 功能, add to project
        new_label = payload["label"]["name"]
        if new_label in PROJECT_TRIGGER_LABEL:
            print(f"Find {new_label} label, add it to project")
            org_name = payload["repository"]["owner"]["login"]
            issue_node_id = payload["issue"]["node_id"]
            result += add_issue_to_project_board_with_number_and_column_name(org_name=org_name,
                                                                             issue_node_id=issue_node_id,
                                                                             project_number=2,
                                                                             column_name="备忘录")

    elif action == "reopened":
        # restore removed labels
        closed_labels = get_issue_removed_labels(repo_name, issue_number)
        result += add_issue_label(repo_name, issue_number, [closed_labels[-1]])
        current_labels = get_issue_label(repo_name, issue_number)
        if len(set(current_labels) & set(PROJECT_TRIGGER_LABEL)) > 0:
            print(f"Find {current_labels} label in reopened issue, restore its state in project")
            org_name = payload["repository"]["owner"]["login"]
            issue_node_id = payload["issue"]["node_id"]
            result += add_issue_to_project_board_with_number_and_column_name(org_name=org_name,
                                                                             issue_node_id=issue_node_id,
                                                                             project_number=2,
                                                                             column_name="备忘录")

    elif action == "closed":
        current_labels = get_issue_label(repo_name, issue_number)
        for label in current_labels:
            if label in LABEL_TO_BE_REMOVED_ON_CLOSING:
                result += remove_one_issue_label(repo_name, issue_number, label)

    return result
