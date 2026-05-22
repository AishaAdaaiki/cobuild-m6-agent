"""
transcript_parser.py
---------------------
Sends the raw Granola transcript to Claude and returns structured data:
  - session metadata (venture name, date, attendees)
  - Linear issues (title, description, priority, suggested owner)
  - key decisions made
  - open questions
  - Slack summary paragraph
"""

import os
import json
import anthropic

SYSTEM_PROMPT = """You are an operator assistant at Utopia Studio, a venture studio in Doha.
You process raw co-build session transcripts and extract structured output for the studio team.

Your job is to produce output that:
1. Saves the tech/product operator from reading the full transcript
2. Creates ready-to-use Linear issues the fellow can act on immediately
3. Gives the studio-only Slack channel a one-paragraph brief

You are precise, concise, and use the studio's voice: declarative, specific, no hedging.
"""

EXTRACTION_PROMPT = """Below is a raw transcript from a Utopia Studio co-build session.

Extract the following and return ONLY valid JSON — no markdown, no explanation, no preamble.

JSON schema:
{
  "session_meta": {
    "venture_name": "string",
    "date": "string or null",
    "attendees": ["string"],
    "module": "string e.g. M6 Product & Technology"
  },
  "issues": [
    {
      "title": "short action title (max 10 words)",
      "description": "2-3 sentence description of what needs to be done and why",
      "priority": "urgent | high | medium | low",
      "suggested_owner": "fellow | tech_lead | studio_ops | tbd",
      "label": "feature | bug | infra | research | design | milestone"
    }
  ],
  "decisions": [
    "one-line statement of each decision reached in the session"
  ],
  "open_questions": [
    "one-line statement of each unresolved question that needs follow-up"
  ],
  "slack_summary": "A 3-4 sentence paragraph for the studio-only Slack channel. State what was built or decided, what is blocked, and what is next. Use declarative language. Start with the venture name."
}

Rules:
- Extract only real action items, not discussion filler
- Priority is 'urgent' only if a deadline or blocker was explicitly mentioned
- suggested_owner maps to: fellow (the founder does it), tech_lead (Utopia tech team), studio_ops (operations), tbd (unclear)
- issues list should have between 3 and 10 items — combine minor related tasks
- decisions and open_questions can each have 1-5 items
- slack_summary must be usable as-is in a Slack message, no placeholders

TRANSCRIPT:
{transcript}
"""


def parse_transcript(transcript_text: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = EXTRACTION_PROMPT.format(transcript=transcript_text)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\n\nRaw output:\n{raw}")

    # Validate required keys
    required = ["session_meta", "issues", "decisions", "open_questions", "slack_summary"]
    for key in required:
        if key not in parsed:
            raise ValueError(f"Missing key in Claude output: {key}")

    return parsed
