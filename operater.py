import datetime
import json
import time

import jwt
import requests

from config import *


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


def github_request(url: str, method: str, data: dict = None, use_personal_token: bool = False) -> str:
    if use_personal_token is False:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {get_access_token()}"
        }
    else:
        headers = {
            "Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}"
        }

    if method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, json=data)
    else:
        response = ""

    if response.status_code >= 400:
        print("GitHub request error: ", response.status_code)
        print(response.text)
    return response.text


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


def get_issue_removed_labels(repo_name: str, issue_number: int) -> list:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/timeline"
    response = json.loads(github_request(url, "GET"))
    return [event["label"]["name"] for event in response if event["event"] == "unlabeled"]


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


def get_project_node_id_by_number(org_name: str, project_number: int) -> str:
    url = "https://api.github.com/graphql"
    data = {"query": 'query{organization(login: "%s") {projectV2(number: %s){id}}}' % (org_name, project_number)}
    response = json.loads(github_request(url, "POST", data, True))
    try:
        return response["data"]["organization"]["projectV2"]["id"]
    except KeyError:
        return ""


def get_project_columns_by_node_id(org_name: str, project_number: int) -> dict:
    url = "https://api.github.com/graphql"
    project_node_id = get_project_node_id_by_number(org_name, project_number)
    data = {
        "query": 'query{ node(id: "%s") { ... on ProjectV2 { fields(first: 20) { nodes { ... on ProjectV2Field { id '
                 'name } ... on ProjectV2IterationField { id name configuration { iterations { startDate id }}} ... '
                 'on ProjectV2SingleSelectField { id name options { id name }}}}}}}' % (
                     project_node_id)}
    response = json.loads(github_request(url, "POST", data, True))
    for item in response["data"]["node"]["fields"]["nodes"]:
        if item["name"] == "Status":
            return item


def add_issue_to_project_board_with_number_and_column_name(org_name: str, issue_node_id: str, project_number: int,
                                                           column_name: str = None) -> str:
    # the column is presented as "option" in the project board by GitHub
    # so needs to convert the column name to an option ID
    url = f"https://api.github.com/graphql"
    project_node_id = get_project_node_id_by_number(org_name, project_number)
    data = {"query": 'mutation {addProjectV2ItemById(input: {projectId: "%s",contentId: "%s"}) {item {id}}}' % (
        project_node_id, issue_node_id)}
    response = json.loads(github_request(url, "POST", data))
    new_card_id = response["data"]["addProjectV2ItemById"]["item"]["id"]
    if column_name:
        status = get_project_columns_by_node_id(org_name, project_number)
        status_field_id = status["id"]
        options = status["options"]
        for option in options:
            if option["name"] == column_name:
                data = {
                    "query": 'mutation {updateProjectV2ItemFieldValue (input: { projectId: "%s", itemId: "%s", '
                             'fieldId: "%s" value: { singleSelectOptionId: "%s" }}) { clientMutationId } }' % (
                                 project_node_id, new_card_id, status_field_id, option["id"])}
    response = github_request(url, "POST", data)
    return response


def get_issue_node_id(repo_name: str, issue_number: int) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}"
    response = json.loads(github_request(url, "GET"))
    return response["node_id"]


def get_issue_language(repo_name: str, issue_number: int) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}"
    response = json.loads(github_request(url, "GET"))
    issue_title = response["title"]
    if r"[ENG]" in issue_title:
        return "ENG"
    else:
        return "CHS"


def get_issue_type(repo_name: str, issue_number: int) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}"
    response = json.loads(github_request(url, "GET"))
    try:
        _ = response['pull_request']
        return "pull_request"
    except KeyError:
        return "issue"


def lock_issue_conversation(repo_name: str, issue_number: int, lock_reason: str = None) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/lock"
    if lock_reason is None:
        response = github_request(url, "PUT")
    else:
        response = github_request(url, "PUT", data={"lock_reason": lock_reason})
    return response


def unlock_issue_conversation(repo_name: str, issue_number: int) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/lock"
    response = github_request(url, "DELETE")
    return response


def hide_issue_comment(comment_node_id: int, reason: str) -> str:
    url = "https://api.github.com/graphql"
    query = '''
    mutation MinimizeComment($input: MinimizeCommentInput!) {
      minimizeComment(input: $input) {
        minimizedComment {
          isMinimized
        }
      }
    }
    '''
    variables = {
        'input': {
            'subjectId': comment_node_id,
            'classifier': reason.upper()
        }
    }
    data = {
        'query': query,
        'variables': variables
    }
    response = github_request(url, "POST", data, True)
    print("Hide comment response:", response)
    return response


def block_user_from_organization(org_name: str, username: str) -> str:
    url = f"https://api.github.com/orgs/{org_name}/blocks/{username}"
    response = github_request(url, "PUT")
    return response


def create_new_milestone(repo_name: str, milestone_name: str, desc: str = None) -> str:
    url = f"https://api.github.com/repos/{repo_name}/milestones"
    data = {"title": milestone_name, "description": str(desc)}
    response = github_request(url, "POST", data)
    return response


def update_milestone(repo_name: str, milestone_number: int, body: dict) -> str:
    url = f"https://api.github.com/repos/{repo_name}/milestones/{milestone_number}"
    response = github_request(url, "PATCH", body)
    return response


def list_repo_milestones(repo_name: str) -> str:
    url = f"https://api.github.com/repos/{repo_name}/milestones"
    response = github_request(url, "GET")
    return response


def update_issue_milestone(repo_name: str, issue_number: int, milestone_number: int) -> str:
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}"
    data = {"milestone": milestone_number}
    response = github_request(url, "PATCH", data)
    return response
