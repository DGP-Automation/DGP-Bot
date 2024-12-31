from google import genai
import requests
import os


generic_api_intro = """
The project is a Python FastAPI application that serves a desktop software for a variety of tasks. The API is running in Python 12 and a nearly latest FastAPI version.
"""

snap_hutao_intro = """
The project is a C# .NET desktop application, build with latest .NET framework and utilize latest features of WinUI 3.
"""

snap_hutao_server_intro = """
The project is a C# ASP.NET web application, build with latest .NET framework.
"""


def create_pull_request_summary(org_name: str, repo_name: str, pr_number: int) -> str:
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    client = genai.Client(api_key=gemini_api_key)
    diff_patch = requests.get(
        f"https://patch-diff.githubusercontent.com/raw/{org_name}/{repo_name}/pull/{pr_number}.patch").content
    match repo_name.lower():
        case "snap.hutao":
            project_intro = snap_hutao_intro
        case "generic-api":
            project_intro = generic_api_intro
        case "snap.hutao.server":
            project_intro = snap_hutao_server_intro
        case _:
            project_intro = ""

    PR_prompt = f"""
    ## System / Role Instruction
    You are an AI assistant that summarizes Pull Request changes in a software project. Review all commits and the diff of changed files to produce a concise, structured summary.

    {project_intro}

    ## User / Task Instruction

    1. Combine Commits

    - It's common to see multiple commits address the same goal (e.g., refactoring a single module or introducing a new feature). In a big picture view, summarize feature changes or bug fixes that span multiple commits.

    2. Changes by feature
    
    - Features usually organized in same folder or different path with same or related folder name.
    - Group changes by feature. List them as separate bullet points under their respective headings.
    - Use collapsible section in here, to avoid cluttering the summary with too many details.

    3. Key Change Highlights

    - In a separate section, list the most significant or “key” changes, such as:
        - Data structure modifications
        - Changes affecting app configuration or environment variables
        - New API endpoints or significant changes to existing endpoints
    - Explain why these changes are critical or how they might affect the overall codebase.


    4. Suggested Test Methods (Only for Python project)
    
    - If the project is not a Python project, skip this section.
    - Provide recommended test scenarios to ensure the changes work correctly and do not break existing functionality. For example:
        - API endpoint tests for new or changed endpoints
        - Unit tests for new utility functions or classes
        - Integration tests if cross-module interactions are introduced

    ## Output Format

    1. Separate the summary into the following sections:
    2. Changes by feature (bullet points grouped by relevant file or router)
    3. Key Change Highlights (focus on major or structural changes)
    4. Suggested Test Method (recommended test scenarios)

    You can find all the commits and changed files in the PR description and patch. Please summarize the changes accordingly. 
    Do not forget to include the PR intro (summarized title, author(s), etc.) in the final summary.
    Avoid unnecessary responses and just include summaries in your response, response should be in markdown format (no need to write in code block because your response will send to reply directly)and you can use GitHub Flavored Markdown for better reading experience.
    Ignore all commits that not associated with code programming, such as localization (resx) and markdown file.
    PR patch:
    ```
    {diff_patch}
    ```
    """
    response = client.models.generate_content(model='gemini-2.0-flash-exp', contents=PR_prompt)
    response = response.text
    print(f"AI Summary for {org_name}/{repo_name}#{pr_number}: \n{response}")
    return response
