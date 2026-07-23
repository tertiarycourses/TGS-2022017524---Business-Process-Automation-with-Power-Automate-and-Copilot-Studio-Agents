# Lab 6: Create Your First Copilot Studio Agent

## Lab Title
IT Support RAG Part A — Build the Agent and Ingest the FAQ

## Lab Objectives
By the end of this lab, you will be able to:
1. Create a new **blank agent** in Microsoft Copilot Studio and configure it yourself
2. Write clear **Instructions** that shape how your agent behaves
3. Identify the main building blocks of an agent (Instructions, Knowledge, Topics, Tools)
4. Upload a realistic internal **IT Service Desk FAQ** as a Knowledge source
5. Map the n8n Activity 7 ingestion nodes to Copilot Studio's managed Knowledge pipeline
6. Run a smoke test to confirm that retrieval works
7. Publish your agent (optional) and understand what Channels are

## Prerequisites
- Completed [Lab 0](../../Day%201/Lab%200%20-%20Environment%20Setup/index.md) (Copilot Studio trial active)
- Read [Module 3](../Module%203%20-%20Business%20Agents%20Concepts.md)
- Signed in at <a href="https://copilotstudio.microsoft.com" target="_blank" rel="noopener">https://copilotstudio.microsoft.com</a> (same environment as Power Automate)
- Downloaded the supplied [`it-faq.pdf`](./assets/it-faq.pdf) knowledge file

## Scenario
You work on the **MyCompany Singapore IT Service Desk**. Staff repeatedly ask how to reset passwords, unlock accounts, enrol in MFA, connect to VPN, troubleshoot Outlook, report phishing, and raise support tickets. Answering the same questions manually delays urgent work.

You will build a grounded **MyCompany IT Support Assistant** that gives concise first-line guidance from the supplied internal FAQ. This is the Copilot Studio equivalent of the **ingestion half** of n8n Activity 7 RAG: load a source document, process it for semantic retrieval, and connect it to an AI agent.

The agent must never invent procedures, request passwords or MFA codes, or downplay security incidents. When the FAQ does not resolve an issue, it must explain how to escalate to the Service Desk.

> **Tip:** An "agent" (sometimes still called a "copilot") is just an AI assistant you configure. You do not write code — you describe what you want in plain English, add some reference material, and test it in a chat window.

## Activity 7 RAG Pattern in Copilot Studio

The n8n activity exposes each RAG component as a node. Copilot Studio performs the same ingestion work as a managed service:

```text
n8n Activity 7:
it-faq.pdf → Upload/Webhook → Data Loader → Splitter → Embeddings → Vector Store

Copilot Studio Lab 6:
it-faq.pdf → Add Knowledge → Managed processing, chunking, embeddings, and search index
```

| n8n Activity 7 component | Copilot Studio equivalent |
|---|---|
| Upload Webhook or document input | **Add knowledge → Files / Upload** |
| Default Data Loader | Managed Knowledge ingestion |
| Text Splitter | Managed document chunking |
| Embeddings model | Managed semantic indexing |
| Simple/Pinecone/Qdrant/Supabase Vector Store | Copilot Studio Knowledge index |
| Successful vector insertion | Knowledge source status is **Ready** |

> **Important:** You do not create a separate Pinecone, Qdrant, or Supabase database in these labs. Copilot Studio manages the retrieval index. Lab 7 connects the answering behaviour to this ready source and tests the retrieval path.

## Which interface are you using?

Microsoft currently provides two Copilot Studio authoring experiences. Use the path that matches your screen:

| If your screen shows… | Follow… |
|---|---|
| **Overview**, **Knowledge**, **Topics**, **Tools/Actions**, and a **Test** pane | **Classic experience** |
| **Build**, **Preview**, **Evaluate**, **Monitor**, with **Knowledge**, **Skills**, and **Tools** on the right | **New experience** |

> **Important:** The two interfaces achieve the same Lab 6 outcome. Do not switch experiences or recreate your agent halfway through the lab. Agents created in the new experience cannot currently be converted to the classic experience.

---

## Step-by-Step Guide

### Step 1: Confirm your environment (~3 minutes)

Before you build anything, make sure you are in the correct environment. This is the single most common cause of problems later in the course.

1. Go to **<a href="https://copilotstudio.microsoft.com" target="_blank" rel="noopener">https://copilotstudio.microsoft.com</a>** and sign in with your course account.
2. Find the **environment selector**:
   - **Classic:** usually at the top-right of the screen.
   - **New:** use the globe/environment control in the Copilot Studio shell (commonly at the lower-left; its position can vary by rollout).
3. Click it and select **Course Sandbox** (your course environment from Lab 0).

> **⚠️ Warning:** Copilot Studio **must use the same environment as Power Automate**. If your agent is built in one environment and your flows live in another, they will not be able to connect to each other in Lab 10. Always confirm the environment name in the top-right before you start. The environment also needs **Dataverse** enabled, because agents are stored there.

### Step 2: Create a blank agent and configure it (~10 minutes)

Use the instructions below for your interface.

#### Classic experience

1. Select **Agents** in the left navigation, then select **Create blank agent**. On some classic Home pages, use **Create an agent** under **Start building from scratch**.
2. Wait for the agent's **Overview** page to open.
3. In **Details**, select **Edit** and enter:
   - **Name:** `MyCompany IT Support Assistant`
   - **Description:** `Provides first-line IT troubleshooting and escalation guidance for MyCompany Singapore staff.`
4. Select **Save**.
5. In **Instructions**, select **Edit**, paste the instruction block below, then select **Save**.

#### New experience

1. Select **Agents** in the left navigation, then select **New Agent**.
2. The designer opens on **Build**, with the agent name field in focus.
3. Enter **Name:** `MyCompany IT Support Assistant`.
4. Paste the instruction block below into the main **Instructions** editor.
5. Select the **Save** (disk) icon at the top.

> **New-interface note:** The current Build page does not expose the classic editable **Description** field. Skip that field for Lab 6. If a description field appears during publishing, enter `Provides first-line IT troubleshooting and escalation guidance for MyCompany Singapore staff.` there. The **… > Settings > Agent details** page contains system identity values such as schema name, solution, and language; it is not the classic Description editor.

#### Instructions for both interfaces

```text
You are the MyCompany Singapore IT Support Assistant for employees.
Use the IT Service Desk FAQ as your source for troubleshooting and escalation guidance.
Give concise, numbered steps in the order staff should perform them.
Never ask for or repeat passwords, MFA codes, recovery codes, or other secrets.
For phishing, lost devices, or suspected security incidents, clearly state the urgent action from the FAQ.
If the FAQ does not cover the issue or its steps fail, say so and direct the user to the IT Portal or ithelpdesk@mycompany-sg.example.com.
When escalating, remind the user to include their full name, asset tag, exact error message, when the issue started, and what they already tried.
Do not invent policies, contact details, system names, or resolution times.
Keep routine answers under 120 words unless the user asks for more detail.
```

> **Tip:** Think of the three fields like this — **Name** is what people see, **Description** is a short note for *you* (and helps other agents/tools recognise it later), and **Instructions** are the actual rules the AI follows in every conversation. Instructions are where almost all of your effort goes.

### Step 3: Tour the agent workspace (~5 minutes)

Now that the agent exists, use this interface map to locate its building blocks:

| Building block | Classic experience | New experience |
|---|---|---|
| Agent configuration | **Overview** | **Build** |
| Behaviour rules | **Instructions** on Overview | Main **Instructions** editor on Build |
| Facts and grounding | **Knowledge** tab | **Knowledge +** on the right of Build |
| Scripted behaviour | **Topics** tab | Primarily **Instructions** and reusable **Skills**; no direct Topics tab |
| Actions and integrations | **Tools** or **Actions** tab | **Tools +** on the right of Build |
| Interactive testing | **Test** pane | **Preview** tab |
| Structured repeatable tests | Not normally used in this lab | **Evaluate** tab |
| Usage and run information | Analytics/monitoring pages | **Monitor** tab |

Click through the relevant areas once so you know where they are. You do not need to add a Skill, Tool, or evaluation yet.

> **Tip:** Remember the four building blocks: **Instructions** = behaviour and tone, **Knowledge** = facts the agent can look up, **Topics** = scripted conversations, **Tools** = things the agent can do. Almost everything in Copilot Studio is one of these four.

> **New-interface note:** Enhanced orchestration uses Instructions, Knowledge, Skills, and Tools to decide what to do. The classic **Topics** tab does not have a one-to-one replacement in this experience.

### Step 4: Ingest the IT FAQ into Knowledge (~10 minutes)

Right now your agent has behaviour rules but no company-specific procedures. Ground it with the supplied [`it-faq.pdf`](./assets/it-faq.pdf), adapted from the Activity 7 RAG mock data in the [Agentic AI Automation with n8n repository](https://github.com/tertiarycourses/TGS-2023035977-Agentic-AI-Automation-with-n8n/tree/main/labs/activity7-rag).

#### Classic experience

1. Open the **Knowledge** tab.
2. Select **+ Add knowledge**.
3. Choose **Files** or **Upload file**.
4. Upload [`it-faq.pdf`](./assets/it-faq.pdf).
5. Set the name to `MyCompany IT Service Desk FAQ` and, if requested, enter: `Internal procedures for passwords, MFA, VPN, Wi-Fi, Outlook, software, printers, hardware, access, phishing, and IT ticket escalation.`
6. Select **Add to agent**.
7. Wait until the source status changes from **Processing** to **Ready**.

#### New experience

1. On **Build**, select **+** beside **Knowledge** on the right.
2. Choose **Files** or **Upload file**.
3. Upload [`it-faq.pdf`](./assets/it-faq.pdf).
4. Set the source name to `MyCompany IT Service Desk FAQ`.
5. If a description is requested, enter: `Internal procedures for passwords, MFA, VPN, Wi-Fi, Outlook, software, printers, hardware, access, phishing, and IT ticket escalation.`
6. Select **Add to agent**, then select the **Save** (disk) icon.
7. Wait for processing to finish. Depending on the rollout, the source may show **Ready**, a spinner, or simply appear as a `MyCompany IT Service Desk FAQ` chip.

> **Tip:** This PDF is internal mock data. Its `.example.com` addresses and phone number are intentionally fictional; do not replace them with personal contact information.

> **RAG checkpoint:** When the source becomes **Ready**, Copilot Studio has completed the equivalent of n8n's load → split → embed → upsert sequence. A visible source alone is not enough; wait for processing to finish.

### Step 5: Smoke-test the retrieval path (~7 minutes)

1. Open the testing surface:
   - **Classic:** open the **Test** pane on the right. If hidden, select **Test** at the top-right.
   - **New:** select the **Preview** tab.
2. Start with these three ingestion smoke tests:
   - `I entered the wrong password several times and my account is locked. What should I do?`
   - `How do I connect to the corporate VPN while working from home?`
   - `I clicked a link in a suspicious email and entered my password. What should I do now?`
3. Compare the responses with the expected evidence:

   | Test | What a grounded answer should include |
   |---|---|
   | Locked account | Wait 15 minutes; use self-service password reset if needed; escalate if still locked |
   | VPN | Open GlobalConnect; use `vpn.mycompany-sg.example.com`; sign in and approve MFA |
   | Phishing compromise | Report phishing, change the password immediately, and call the Service Desk |

4. Confirm that the agent never asks for the user's password or MFA code.
5. Check for a citation or reference to `it-faq.pdf` where the interface provides citations.

> **Tip:** This is only a smoke test that the ingestion path works. In Lab 7 you will perform a fuller RAG evaluation with citations, negative tests, source-only controls, and troubleshooting.

### Step 6: Iterate on your Instructions (~5 minutes)

The first version of an agent is rarely perfect. Tuning the Instructions is normal and expected.

1. Review your test results. If answers are too vague, too long, or omit escalation details, return to your instruction editor:
   - **Classic:** open **Overview** and select **Edit** in **Instructions**.
   - **New:** return to **Build** and click in the main **Instructions** editor.
2. Add a line to make the change you want, for example:
   ```
   For every troubleshooting answer, separate "Try this first" from "Escalate when".
   Never ask the user to share a password, MFA code, recovery code, or authentication secret.
   ```
3. Save the change:
   - **Classic:** select **Save**.
   - **New:** select the **Save** (disk) icon.
4. Start a fresh test:
   - **Classic:** return to the **Test** pane and select **Start new test session** (circular-arrow/refresh).
   - **New:** return to **Preview** and select **New chat**.
5. Ask the questions again and confirm the updated behaviour.

> **⚠️ Warning:** Existing test conversations do **not** always pick up changes. Start a new test session in Classic or a **New chat** in the new experience after editing Instructions.

### Step 7: Publish the agent (optional) (~5 minutes)

Publishing makes your latest version live so it can be shared. You do not have to deploy it anywhere yet.

> **Note:** A Copilot Studio **trial** license lets you create and test agents in the Test pane, but does **not** let you publish them. If Publish is blocked on your account, simply read through this step — everything else in the course works from the Test pane.

1. Select **Publish** at the top-right, then confirm by selecting **Publish** again.
2. After publishing:
   - **Classic:** open **Channels** to browse Microsoft Teams, demo website, and other deployment options.
   - **New:** use the publish confirmation options to **Share** the agent or add it to the organisation catalogue. Channel availability may differ while the new experience is in preview.
3. You do not need to connect a channel or share the agent for this lab.

---

## Checkpoint
You have successfully completed this lab when:
- ✅ You confirmed you are in the **Course Sandbox** environment (matching Power Automate)
- ✅ An agent named **MyCompany IT Support Assistant** exists with your custom **Instructions**
- ✅ The supplied **MyCompany IT Service Desk FAQ** is ready or has finished processing
- ✅ You can explain how **Add knowledge** replaces the n8n loader, splitter, embeddings, and vector-store nodes
- ✅ The agent passes the account-lockout, VPN, and phishing smoke tests in **Test** (Classic) or **Preview** (New)
- ✅ The agent never requests passwords, MFA codes, or other secrets
- ✅ You edited the Instructions and saw the change after starting a fresh test session or **New chat**

## Troubleshooting
| Problem | Cause | Solution |
|---------|-------|----------|
| Agent ignores your new instructions | The test is using an existing conversation | Save, then use **Start new test session** (Classic) or **New chat** in Preview (New). |
| Knowledge source stuck on "Processing" | File processing or a busy service | Wait a minute or two and confirm the PDF opens locally. If it persists, remove the source and upload `it-faq.pdf` again. |
| Replies are generic or unhelpful | No grounding, or vague instructions | Make sure a Knowledge source is **Ready** and tighten your Instructions (be specific about tone and scope). |
| Can't see the Test pane | You are using the new experience, or the Classic pane is collapsed | Select **Test** in Classic or open the **Preview** tab in the new experience. |
| Can't find Description | The new Build page does not expose the classic Description field | Skip it for Lab 6; do not enter it under **Agent settings**. Add it during Publish only if a description field appears. |
| Can't find Topics | The new experience uses enhanced orchestration | Use **Instructions**, **Skills**, and **Tools**; no Topic is required in Lab 6. |
| Tools/flows won't connect later | Wrong environment | Use the **environment selector** (top-right) to switch to the same environment as Power Automate (**Course Sandbox**). |
| Can't find **Create blank agent** | Interface variation | In Classic use **Create blank agent** or **Create an agent**. In the new experience use **Agents > New Agent**. |

## Key Takeaways
- An agent's behaviour is shaped mainly by its **Instructions** — clear instructions give predictable answers.
- The classic building blocks are **Instructions**, **Knowledge**, **Topics**, and **Tools/Actions**; the new experience emphasises **Instructions**, **Knowledge**, **Skills**, and **Tools**.
- **Knowledge** grounds answers in real content so the agent stops guessing.
- A **Ready** source is the Copilot Studio equivalent of a successfully populated vector store.
- Real IT support agents need explicit security boundaries: never request secrets and escalate suspected compromise immediately.
- The **Test** pane (Classic) or **Preview** tab (New) is your build-and-iterate loop.
- Always work in the **same environment** as your Power Automate flows, and that environment needs **Dataverse**.

## Duration
~45 minutes

## Next Steps
Proceed to [Lab 7: Add Knowledge to Your Agent](../Lab%207%20-%20Add%20Knowledge%20to%20Your%20Agent/index.md).
