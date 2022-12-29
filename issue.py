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
    "签到": "area-SignIn"
}


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
            data = f"device_id: {device_id} \n```\n{log_dict['data']}\n```"
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
    app_version = re.search(r"(Snap Hutao 版本\n\n)(.)+(### 设备 ID)", body)
    if app_version:
        app_version = app_version.group(0).replace("Snap Hutao 版本\n\n", "")
        app_version = app_version.replace("### 设备 ID", "")
        metadata = json.loads(requests.get("https://api.github.com/repos/DGP-Studio/Snap.Hutao/releases/latest").text)
        latest_version = metadata["tag_name"]
        if app_version != latest_version:
            return {"code": 1, "app_version": app_version, "latest_version": latest_version,
                    "data":f"请更新至最新版本 {latest_version}"}
        return {"code": 2, "data": app_version}
    else:
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
        # Check app version
        app_version_checker_return = app_version_checker(payload["issue"]["body"])
        if app_version_checker_return["code"] == 1:
            print("App version outdated")
            result += make_issue_comment(repo_name, issue_number, app_version_checker_return["data"])
        else:
            print("App version check pass")

    elif action == "edited":
        # Bad title issue processor
        had_bad_title = False
        bad_title_fixed_before = False
        bot_comments = get_bot_comment_in_issue(repo_name, issue_number)
        for bot_comment in bot_comments:
            if "请通过编辑功能设置一个合适的标题" in bot_comment["body"]:
                had_bad_title = True
            if "标题已经修改" in bot_comment["body"]:
                bad_title_fixed_before = True
        if had_bad_title and not bad_title_fixed_before:
            if not bad_title_checker(payload["issue"]["title"]):
                result += reopen_issue(repo_name, issue_number)
                result += make_issue_comment(repo_name, issue_number, "标题已经修改，已重新开启 Issue")
                result += remove_one_issue_label(repo_name, issue_number, "需要更多信息")

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
