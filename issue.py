import requests

from config import *
from operater import *
import re
from dgp_tools import *

CATEGORY_MATCHER = {
    "安装和环境": "area-LifeCycle",
    "成就管理": "area-Achievement",
    "角色信息面板": "area-AvatarInfo",
    "游戏启动器": "area-GameLauncher",
    "实时便笺": "area-DailyNote",
    "养成计算器": "area-Calculator",
    "用户面板": "area-UserPanel",
    "文件缓存": "area-FileCache",
    "祈愿记录": "area-Gacha",
    "玩家查询": "area-GameRecord",
    "胡桃数据库": "area-HutaoAPI",
    "用户界面": "area-UserInterface",
    "公告": "area-Announcement",
    "签到": "area-SignIn",
    "胡桃云": "area-HutaoCloud",
    "胡桃帐号": "area-HutaoAccount"
}

OUTDATED_WINDOWS_VERSION = ["18362", "18363", "19041",
                            "19042", "19043", "19044",
                            "1903", "2004", "20H2",
                            "21H1", "21H2"]


def bad_title_checker(title: str):
    bad_title_list = ["合适的标题", "请在这里填写角色名称"]
    for bad_title in bad_title_list:
        if bad_title in title:
            return True
    return False


def log_dump(body: str) -> dict:
    device_id = re.search(r"(设备 ID\n\n)(\w|\d){32}(\n\n)", body)
    if device_id:
        device_id = device_id.group(0).replace("设备 ID\n\n", "")
        device_id = device_id.replace("\n\n", "")
        print("find device_id: {}".format(device_id))
        log_dict = get_log(device_id)
        if log_dict["data"]:
            log_data = ""
            for this_log in log_dict["data"]:
                this_log_data = this_log["info"].replace(r'\n', '\n').replace(r'\r', '\r')
                this_log_data = f"\n```\n{this_log_data}\n```\n"
                log_data += this_log_data
            data = f"device_id: {device_id} \n{log_data}"
            return {"code": 1, "device_id": device_id, "data": data}
        else:
            data = f"device_id: {device_id} \n无已捕获的错误日志"
            data = f"{data}"
            return {"code": 2, "device_id": device_id, "data": data}
    else:
        return {"code": 0, "device_id": None, "data": "未找到设备 ID"}


def category_tag(body: str) -> str | None:
    category_str = re.search(r"(问题分类\n\n)(.){2,8}(\n\n)", body)
    if category_str:
        category_str = category_str.group(0).replace("问题分类\n\n", "")
        category_str = category_str.replace("\n\n", "")
        try:
            return CATEGORY_MATCHER[category_str]
        except KeyError:
            return None


def app_version_checker(body: str) -> dict:
    app_version = re.search(r"(Snap Hutao 版本)(\n\n)(.)+(\n\n)(### 设备 ID)", body)
    if app_version:
        app_version = app_version.group(0).replace("Snap Hutao 版本\n\n", "")
        app_version = app_version.replace("### 设备 ID", "")
        stable_metadata = json.loads(requests.get("https://patcher.dgp-studio.cn/hutao/stable").text)
        beta_metadata = json.loads(requests.get("https://patcher.dgp-studio.cn/hutao/beta").text)
        latest_version = [stable_metadata["tag_name"], beta_metadata["tag_name"]]
        if any(app_version.startswith(version) for version in latest_version):
            return {"code": 2, "data": app_version}
        else:
            return {"code": 1, "app_version": app_version, "latest_version": latest_version,
                    "data": f"请更新至最新版本: \n"
                            f" 稳定版: [{stable_metadata['tag_name']}](https://apps.microsoft.com/store/detail/snap-hutao/9PH4NXJ2JN52) \n"
                            f" 测试版: [{beta_metadata['tag_name']}]({beta_metadata['browser_download_url']})"}
    else:
        return {"code": 0, "data": "未找到版本号"}


def windows_version_checker(body: str) -> dict:
    windows_version = re.search(r"(Windows 版本)(\n\n)(.)+(\n\n)(### Snap Hutao 版本)", body)
    if windows_version:
        windows_version = windows_version.group(0).replace("Windows 版本\n\n", "")
        windows_version = windows_version.replace("\n\n### Snap Hutao 版本", "")
        if any(version in windows_version for version in OUTDATED_WINDOWS_VERSION):
            return {"code": 1, "data": windows_version}
        else:
            return {"code": 2, "data": windows_version}
    else:
        print("未找到版本号")
        return {"code": 0, "data": "未找到版本号"}


async def issue_handler(payload: dict):
    # Check Issue Status
    result = ""
    action = payload["action"]
    issue_number = payload["issue"]["number"]
    repo_name = payload["repository"]["full_name"]
    sender_name = payload["sender"]["login"]
    if action == "opened":
        # Bad title issue processor
        if bad_title_checker(payload["issue"]["title"]):
            print("Bad title issue found")
            result += make_issue_comment(repo_name, issue_number, f"@{sender_name} 请通过编辑功能设置一个合适的标题")
            result += close_issue(repo_name, issue_number, "not_planned")
            result += add_issue_label(repo_name, issue_number, ["需要更多信息"])
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
            this_issue_comment = this_windows_version + " 是一个过时的 Windows 版本。 \n## Windows 10 " \
                                                        "生命周期\n![image](" \
                                                        "https://user-images.githubusercontent.com/10614984/220493442-cad6b7e9-3e06-4184-8e42-950ee8587e11.png)\n\n" \
                                                        "## Snap Hutao 最低系统要求 \n" \
                                                        "- Windows 10 Build 19045 (22H2)\n" \
                                                        "  - 低于该版本可能会导致程序会有不可预知的错误"
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
            if "请通过编辑功能设置一个合适的标题" in bot_comment["body"]:
                had_bad_title = True
            if "标题已经修改" in bot_comment["body"]:
                bad_title_fixed_before = True
        if "过时的版本" in issue_labels:
            had_legacy_version = True
        # Action
        if had_bad_title and not bad_title_fixed_before:
            if not bad_title_checker(payload["issue"]["title"]):
                result += reopen_issue(repo_name, issue_number)
                result += make_issue_comment(repo_name, issue_number, "标题已经修改")
                result += remove_one_issue_label(repo_name, issue_number, "需要更多信息")
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
        project_trigger_label = ["BUG", "功能", "bug"]
        new_label = payload["label"]["name"]
        if new_label in project_trigger_label:
            print(f"Find {new_label} label, add it to project")
            org_name = payload["repository"]["owner"]["login"]
            issue_node_id = payload["issue"]["node_id"]
            result += add_issue_to_project_board_with_number_and_column_name(org_name=org_name,
                                                                             issue_node_id=issue_node_id,
                                                                             project_number=2,
                                                                             column_name="备忘录")
    return result
