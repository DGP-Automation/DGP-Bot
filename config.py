import os
from dotenv import load_dotenv

load_dotenv()

# Private Key
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
if PRIVATE_KEY is None:
    PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH')
    PRIVATE_KEY = open(PRIVATE_KEY_PATH, "r").read()
# App ID
APP_ID = os.getenv('APP_ID')
# Installation ID
INSTALLATION_ID = os.getenv('INSTALLATION_ID')
# GitHub Personal Token
GITHUB_PERSONAL_TOKEN = os.getenv('GITHUB_PERSONAL_TOKEN')

# Global Variables
AUTHORIZED_LEVEL = ["owner", "member"]
access_token = ""
access_token_generated_time = 0
LABEL_TO_BE_REMOVED_ON_CLOSING = ["priority:high", "priority:low", "priority:medium", "需要社区帮助", "priority:none",
                                  "need-triage", "需要更多信息"]
OUTDATED_WINDOWS_VERSION = ["18362", "18363", "19041",
                            "19042", "19043", "19044",
                            "1903", "2004", "20H2",
                            "21H1", "21H2", "22000"]
CATEGORY_MATCHER = {
    "安装和环境": "area-LifeCycle",
    "成就管理": "area-Achievement",
    "角色信息面板": "area-AvatarInfo",
    "游戏启动器": "area-GameLauncher",
    "实时便笺": "area-DailyNote",
    "养成计算": "area-Cultivation",
    "用户面板": "area-UserPanel",
    "文件缓存": "area-FileCache",
    "祈愿记录": "area-Gacha",
    "玩家查询": "area-GameRecord",
    "胡桃数据库": "area-HutaoAPI",
    "用户界面": "area-UserInterface",
    "公告": "area-Announcement",
    "签到": "area-SignIn",
    "胡桃云": "area-HutaoCloud",
    "胡桃帐号": "area-Passport"
}

CATEGORY_MATCHER_ENG = {
    "Installation and Environment": "area-LifeCycle",
    "Achievement": "area-Achievement",
    "My Character": "area-AvatarInfo",
    "Game Launcher": "area-GameLauncher",
    "Realtime Note": "area-DailyNote",
    "Develop Plan": "area-Cultivation",
    "User Panel": "area-UserPanel",
    "File Cache": "area-FileCache",
    "Wish Export": "area-Gacha",
    "Game Record": "area-GameRecord",
    "Hutao Database": "area-HutaoAPI",
    "User Interface": "area-UserInterface",
    "Announcement": "area-Announcement",
    "Checkin": "area-SignIn",
    "Snap Hutao Cloud": "area-HutaoCloud",
    "Snap Hutao Account": "area-Passport"
}

VALID_PUSH_REF = ["refs/heads/main", "refs/heads/develop"]
