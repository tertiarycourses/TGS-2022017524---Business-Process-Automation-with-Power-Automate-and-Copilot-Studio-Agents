# Lab 6A: External Enquiry Webhook

## Lab Title
Trigger Power Automate from an External Online Form

## Lab Objectives
By the end of this lab, you will be able to:
1. Create an inbound webhook with **When an HTTP request is received**
2. Define and validate a JSON request schema
3. Send an email using values submitted by an external webpage
4. Return a JSON response to the webpage
5. Test the saved production URL and apply basic webhook security

## Prerequisites
- Completed [Lab 5](../Lab%205%20-%20Form%20Submission%20Workflow/index.md)
- Access to Power Automate in the **Course Sandbox** environment
- A Power Automate plan that permits the premium **Request** connector
- A mailbox-enabled Microsoft 365 account
- The supplied [`enquiry-form.html`](assets/enquiry-form.html)

> **Licensing note:** The **Request** connector is marked with a diamond icon in Power Automate and normally requires a premium entitlement. If your tenant blocks it, follow the demonstration with the trainer rather than selecting the similarly named **HTTP**, **HTTP Webhook**, or **HTTP + Swagger** actions.

## Scenario
ACME Pte Ltd wants its own branded enquiry page rather than a Microsoft Forms page. When a visitor submits the page, JavaScript sends JSON to a Power Automate production URL. The flow emails the service team and returns a confirmation to the same page.

This adapts the external web-interface pattern from the [n8n Activity 6 finance-advisor example](https://github.com/tertiarycourses/TGS-2023035977-Agentic-AI-Automation-with-n8n/tree/main/labs/activity6-finance-advisor): a browser interface calls an automation endpoint, receives a result, and presents it to the user.

```text
External enquiry page
        |
        | POST JSON
        v
When an HTTP request is received
        |
        +--> Parse JSON
        |
        +--> Send an email (V2)
        |
        +--> Response (JSON)
```

> **Security warning:** The generated URL contains access information. Treat it like a secret. Never commit it to GitHub or hard-code it in a public webpage. The supplied page asks for the URL at run time and does not save it.

---

## Step-by-Step Guide

### Step 1: Create the webhook flow (~5 minutes)

1. Open [Power Automate](https://make.powerautomate.com) and confirm the environment is **Course Sandbox**.
2. Create an **Automated cloud flow**.
3. Name it `Lab 6A - External Enquiry Webhook`.
4. Search for `HTTP request`.
5. Under **Request**, select **When an HTTP request is received**.

> **Choose the trigger shown under Request.** Do not choose **HTTP Webhook** under HTTP. HTTP Webhook is an action used to subscribe to another service; it does not create the incoming production URL required in this lab.

**New designer**

- Select **Add a trigger**, search `HTTP`, then select **When an HTTP request is received** under **Request**.

**Classic designer**

- Choose **Skip**, search triggers for `Request`, then select **When an HTTP request is received**.

### Step 2: Parse the browser's JSON request (~10 minutes)

1. Open the trigger.
2. For **Who can trigger the flow?**, choose **Anyone** for this controlled classroom exercise.
3. Leave **Request Body JSON Schema** blank.
4. Add the **Parse JSON** action below the trigger.
5. In **Content**, open the **fx** expression editor and enter:

```text
json(triggerBody())
```

6. Under **Schema**, select **Use sample payload to generate schema** and paste:

```json
{
  "name": "Jane Tan",
  "email": "jane@example.com",
  "subject": "Course enquiry",
  "message": "I would like to know the next available course date."
}
```

7. Select **Done**. Confirm the schema contains the four string properties.

The supplied page sends its JSON as `text/plain` so the browser can make a simple cross-origin request without an OPTIONS preflight. **Parse JSON** converts that text into properties Power Automate can use safely.

> **New/classic difference:** In the new designer, authentication may appear directly on the trigger card. In the classic designer, open the trigger's **…** menu and check **Settings**. If your administrator has removed the **Anyone** option, use the authentication method required by your tenant and test with an authenticated client.

### Step 3: Add the email action (~10 minutes)

1. Below the trigger, select **+** → **Add an action**.
2. Add **Send an email (V2)** from Office 365 Outlook.
3. Configure:
   - **To:** your working training mailbox
   - **Subject:** type `Website enquiry from `, then insert the dynamic value **name**
   - **Body:**

```text
A new enquiry was submitted through the external website.

Name: [name]
Email: [email]
Subject: [subject]
Message: [message]
```

4. Replace each bracketed item with its matching dynamic value from **Parse JSON**.

### Step 4: Return a response to the webpage (~10 minutes)

1. Add another action after the email.
2. Search for `Response` and select **Response** under **Request**.
3. Configure:
   - **Status Code:** `200`
   - **Headers:**

     | Key | Value |
     |---|---|
     | `Content-Type` | `application/json` |
     | `Access-Control-Allow-Origin` | `*` |

   - **Body:**

```json
{
  "success": true,
  "message": "Your enquiry has been received. Our team will reply within one business day."
}
```

> `Access-Control-Allow-Origin: *` is included only so the classroom HTML page can read the response. For a real deployment, replace `*` with the exact approved website origin and put the webhook behind an authenticated server-side API or proxy.

### Step 5: Save and copy the production URL (~5 minutes)

1. Select **Save**.
2. Reopen the trigger if necessary.
3. Copy the **HTTP POST URL**.
4. Paste it temporarily into a private note. Do **not** paste it into this repository or a screenshot shared publicly.

> The URL is generated only after the flow has been saved. It is the Power Automate equivalent of an n8n **Production URL**: every valid POST request can start a real run while the flow is turned on.

### Step 6: Run the supplied enquiry page (~10 minutes)

1. Download or open [`assets/enquiry-form.html`](assets/enquiry-form.html).
2. Open the file in Chrome or Edge.
3. Paste the production URL into **Power Automate webhook URL**.
4. Enter:
   - **Full name:** `Jane Tan`
   - **Email:** `jane@example.com`
   - **Subject:** `Course enquiry`
   - **Message:** `I would like to know the next available course date.`
5. Select **Submit enquiry**.
6. Confirm the page displays the success message returned by Power Automate.
7. Confirm the email arrives with all four values.

### Step 7: Verify the run (~5 minutes)

1. Return to Power Automate.
2. Open **My flows** → `Lab 6A - External Enquiry Webhook`.
3. Open the latest run.
4. Confirm the trigger, email, and Response actions all have green checks.
5. Expand the trigger **Inputs** and verify the submitted JSON.

## Optional command-line test

If the browser reports a CORS or network error, test the flow independently with `curl`. Replace the placeholder with your private URL:

```bash
curl -X POST 'PASTE_YOUR_PRIVATE_URL_HERE' \
  -H 'Content-Type: text/plain;charset=UTF-8' \
  -d '{"name":"Jane Tan","email":"jane@example.com","subject":"Course enquiry","message":"Please contact me."}'
```

If `curl` succeeds but the webpage fails, the flow is working and the remaining issue is browser-origin policy. In production, send the request through a same-origin backend rather than exposing the Power Automate URL in browser code.

---

## Checkpoint
- ✅ The trigger is **When an HTTP request is received** under **Request**
- ✅ The schema contains `name`, `email`, `subject`, and `message`
- ✅ The flow sends an email containing the submitted values
- ✅ The flow returns a `200` JSON response
- ✅ The external page can submit a test enquiry
- ✅ The production URL is kept private

## Troubleshooting

| Problem | Solution |
|---|---|
| Only HTTP, HTTP Webhook, or HTTP + Swagger appears | Select **When an HTTP request is received** under **Request**. The diamond indicates a premium connector. |
| HTTP POST URL is blank | Save the flow once, then reopen the trigger. |
| `401` or `403` | The trigger authentication does not permit the caller, or a tenant policy blocks anonymous requests. Check **Who can trigger the flow?** |
| Browser says `Failed to fetch` | Test with `curl`. If that works, use the Response CORS header for the lab or a server-side proxy for production. |
| Parse JSON fails | Confirm **Content** is the expression token `json(triggerBody())` and the webpage is sending the supplied JSON structure. |
| Email fields are blank | Insert values from **Parse JSON** rather than typing `[name]`, `[email]`, and the other labels as plain text. |
| Flow times out | Power Automate request/response flows must respond within the platform time limit. Keep synchronous work short. |

## Key Takeaways
- **When an HTTP request is received** creates an inbound webhook; **HTTP Webhook** is a different outbound subscription action.
- Saving the flow generates a stable production POST URL.
- **Parse JSON** turns the browser's JSON text into trusted dynamic values.
- The **Response** action lets an external page receive a structured result.
- An anonymous production URL is convenient but sensitive; protect or proxy it for real systems.

## Duration
~55 minutes

## Next Steps
Proceed to [Lab 6B: Webhook Chatbot](../Lab%206B%20-%20Webhook%20Chatbot/index.md) and reuse the same request/response pattern for a chat interface.
