#!/usr/bin/env python3
"""Generate consistent flowchart PNGs for every active course lab."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LABS = {
    "labs/Day 1/Lab 0 - Environment Setup": (
        "Lab 0 - Shared Course Environment",
        ["Microsoft 365 account", "Course Sandbox\\nwith Dataverse", "Power Automate", "Copilot Studio", "Ready for Labs 1-10"],
        [(0, 1, "sign in"), (1, 2, "select same environment"), (1, 3, "select same environment"), (2, 4, "verify"), (3, 4, "verify")],
    ),
    "labs/Day 1/Lab 1 - Instant Email Flow": (
        "Lab 1 - Prompt-Created Email Automation",
        ["Learner describes flow\\nin natural language", "Power Automate Copilot\\ncreates draft", "Manual trigger\\nCustomerName", "Send email (V2)", "Outlook inbox"],
        [(0, 1, "prompt"), (1, 2, "review and correct"), (2, 3, "dynamic content"), (3, 4, "deliver")],
    ),
    "labs/Day 1/Lab 2 - Instant Excel Logging Flow": (
        "Lab 2 - Enquiry to Excel",
        ["Manual trigger", "Name + Email + Message", "Add a row into a table", "Enquiry Log.xlsx\\nEnquiryTable", "Run history"],
        [(0, 1, "capture"), (1, 2, "map columns"), (2, 3, "write row"), (3, 4, "verify")],
    ),
    "labs/Day 1/Lab 3 - Scheduled Flow": (
        "Lab 3 - Scheduled Reminder",
        ["Recurrence trigger", "Weekday schedule\\nSingapore time", "Prepare reminder", "Send email (V2)", "Team inbox"],
        [(0, 1, "fires"), (1, 2, "compose"), (2, 3, "send"), (3, 4, "deliver")],
    ),
    "labs/Day 1/Lab 4 - Automated Form Flow": (
        "Lab 4 - Automated Form to Email and Excel",
        ["Customer submits\\nMicrosoft Form", "New response trigger", "Get response details", "Send team email", "Add Excel row"],
        [(0, 1, "response"), (1, 2, "Response Id"), (2, 3, "Full Name, Email, Message"), (2, 4, "map fields")],
    ),
    "labs/Day 1/Lab 5 - Human Approval Flow": (
        "Lab 5 - Human Approval with Two Outcomes",
        ["Manual request", "Start and wait\\nfor approval", "Human decision", "Outcome condition", "Approved email", "Rejected email"],
        [(0, 1, "submit"), (1, 2, "pause"), (2, 3, "outcome"), (3, 4, "Approve"), (3, 5, "Reject")],
    ),
    "labs/Day 1/Lab 6A - External Enquiry Webhook": (
        "Lab 6A - External Website Webhook",
        ["Website enquiry form", "HTTP POST\\nproduction URL", "Parse JSON", "Send email", "HTTP JSON response", "Website result"],
        [(0, 1, "submit"), (1, 2, "body"), (2, 3, "notify"), (3, 4, "success"), (4, 5, "display")],
    ),
    "labs/Day 1/Lab 6B - Webhook Chatbot": (
        "Lab 6B - Deterministic Webhook Chatbot",
        ["Browser chatbot", "HTTP POST", "Parse JSON", "Normalise message", "Switch routes", "JSON bot reply", "Chat window"],
        [(0, 1, "message"), (1, 2, "body"), (2, 3, "clean"), (3, 4, "match topic"), (4, 5, "response"), (5, 6, "render")],
    ),
    "labs/Day 2/Lab 7A - Create IT Support Agent": (
        "Lab 7A - Prompt-Create an IT Support Agent",
        ["Natural-language\\nagent prompt", "Copilot Studio\\ngenerates agent", "Review instructions", "Preview conversation", "Refine and save"],
        [(0, 1, "create"), (1, 2, "inspect"), (2, 3, "test"), (3, 4, "improve")],
    ),
    "labs/Day 2/Lab 7B - IT Support RAG Agent": (
        "Lab 7B - Grounded IT Support RAG",
        ["User question", "IT Support agent", "Approved IT FAQ\\nknowledge source", "Retrieve relevant passage", "Grounded answer\\nwith citation", "Refuse unsupported claims"],
        [(0, 1, "ask"), (1, 2, "search"), (2, 3, "retrieve"), (3, 4, "ground"), (2, 5, "no evidence")],
    ),
    "labs/Day 2/Lab 8 - Deploy Agent to Teams and Website": (
        "Lab 8 - Publish Agent and Connect Website",
        ["Marina Trust\\nCopilot agent", "Publish", "Microsoft Teams", "Website enquiry form", "Ordinary HTTP flow\\n(no agent)", "Website result"],
        [(0, 1, "channel"), (1, 2, "chat"), (3, 4, "POST"), (4, 5, "JSON response")],
    ),
    "labs/Day 2/Lab 9 - Banking Onboarding Agent Flow": (
        "Lab 9 - Copilot Agent Calls a Deterministic Flow",
        ["Teams or website chat", "Marina Trust\\nCopilot agent", "Agent flow tool", "Deterministic conditions", "Respond to the agent", "Answer in chat"],
        [(0, 1, "conversation"), (1, 2, "confirmed inputs"), (2, 3, "evaluate"), (3, 4, "structured outputs"), (4, 1, "tool result"), (1, 5, "present")],
    ),
    "labs/Day 2/Lab 10 - Procurement Request Workflow": (
        "Lab 10 - Copilot Agent Calls a Prompt Flow",
        ["Teams or website chat", "Marina Trust\\nCopilot agent", "Prompt flow tool", "AI Builder prompt\\nplus guardrails", "Parse and validate", "Respond to the agent", "Controlled draft in chat"],
        [(0, 1, "conversation"), (1, 2, "confirmed enquiry"), (2, 3, "generate"), (3, 4, "structured JSON"), (4, 5, "safe outputs"), (5, 1, "tool result"), (1, 6, "present")],
    ),
}


def quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_dot(title: str, nodes: list[str], edges: list[tuple[int, int, str]]) -> str:
    node_lines = []
    for index, label in enumerate(nodes):
        fill = "#E8F1FF"
        border = "#1F6FEB"
        if index == 0:
            fill, border = "#E8F7EF", "#16845B"
        elif index == len(nodes) - 1:
            fill, border = "#FFF4E5", "#B56A00"
        node_lines.append(
            f'n{index} [label="{quote(label)}", fillcolor="{fill}", color="{border}"];'
        )
    edge_lines = [
        f'n{source} -> n{target} [label="{quote(label)}"];'
        for source, target, label in edges
    ]
    return f"""digraph lab {{
  graph [label="{quote(title)}", labelloc=t, fontsize=20, fontname="Arial Bold",
         bgcolor="white", pad=0.3, nodesep=0.35, ranksep=0.55, splines=ortho];
  rankdir=LR;
  node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11,
        margin="0.20,0.12", penwidth=1.5];
  edge [fontname="Arial", fontsize=9, color="#59636E", fontcolor="#39424E",
        arrowsize=0.75, penwidth=1.2];
  {" ".join(node_lines)}
  {" ".join(edge_lines)}
}}
"""


def main() -> None:
    for relative, (title, nodes, edges) in LABS.items():
        lab = ROOT / relative
        assets = lab / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        dot_path = assets / "flowchart.dot"
        png_path = assets / "flowchart.png"
        dot_path.write_text(build_dot(title, nodes, edges), encoding="utf-8")
        subprocess.run(
            ["dot", "-Tpng", "-Gdpi=150", str(dot_path), "-o", str(png_path)],
            check=True,
        )
        print(png_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
