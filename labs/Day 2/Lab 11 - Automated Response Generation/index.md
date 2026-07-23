# Lab 11: Automated Response Generation

## Lab Title
Use AI Prompts to Generate Professional Responses Automatically

## Lab Objectives
By the end of this lab, you will be able to:
1. Add an AI Builder **Run a prompt** action inside a flow
2. Feed captured enquiry data into the prompt to generate tailored text
3. Control the **length, tone, and format** of the AI output
4. Email the AI-generated response automatically
5. Compare a static template versus an AI-generated response and know when to use each

## Prerequisites
- Completed [Lab 10](../Lab%2010%20-%20Procurement%20Request%20Workflow/index.md)
- A **Sales Enquiry Assistant** agent (from Lab 9) you can reuse

> **⚠️ Warning:** As in Lab 10, the agent and the flow must both be in the **Course Sandbox** environment, or the agent cannot call its flow. Confirm the environment picker (top-right) in both <a href="https://copilotstudio.microsoft.com" target="_blank" rel="noopener">Copilot Studio</a> and <a href="https://make.powerautomate.com" target="_blank" rel="noopener">Power Automate</a>.

## Scenario
At **ACME Pte Ltd**, every sales enquiry currently gets the same copy-paste reply. It works, but it feels impersonal. In this lab you'll reuse your **Sales Enquiry Assistant** from Lab 9 and add a flow that uses an **AI prompt** to draft a warm, personalised reply from the customer's captured details — then emails it automatically. This shows how generative AI turns the structured data you captured into polished, individual communication, while still keeping you in control of length and tone.

---

## Step-by-Step Guide

### Step 1: Understand where the AI prompt runs (~5 minutes)
1. An AI prompt can run in two equivalent places:
   - **In a Power Automate flow** — using the **Run a prompt** action (AI Builder).
   - **In Copilot Studio** — by adding a **Prompt** tool to a topic.
2. This lab uses the **flow** approach because it builds directly on the agent + flow skills from Lab 10 and keeps the "generate" and "email" steps together in one place.

> **Tip:** Both options call the same underlying AI Builder model. Choosing the flow approach simply means generation and emailing live in one flow you can inspect via run history.

### Step 2: Reuse the Sales Enquiry Assistant and add a flow (~10 minutes)
1. Open your **Sales Enquiry Assistant** agent (from Lab 9) and open the **New Sales Enquiry** topic.
2. After the summary **Send a message** node, select the **+** node, choose **Add a tool**, then **New Agent flow**.
3. The **agent flow designer** opens with the trigger **When an agent calls the flow** and a **Respond to the agent** action already in place. Confirm you are still in the **Course Sandbox** environment.
4. On the trigger, select **+ Add an input** and add four inputs (matching the variables from Lab 9):
   - Type **Text**, name `customerName`
   - Type **Text**, name `company`
   - Type **Text**, name `product`
   - Type **Number**, name `quantity`

### Step 3: Add the AI prompt action (~15 minutes)
1. Select the **+** between the trigger and **Respond to the agent**, search for **Run a prompt** under **AI Builder**, and select it. *(This action was called "Create text with GPT using a prompt" until May 2025; the separate "Create text with GPT" action is deprecated.)*
2. In the action's **Prompt** dropdown, choose **+ New custom prompt** (rather than one of the prebuilt prompts). The **prompt builder** opens.
3. Write the prompt instruction below. Wherever a value comes from the enquiry, insert it from the **Dynamic content** panel rather than typing it:
   ```
   Write a warm, professional email reply (maximum 120 words) to a sales enquiry
   for ACME Pte Ltd.
   Customer name: {customerName}
   Company: {company}
   Product of interest: {product}
   Quantity: {quantity}

   The email should:
   - Thank the customer by name
   - Acknowledge the product and quantity
   - Say a sales representative will follow up within 1 business day with pricing
   - End with a professional sign-off from "The ACME Sales Team"
   Output only the email body text. Do not include the prompt or these instructions.
   ```
4. Select **Save** on the prompt. The action now produces a generated **Text** output.

> **Tip:** Notice the prompt explicitly states **length** (max 120 words), **tone** (warm, professional), **content** (what to mention), and **format** ("output only the email body"). Controlling all four is what separates a reliable AI step from an unpredictable one — this is the structured prompt design from Module 3 applied to output generation.

### Step 4: Email the generated response (~10 minutes)
1. Select the **+** below the prompt action (still above **Respond to the agent**), search for **Send an email (V2)** (Office 365 Outlook), and select it.
2. Fill in the email:
   - **To:** your own email (for testing; in production you would use a captured customer email variable)
   - **Subject:** type `Re: Your enquiry about `, then insert the **product** dynamic content
   - **Body:** insert the prompt's **Text** output (the generated email text) from the **Dynamic content** panel
3. Select the **Respond to the agent** action at the end of the flow, select **+ Add an output**, and return a **Text** output named `result` with value `Reply drafted and sent.`
4. Select **Save draft**, then **Publish** the flow, then return to your agent in Copilot Studio.

> **⚠️ Warning:** If **Send an email** shows an **"Unauthorized"** error, reconnect the **Office 365 Outlook** connection with a mailbox-enabled work account. Every connection used by the flow must show a green ✓ before it will run.

### Step 5: Wire the inputs and test (~10 minutes)
1. Back in the topic, select the flow's tool node and map each input to its matching topic variable — the flow gets empty values if you skip this:
   - input `customerName` → variable `customerName`
   - input `company` → variable `company`
   - input `product` → variable `product`
   - input `quantity` → variable `quantity`
2. (Optional) After the tool node, add a **Send a message** node showing `{result}` so the agent confirms the email was sent.
3. Select **Save** to save the topic.
4. Open the **Test** pane, select the **Start new test session** (refresh) icon, type a message that starts the enquiry (the agent recognises it from the topic **Description**), and run the enquiry:
   - Name: `Mei Ling`, Company: `BrightTech`, Product: `Air Fryer Pro`, Quantity: `25`
5. Confirm:
   - The flow runs successfully (check **run history** if unsure).
   - You receive a **uniquely worded, personalised** email — not a fixed template.
6. Run it again with different details and compare the two emails; the AI adapts the wording each time.

> **Tip:** If the email body contains the prompt instructions, your "Output only the email body text" line is missing or you mapped the wrong field — map only the prompt **output**, and keep that instruction in the prompt.

### Step 6: Compare template versus AI (~5 minutes)
1. Recall the **static template** email from Day 1: it is fast and 100% predictable, but identical for every customer.
2. The **AI-generated** response is personalised and natural, but you must guide it with a precise prompt and review it for accuracy.
3. Note the best-practice rule: use AI for **drafting the wording**, and keep critical facts (prices, policies, legal terms) as controlled static text or knowledge — never let the model invent them.

> **Tip:** A safe production pattern is "AI drafts, human (or fixed text) confirms the facts." Personalisation from AI plus controlled facts gives you the best of both.

---

## Checkpoint
You are ready to finish when all of the following are true:
- ✅ A flow that calls an **AI prompt** with the four enquiry inputs
- ✅ A personalised email generated and sent automatically from the agent conversation
- ✅ The email contains **only the body** (no leaked prompt instructions)
- ✅ You can explain when to use a static template versus an AI-generated reply

## Troubleshooting
| Problem | Solution |
|---------|----------|
| No **Run a prompt** action available | Search for **Run a prompt** under **AI Builder**; confirm AI Builder is available in this environment (the trial / developer environment includes it). The old **Create text with GPT** action is deprecated — do not use it. |
| "Unauthorized" error on Send an email | Reconnect the **Office 365 Outlook** connection with a mailbox-enabled account; every connection must show a green ✓. |
| Output too long or wrong tone | Tighten the prompt: state the word limit, the tone, and "output only the email body." |
| Captured values not appearing in the email | Confirm you inserted them as **dynamic content** inside the prompt, and that the topic inputs are **mapped** to the variables. |
| Email body shows the prompt instructions | Add "Output only the email body text" to the prompt and map only the prompt **output** into the email body. |
| Flow doesn't appear in the topic | Refresh Copilot Studio; ensure the flow is **published** in the **same environment (Course Sandbox)**. |

## Key Takeaways
- **AI prompts** turn the structured data you captured into polished, personalised text.
- You control quality by specifying **length, tone, content, and format** — especially "output only the email body."
- Combine AI drafting with controlled facts for responses that are both personal and reliable.
- The same agent + flow pattern from Lab 10 now powers generative output, not just logging.

## Duration
~45 minutes

## Next Steps
You've completed all the hands-on labs. Next: course wrap-up, briefing for assessment, then the WSQ assessment (Written Assessment 4:00–5:00 PM, Practical Performance 5:00–6:00 PM).
