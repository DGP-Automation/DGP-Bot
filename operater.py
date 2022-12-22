import json

from config import *
import requests
import datetime
import jwt
import time


def get_access_token() -> str:
    global access_token_generated_time, access_token
    current_time = int(time.time())
    if current_time - access_token_generated_time <= 1800:
        return access_token
    else:
        # Get GWT from Private Key
        time_since_epoch_in_seconds = int(datetime.datetime.now().timestamp())
        cert_bytes = PRIVATE_KEY.encode()
        payload = {
            "iat": time_since_epoch_in_seconds - 60,
            "exp": time_since_epoch_in_seconds + (5 * 60),
            "iss": APP_ID
        }
        encoded_jwt = jwt.encode(payload, cert_bytes, algorithm="RS256")

        # Generate Access Token
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {encoded_jwt}"
        }
        new_access_token = requests.post(f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens",
                                         headers=headers).json()["token"]
        access_token = new_access_token
        access_token_generated_time = current_time
        return access_token


def github_request(url: str, method: str, data: dict = None) -> str:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {get_access_token()}"
    }
    if method == "POST":
        response = requests.post(url, headers=headers, json=data).text
    elif method == "GET":
        response = requests.get(url, headers=headers).text
    elif method == "DELETE":
        response = requests.delete(url, headers=headers).text
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data).text
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, json=data).text
    else:
        response = ""
    return response


def get_issue_comments(repo_name: str, issue_number: int) -> list:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/comments"
    response = json.loads(github_request(url, "GET"))
    return response


def get_bot_comment_in_issue(repo_name: str, issue_number: int) -> list:
    comments = get_issue_comments(repo_name, issue_number)
    bot_comments = []
    for comment in comments:
        if comment["user"]["id"] == 119836810:
            bot_comments.append(comment)
    return bot_comments


def make_issue_comment(repo_name: str, issue_number: int, comment: str) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/comments"
    data = {"body": comment}
    response = github_request(url, "POST", data)
    return response


def get_issue_label(repo_name: str, issue_number: int) -> list:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/labels"
    response = json.loads(github_request(url, "GET"))
    if response:
        return [label["name"] for label in response]
    else:
        return []


def add_issue_label(repo_name: str, issue_number: int, label: list) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/labels"
    data = {"labels": label}
    response = github_request(url, "POST", data)
    return response


def remove_one_issue_label(repo_name: str, issue_number: int, label: str) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/labels/{label}"
    response = github_request(url, "DELETE")
    return response


def set_issue_labels(repo_name: str, issue_number: int, label: list) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/labels"
    data = {"labels": label}
    response = github_request(url, "PUT", data)
    return response


def close_issue(repo_name: str, issue_number: int, reason: str) -> str:
    allowed_reason = ["completed", "not_planned", "reopened"]
    if reason not in allowed_reason:
        return "Invalid reason"
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}"
    data = {"state": "closed", "state_reason": reason}
    response = github_request(url, "PATCH", data)
    return response


def reopen_issue(repo_name: str, issue_number: int) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}"
    data = {"state": "open"}
    response = github_request(url, "PATCH", data)
    return response


def get_issue_with_label(repo_name: str, label: str) -> list:
    url = f"https://api.github.com/repos/{repo_name}/issues?state=all&labels={label}"
    response = json.loads(github_request(url, "GET"))
    return response