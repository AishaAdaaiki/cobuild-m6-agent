"""
slack_client.py
----------------
Posts the co-build session summary to the studio-only Slack channel.

Required env vars:
  SLACK_BOT_TOKEN      — xoxb-... bot token
  SLACK_CHANNEL_ID     — the studio-only channel ID (e.g. C0XXXXXXX)
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def post_summary(slack_summary: str, session_meta: dict) -> None:
    """
    Posts a formatted session summary to the studio-only Slack channel.
    """
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    channel_id = os.environ["SLACK_CHANNEL_ID"]

    venture = session_meta.get("venture_name", "Unknown Venture")
    module = session_meta.get("module", "M6")
    date = session_meta.get("date", "")
    attendees = ", ".join(session_meta.get("attendees", []))

    header = f"*Co-Build Session Brief · {venture} · {module}*"
    if date:
        header += f" · {date}"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Co-Build Brief · {venture}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": slack_summary},
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Attendees:* {attendees or 'see transcript'} · *Module:* {module}",
                }
            ],
        },
    ]

    try:
        client.chat_postMessage(
            channel=channel_id,
            text=f"{header}\n\n{slack_summary}",  # fallback text
            blocks=blocks,
        )
        print(f"  [slack] summary posted to {channel_id}")
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")
