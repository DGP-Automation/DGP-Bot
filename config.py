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
                                  "needs-triage", "需要更多信息"]
PROJECT_TRIGGER_LABEL = ["BUG", "功能", "bug"]
OUTDATED_WINDOWS_VERSION = ["18362", "18363", "19041",
                            "19042", "19043", "19044",
                            "1903", "2004", "20H2",
                            "21H1", "21H2", "22000"]
CATEGORY_MATCHER = {
    "安装和环境": "area-LifeCycle",
    "游戏启动器": "area-GameLauncher",
    "祈愿记录": "area-Gacha",
    "成就管理": "area-Achievement",
    "我的角色": "area-AvatarInfo",
    "实时便笺": "area-DailyNote",
    "养成计算": "area-Cultivation",
    "深境螺旋/胡桃数据库": "area-HutaoAPI",
    "米游社账号面板": "area-UserPanel",
    "文件缓存": "area-FileCache",
    "玩家查询": "area-GameRecord",
    "用户界面": "area-UserInterface",
    "公告": "area-Announcement",
    "每日签到奖励": "area-CheckIn",
    "胡桃通行证/胡桃云": "area-Passport",
    "Wiki": "needs-triage",
    "其它": "needs-triage"
}

CATEGORY_MATCHER_ENG = {
    "Installation and Environment": "area-LifeCycle",
    "Game Launcher": "area-GameLauncher",
    "Wish Export": "area-Gacha",
    "Achievement": "area-Achievement",
    "My Character": "area-AvatarInfo",
    "Realtime Note": "area-DailyNote",
    "Develop Plan": "area-Cultivation",
    "MiHoYo Account Panel": "area-UserPanel",
    "File Cache": "area-FileCache",
    "Daily Checkin Reward": "area-CheckIn",
    "Hutao Passport/Hutao Cloud": "area-Passport",
    "Hutao Database": "area-HutaoAPI",
    "User Interface": "area-UserInterface",
    "Announcement": "area-Announcement",
    "Wiki": "needs-triage",
    "Others": "needs-triage"
}

VALID_PUSH_REF = ["refs/heads/main", "refs/heads/develop"]

DISCORD_PUSH_CHANNEL_ID = os.getenv('DISCORD_PUSH_CHANNEL_ID')
DISCORD_PUSH_WEBHOOK_SECRET = os.getenv('DISCORD_PUSH_WEBHOOK_SECRET')
