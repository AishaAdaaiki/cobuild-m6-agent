"""
Co-Build Session Agent · Utopia Studio M6
------------------------------------------
Input  : raw Granola transcript (text file or stdin)
Output : structured JSON → Linear issues + Slack summary
"""

import os
import json
import argparse
from pathlib import Path

from transcript_parser import parse_transcript
from linear_client import create_issues
from slack_client import post_summary


def run_agent(transcript_path: str, dry_run: bool = False) -> dict:
    """
    Full pipeline:
      1. Read transcript
      2. Claude extracts decisions / actions / questions
      3. Format as Linear issues
      4. Post Slack summary to studio-only channel
      5. Return structured JSON
    """
    transcript_text = Path(transcript_path).read_text(encoding="utf-8")
    print(f"[agent] transcript loaded ({len(transcript_text)} chars)")

    # Step 1 — parse with Claude
    parsed = parse_transcript(transcript_text)
    print(f"[agent] extracted {len(parsed['issues'])} issues, "
          f"{len(parsed['decisions'])} decisions, "
          f"{len(parsed['open_questions'])} open questions")

    result = {
        "session": parsed["session_meta"],
        "issues": parsed["issues"],
        "decisions": parsed["decisions"],
        "open_questions": parsed["open_questions"],
        "slack_summary": parsed["slack_summary"],
        "linear_urls": [],
    }

    if dry_run:
        print("[agent] DRY RUN — skipping Linear + Slack API calls")
        return result

    # Step 2 — create Linear issues
    linear_urls = create_issues(parsed["issues"])
    result["linear_urls"] = linear_urls
    print(f"[agent] created {len(linear_urls)} Linear issues")

    # Step 3 — post to Slack
    post_summary(parsed["slack_summary"], parsed["session_meta"])
    print("[agent] Slack summary posted")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Co-Build Session Agent — transcript → Linear + Slack"
    )
    parser.add_argument("transcript", help="Path to Granola transcript (.txt)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and extract only — skip API calls",
    )
    parser.add_argument(
        "--output",
        default="output.json",
        help="Path to write JSON output (default: output.json)",
    )
    args = parser.parse_args()

    result = run_agent(args.transcript, dry_run=args.dry_run)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\n[agent] output written to {output_path}")
    print("\n--- SLACK SUMMARY ---")
    print(result["slack_summary"])
    print("\n--- LINEAR ISSUES ---")
    for i, issue in enumerate(result["issues"], 1):
        print(f"  {i}. [{issue['priority']}] {issue['title']}")


if __name__ == "__main__":
    main()
