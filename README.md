# Co-Build Session Agent · Utopia Studio M6

> Turns a raw Granola co-build transcript into Linear issues + a Slack summary — automatically, in one run.

---

## What it does

After every M6 Product & Technology co-build session, someone has to:
1. Read the full Granola transcript
2. Decide what became an action item
3. Write up Linear issues manually
4. Draft a summary for the studio-only Slack channel

This agent does all four steps in under 30 seconds.

**Input:** raw `.txt` transcript from Granola  
**Output:**
- Structured JSON with session metadata, issues, decisions, open questions, and Slack summary
- Linear issues created via API (title, description, priority, label, owner)
- Slack message posted to the studio-only channel

The JSON output is machine-readable — another Utopia OS agent can pick it up to trigger follow-up actions (e.g. a G0 checklist checker, a fellow progress tracker).

---

## How to run

### 1. Clone and install

```bash
git clone https://github.com/AishaAdaaiki/cobuild-m6-agent.git
cd cobuild-m6-agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

You need:
- `ANTHROPIC_API_KEY` — from [console.anthropic.com](https://console.anthropic.com)
- `LINEAR_API_KEY` — from Linear → Settings → API → Personal API keys
- `LINEAR_TEAM_ID` — from Linear → Settings → Team → copy the ID from the URL
- `SLACK_BOT_TOKEN` — from your Slack app → OAuth & Permissions → Bot Token
- `SLACK_CHANNEL_ID` — right-click the channel in Slack → Copy link → extract the ID

### 3. Run on the sample transcript

```bash
# Dry run — parses and extracts, skips API calls
python src/agent.py sample_data/sample_transcript.txt --dry-run

# Full run — creates Linear issues + posts to Slack
python src/agent.py sample_data/sample_transcript.txt --output output.json
```

### 4. Run on your own transcript

Export your Granola transcript as `.txt` and run:

```bash
python src/agent.py path/to/your/transcript.txt --output output.json
```

---

## Prompts used

### System prompt (in `transcript_parser.py`)
```
You are an operator assistant at Utopia Studio, a venture studio in Doha.
You process raw co-build session transcripts and extract structured output for the studio team.
Your job is to produce output that:
1. Saves the tech/product operator from reading the full transcript
2. Creates ready-to-use Linear issues the fellow can act on immediately
3. Gives the studio-only Slack channel a one-paragraph brief
You are precise, concise, and use the studio's voice: declarative, specific, no hedging.
```

### Extraction prompt
Sends the full transcript and asks Claude to return structured JSON with:
- `session_meta` — venture name, date, attendees, module
- `issues` — title, description, priority, suggested_owner, label
- `decisions` — list of decisions made
- `open_questions` — unresolved questions
- `slack_summary` — ready-to-paste Slack paragraph

Full prompt in `src/transcript_parser.py`.

---

## Tools and APIs called

| Tool | Purpose |
|------|---------|
| Anthropic Claude API (`claude-sonnet-4-20250514`) | Parse transcript, extract structured data |
| Linear GraphQL API | Create issues with priority, labels, project assignment |
| Slack Web API (`chat.postMessage`) | Post formatted summary to studio-only channel |

---

## Project structure

```
cobuild-m6-agent/
├── src/
│   ├── agent.py              # entry point — orchestrates the pipeline
│   ├── transcript_parser.py  # Claude API call + JSON extraction
│   ├── linear_client.py      # Linear GraphQL issue creation
│   └── slack_client.py       # Slack message posting
├── sample_data/
│   ├── sample_transcript.txt # realistic Granola transcript for demo
│   └── sample_output.json    # exact output the agent produces
├── requirements.txt
├── .env.example
└── README.md
```

---

## Sample output

See [`sample_data/sample_output.json`](sample_data/sample_output.json) for the full output from the sample transcript.

Slack summary example:
> Flowpath Logistics co-build (M6) — 20 May. Three blockers addressed: Qatar Customs API is being escalated for official sandbox access (Noor, this week), Mapbox is being upgraded to paid immediately, and QSTP translation is in progress (EOW). Auth is on Sara's plate by Thursday for Friday review. Three overdue Linear items (API doc, data model, competitive landscape) are resolved by Wednesday — G0 is in 12 days and the milestone tracker is at ~40%. No critical risks to the 3-week PWA beta target assuming customs can be mocked.

---

## Utopia OS fit

This agent is designed as a node in Utopia OS:

```
Granola transcript
       ↓
[cobuild-m6-agent]  ← this repo
       ↓
  output.json
       ↓
[G0 checklist agent]  ← next node: reads issues, checks against G0 gates
       ↓
[daily briefing agent]  ← flags at-risk fellows to Fellowships team
```

The JSON output schema is stable and documented — any downstream agent can parse `issues`, `decisions`, and `open_questions` without a human in the middle.
