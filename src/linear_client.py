"""
linear_client.py
-----------------
Creates Linear issues from the structured output of transcript_parser.
Uses the Linear GraphQL API.

Required env vars:
  LINEAR_API_KEY   — your Linear personal API key
  LINEAR_TEAM_ID   — the team ID to create issues under
  LINEAR_PROJECT_ID (optional) — attach issues to a specific project
"""

import os
import requests

LINEAR_API_URL = "https://api.linear.app/graphql"

PRIORITY_MAP = {
    "urgent": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}

LABEL_COLORS = {
    "feature": "feature",
    "bug": "bug",
    "infra": "infra",
    "research": "research",
    "design": "design",
    "milestone": "milestone",
}


def _headers() -> dict:
    return {
        "Authorization": os.environ["LINEAR_API_KEY"],
        "Content-Type": "application/json",
    }


def _run_query(query: str, variables: dict) -> dict:
    response = requests.post(
        LINEAR_API_URL,
        json={"query": query, "variables": variables},
        headers=_headers(),
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(f"Linear API error: {data['errors']}")
    return data


def get_label_id(label_name: str, team_id: str) -> str | None:
    """Look up a label ID by name in the given team."""
    query = """
    query Labels($teamId: String!) {
      team(id: $teamId) {
        labels {
          nodes { id name }
        }
      }
    }
    """
    data = _run_query(query, {"teamId": team_id})
    labels = data["data"]["team"]["labels"]["nodes"]
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]
    return None


def create_issue(issue: dict, team_id: str, project_id: str | None = None) -> str:
    """
    Create a single Linear issue. Returns the issue URL.
    """
    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          url
          title
        }
      }
    }
    """

    label_id = get_label_id(issue.get("label", ""), team_id)

    variables = {
        "input": {
            "teamId": team_id,
            "title": issue["title"],
            "description": issue["description"],
            "priority": PRIORITY_MAP.get(issue.get("priority", "medium"), 3),
        }
    }

    if project_id:
        variables["input"]["projectId"] = project_id

    if label_id:
        variables["input"]["labelIds"] = [label_id]

    data = _run_query(mutation, variables)
    return data["data"]["issueCreate"]["issue"]["url"]


def create_issues(issues: list[dict]) -> list[str]:
    """
    Create all issues. Returns list of Linear URLs.
    """
    team_id = os.environ["LINEAR_TEAM_ID"]
    project_id = os.environ.get("LINEAR_PROJECT_ID")

    urls = []
    for issue in issues:
        url = create_issue(issue, team_id, project_id)
        urls.append(url)
        print(f"  [linear] created: {issue['title']} → {url}")

    return urls
