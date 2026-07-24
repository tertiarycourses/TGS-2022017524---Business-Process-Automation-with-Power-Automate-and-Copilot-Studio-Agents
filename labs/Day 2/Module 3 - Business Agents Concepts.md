# Module 3: Building Business Agents with Copilot Studio

> **Read this before the Day 2 labs.** ~15 minutes.

On Day 1 you built the **hands** — Power Automate flows that send email, log to Excel, and run approvals. Today you build the **brain and mouth**: a Copilot Studio **agent** that talks to people in plain language and hands clean, structured data to those flows.

By the end of this reading you'll know what an agent is made of, how to make it produce *predictable* data (the make-or-break skill), and how an agent calls a flow as a tool.

---

## 1. What is a business agent?

A **business agent** is an AI assistant you build in **Copilot Studio**. People chat with it in natural language ("I'd like a quote for 100 units"), and the agent:

- **Understands** the request
- **Asks** for any missing details
- **Captures** the information as clean, structured data
- **Hands off** that data to a Power Automate flow to take action

```
   Day 1                          Day 2
 ┌────────┐                    ┌──────────┐
 │ FLOWS  │  the "hands"       │  AGENT   │  the "brain & mouth"
 │ do work│  ◄───── calls ──── │ talks &  │
 └────────┘                    │ captures │
                               └──────────┘
```

The agent is the friendly front door; the flow is the engine room behind it.

---

## 2. The building blocks of a Copilot Studio agent

An agent is assembled from five kinds of building block. You'll meet each one across today's labs.

| Block | What it is | Example | First seen |
|-------|------------|---------|-----------|
| **Instructions** | Plain-language directions that shape the agent's behaviour and personality | "You are an IT support assistant. Use approved guidance and escalate safely." | Lab 7A |
| **Knowledge** | Documents / sites the agent can answer from (RAG) | IT support FAQ | Lab 7B |
| **Topics** | Explicit conversation flows used by classic agents; the new experience instead relies on enhanced orchestration, Skills and Tools | A classic "Banking onboarding enquiry" topic that collects a structured request | Lab 9 (classic path) |
| **Tools** (formerly *Actions*) | Things an agent can invoke, including **Power Automate agent flows** and prompt-based flows | "Assess onboarding enquiry" / "Draft customer enquiry response" | Labs 9–10 |
| **Variables / tool inputs** | Named values captured explicitly in classic Topics or inferred from confirmed context in the new experience | `fullName`, `category`, `message` | Lab 9 |

> **Knowledge = RAG.** When you upload documents, the agent uses **Retrieval-Augmented Generation**: it *retrieves* the relevant passages from your files and *generates* an answer grounded in them — so it speaks from your content, not the open internet. You'll set this up in Lab 7B.

---

## 3. Prompt design for structured outputs

This is the single most important skill for connecting agents to workflows: getting the agent to produce **structured, predictable data** — not just free-flowing chat.

**Why it matters.** A flow needs clean, named fields. Compare what the agent might hand over:

| The agent hands the flow… | Can the flow use it? |
|---------------------------|----------------------|
| `"the guy from ABC wants some units maybe 100"` | ❌ No — nothing to log reliably |
| `name=John, company=ABC, product=Widget, quantity=100` | ✅ Yes — every field drops straight into a row |

When the data is clean and structured, **every downstream step just works**. When it's messy, the whole workflow is unreliable.

### Three techniques to get structured output

1. **Capture into named variables.** Use question nodes that store each answer in its own variable (`customerName`, `email`, `quantity`). This is the most reliable method, and you'll use it in **Labs 9 and 10**.

2. **Write precise instructions.** Tell the agent exactly what to collect and in what form:
   > *"Collect these four items one at a time: customer name, company, product of interest, and quantity. Do not proceed until all four are provided. Confirm the details back to the user before finishing."*

3. **Ask AI to format the result.** When you want a generated summary, specify the format explicitly:
   > *"Summarize the enquiry as: Customer: &lt;name&gt;; Company: &lt;company&gt;; Product: &lt;product&gt;; Qty: &lt;quantity&gt;; Notes: &lt;notes&gt;."*

### Good-prompt checklist

- ✅ State the agent's **role and goal**
- ✅ List the **exact fields** to collect
- ✅ Specify the **output format**
- ✅ Say **what to do when information is missing**
- ✅ Keep **tone** instructions short and clear

> **Structured agent output = clean flow inputs.** This is the through-line of Day 2. If the agent captures tidy variables, the flow receives tidy inputs — and the handoff in section 4 works first time.

---

## 4. Connecting agents to Power Automate flows

Once the agent has captured the data, it calls a flow as a **tool**:

```
USER chats with AGENT  →  AGENT captures variables  →  AGENT calls FLOW (tool)
                                                          passing variables as inputs
                                                              │
                                                              ▼
                                            FLOW runs actions (log, email, approve)
                                                              │
                                                              ▼
                                            FLOW returns a result  →  AGENT confirms to user
```

The key points:

- The agent **passes its variables** (outputs) into the flow's **inputs**.
- The flow does the work and can **return a value** — say, a reference number — for the agent to show the user.
- This is exactly the same flow-building you learned on Day 1. **Only the trigger changes** — to *"When an agent calls the flow."*

> **It's still Day-1 Power Automate underneath.** Same designer, same actions, same Save → Test → run-history loop. The agent simply replaces the manual "Run" button as the thing that starts the flow.

---

## 5. Power Automate versus n8n AI Agent

Power Automate by itself is similar to a normal n8n automation: a trigger starts
fixed actions, conditions and connectors. To obtain the n8n **AI Agent**
pattern, Copilot Studio becomes the conversational orchestrator and the Power
Automate flow becomes one of its tools.

| n8n concept | Microsoft equivalent |
|---|---|
| Chat Trigger or Webhook | Copilot Studio Teams/website channel, or Power Automate HTTP Request |
| AI Agent node | Copilot Studio agent |
| System prompt | Agent Instructions |
| Vector store / RAG tool | Copilot Studio Knowledge |
| Workflow tool | Power Automate agent flow |
| Tool input schema | Inputs on **When an agent calls the flow** |
| Tool result | Outputs on **Respond to the agent** |
| LLM prompt node | AI Builder **Run a prompt** inside an agent flow |

Do not try to place the whole Copilot Studio agent inside an ordinary
Power Automate action. Use this direction instead:

```text
User → Copilot Studio agent → Power Automate agent flow (tool)
                              ├── Outlook / Excel / approvals / APIs
                              ├── optional AI Builder prompt
                              └── Respond to the agent → answer in chat
```

### Add a Power Automate agent flow to Copilot Studio

1. Ensure Power Automate and Copilot Studio use the same environment.
2. In Copilot Studio, open the agent and select
   **Tools → Add a tool → New tool → Agent flow**.
3. Build the flow with **When an agent calls the flow**.
4. Add named inputs for the values the agent must supply.
5. Add the required Power Automate actions.
6. Finish with **Respond to the agent** and add named outputs.
7. Save the flow and return to the agent.
8. Give the tool a clear name and description so the agent knows when to call
   it.
9. Map each tool input from confirmed conversation context or classic Topic
   variables.
10. Save, publish and test first in Preview, then in Teams or the website
    channel.

### Import an agent-flow solution

Labs 9 and 10 include solution ZIPs because agent-callable flows are solution
components.

1. In Power Automate, choose **Solutions → Import solution**.
2. Upload the lab-specific ZIP without extracting it.
3. Select **Next → Import**.
4. Open the imported solution and its flow.
5. Save the flow.
6. In Copilot Studio, add the imported flow under **Tools**.
7. Map the inputs, save, publish and test.

The Lab 9 package is connector-free and immediately testable. The Lab 10
package has a connector-free safe fallback; using AI Builder still requires
the learner to select a prompt and connection owned by their environment.

---

## 6. What you'll build on Day 2

Day 2 is organised as two connected projects. Each lab adds one capability and
reuses the artifact created previously.

### Project A — MyCompany IT Support

| Lab | Build | New capability |
|---|---|---|
| **7A** | Prompt-create `MyCompany IT Support Assistant` | Identity, Instructions, safety boundaries and Preview/Test |
| **7B** | Upgrade the same agent | Approved FAQ Knowledge, RAG, citations, evaluation and publishing |

### Project B — Marina Trust Omnichannel Enquiries

| Lab | Build | New capability |
|---|---|---|
| **8** | Prompt-create `Marina Trust Enquiry Agent`; publish to Teams; connect the supplied standalone website form to Power Automate | Channels plus an ordinary HTTP-triggered flow with no agent in the website path |
| **9** | Upgrade the same Marina Trust agent in Teams and website chat | Structured capture and a deterministic agent flow |
| **10** | Upgrade the same Marina Trust agent again | Guarded AI prompt flow with structured output and escalation |

The progression is deliberate:

```text
Lab 7A: Instructions
   ↓
Lab 7B: Instructions + Knowledge + Evaluation
   ↓
Lab 8: Publish agent to Teams + website integration
   ↓
Lab 9: Same agent + deterministic tool
   ↓
Lab 10: Same agent + AI prompt tool
```

By Lab 10 you will be able to distinguish an informational agent, an ordinary
Power Automate flow, a deterministic agent flow and an AI prompt flow.

---

**Next:** [Lab 7A: Create the IT Support Agent](Lab%207A%20-%20Create%20IT%20Support%20Agent/index.md)
