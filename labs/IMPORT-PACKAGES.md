# Importable Lab Packages

Portable Power Automate flows include individual `.zip` packages. Download and
extract [Power-Automate-Lab-Import-Packages.zip](Power-Automate-Lab-Import-Packages.zip)
to obtain every available package, including the Day 2 solution, or download
one package from its lab folder.
The smaller
[Day 1-only bundle](Day%201/00-Power-Automate-Lab-Import-Packages.zip) excludes
the Lab 8 website flow.

Every flow-based lab guide now offers:

1. **Part 1 — Build step by step**
2. **Part 2 — Import the packaged flow**

The individual ZIP is stored beside that lab's `index.md`.

## Import steps for Labs 1–6B and Lab 8

1. Sign in to [Power Automate](https://make.powerautomate.com) and select the
   course environment.
2. Open **My flows** → **Import** → **Import Package (Legacy)**.
3. Upload **one individual lab ZIP**. Do not upload the outer bundle.
4. For the flow row, choose **Create as new**.
5. For each connection row, choose an existing connection or create one.
6. Select **Import**, open the imported flow, complete the items in the
   **After import** column below, then **Save** and **Test**.

> Some organisations disable legacy packages and require all flows to be
> created in Dataverse solutions. If **Import Package (Legacy)** is unavailable,
> follow the lab's manual steps or ask the trainer for a solution exported from
> the same training environment.

## Package matrix

| Lab | Package | After import |
|---|---|---|
| Lab 1 | `Lab1-Send-Confirmation-Email.zip` | Reconnect Outlook; replace `YOUR_EMAIL@YOUR_TENANT` with your email |
| Lab 2 | `Lab2-Log-Enquiry-to-Excel.zip` | Reconnect Excel; reselect `Enquiry Log.xlsx` and `EnquiryTable` |
| Lab 3 | `Lab3-Scheduled-Enquiry-Reminder.zip` | Reconnect Outlook; set the recipient; check the Singapore schedule |
| Lab 4 | `Lab4-Automated-Form-to-Email-and-Excel.zip` | Reselect your Form, workbook and table; remap Full Name, Email and Your Message |
| Lab 5 | `Lab5-Human-Approval.zip` | Reconnect Approvals and Outlook; replace `YOUR_ACCOUNT@YOUR_TENANT` with a real tenant user |
| Lab 6A | `Lab6A-External-Enquiry-Webhook.zip` | Reconnect Outlook; set recipient; save once to generate the HTTP POST URL |
| Lab 6B | `Lab6B-Webhook-Chatbot.zip` | Save once to generate the HTTP POST URL; paste it into the supplied webpage |
| Lab 8 Part B | `Lab8-Marina-Trust-Website-Enquiry.zip` | Reconnect Excel and Outlook; select `Retail Banking Onboarding.xlsx` and `OnboardingTable`; save once to generate the HTTP POST URL |
| Lab 9 | `Lab9-Banking-Onboarding-Agent-Flow-Solution.zip` | Import through **Solutions**; no connector binding is required; attach the imported flow to the agent |
| Lab 10 | `Lab10-Customer-Enquiry-Prompt-Flow-Solution.zip` | Import through **Solutions**; the safe fallback runs without a connector; attach it to the agent or replace its drafting actions with your tenant's AI Builder prompt |

These packages deliberately do not contain passwords, access tokens, tenant
IDs, personal email addresses, Microsoft Form IDs, or OneDrive file IDs.

## Website assets

| Lab | Website asset | How it connects |
|---|---|---|
| Lab 6A | `assets/enquiry-form.html` | Paste the saved HTTP production URL into the page configuration |
| Lab 6B | `assets/webhook-chatbot.html` | Paste the saved HTTP production URL into the page configuration |
| Lab 8 | `website-version/` | Set `POWER_AUTOMATE_URL` in `script.js`, then serve the folder through a local web server |
| Labs 9–10 | Copilot Studio website channel | Publish the shared Marina Trust agent, copy the channel embed code and add it to the website host |

Labs without a website step do not need a web asset.

## Why Labs 9 and 10 use solution imports

Lab 8 Part B is an ordinary HTTP-triggered cloud flow, so it has a legacy import
package. Copilot Studio agents, topics, knowledge sources, prompts and
agent-bound flows in Labs 9 and 10 are Dataverse solution components. Microsoft
requires an agent-callable flow to be a **solution flow**, so those components
must be imported through **Solutions → Import solution**, not **My flows →
Import Package (Legacy)**.

Use the package inside the applicable lab folder:

- [Lab 9 Banking Onboarding Agent Flow](Day%202/Lab%209%20-%20Banking%20Onboarding%20Agent%20Flow/Lab9-Banking-Onboarding-Agent-Flow-Solution.zip)
- [Lab 10 Customer Enquiry Prompt Flow](Day%202/Lab%2010%20-%20Procurement%20Request%20Workflow/Lab10-Customer-Enquiry-Prompt-Flow-Solution.zip)

1. Open **Power Automate** → **Solutions** → **Import solution**.
2. Upload the ZIP without extracting it.
3. Select **Next** → **Import**.
4. Open the imported solution and its lab flow.
5. Save the flow, then add it to the agent as a tool.

The Lab 9 solution contains a complete connector-free deterministic decision
flow. The Lab 10 solution contains an immediately runnable connector-free safe
response fallback. Part 1 of Lab 10 shows how to replace that fallback with AI
Builder, which always requires a connection and prompt owned by the student's
environment. Each learner must also:

- ingest knowledge in their own environment;
- create or select their own agent;
- grant the agent access to their own connections and files; and
- publish to channels allowed by their tenant.

Each ZIP contains its flow component only. The learner's agent, knowledge,
connection permissions and publication channels remain environment-specific.

> **What "import-ready" means:** the flow definition is complete. Microsoft
> still requires the learner to sign in to connectors and choose tenant-owned
> Forms, workbooks, tables, prompts or recipients. Passwords, access tokens,
> tenant IDs and personal resource IDs are intentionally never embedded.

Microsoft references:

- [Create and manage Copilot Studio solutions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-overview)
- [Export and import agents using solutions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export)
- [Agent-flow requirements](https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview)

## Rebuild the packages

Course maintainers can regenerate every portable ZIP and both bundles with:

```bash
python3 scripts/build_day2_agent_flow_solution.py
python3 scripts/build_lab_flow_packages.py
python3 scripts/validate_lab_flow_packages.py
```

## Validation status

The ZIP layout, manifest JSON/XML, workflow definition JSON, connector maps,
agent trigger/response contract and placeholder scan are validated locally by
`scripts/validate_lab_flow_packages.py`. Microsoft still requires each tenant
to validate licensing, connector policy and connection permissions during
import.
