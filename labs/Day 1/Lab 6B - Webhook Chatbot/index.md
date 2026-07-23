# Lab 6B: Webhook Chatbot

## Lab Title
Trigger a Browser Chatbot with a Power Automate Webhook

## Lab Objectives
By the end of this lab, you will be able to:
1. Receive chat messages through a Power Automate production URL
2. Maintain a simple session identifier in the browser request
3. Route messages with a **Switch** control
4. Return a bot reply as JSON
5. Connect and test the supplied browser chat interface

## Prerequisites
- Completed [Lab 6A](../Lab%206A%20-%20External%20Enquiry%20Webhook/index.md)
- Access to the premium **Request** connector
- The supplied [`webhook-chatbot.html`](assets/webhook-chatbot.html)

## Scenario
ACME Pte Ltd wants a small help widget on its website. A visitor sends a message, the page posts it to Power Automate, and the flow returns an immediate reply. This mirrors the interaction pattern in [n8n Activity 6](https://github.com/tertiarycourses/TGS-2023035977-Agentic-AI-Automation-with-n8n/tree/main/labs/activity6-finance-advisor), where a chat interface triggers an automation and receives its response, but uses a browser chat widget and Power Automate instead of Telegram and n8n.

This Day 1 version uses deterministic replies so you can see the webhook mechanics clearly. On Day 2, Copilot Studio provides the AI reasoning, knowledge grounding, and richer conversation management.

```text
Browser chatbot
      |
      | POST { sessionId, message }
      v
When an HTTP request is received
      |
      +--> Parse JSON
      +--> Normalise message
      +--> Switch
      +--> Set botReply
      |
      v
Response { reply }
```

> **Security warning:** This lab uses an anonymously callable production URL for a controlled exercise. Do not embed that URL in a public production site. Use authentication, rate limiting, validation, and a server-side proxy for a real chatbot.

---

## Step-by-Step Guide

### Step 1: Create the chatbot webhook (~5 minutes)

1. In [Power Automate](https://make.powerautomate.com), create an **Automated cloud flow**.
2. Name it `Lab 6B - Webhook Chatbot`.
3. Add **When an HTTP request is received** under **Request**.
4. For this controlled lab, set **Who can trigger the flow?** to **Anyone** if your tenant permits it.

**New designer**

- Select **Add a trigger** → search `HTTP` → choose **When an HTTP request is received** under **Request**.

**Classic designer**

- Search the trigger list for `Request` → choose **When an HTTP request is received**.

> Do not select **HTTP Webhook** under HTTP. It subscribes to an external service; it is not the incoming browser endpoint used here.

### Step 2: Parse the chat request (~10 minutes)

1. Leave the trigger's **Request Body JSON Schema** blank.
2. Add **Parse JSON** below the trigger.
3. In **Content**, use the **fx** expression editor:

```text
json(triggerBody())
```

4. Under **Schema**, choose **Use sample payload to generate schema** and paste:

```json
{
  "sessionId": "web-001",
  "message": "opening hours"
}
```

5. Select **Done**.

The `sessionId` lets a caller identify a conversation. This simple flow does not store chat history, but a production system could use it as a key in Dataverse, SharePoint, or another database.

The browser sends the payload as `text/plain` to avoid a cross-origin OPTIONS preflight. **Parse JSON** converts the JSON text into usable dynamic values.

### Step 3: Initialise the reply (~5 minutes)

1. Add **Initialize variable**.
2. Configure:
   - **Name:** `botReply`
   - **Type:** `String`
   - **Value:** `I can help with opening hours, contact details, or courses. Please choose one of those topics.`

This is the fallback response for any message that does not match a known route.

### Step 4: Normalise the message (~5 minutes)

1. Add a **Compose** action.
2. Rename it `Normalise message`.
3. In **Inputs**, use the **fx** expression editor and enter:

```text
toLower(trim(body('Parse_JSON')?['message']))
```

4. Confirm it becomes an expression token.

Normalising removes extra spaces and makes `Opening Hours` match `opening hours`.

### Step 5: Route the conversation (~15 minutes)

1. Add a **Switch** control.
2. In **On**, insert **Outputs** from `Normalise message`.
3. Add these cases:

| Case value | Action inside the case | `botReply` value |
|---|---|---|
| `opening hours` | **Set variable** | `Our support desk is open Monday to Friday, 9:00 AM to 6:00 PM Singapore time.` |
| `contact details` | **Set variable** | `Email help@acme.example or call +65 6000 1234 during business hours.` |
| `courses` | **Set variable** | `We offer instructor-led automation and AI courses. Please submit an enquiry for the latest schedule.` |

4. Leave the **Default** branch empty. The initial fallback remains unchanged.

**New designer**

- Select **+** → **Add an action** → **Control** → **Switch**.
- Within each case, select **+** and add **Set variable**.

**Classic designer**

- Select **New step** → **Built-in** → **Control** → **Switch**.
- Choose **Add a case**, then add **Set variable** inside it.

### Step 6: Return the bot reply (~10 minutes)

1. Add **Response** after the entire Switch control, not inside an individual case.
2. Configure:
   - **Status Code:** `200`
   - **Headers:**

     | Key | Value |
     |---|---|
     | `Content-Type` | `application/json` |
     | `Access-Control-Allow-Origin` | `*` |

   - **Body:**

```json
{
  "reply": "INSERT_BOT_REPLY_HERE"
}
```

3. Delete `INSERT_BOT_REPLY_HERE` and insert the dynamic value **botReply**.
4. Save the flow.
5. Reopen the trigger and copy its **HTTP POST URL** to a private note.

> Keep the quotation marks around the dynamic token in the JSON editor if Power Automate treats the body as raw JSON. The final response must look like `{"reply":"some text"}` in the run history.

### Step 7: Test with the supplied chat page (~10 minutes)

1. Open [`assets/webhook-chatbot.html`](assets/webhook-chatbot.html) in Chrome or Edge.
2. Paste the production URL into **Power Automate webhook URL**.
3. Select **Connect**.
4. Send each supported message:
   - `opening hours`
   - `contact details`
   - `courses`
5. Send `refund policy` and confirm the fallback reply appears.
6. In Power Automate, open the run history and inspect the Switch case taken for each message.

### Step 8: Compare with a production chatbot (~5 minutes)

Record two limitations of this lab bot:

1. It matches only predefined phrases.
2. It does not remember earlier turns on the server.

Record two production improvements:

1. Put an authenticated, rate-limited API or proxy in front of the flow.
2. Replace the Switch with Copilot Studio or an approved AI action and persist state using `sessionId`.

---

## Checkpoint
- ✅ Parse JSON produces `sessionId` and `message`
- ✅ The input is normalised before routing
- ✅ A Switch supplies three supported replies and one fallback
- ✅ The Response action is after the Switch and returns `botReply`
- ✅ The browser page shows each reply
- ✅ The webhook URL is not saved in the HTML or repository

## Troubleshooting

| Problem | Solution |
|---|---|
| Every message gets the fallback | Confirm the Switch uses **Outputs** from `Normalise message` and the case values are lowercase exact matches. |
| Response action runs before a branch finishes | Move **Response** below and outside the whole Switch control. |
| Page displays `undefined` | Confirm the response property is named exactly `reply`. |
| Parse JSON fails | Confirm its Content is the expression `json(triggerBody())` and the supplied page has not been modified to send a different structure. |
| Browser says `Failed to fetch` | Check the URL, trigger authentication, flow run history, and the lab CORS response header. Test with `curl` as shown in Lab 6A. |
| Flow says invalid JSON | Recreate the Response body and insert the `botReply` token in place of the placeholder text. |
| HTTP trigger unavailable | The Request connector is premium or disabled by tenant policy. Ask the trainer for the demonstration environment. |

## Optional AI Upgrade

If your tenant includes an approved generative AI action, you may replace the Switch with that action and instruct it to answer only from approved ACME support content. Keep the same HTTP request and Response contract so the browser page does not need to change.

Do not send confidential or personal information to an AI service unless your organisation has approved the data handling.

## Key Takeaways
- A browser chatbot is a user interface around a request/response API.
- Power Automate can expose that API through a saved HTTP Request trigger.
- `sessionId` prepares the design for future conversation state.
- Deterministic routing is easy to test; AI adds flexibility but also needs grounding and safety controls.
- The webhook contract can remain stable even when the internal bot logic changes.

## Duration
~60 minutes

## Next Steps
You have completed Day 1. Proceed to [Day 2 — Module 3: Business Agents Concepts](../../Day%202/Module%203%20-%20Business%20Agents%20Concepts.md).
