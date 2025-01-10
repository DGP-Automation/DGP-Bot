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

snap_hutao_docs_intro = """
This project is not a programming project, it's the documentation project for Snap.Hutao. This project used VuePress to build the documentation website, and the content is written in Markdown.
You do not need to do anything with Vue-related files, only focus on the Markdown files. Checks for correct grammar, accurate wording, and can provide clear guidance.
If this PR is for a software changelog update, provide a copy of the English changelog translated by you in Markdown raw text using a code block while retaining the Chinese changelog style.
If the PR only update the Chinese document, but not include the English document, provide an instruction to modify the English document, use code block to wrap the Markdown raw content.
When listing the change summaries, list the paths to all the documents that have changed, so that we can easily find the corresponding documents when reviewing them.
"""


def remove_less_important_changes(full_text: str) -> str:
    text_parts = full_text.split("diff --git")
    filtered_parts = []

    for part in text_parts:
        if not part.strip():
            continue
        first_line = part.strip().splitlines()[0]

        if not (first_line.endswith(".md") or first_line.endswith(".resx")):
            filtered_parts.append(part)
    result_text = "diff --git".join(filtered_parts)

    return result_text


async def create_pull_request_summary(org_name: str, repo_name: str, pr_number: int) -> str:
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    client = genai.Client(api_key=gemini_api_key)
    diff_patch_url = f"https://patch-diff.githubusercontent.com/raw/{org_name}/{repo_name}/pull/{pr_number}.patch"
    diff_patch = requests.get(diff_patch_url).text
    match repo_name.lower():
        case "snap.hutao":
            project_intro = snap_hutao_intro
        case "generic-api":
            project_intro = generic_api_intro
        case "snap.hutao.server":
            project_intro = snap_hutao_server_intro
        case "snap.hutao.docs":
            project_intro = snap_hutao_docs_intro
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

    - If the project is not a Python project, skip this section and do not give any output in this section.
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
    """
    # Test prompt
    full_prompt = PR_prompt + f"""
    PR patch:
    ```
    {remove_less_important_changes(diff_patch)}
    ```
    """

    try:
        token_count_resp = client.models.count_tokens(
            model="gemini-2.0-flash-exp",
            contents=full_prompt,
        )
        print(f"Token count: {token_count_resp.total_tokens}")
    except genai.errors.ClientError:
        # Too long
        print(f"PR Prompt is too long: {len(full_prompt)}, using pr diff")
        pr_diff = requests.get(
            f"https://patch-diff.githubusercontent.com/raw/{org_name}/{repo_name}/pull/{pr_number}.diff").text
        full_prompt = PR_prompt + f"""
        PR patch:
        ```
        {remove_less_important_changes(pr_diff)}
        ```
        """
        try:
            token_count_resp = client.models.count_tokens(
                model="gemini-2.0-flash-exp",
                contents=full_prompt,
            )
            print(f"Token count: {token_count_resp.total_tokens}")
        except genai.errors.ClientError as e:
            raise RuntimeError(f"Error: {e}")
        if token_count_resp.total_tokens > 1000000:
            raise RuntimeError(f"PR Prompt is too long: {token_count_resp.total_tokens}, please reduce")
    print("Prompt prepared, generating AI summary...")
    response = client.models.generate_content(model='gemini-2.0-flash-exp', contents=full_prompt)
    response = response.text
    print(f"AI Summary for {org_name}/{repo_name}#{pr_number}: \n{response}")
    return response
