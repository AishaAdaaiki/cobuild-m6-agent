# Co-Build Session Agent · Utopia Studio M6

> Turns a raw Granola co-build transcript into Linear issues + a Slack summary — automatically, in one run.

---

## What it does

After every M6 Product & Technology co-build session, the studio tech lead manually:
1. Reads the full Granola transcript
2. Decides what became an action item
3. Types each issue into Linear one by one
4. Drafts a summary for the studio-only Slack channel

This agent does all four steps in under 30 seconds.

**Input:** raw `.txt` transcript from Granola
**Output:**
- Structured JSON with session metadata, issues, decisions, open questions, and Slack summary
- Linear issues created via API (title, description, priority, label, suggested owner)
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
- `OPENROUTER_API_KEY` — from [openrouter.ai](https://openrouter.ai) → Keys → Create Key (free)
- `LINEAR_API_KEY` — from Linear → Settings → API → Personal API keys
- `LINEAR_TEAM_ID` — run the query below to get the UUID
- `SLACK_BOT_TOKEN` — from your Slack app → OAuth & Permissions → Bot Token
- `SLACK_CHANNEL_ID` — right-click the channel in Slack → View channel details → copy the ID

**Getting your Linear Team UUID:**
```bash
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: YOUR_LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id name } } }"}' \
  | python3 -m json.tool
```

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

### System prompt
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
Sends the full transcript and instructs the model to return structured JSON with:
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
| OpenRouter API (`openrouter/auto`) | LLM inference — transcript parsing and structured extraction |
| Linear GraphQL API | Create issues with priority, labels, and project assignment |
| Slack Web API (`chat.postMessage`) | Post formatted summary to studio-only channel |

---

## Project structure

```
cobuild-m6-agent/
├── src/
│   ├── agent.py              # entry point — orchestrates the pipeline
│   ├── transcript_parser.py  # OpenRouter API call + JSON extraction
│   ├── linear_client.py      # Linear GraphQL issue creation
│   └── slack_client.py       # Slack message posting
├── sample_data/
│   ├── sample_transcript.txt # realistic Granola transcript for demo
│   └── sample_output.json    # example of full agent output
├── requirements.txt
├── .env.example
├── writeup.md
└── README.md
```

---

## Sample output

See [`sample_data/sample_output.json`](sample_data/sample_output.json) for the full output.

Slack summary example:
> Flowpath Logistics is unblocked on critical path items for the PWA. Qatar Customs API access is being secured by Studio Ops, expected within two weeks. Mapbox has been upgraded to a paid tier. The Fellow will deliver authentication flow by Thursday and onboarding wireframes by Wednesday. Outstanding M6 checklist items and QSTP license translation are also in progress by Studio Ops.

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
[G0 checklist agent]  ← reads issues, checks against G0 gates
       ↓
[daily briefing agent]  ← flags at-risk fellows to Fellowships team
```

The JSON output schema is stable — any downstream agent can parse `issues`, `decisions`, and `open_questions` without a human in the middle.
