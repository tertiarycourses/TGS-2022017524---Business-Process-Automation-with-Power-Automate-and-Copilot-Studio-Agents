#!/usr/bin/env python3
"""Validate the locally generated Power Automate legacy lab packages."""

from __future__ import annotations

import json
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"
EXPECTED = {
    "Lab1-Send-Confirmation-Email.zip",
    "Lab2-Log-Enquiry-to-Excel.zip",
    "Lab3-Scheduled-Enquiry-Reminder.zip",
    "Lab4-Automated-Form-to-Email-and-Excel.zip",
    "Lab5-Human-Approval.zip",
    "Lab6A-External-Enquiry-Webhook.zip",
    "Lab6B-Webhook-Chatbot.zip",
    "Lab8-Marina-Trust-Website-Enquiry.zip",
}
FORBIDDEN = ("angch@", "alfredang@", "training1@", "sig=", "token=")
DAY2_SOLUTIONS = {
    LABS / "Day 2" / "00-Copilot-Studio-Day-2-Flow-Templates-Solution.zip": {
        "unique_name": "CopilotStudioDay2FlowTemplates",
        "workflows": {
            "Lab 9 - Assess Banking Onboarding Enquiry",
            "Lab 10 - Draft Customer Enquiry Response",
        },
    },
    LABS
    / "Day 2"
    / "Lab 9 - Banking Onboarding Agent Flow"
    / "Lab9-Banking-Onboarding-Agent-Flow-Solution.zip": {
        "unique_name": "Lab9BankingOnboardingAgentFlow",
        "workflows": {"Lab 9 - Assess Banking Onboarding Enquiry"},
    },
    LABS
    / "Day 2"
    / "Lab 10 - Procurement Request Workflow"
    / "Lab10-Customer-Enquiry-Prompt-Flow-Solution.zip": {
        "unique_name": "Lab10CustomerEnquiryPromptFlow",
        "workflows": {"Lab 10 - Draft Customer Enquiry Response"},
    },
}


def validate(package: Path) -> None:
    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        with zipfile.ZipFile(package) as archive:
            archive.testzip()
            archive.extractall(temp)

        manifest_path = temp / "manifest.json"
        assert manifest_path.exists(), f"{package}: missing manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["schema"] == "1.0", f"{package}: wrong manifest schema"

        definitions = list((temp / "Microsoft.Flow" / "flows").glob("*/definition.json"))
        assert len(definitions) == 1, f"{package}: expected one flow definition"
        definition = json.loads(definitions[0].read_text(encoding="utf-8"))
        assert definition["properties"]["definition"]["triggers"], f"{package}: no trigger"
        assert definition["properties"]["definition"]["actions"], f"{package}: no actions"

        folder = definitions[0].parent
        apis = json.loads((folder / "apisMap.json").read_text(encoding="utf-8"))
        connections = json.loads((folder / "connectionsMap.json").read_text(encoding="utf-8"))
        references = definition["properties"]["connectionReferences"]
        assert set(apis) == set(connections) == set(references), (
            f"{package}: connector maps do not agree"
        )

        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in temp.rglob("*.json")
        ).lower()
        for text in FORBIDDEN:
            assert text not in combined, f"{package}: forbidden text {text!r}"


def validate_day2_solution(
    package: Path,
    unique_name: str,
    expected_workflows: set[str],
) -> None:
    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        with zipfile.ZipFile(package) as archive:
            assert archive.testzip() is None, f"{package}: corrupt ZIP"
            archive.extractall(temp)

        solution = ET.parse(temp / "solution.xml").getroot()
        assert solution.findtext("./SolutionManifest/UniqueName") == unique_name
        assert solution.findtext("./SolutionManifest/Managed") == "0"

        customization = ET.parse(temp / "customizations.xml").getroot()
        workflows = customization.findall("./Workflows/Workflow")
        assert len(workflows) == len(expected_workflows), (
            f"{package}: wrong workflow count"
        )
        names = {workflow.attrib["Name"] for workflow in workflows}
        assert names == expected_workflows

        for workflow in workflows:
            json_name = workflow.findtext("JsonFileName")
            assert json_name, f"{package}: workflow JSON path missing"
            definition = json.loads(
                (temp / json_name.lstrip("/")).read_text(encoding="utf-8")
            )
            flow = definition["properties"]["definition"]
            trigger = next(iter(flow["triggers"].values()))
            response = flow["actions"]["Respond_to_Copilot"]
            assert trigger["kind"] == "PowerVirtualAgents"
            assert response["kind"] == "PowerVirtualAgents"
            assert response["type"] == "Response"
            assert len(flow["actions"]) > 1, f"{package}: starter has no processing"

        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in temp.rglob("*")
            if path.is_file()
        ).lower()
        for text in FORBIDDEN:
            assert text not in combined, f"{package}: forbidden text {text!r}"


def main() -> None:
    packages = sorted(
        package
        for package in LABS.rglob("*.zip")
        if package.name in EXPECTED
    )
    assert {package.name for package in packages} == EXPECTED, "missing expected packages"
    for package in packages:
        validate(package)
        print(f"PASS {package.relative_to(ROOT)}")
    for package, expected in DAY2_SOLUTIONS.items():
        assert package.exists(), f"missing Day 2 solution package: {package}"
        validate_day2_solution(
            package,
            expected["unique_name"],
            expected["workflows"],
        )
        print(f"PASS {package.relative_to(ROOT)}")
    print(
        f"PASS {len(packages)} legacy package(s) + "
        f"{len(DAY2_SOLUTIONS)} solution package(s)"
    )


if __name__ == "__main__":
    main()
