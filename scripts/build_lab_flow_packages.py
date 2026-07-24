#!/usr/bin/env python3
"""Build deterministic Power Automate legacy import packages for course labs.

These packages are teaching templates. Connector connections and tenant-owned
resources (Forms, Excel workbooks/tables, users) must be selected after import.

Run this file whenever a packaged flow definition changes:

    python3 scripts/build_lab_flow_packages.py
"""

from __future__ import annotations

import json
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"
CREATED_TIME = "2026-07-24T00:00:00Z"
NAMESPACE = uuid.UUID("6ac4359e-993e-4cf7-b91d-c934a4f82ca2")


CONNECTORS = {
    "shared_office365": {
        "display": "Office 365 Outlook",
        "icon": "https://connectoricons-prod.azureedge.net/releases/v1.0.1664/1.0.1664.3477/office365/icon.png",
    },
    "shared_excelonlinebusiness": {
        "display": "Excel Online (Business)",
        "icon": "https://connectoricons-prod.azureedge.net/releases/v1.0.1664/1.0.1664.3477/excelonlinebusiness/icon.png",
    },
    "shared_approvals": {
        "display": "Approvals",
        "icon": "https://connectoricons-prod.azureedge.net/releases/v1.0.1664/1.0.1664.3477/approvals/icon.png",
    },
    "shared_microsoftforms": {
        "display": "Microsoft Forms",
        "icon": "https://connectoricons-prod.azureedge.net/releases/v1.0.1664/1.0.1664.3477/microsoftforms/icon.png",
    },
}


def stable_uuid(label: str) -> str:
    return str(uuid.uuid5(NAMESPACE, label))


def request_button(properties: dict[str, dict], required: list[str]) -> dict:
    return {
        "manual": {
            "type": "Request",
            "kind": "Button",
            "inputs": {
                "schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            },
        }
    }


def text_input(title: str, description: str) -> dict:
    return {
        "title": title,
        "type": "string",
        "x-ms-dynamically-added": True,
        "description": description,
        "x-ms-content-hint": "TEXT",
    }


def openapi_action(
    connector: str,
    operation: str,
    parameters: dict,
    run_after: dict,
) -> dict:
    return {
        "runAfter": run_after,
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": connector,
                "operationId": operation,
                "apiId": f"/providers/Microsoft.PowerApps/apis/{connector}",
            },
            "parameters": parameters,
            "authentication": "@parameters('$authentication')",
        },
    }


def office_email(to: str, subject: str, body: str, run_after: dict) -> dict:
    return openapi_action(
        "shared_office365",
        "SendEmailV2",
        {
            "emailMessage/To": to,
            "emailMessage/Subject": subject,
            "emailMessage/Body": body,
            "emailMessage/Importance": "Normal",
        },
        run_after,
    )


def workflow(display_name: str, triggers: dict, actions: dict, connectors: list[str]) -> dict:
    parameters = {
        "$authentication": {"defaultValue": {}, "type": "SecureObject"},
    }
    if connectors:
        parameters["$connections"] = {"defaultValue": {}, "type": "Object"}

    connection_references = {
        connector: {
            "connectionName": connector.replace("_", "-"),
            "source": "Invoker",
            "id": f"/providers/Microsoft.PowerApps/apis/{connector}",
            "tier": "NotSpecified",
        }
        for connector in connectors
    }
    flow_id = stable_uuid(display_name)
    return {
        "name": flow_id,
        "id": f"/providers/Microsoft.Flow/flows/{flow_id}",
        "type": "Microsoft.Flow/flows",
        "properties": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_logicflows",
            "displayName": display_name,
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": parameters,
                "triggers": triggers,
                "actions": actions,
                "outputs": {},
            },
            "connectionReferences": connection_references,
            "flowFailureAlertSubscribed": False,
            "isManaged": False,
        },
    }


def lab_specs() -> list[dict]:
    lab1 = workflow(
        "Lab 1 - Send Confirmation Email",
        request_button(
            {"text": text_input("CustomerName", "Please enter the customer name")},
            ["text"],
        ),
        {
            "Send_an_email_(V2)": office_email(
                "YOUR_EMAIL@YOUR_TENANT",
                "Thank you for your enquiry",
                "<p>Hi @{triggerBody()?['text']}, thank you for contacting ACME Customer "
                "Operations. Your enquiry has been logged and a service officer will respond "
                "within 1 business day.</p>",
                {},
            )
        },
        ["shared_office365"],
    )

    lab2 = workflow(
        "Lab 2 - Log Enquiry to Excel",
        request_button(
            {
                "name": text_input("Name", "Customer name"),
                "email": text_input("Email", "Customer email"),
                "message": text_input("Message", "Customer enquiry"),
            },
            ["name", "email", "message"],
        ),
        {
            "Add_a_row_into_a_table": openapi_action(
                "shared_excelonlinebusiness",
                "AddRowV2",
                {
                    "source": "me",
                    "drive": "SELECT_AFTER_IMPORT",
                    "file": "SELECT_AFTER_IMPORT",
                    "table": "EnquiryTable",
                    "item/Date": "@formatDateTime(utcNow(),'yyyy-MM-dd HH:mm')",
                    "item/Name": "@triggerBody()?['name']",
                    "item/Email": "@triggerBody()?['email']",
                    "item/Message": "@triggerBody()?['message']",
                    "item/Status": "New",
                },
                {},
            )
        },
        ["shared_excelonlinebusiness"],
    )

    approval = openapi_action(
        "shared_approvals",
        "StartAndWaitForAnApproval",
        {
            "approvalType": "Basic",
            "ApprovalCreationInput/title": "Approval needed: @{triggerBody()?['requestDetails']}",
            "ApprovalCreationInput/assignedTo": "YOUR_ACCOUNT@YOUR_TENANT",
            "ApprovalCreationInput/details": "Requester: @{triggerBody()?['requesterName']}<br>"
            "Email: @{triggerBody()?['requesterEmail']}<br>"
            "Request: @{triggerBody()?['requestDetails']}",
            "ApprovalCreationInput/enableNotifications": True,
            "ApprovalCreationInput/enableReassignment": True,
        },
        {},
    )
    lab3 = workflow(
        "Lab 5 - Human Approval",
        request_button(
            {
                "requesterName": text_input("RequesterName", "Requester name"),
                "requesterEmail": text_input("RequesterEmail", "Requester email"),
                "requestDetails": text_input("RequestDetails", "Request details"),
            },
            ["requesterName", "requesterEmail", "requestDetails"],
        ),
        {
            "Start_and_wait_for_an_approval": approval,
            "Condition": {
                "runAfter": {"Start_and_wait_for_an_approval": ["Succeeded"]},
                "type": "If",
                "expression": {
                    "and": [
                        {
                            "equals": [
                                "@outputs('Start_and_wait_for_an_approval')?['body/outcome']",
                                "Approve",
                            ]
                        }
                    ]
                },
                "actions": {
                    "Send_approval_email": office_email(
                        "@triggerBody()?['requesterEmail']",
                        "Your request was approved",
                        "<p>Hi @{triggerBody()?['requesterName']}, your request was approved.</p>",
                        {},
                    )
                },
                "else": {
                    "actions": {
                        "Send_rejection_email": office_email(
                            "@triggerBody()?['requesterEmail']",
                            "Your request was not approved",
                            "<p>Hi @{triggerBody()?['requesterName']}, your request was not approved.</p>",
                            {},
                        )
                    }
                },
            },
        },
        ["shared_approvals", "shared_office365"],
    )

    lab4 = workflow(
        "Lab 3 - Scheduled Enquiry Reminder",
        {
            "Recurrence": {
                "type": "Recurrence",
                "recurrence": {
                    "frequency": "Week",
                    "interval": 1,
                    "timeZone": "Singapore Standard Time",
                    "schedule": {
                        "weekDays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                        "hours": [9],
                        "minutes": [0],
                    },
                },
            }
        },
        {
            "Send_an_email_(V2)": office_email(
                "YOUR_EMAIL@YOUR_TENANT",
                "Daily reminder: review new enquiries",
                "<p>Good morning. Please review and follow up on all new customer enquiries.</p>",
                {},
            )
        },
        ["shared_office365"],
    )

    lab5 = workflow(
        "Lab 4 - Automated Form to Email and Excel",
        {
            "When_a_new_response_is_submitted": {
                "type": "OpenApiConnectionWebhook",
                "inputs": {
                    "host": {
                        "connectionName": "shared_microsoftforms",
                        "operationId": "CreateFormWebhook",
                        "apiId": "/providers/Microsoft.PowerApps/apis/shared_microsoftforms",
                    },
                    "parameters": {"form_id": "SELECT_YOUR_FORM_AFTER_IMPORT"},
                    "authentication": "@parameters('$authentication')",
                },
            }
        },
        {
            "Get_response_details": openapi_action(
                "shared_microsoftforms",
                "GetFormResponseById",
                {
                    "form_id": "SELECT_YOUR_FORM_AFTER_IMPORT",
                    "response_id": "@triggerBody()?['resourceData/responseId']",
                },
                {},
            ),
            "Send_an_email_(V2)": office_email(
                "YOUR_EMAIL@YOUR_TENANT",
                "New customer enquiry received",
                "<p>A new enquiry was submitted. After import, replace this body with the "
                "Full Name, Email and Your Message dynamic values from Get response details.</p>"
                "<pre>@{string(body('Get_response_details'))}</pre>",
                {"Get_response_details": ["Succeeded"]},
            ),
            "Add_a_row_into_a_table": openapi_action(
                "shared_excelonlinebusiness",
                "AddRowV2",
                {
                    "source": "me",
                    "drive": "SELECT_AFTER_IMPORT",
                    "file": "SELECT_AFTER_IMPORT",
                    "table": "EnquiryTable",
                    "item/Date": "@formatDateTime(utcNow(),'yyyy-MM-dd HH:mm')",
                    "item/Name": "MAP_FULL_NAME_AFTER_IMPORT",
                    "item/Email": "MAP_EMAIL_AFTER_IMPORT",
                    "item/Message": "MAP_YOUR_MESSAGE_AFTER_IMPORT",
                    "item/Status": "New",
                },
                {"Send_an_email_(V2)": ["Succeeded"]},
            ),
        },
        ["shared_microsoftforms", "shared_office365", "shared_excelonlinebusiness"],
    )

    enquiry_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "subject": {"type": "string"},
            "message": {"type": "string"},
        },
        "required": ["name", "email", "subject", "message"],
    }
    lab6a = workflow(
        "Lab 6A - External Enquiry Webhook",
        {
            "manual": {
                "type": "Request",
                "kind": "Http",
                "inputs": {"schema": {"type": "string"}},
            }
        },
        {
            "Parse_JSON": {
                "type": "ParseJson",
                "inputs": {"content": "@json(triggerBody())", "schema": enquiry_schema},
                "runAfter": {},
            },
            "Send_an_email_(V2)": office_email(
                "YOUR_EMAIL@YOUR_TENANT",
                "Business banking enquiry: @{body('Parse_JSON')?['subject']}",
                "<p><strong>Name:</strong> @{body('Parse_JSON')?['name']}<br>"
                "<strong>Email:</strong> @{body('Parse_JSON')?['email']}<br>"
                "<strong>Message:</strong> @{body('Parse_JSON')?['message']}</p>",
                {"Parse_JSON": ["Succeeded"]},
            ),
            "Response": {
                "type": "Response",
                "kind": "Http",
                "inputs": {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": {
                        "success": True,
                        "message": "Thank you. Your enquiry was submitted successfully.",
                    },
                },
                "runAfter": {"Send_an_email_(V2)": ["Succeeded"]},
            },
        },
        ["shared_office365"],
    )

    chat_schema = {
        "type": "object",
        "properties": {
            "sessionId": {"type": "string"},
            "message": {"type": "string"},
        },
        "required": ["sessionId", "message"],
    }
    lab6b = workflow(
        "Lab 6B - Webhook Chatbot",
        {
            "manual": {
                "type": "Request",
                "kind": "Http",
                "inputs": {"schema": {"type": "string"}},
            }
        },
        {
            "Parse_JSON": {
                "type": "ParseJson",
                "inputs": {"content": "@json(triggerBody())", "schema": chat_schema},
                "runAfter": {},
            },
            "Initialise_botReply": {
                "type": "InitializeVariable",
                "inputs": {
                    "variables": [
                        {
                            "name": "botReply",
                            "type": "string",
                            "value": "I can help with opening hours, contact details, or "
                            "account-opening documents. For anything else, please contact "
                            "Customer Operations.",
                        }
                    ]
                },
                "runAfter": {"Parse_JSON": ["Succeeded"]},
            },
            "Normalise_message": {
                "type": "Compose",
                "inputs": "@toLower(trim(body('Parse_JSON')?['message']))",
                "runAfter": {"Initialise_botReply": ["Succeeded"]},
            },
            "Route_message": {
                "type": "Switch",
                "expression": "@outputs('Normalise_message')",
                "runAfter": {"Normalise_message": ["Succeeded"]},
                "cases": {
                    "Opening_hours": {
                        "case": "opening hours",
                        "actions": {
                            "Set_opening_hours_reply": {
                                "type": "SetVariable",
                                "inputs": {
                                    "name": "botReply",
                                    "value": "We are open Monday to Friday, 9:00 AM to 6:00 PM.",
                                },
                            }
                        },
                    },
                    "Contact_details": {
                        "case": "contact details",
                        "actions": {
                            "Set_contact_reply": {
                                "type": "SetVariable",
                                "inputs": {
                                    "name": "botReply",
                                    "value": "Email help@acme.example or call +65 6000 0000.",
                                },
                            }
                        },
                    },
                    "Documents": {
                        "case": "documents",
                        "actions": {
                            "Set_documents_reply": {
                                "type": "SetVariable",
                                "inputs": {
                                    "name": "botReply",
                                    "value": "For an SME current-account enquiry, prepare the "
                                    "company registration profile, authorised signatory "
                                    "identification and proof of business address. A service "
                                    "officer will confirm the final checklist.",
                                },
                            }
                        },
                    },
                },
                "default": {"actions": {}},
            },
            "Response": {
                "type": "Response",
                "kind": "Http",
                "inputs": {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": {"reply": "@{variables('botReply')}"},
                },
                "runAfter": {"Route_message": ["Succeeded"]},
            },
        },
        [],
    )

    onboarding_schema = json.loads(
        (
            LABS
            / "Day 2"
            / "Lab 8 - Deploy Agent to Teams and Website"
            / "website-version"
            / "request-schema.json"
        ).read_text(encoding="utf-8")
    )
    minimum_deposit = (
        "@if(equals(body('Parse_JSON')?['accountType'],'Savings'),500,"
        "if(equals(body('Parse_JSON')?['accountType'],'Joint Savings'),1000,"
        "if(equals(body('Parse_JSON')?['accountType'],'Student Account'),0,"
        "if(equals(body('Parse_JSON')?['accountType'],'Current'),3000,"
        "if(equals(body('Parse_JSON')?['accountType'],'Fixed Deposit'),10000,5000)))))"
    )
    decision = (
        "@if(equals(body('Parse_JSON')?['nric'],'S8412345D'),'DUPLICATE',"
        "if(greater(ticks(addToTime(body('Parse_JSON')?['dateOfBirth'],18,'Year')),"
        "ticks(utcNow())),'REJECTED',"
        "if(equals(body('Parse_JSON')?['pep'],'Yes'),'REVIEW',"
        "if(equals(body('Parse_JSON')?['foreignTaxResident'],'Yes'),'REVIEW',"
        "if(less(float(body('Parse_JSON')?['initialDeposit']),"
        "float(outputs('Minimum_Deposit'))),'REJECTED',"
        "if(and(equals(body('Parse_JSON')?['accountType'],'Current'),"
        "equals(body('Parse_JSON')?['employmentStatus'],'Unemployed')),'REJECTED',"
        "if(and(equals(body('Parse_JSON')?['accountType'],'Fixed Deposit'),"
        "less(float(body('Parse_JSON')?['annualIncome']),30000)),'REJECTED',"
        "'APPROVED')))))))"
    )
    reason = (
        "@if(equals(body('Parse_JSON')?['nric'],'S8412345D'),"
        "'A fictitious existing customer record uses this test identity.',"
        "if(greater(ticks(addToTime(body('Parse_JSON')?['dateOfBirth'],18,'Year')),"
        "ticks(utcNow())),'The applicant must be at least 18.',"
        "if(equals(body('Parse_JSON')?['pep'],'Yes'),"
        "'Enhanced due diligence is required.',"
        "if(equals(body('Parse_JSON')?['foreignTaxResident'],'Yes'),"
        "'Tax-residency review is required.',"
        "if(less(float(body('Parse_JSON')?['initialDeposit']),"
        "float(outputs('Minimum_Deposit'))),'The minimum deposit was not met.',"
        "if(and(equals(body('Parse_JSON')?['accountType'],'Current'),"
        "equals(body('Parse_JSON')?['employmentStatus'],'Unemployed')),"
        "'The employment criterion was not met.',"
        "if(and(equals(body('Parse_JSON')?['accountType'],'Fixed Deposit'),"
        "less(float(body('Parse_JSON')?['annualIncome']),30000)),"
        "'The income criterion was not met.',"
        "'The application meets the selected account criteria.')))))))"
    )
    risk_flags = (
        "@if(greater(ticks(addToTime(body('Parse_JSON')?['dateOfBirth'],18,'Year')),"
        "ticks(utcNow())),'MINOR',"
        "if(equals(body('Parse_JSON')?['pep'],'Yes'),'PEP',"
        "if(equals(body('Parse_JSON')?['foreignTaxResident'],'Yes'),"
        "'CRS_FATCA','')))"
    )
    lab8 = workflow(
        "Lab 8 - Marina Trust Website Enquiry",
        {
            "manual": {
                "type": "Request",
                "kind": "Http",
                "inputs": {"schema": {"type": "string"}},
            }
        },
        {
            "Parse_JSON": {
                "type": "ParseJson",
                "inputs": {
                    "content": "@json(triggerBody())",
                    "schema": onboarding_schema,
                },
                "runAfter": {},
            },
            "Application_ID": {
                "type": "Compose",
                "inputs": "@concat('APP-',formatDateTime(utcNow(),'yyyyMMdd-HHmmss'))",
                "runAfter": {"Parse_JSON": ["Succeeded"]},
            },
            "Minimum_Deposit": {
                "type": "Compose",
                "inputs": minimum_deposit,
                "runAfter": {"Application_ID": ["Succeeded"]},
            },
            "Decision": {
                "type": "Compose",
                "inputs": decision,
                "runAfter": {"Minimum_Deposit": ["Succeeded"]},
            },
            "Reason": {
                "type": "Compose",
                "inputs": reason,
                "runAfter": {"Decision": ["Succeeded"]},
            },
            "Risk_Flags": {
                "type": "Compose",
                "inputs": risk_flags,
                "runAfter": {"Reason": ["Succeeded"]},
            },
            "Add_a_row_into_a_table": openapi_action(
                "shared_excelonlinebusiness",
                "AddRowV2",
                {
                    "source": "me",
                    "drive": "SELECT_AFTER_IMPORT",
                    "file": "SELECT_AFTER_IMPORT",
                    "table": "OnboardingTable",
                    "item/ApplicationId": "@outputs('Application_ID')",
                    "item/SubmittedAt": "@utcNow()",
                    "item/FullName": "@body('Parse_JSON')?['fullName']",
                    "item/NRIC": "@body('Parse_JSON')?['nric']",
                    "item/Email": "@body('Parse_JSON')?['email']",
                    "item/AccountType": "@body('Parse_JSON')?['accountType']",
                    "item/Decision": "@outputs('Decision')",
                    "item/Reason": "@outputs('Reason')",
                    "item/RiskFlags": "@outputs('Risk_Flags')",
                },
                {"Risk_Flags": ["Succeeded"]},
            ),
            "Send_an_email_(V2)": office_email(
                "@body('Parse_JSON')?['email']",
                "Marina Trust onboarding enquiry @{outputs('Application_ID')}",
                "<p>Hello @{body('Parse_JSON')?['fullName']},</p>"
                "<p>Reference: @{outputs('Application_ID')}<br>"
                "Account type: @{body('Parse_JSON')?['accountType']}<br>"
                "Decision: @{outputs('Decision')}<br>"
                "Reason: @{outputs('Reason')}</p>"
                "<p>This controlled pilot uses fictitious data and does not open a real account.</p>",
                {"Add_a_row_into_a_table": ["Succeeded"]},
            ),
            "Response": {
                "type": "Response",
                "kind": "Http",
                "inputs": {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": {
                        "applicationId": "@{outputs('Application_ID')}",
                        "decision": "@{outputs('Decision')}",
                        "reason": "@{outputs('Reason')}",
                        "riskFlags": "@{if(empty(outputs('Risk_Flags')),json('[]'),createArray(outputs('Risk_Flags')))}",
                        "emailSent": True,
                    },
                },
                "runAfter": {"Send_an_email_(V2)": ["Succeeded"]},
            },
        },
        ["shared_excelonlinebusiness", "shared_office365"],
    )

    return [
        {
            "folder": "Day 1/Lab 1 - Instant Email Flow",
            "filename": "Lab1-Send-Confirmation-Email.zip",
            "description": "Manual trigger and confirmation email.",
            "connectors": ["shared_office365"],
            "flow": lab1,
        },
        {
            "folder": "Day 1/Lab 2 - Instant Excel Logging Flow",
            "filename": "Lab2-Log-Enquiry-to-Excel.zip",
            "description": "Manual enquiry input and Excel table logging.",
            "connectors": ["shared_excelonlinebusiness"],
            "flow": lab2,
        },
        {
            "folder": "Day 1/Lab 3 - Scheduled Flow",
            "filename": "Lab3-Scheduled-Enquiry-Reminder.zip",
            "description": "Weekday recurrence and reminder email.",
            "connectors": ["shared_office365"],
            "flow": lab4,
        },
        {
            "folder": "Day 1/Lab 4 - Automated Form Flow",
            "filename": "Lab4-Automated-Form-to-Email-and-Excel.zip",
            "description": "Microsoft Forms trigger, details, email and Excel logging scaffold.",
            "connectors": [
                "shared_microsoftforms",
                "shared_office365",
                "shared_excelonlinebusiness",
            ],
            "flow": lab5,
        },
        {
            "folder": "Day 1/Lab 5 - Human Approval Flow",
            "filename": "Lab5-Human-Approval.zip",
            "description": "Approval request with approved and rejected email branches.",
            "connectors": ["shared_approvals", "shared_office365"],
            "flow": lab3,
        },
        {
            "folder": "Day 1/Lab 6A - External Enquiry Webhook",
            "filename": "Lab6A-External-Enquiry-Webhook.zip",
            "description": "Inbound HTTP request, JSON parsing, email and JSON response.",
            "connectors": ["shared_office365"],
            "flow": lab6a,
        },
        {
            "folder": "Day 1/Lab 6B - Webhook Chatbot",
            "filename": "Lab6B-Webhook-Chatbot.zip",
            "description": "Inbound HTTP chatbot with deterministic routing and JSON response.",
            "connectors": [],
            "flow": lab6b,
        },
        {
            "folder": "Day 2/Lab 8 - Deploy Agent to Teams and Website",
            "filename": "Lab8-Marina-Trust-Website-Enquiry.zip",
            "description": (
                "Website HTTP request, deterministic onboarding rules, Excel logging, "
                "confirmation email and JSON response."
            ),
            "connectors": ["shared_excelonlinebusiness", "shared_office365"],
            "flow": lab8,
        },
    ]


def package_manifest(spec: dict) -> tuple[dict, dict, dict]:
    flow = spec["flow"]
    flow_id = flow["name"]
    resources = {}
    dependencies = []
    apis_map = {}
    connections_map = {}

    for connector in spec["connectors"]:
        api_uuid = stable_uuid(f"{flow_id}:{connector}:api")
        connection_uuid = stable_uuid(f"{flow_id}:{connector}:connection")
        connection_name = connector.replace("_", "-")
        meta = CONNECTORS[connector]
        dependencies.extend([api_uuid, connection_uuid])
        apis_map[connector] = api_uuid
        connections_map[connector] = connection_uuid
        resources[api_uuid] = {
            "id": f"/providers/Microsoft.PowerApps/apis/{connector}",
            "name": connector,
            "type": "Microsoft.PowerApps/apis",
            "suggestedCreationType": "Existing",
            "creationType": "Existing",
            "details": {"displayName": meta["display"], "iconUri": meta["icon"]},
            "configurableBy": "System",
            "hierarchy": "Child",
            "dependsOn": [],
        }
        resources[connection_uuid] = {
            "id": f"/providers/Microsoft.PowerApps/apis/{connector}/connections/{connection_name}",
            "name": connection_name,
            "type": "Microsoft.PowerApps/apis/connections",
            "suggestedCreationType": "Existing",
            "creationType": "Existing",
            "details": {"displayName": meta["display"], "iconUri": meta["icon"]},
            "configurableBy": "User",
            "hierarchy": "Child",
            "dependsOn": [api_uuid],
        }

    resources[flow_id] = {
        "id": f"/providers/Microsoft.Flow/flows/{flow_id}",
        "name": flow_id,
        "type": "Microsoft.Flow/flows",
        "suggestedCreationType": "New",
        "creationType": "Existing, New, Update",
        "details": {"displayName": flow["properties"]["displayName"]},
        "configurableBy": "User",
        "hierarchy": "Root",
        "dependsOn": dependencies,
    }
    manifest = {
        "schema": "1.0",
        "details": {
            "displayName": flow["properties"]["displayName"],
            "description": (
                f"{spec['description']} Teaching package: reconnect connections and "
                "select tenant-owned resources after import."
            ),
            "createdTime": CREATED_TIME,
            "packageTelemetryId": stable_uuid(f"{flow_id}:telemetry"),
            "creator": "Tertiary Infotech Academy",
            "sourceEnvironment": "",
        },
        "resources": resources,
    }
    return manifest, apis_map, connections_map


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_package(spec: dict) -> Path:
    destination = LABS / spec["folder"] / spec["filename"]
    manifest, apis_map, connections_map = package_manifest(spec)
    flow_id = spec["flow"]["name"]

    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        flow_folder = temp / "Microsoft.Flow" / "flows" / flow_id
        flow_folder.mkdir(parents=True)
        write_json(temp / "manifest.json", manifest)
        write_json(flow_folder / "definition.json", spec["flow"])
        write_json(flow_folder / "apisMap.json", apis_map)
        write_json(flow_folder / "connectionsMap.json", connections_map)

        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(temp.rglob("*")):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(temp).as_posix())
                    info.date_time = (2026, 7, 24, 0, 0, 0)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, path.read_bytes())
    return destination


def write_bundle(bundle: Path, packages: list[Path]) -> Path:
    guide = LABS / "IMPORT-PACKAGES.md"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("README.md")
        info.date_time = (2026, 7, 24, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, guide.read_bytes())
        for package in packages:
            info = zipfile.ZipInfo(package.name)
            info.date_time = (2026, 7, 24, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, package.read_bytes())
    return bundle


def build_bundles(packages: list[Path]) -> list[Path]:
    day1_packages = [
        package for package in packages if (LABS / "Day 1") in package.parents
    ]
    day2_solutions = [
        LABS
        / "Day 2"
        / "Lab 9 - Banking Onboarding Agent Flow"
        / "Lab9-Banking-Onboarding-Agent-Flow-Solution.zip",
        LABS
        / "Day 2"
        / "Lab 10 - Procurement Request Workflow"
        / "Lab10-Customer-Enquiry-Prompt-Flow-Solution.zip",
    ]
    all_packages = [*packages]
    all_packages.extend(
        solution for solution in day2_solutions if solution.exists()
    )
    return [
        write_bundle(
            LABS / "Day 1" / "00-Power-Automate-Lab-Import-Packages.zip",
            day1_packages,
        ),
        write_bundle(
            LABS / "Power-Automate-Lab-Import-Packages.zip",
            all_packages,
        ),
    ]


def main() -> None:
    packages = [build_package(spec) for spec in lab_specs()]
    bundles = build_bundles(packages)
    for package in packages:
        print(package.relative_to(ROOT))
    for bundle in bundles:
        print(bundle.relative_to(ROOT))


if __name__ == "__main__":
    main()
