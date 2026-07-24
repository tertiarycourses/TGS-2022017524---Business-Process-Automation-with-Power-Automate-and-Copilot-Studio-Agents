#!/usr/bin/env python3
"""Build combined and lab-specific Day 2 agent-flow solution packages."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DAY2 = ROOT / "labs/Day 2"
OUTPUT = DAY2 / "00-Copilot-Studio-Day-2-Flow-Templates-Solution.zip"
LAB9_OUTPUT = (
    DAY2
    / "Lab 9 - Banking Onboarding Agent Flow"
    / "Lab9-Banking-Onboarding-Agent-Flow-Solution.zip"
)
LAB10_OUTPUT = (
    DAY2
    / "Lab 10 - Procurement Request Workflow"
    / "Lab10-Customer-Enquiry-Prompt-Flow-Solution.zip"
)

LAB9_ID = "2f61f074-2493-47e4-8e12-6bda1bc45e91"
LAB10_ID = "517d4932-2de7-4f98-a91d-c69152488510"


def agent_flow(
    *,
    inputs: list[tuple[str, str, str]],
    outputs: list[tuple[str, str]],
    actions: dict | None = None,
) -> dict:
    input_properties = {}
    required = []
    for name, data_type, description in inputs:
        content_hint = "NUMBER" if data_type == "number" else "TEXT"
        input_properties[name] = {
            "title": name,
            "type": data_type,
            "x-ms-dynamically-added": True,
            "description": description,
            "x-ms-content-hint": content_hint,
        }
        required.append(name)

    output_body = {name: value for name, value in outputs}
    output_properties = {
        name: {
            "title": name,
            "type": "string",
            "x-ms-dynamically-added": True,
        }
        for name, _ in outputs
    }

    return {
        "schemaVersion": "1.0.0.0",
        "properties": {
            "connectionReferences": {},
            "definition": {
                "$schema": (
                    "https://schema.management.azure.com/providers/"
                    "Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#"
                ),
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"},
                    "$authentication": {
                        "defaultValue": {},
                        "type": "SecureObject",
                    },
                },
                "triggers": {
                    "manual": {
                        "type": "Request",
                        "kind": "PowerVirtualAgents",
                        "inputs": {
                            "schema": {
                                "type": "object",
                                "properties": input_properties,
                                "required": required,
                            }
                        },
                    }
                },
                "actions": (actions or {}) | {
                    "Respond_to_Copilot": {
                        "runAfter": (
                            {next(reversed(actions)): ["Succeeded"]}
                            if actions
                            else {}
                        ),
                        "type": "Response",
                        "kind": "PowerVirtualAgents",
                        "inputs": {
                            "statusCode": 200,
                            "body": output_body,
                            "schema": {
                                "type": "object",
                                "properties": output_properties,
                            },
                        },
                    }
                },
                "outputs": {},
            },
        },
    }


LAB9_FLOW = agent_flow(
    inputs=[
        ("fullName", "string", "Applicant full name"),
        ("email", "string", "Applicant email address"),
        ("accountType", "string", "Requested account type"),
        ("employmentStatus", "string", "Applicant employment status"),
        ("annualIncome", "number", "Applicant annual income"),
        ("initialDeposit", "number", "Proposed initial deposit"),
        ("pep", "string", "Whether the applicant is a politically exposed person"),
        (
            "foreignTaxResident",
            "string",
            "Whether the applicant is a foreign tax resident",
        ),
    ],
    outputs=[
        ("decision", "@outputs('Evaluate_decision')"),
        (
            "responseMessage",
            "@outputs('Build_response_message')",
        ),
        ("reference", "@concat('MT-',formatDateTime(utcNow(),'yyyyMMddHHmmss'))"),
    ],
    actions={
        "Evaluate_decision": {
            "runAfter": {},
            "type": "Compose",
            "inputs": (
                "@if(or(equals(toLower(triggerBody()?['pep']),'yes'),"
                "equals(toLower(triggerBody()?['foreignTaxResident']),'yes')),"
                "'Manual Review',if(less(float(triggerBody()?['initialDeposit']),"
                "1000),'More Information Required','Eligible for Review'))"
            ),
        },
        "Build_response_message": {
            "runAfter": {"Evaluate_decision": ["Succeeded"]},
            "type": "Compose",
            "inputs": (
                "@if(equals(outputs('Evaluate_decision'),'Manual Review'),"
                "'Your onboarding enquiry requires review by a human specialist.',"
                "if(equals(outputs('Evaluate_decision'),"
                "'More Information Required'),"
                "'Please provide an initial deposit of at least SGD 1,000 for "
                "this classroom scenario.',"
                "'Your onboarding enquiry is eligible for the next review stage.'))"
            ),
        },
    },
)

LAB10_FLOW = agent_flow(
    inputs=[
        ("fullName", "string", "Customer full name"),
        ("email", "string", "Customer email address"),
        ("category", "string", "Enquiry category"),
        ("message", "string", "Customer enquiry message"),
    ],
    outputs=[
        ("category", "@outputs('Classify_category')"),
        ("priority", "@outputs('Set_priority')"),
        (
            "draftResponse",
            "@outputs('Draft_safe_response')",
        ),
        ("escalationRequired", "@outputs('Set_escalation')"),
        ("reference", "@concat('MT-',formatDateTime(utcNow(),'yyyyMMddHHmmss'))"),
    ],
    actions={
        "Classify_category": {
            "runAfter": {},
            "type": "Compose",
            "inputs": (
                "@if(contains(toLower(triggerBody()?['message']),'card'),"
                "'Cards',if(contains(toLower(triggerBody()?['message']),'fee'),"
                "'Fees','General Enquiry'))"
            ),
        },
        "Set_priority": {
            "runAfter": {"Classify_category": ["Succeeded"]},
            "type": "Compose",
            "inputs": (
                "@if(or(contains(toLower(triggerBody()?['message']),'fraud'),"
                "contains(toLower(triggerBody()?['message']),'stolen')),"
                "'Urgent','Normal')"
            ),
        },
        "Set_escalation": {
            "runAfter": {"Set_priority": ["Succeeded"]},
            "type": "Compose",
            "inputs": "@if(equals(outputs('Set_priority'),'Urgent'),'Yes','No')",
        },
        "Draft_safe_response": {
            "runAfter": {"Set_escalation": ["Succeeded"]},
            "type": "Compose",
            "inputs": (
                "@if(equals(outputs('Set_escalation'),'Yes'),"
                "concat('Thank you ',triggerBody()?['fullName'],"
                "'. A human specialist must review this urgent customer enquiry.'),"
                "concat('Thank you ',triggerBody()?['fullName'],"
                "'. We received your ',toLower(outputs('Classify_category')),"
                "' enquiry and will respond within one business day.'))"
            ),
        },
    },
)


def workflow_xml(flow_id: str, name: str, filename: str) -> str:
    return f"""    <Workflow WorkflowId="{{{flow_id}}}" Name="{name}">
      <JsonFileName>/Workflows/{filename}</JsonFileName>
      <Type>1</Type>
      <Subprocess>0</Subprocess>
      <Category>5</Category>
      <Mode>0</Mode>
      <Scope>4</Scope>
      <OnDemand>0</OnDemand>
      <TriggerOnCreate>0</TriggerOnCreate>
      <TriggerOnDelete>0</TriggerOnDelete>
      <AsyncAutodelete>0</AsyncAutodelete>
      <SyncWorkflowLogOnFailure>0</SyncWorkflowLogOnFailure>
      <StateCode>0</StateCode>
      <StatusCode>1</StatusCode>
      <RunAs>1</RunAs>
      <IsTransacted>1</IsTransacted>
      <IntroducedVersion>1.0.0.0</IntroducedVersion>
      <IsCustomizable>1</IsCustomizable>
      <BusinessProcessType>0</BusinessProcessType>
      <IsCustomProcessingStepAllowedForOtherPublishers>1</IsCustomProcessingStepAllowedForOtherPublishers>
      <PrimaryEntity>none</PrimaryEntity>
      <LocalizedNames>
        <LocalizedName languagecode="1033" description="{name}" />
      </LocalizedNames>
    </Workflow>"""


def solution_xml(
    unique_name: str,
    display_name: str,
    description: str,
    components: list[tuple[str, str]],
) -> str:
    roots = "\n".join(
        f'      <RootComponent type="29" id="{{{flow_id}}}" behavior="0" />'
        for flow_id, _ in components
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml version="9.2.0.0" SolutionPackageVersion="9.2" languagecode="1033" generatedBy="CrmLive" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SolutionManifest>
    <UniqueName>{unique_name}</UniqueName>
    <LocalizedNames>
      <LocalizedName description="{display_name}" languagecode="1033" />
    </LocalizedNames>
    <Descriptions>
      <Description description="{description}" languagecode="1033" />
    </Descriptions>
    <Version>1.0.0.3</Version>
    <Managed>0</Managed>
    <Publisher>
      <UniqueName>TertiaryInfotechTraining</UniqueName>
      <LocalizedNames>
        <LocalizedName description="Tertiary Infotech Training" languagecode="1033" />
      </LocalizedNames>
      <Descriptions>
        <Description description="Reusable training solutions for Copilot Studio and Power Automate labs." languagecode="1033" />
      </Descriptions>
      <EMailAddress xsi:nil="true"></EMailAddress>
      <SupportingWebsiteUrl xsi:nil="true"></SupportingWebsiteUrl>
      <CustomizationPrefix>tif</CustomizationPrefix>
      <CustomizationOptionValuePrefix>52846</CustomizationOptionValuePrefix>
      <Addresses />
    </Publisher>
    <RootComponents>
{roots}
    </RootComponents>
    <MissingDependencies />
  </SolutionManifest>
</ImportExportXml>
"""

def customizations_xml(
    components: list[tuple[str, str, str]],
) -> str:
    workflows = "\n".join(
        workflow_xml(flow_id, name, filename)
        for flow_id, name, filename in components
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Entities />
  <Roles />
  <Workflows>
{workflows}
  </Workflows>
  <FieldSecurityProfiles />
  <Templates />
  <EntityMaps />
  <EntityRelationships />
  <OrganizationSettings />
  <optionsets />
  <CustomControls />
  <EntityDataProviders />
  <connectionreferences />
  <Languages>
    <Language>1033</Language>
  </Languages>
</ImportExportXml>
"""

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/octet-stream" />
  <Default Extension="json" ContentType="application/octet-stream" />
</Types>
"""


def write_entry(archive: zipfile.ZipFile, name: str, content: str) -> None:
    info = zipfile.ZipInfo(name, date_time=(2026, 7, 24, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, content.encode("utf-8"))


LAB9_FILENAME = f"Lab9AssessBankingOnboardingEnquiry-{LAB9_ID.upper()}.json"
LAB10_FILENAME = f"Lab10DraftCustomerEnquiryResponse-{LAB10_ID.upper()}.json"
COMPONENTS = {
    "lab9": (
        LAB9_ID,
        "Lab 9 - Assess Banking Onboarding Enquiry",
        LAB9_FILENAME,
        LAB9_FLOW,
    ),
    "lab10": (
        LAB10_ID,
        "Lab 10 - Draft Customer Enquiry Response",
        LAB10_FILENAME,
        LAB10_FLOW,
    ),
}


def build_solution(
    output: Path,
    unique_name: str,
    display_name: str,
    description: str,
    component_keys: list[str],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    selected = [COMPONENTS[key] for key in component_keys]
    with zipfile.ZipFile(output, "w") as archive:
        write_entry(archive, "[Content_Types].xml", CONTENT_TYPES_XML)
        write_entry(
            archive,
            "solution.xml",
            solution_xml(
                unique_name,
                display_name,
                description,
                [(flow_id, name) for flow_id, name, _, _ in selected],
            ),
        )
        write_entry(
            archive,
            "customizations.xml",
            customizations_xml(
                [(flow_id, name, filename) for flow_id, name, filename, _ in selected]
            ),
        )
        for _, _, filename, flow in selected:
            write_entry(
                archive,
                f"Workflows/{filename}",
                json.dumps(flow, indent=2, ensure_ascii=False),
            )
    print(output)


def main() -> None:
    build_solution(
        OUTPUT,
        "CopilotStudioDay2FlowTemplates",
        "Copilot Studio Day 2 Flow Templates",
        "Import-ready agent-flow templates for Labs 9 and 10.",
        ["lab9", "lab10"],
    )
    build_solution(
        LAB9_OUTPUT,
        "Lab9BankingOnboardingAgentFlow",
        "Lab 9 Banking Onboarding Agent Flow",
        "Complete connector-free deterministic agent flow for Lab 9.",
        ["lab9"],
    )
    build_solution(
        LAB10_OUTPUT,
        "Lab10CustomerEnquiryPromptFlow",
        "Lab 10 Customer Enquiry Prompt Flow",
        "Runnable safe-response fallback for the Lab 10 prompt flow.",
        ["lab10"],
    )


if __name__ == "__main__":
    main()
