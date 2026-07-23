# Lab 7: Add Knowledge to Your Agent (Grounding / RAG)

## Lab Title
IT Support RAG Part B — Retrieve, Cite, and Refuse Unsupported Answers

## Lab Objectives
By the end of this lab, you will be able to:
1. Explain **grounding** and **RAG** (Retrieval-Augmented Generation) in plain, everyday terms
2. Add one or more **Knowledge** sources to a Copilot Studio agent (files, public website, or SharePoint)
3. Turn off **Allow ungrounded responses** (general knowledge) so the agent answers only from your content
4. Test that the agent answers **from your documents** and shows **citations**
5. Confirm the agent declines to answer when the information is not in your sources (no made-up answers)
6. Tell the difference between **Instructions** (behaviour) and **Knowledge** (facts)
7. Map the n8n Activity 7 retriever-and-chat workflow to Copilot Studio

## Prerequisites
- Completed [Lab 6](../Lab%206%20-%20Create%20Your%20First%20Agent/index.md) (you have an agent)
- The supplied [`it-faq.pdf`](../Lab%206%20-%20Create%20Your%20First%20Agent/assets/it-faq.pdf) from Lab 6

## Scenario
Your **MyCompany IT Support Assistant** from Lab 6 already has an indexed IT FAQ. You will now complete the **answering half** of the Activity 7 RAG pattern: connect the agent's behaviour to the ready knowledge source, retrieve relevant passages, generate a grounded response, expose the result in chat, and reject unsupported questions.

In this lab you will inspect and harden the **MyCompany IT Service Desk FAQ** knowledge source, then prove that the agent answers from that source and nothing else. This is the technique that makes business agents trustworthy.

> **Tip:** **Grounding** means tying the agent's answers to specific source material you provide, so it cannot just invent things. **RAG** (Retrieval-Augmented Generation) is the technology that does this.

### How RAG works (in plain terms)
1. You add documents to **Knowledge**. Copilot Studio breaks them into small passages and indexes them.
2. A user asks a question.
3. The agent **retrieves** the few passages most relevant to that question.
4. The agent **generates** an answer using *only* those passages, and shows **citations** pointing back to the source.

> **RAG in one line:** *Find the relevant text in your documents → hand it to the AI → it answers from that text, with citations.* This keeps answers accurate and up to date without retraining any model.

### Activity 7 answering workflow translated

```text
n8n Activity 7:
Chat/Telegram/Webhook → AI Agent → Vector Store Retriever → Chat Model → Response

Copilot Studio Lab 7:
Test or Preview chat → Generative orchestration → Ready Knowledge source → Grounded answer + citation
```

| n8n Activity 7 component | Copilot Studio equivalent |
|---|---|
| Telegram Trigger, Chat Trigger, or Webhook | **Test** pane (Classic) or **Preview** (New) |
| AI Agent node | Copilot Studio agent with **Instructions** |
| Vector Store Retriever tool | Ready **Knowledge** source |
| Chat model | Agent model selected by the environment |
| Respond to Webhook / Telegram message | Agent chat response with citation |
| Retriever returns no matching content | Agent declines and offers escalation |

> **Why there is no webhook in this lab:** Copilot Studio supplies its own test chat and publishable channels. A Power Automate HTTP webhook is useful when an external application must call a flow, but it is not required to prove that this agent retrieves from its Knowledge source.

---

## Step-by-Step Guide

### Step 1: Prepare a knowledge source (~5 minutes)

1. Download or locate the supplied [`it-faq.pdf`](../Lab%206%20-%20Create%20Your%20First%20Agent/assets/it-faq.pdf).
2. Open it and identify at least four topics, such as password reset, VPN, phishing, and laptop troubleshooting.
3. If you already uploaded this file in Lab 6, reuse that ready source. If it is missing, you will upload it in Step 3.

> **Tip:** Keep the document focused and tidy — use clear headings and short paragraphs. Clean, well-structured content leads to much better retrieval and more accurate answers.

### Step 2: Open the agent and verify its Knowledge source (~3 minutes)

1. Go to **<a href="https://copilotstudio.microsoft.com" target="_blank" rel="noopener">https://copilotstudio.microsoft.com</a>** and confirm the **environment selector** (top-right) shows **Course Sandbox**.
2. Open your **MyCompany IT Support Assistant** agent from Lab 6.
3. Locate Knowledge using the path for your interface:
   - **Classic:** select the **Knowledge** tab.
   - **New:** on **Build**, locate **Knowledge** on the right.
4. Confirm **MyCompany IT Service Desk FAQ** appears. Do not add a duplicate source.

> **⚠️ Warning:** Make sure you are in the **same environment** as your Lab 6 agent and your Power Automate flows. If the environment is wrong, you may be editing a different (or empty) agent.

### Step 3: Repair the ingestion only if the source is missing (~10 minutes)

1. Look for **MyCompany IT Service Desk FAQ** in the Knowledge list.
2. If it is already present, confirm its status is **Ready** and continue to Step 4.
3. If it is missing, select **+ Add knowledge**, choose **Files** / **Upload**, and upload `it-faq.pdf`.
4. Give the source the name `MyCompany IT Service Desk FAQ`.
5. If prompted for a description, enter `Approved first-line IT support, troubleshooting, security incident, and Service Desk escalation procedures for MyCompany Singapore staff.`
6. Select **Add to agent** and wait until its status changes from **Processing** to **Ready**.

> **⚠️ Warning:** Do **not** test until the status reads **Ready**. While a source is still **Processing**, the agent cannot use it and may reply that it has no information.

### Step 4: Restrict answers to approved sources (~4 minutes)

By default the agent may blend in general AI/web knowledge. For an internal IT helpdesk you usually want procedural answers **only** from approved MyCompany documents.

1. Apply the controls available in your interface:
   - **Classic:** open **Settings → Generative AI**. In **Knowledge**, turn **Allow ungrounded responses** **Off**. Also turn **Use information from the web** or **Web Search** **Off**.
   - **New:** on **Build**, remove the **Search all websites** source if it is present. Open **… → Settings → AI & behavior** and turn off a general-knowledge or ungrounded-response option if your tenant exposes one.
2. Add or confirm these lines in **Instructions**:
   ```text
   Answer IT procedure questions only from the approved Knowledge sources and cite the source.
   If the source does not contain the answer, say that clearly and offer the Service Desk escalation route.
   ```
3. Save the agent.
4. Start a new test conversation so the controls take effect.

> **Tip:** Turn **Allow ungrounded responses** (and **Web Search**) **on** when you want the agent to also answer broad, everyday questions. Turn them **off** when you need tight control and want to prevent answers that did not come from your documents.

### Step 5: Test that answers come from your document (~10 minutes)

1. Open the testing surface and start a fresh conversation:
   - **Classic:** open **Test** and select **Start new test session**.
   - **New:** open **Preview** and select **New chat**.
2. Ask questions that can **only** be answered from `it-faq.pdf`, for example:
   - `My account is locked. What should I do?`
   - `How do I connect to GlobalConnect VPN?`
   - `Where should I report a suspicious email?`
3. Confirm each answer matches the facts in your document.
4. Look **underneath each answer** for **citations** or **references** (often numbered, like `[1]`, or a "1 reference" link). Click a citation to confirm it points back to your source.

> **Tip:** Citations are your proof that grounding worked. If an answer has no citation, it may have come from general knowledge rather than your document.

### Step 6: Confirm the agent declines when it doesn't know (~5 minutes)

This is the most important test — it proves the agent will not make things up.

1. In **Test** (Classic) or **Preview** (New), ask something that is **not** in your document, for example:
   - `How many days of annual leave do I have?`
   - `Can you give me the finance team's payroll schedule?`
2. The agent should say the FAQ does not contain that information and direct the user to the appropriate department or Service Desk instead of inventing an answer.
3. If instead it confidently invents an answer, that is a **hallucination**. Re-check that **Allow ungrounded responses is Off** (Step 4) and that your Instructions tell it to answer only from provided sources.

> **Tip:** A trustworthy business agent saying *"I don't have that information"* is a success, not a failure. Declining gracefully is exactly the behaviour you want.

### Step 7: Tune your sources (~5 minutes)

1. If an answer is weak or missing, improve the **source document** — add clearer headings and more detail — then re-upload or refresh the source.
2. Add a **second** Knowledge source for broader coverage (for example, a product page website). Give each source a **distinct name and description** so the agent can tell them apart.
3. Reinforce grounding in the **Instructions** (Overview tab). Add a line such as:
   ```
   Only answer using the provided knowledge sources, and cite them.
   If the answer is not in the sources, say you don't have that information.
   ```
4. Select **Save**, refresh the Test pane, and re-test.

---

## Checkpoint
You have successfully completed this lab when:
- ✅ At least one **Knowledge** source shows the status **Ready**
- ✅ The agent answers IT support questions **from `it-faq.pdf`**, with visible **citations**
- ✅ **Allow ungrounded responses** is turned **Off** (if you chose the recommended setup)
- ✅ The agent **declines** to answer (no hallucination) when the information is not in your sources
- ✅ You can map the n8n **AI Agent + Vector Store Retriever + response** chain to Copilot Studio
- ✅ You can explain the difference between **Instructions** and **Knowledge**

## Troubleshooting
| Problem | Cause | Solution |
|---------|-------|----------|
| Source stuck on "Processing" | Large or busy source | Wait a minute or two; if it persists, try a smaller file or a single web page. |
| Agent ignores the document | Source not ready, or no description | Confirm the source is **Ready**; add a clear description; in Instructions, tell it to answer from knowledge. |
| Answers come from the web, not my doc | Web search / ungrounded answers are on | Turn **off** **Allow ungrounded responses** and **Use information from the web** in Settings → **Generative AI** (Knowledge section), then **Save** and refresh the Test pane. |
| No citations appear | Answer was not grounded | Ensure the answer actually came from a Ready source; check that **Allow ungrounded responses** is off. |
| Agent makes things up | Hallucination | Turn off **Allow ungrounded responses** and add an Instruction to decline when info is missing. |
| Edits not reflected in chat | Test pane caching | Select the **Start new test session** (refresh) icon at the top of the **Test** pane to restart the conversation. |

## Key Takeaways
- **Knowledge = grounding (RAG):** the agent retrieves passages from your documents and answers from them, with citations.
- Use **Instructions** for *behaviour and tone*; use **Knowledge** for *facts*.
- Turning **Allow ungrounded responses off** (and **Web Search off**) keeps answers strictly inside your own content.
- **Citations** let you and your users verify exactly where an answer came from.
- A grounded agent that **declines** when it doesn't know is working correctly — that is how you avoid hallucinations.

## Duration
~40 minutes

## Next Steps
Proceed to [Lab 8: Add Tools and Actions to Your Agent](../Lab%208%20-%20Add%20Tools%20and%20Actions/index.md).
