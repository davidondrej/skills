# Send Email — DeepAPI Endpoint Reference

Generated endpoint reference for the `send-email` rows of the `deepapi` skill router. Bundle version: ee61bded3e6a. This file is always managed — it is refreshed with the bundle even when `../SKILL.md` has been customized.

Shared protocol (environment, auth, idempotency, dry-run, polling, and error handling) lives in `../SKILL.md`. This file carries the full per-endpoint detail.

## Workflow Guidance

Use this reference to draft, review, send, read, and organize agent email.

### Recommended workflows

- Draft for review: create with `send: false`, show the recipient, subject, and body, then send the saved draft only after approval.
- Explicit direct send: use `send: true` only when the user clearly asked to send now.
- Inbox work: list or read messages, draft a context-aware reply, and preserve the thread.
- Identity setup: use the default workspace identity unless the task requires a specific identity or sending domain.

Keep recipients intentional, avoid empty or low-context messages, and never claim delivery from a draft response.

## Endpoint Details

## Send Email

`POST /v1/email/send`

Create an email draft from a workspace email identity; set send=true to send it.

- Capability: `email.send`
- Scope: `email:send`
- Side effects: Creates a draft, or sends an email within the workspace send caps.
- Cost: Uses configured email unit pricing; the route does not accept maxCostUsd. The workspace inbox is billed separately. Check debitMicrousd in the response.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- If email_identity_confirmation_required is returned, show the user the live trial and recurring prices, ask for the sender name, and retry only after approval with confirmInboxCharge=true. Renewal never starts silently: a trial inbox expires unless the user enables renewal (Email page, or PATCH /v1/email/identities/{emailIdentityId} with enableRenewal true).
- Direct sending works out of the box with per-workspace daily/monthly caps that grow with clean sending history. When unsure, keep send=false (draft) and let the user review first.
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.
- Emails from the standard DeepAPI sending domain include a mandatory linked 'Sent via DeepAPI' footer. Verified customer-owned domains do not.
- Attachments, hidden HTML, image HTML, URL shorteners, and high-risk direct sends are blocked by policy.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "to",
    "subject"
  ],
  "properties": {
    "emailIdentityId": {
      "type": "string",
      "description": "Optional DeepAPI email identity id. Omit to use the workspace default."
    },
    "confirmInboxCharge": {
      "type": "boolean",
      "default": false,
      "description": "Required only when no inbox exists. Set true after the user approves the price returned by email_identity_confirmation_required (a first inbox is a $0.10 seven-day trial; renewal stays off until enabled)."
    },
    "username": {
      "type": "string",
      "description": "Optional local part for first inbox setup. Omit for a deepagent001-deepagent999 fallback."
    },
    "displayName": {
      "type": "string",
      "description": "Optional sender display name for first inbox setup. Omit for DeepAgent."
    },
    "to": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "object",
          "additionalProperties": true
        }
      ],
      "description": "One recipient or an array of recipients. Comma-separated strings are rejected. Direct sends allow one recipient."
    },
    "cc": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "object",
          "additionalProperties": true
        }
      ],
      "description": "Use an array for multiple recipients. Comma-separated strings are rejected."
    },
    "bcc": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "object",
          "additionalProperties": true
        }
      ],
      "description": "Use an array for multiple recipients. Comma-separated strings are rejected."
    },
    "replyTo": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "object",
          "additionalProperties": true
        }
      ]
    },
    "subject": {
      "type": "string"
    },
    "text": {
      "type": "string"
    },
    "html": {
      "type": "string"
    },
    "labels": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "attachments": {
      "description": "Present but blocked by MVP outbound email policy."
    },
    "send": {
      "type": "boolean",
      "default": false,
      "description": "Omit or set false for draft mode. Direct send requires approval."
    },
    "mode": {
      "type": "string",
      "enum": [
        "draft",
        "send"
      ],
      "default": "draft",
      "description": "Must agree with send when both fields are present."
    },
    "sendAt": {
      "type": "string",
      "description": "Optional scheduled send time. Scheduled emails use the same safety and quota checks as direct sends."
    },
    "clientId": {
      "type": "string",
      "description": "Optional caller id folded into idempotency."
    },
    "inReplyTo": {
      "type": "string",
      "description": "Optional real reply thread id."
    },
    "dryRun": {
      "type": "boolean",
      "default": false,
      "description": "Zero-spend preview: validate this request and return the exact credit hold it would place (status dry_run plus an estimate object) without reserving, charging, or running anything."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{
  "to": "<email-address>",
  "subject": "Quick hello",
  "text": "Hi, this is a draft from my agent.",
  "send": false
}
```

## Receive Email

`GET /v1/email/messages`

Read messages for a workspace email identity.

- Capability: `email.messages`
- Scope: `email:read`
- Side effects: Reads messages only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.

Query parameters schema:
```json
{
  "type": "object",
  "properties": {
    "emailIdentityId": {
      "type": "string",
      "description": "Optional DeepAPI email identity id. Omit to use the workspace default."
    },
    "limit": {
      "type": "integer",
      "description": "Optional page size."
    },
    "pageToken": {
      "type": "string",
      "description": "Optional pagination token from the previous page response."
    },
    "labels": {
      "type": "string",
      "description": "Optional label filter. Repeat the param to require multiple labels."
    },
    "before": {
      "type": "string",
      "description": "Optional ISO 8601 timestamp; only items before this time."
    },
    "after": {
      "type": "string",
      "description": "Optional ISO 8601 timestamp; only items after this time."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## List Drafts

`GET /v1/email/drafts`

List pending email drafts for a workspace email identity.

- Capability: `email.drafts`
- Scope: `email:read`
- Side effects: Reads drafts only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.

Query parameters schema:
```json
{
  "type": "object",
  "properties": {
    "emailIdentityId": {
      "type": "string",
      "description": "Optional DeepAPI email identity id. Omit to use the workspace default."
    },
    "limit": {
      "type": "integer",
      "description": "Optional page size."
    },
    "pageToken": {
      "type": "string",
      "description": "Optional pagination token from the previous page response."
    },
    "labels": {
      "type": "string",
      "description": "Optional label filter. Repeat the param to require multiple labels."
    },
    "before": {
      "type": "string",
      "description": "Optional ISO 8601 timestamp; only items before this time."
    },
    "after": {
      "type": "string",
      "description": "Optional ISO 8601 timestamp; only items after this time."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## Email Identities

`GET /v1/email/identities`

List the workspace email identities and the emailIdentityId values other email routes accept.

- Capability: `email.identities`
- Scope: `email:read`
- Side effects: Reads email identities only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.
- If the list is empty, create an inbox through the confirmed inbox flow or on the Email page. A disabled inbox must be re-enabled there.
- trial: true means the inbox expires at trialEndsAt unless renewal is enabled (PATCH /v1/email/identities/{emailIdentityId} with the user's approval).

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## Send Draft

`POST /v1/email/drafts/{draftId}/send`

Approve and send an existing draft by draftId after review.

- Capability: `email.drafts.send`
- Scope: `email:send`
- Side effects: Sends the reviewed draft as a real email within the workspace send caps.
- Cost: Uses configured email unit pricing; the route does not accept maxCostUsd. Check debitMicrousd in the response.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- Send a draft only after it has been reviewed (by the user or a supervising agent).
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.
- Emails from the standard DeepAPI sending domain include a mandatory linked 'Sent via DeepAPI' footer. Verified customer-owned domains do not.
- Sending re-checks recipient and content policy against the stored draft; blocked drafts stay drafts.

Request body schema:
```json
{
  "type": "object",
  "properties": {
    "emailIdentityId": {
      "type": "string",
      "description": "Optional DeepAPI email identity id. Omit to use the workspace default."
    },
    "dryRun": {
      "type": "boolean",
      "default": false,
      "description": "Zero-spend preview: validate this request and return the exact credit hold it would place (status dry_run plus an estimate object) without reserving, charging, or running anything."
    }
  },
  "additionalProperties": false
}
```

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "draftId"
  ],
  "properties": {
    "draftId": {
      "type": "string",
      "description": "Draft id returned by POST /v1/email/send or GET /v1/email/drafts."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{}
```

Example path params: `{"draftId":"draft_123"}`

## Add Sending Domain

`POST /v1/email/domains`

Add a customer-owned domain to send email from, and get the DNS records to publish.

- Capability: `email.domains.create`
- Scope: `email:send`
- Side effects: Registers the domain and charges the one-time domain setup fee.
- Cost: One-time $3.125 fee per domain added; the route does not accept maxCostUsd. Verify, list, and remove are free.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- Adding a domain is a one-time charge. Publish the returned dnsRecords at the domain's DNS host, then call POST /v1/email/domains/{domainId}/verify.
- Verified customer-owned domains get 5x the automatic trust-tier send limits by default; explicit manual limits, including 0 (disabled), remain exact.
- Prefer a subdomain like agent.yourdomain.com when the root domain already sends email; the MX record is only required to RECEIVE mail on the domain.
- DNS propagation can take minutes to 48 hours. Re-run verify until verified is true; checking is free.
- Only domains the user controls: you must be able to edit their DNS records.

Request body schema:
```json
{
  "type": "object",
  "required": [
    "domain"
  ],
  "properties": {
    "domain": {
      "type": "string",
      "description": "The domain to send from, e.g. agent.example.com. Use a subdomain when the root domain already handles email."
    },
    "dryRun": {
      "type": "boolean",
      "default": false,
      "description": "Zero-spend preview: validate this request and return the exact credit hold it would place (status dry_run plus an estimate object) without reserving, charging, or running anything."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{
  "domain": "agent.example.com"
}
```

## Sending Domains

`GET /v1/email/domains`

List the workspace's customer-owned sending domains with status and pending DNS records.

- Capability: `email.domains`
- Scope: `email:read`
- Side effects: Reads domains only.
- Cost: Read route returns debitMicrousd 0.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

## Verify Sending Domain

`POST /v1/email/domains/{domainId}/verify`

Re-check the domain's DNS records and refresh its verification status.

- Capability: `email.domains.verify`
- Scope: `email:send`
- Side effects: Triggers a DNS verification check; free and safe to repeat.
- Cost: Verification checks are free and repeatable.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Adding a domain is a one-time charge. Publish the returned dnsRecords at the domain's DNS host, then call POST /v1/email/domains/{domainId}/verify.
- Verified customer-owned domains get 5x the automatic trust-tier send limits by default; explicit manual limits, including 0 (disabled), remain exact.
- Prefer a subdomain like agent.yourdomain.com when the root domain already sends email; the MX record is only required to RECEIVE mail on the domain.
- DNS propagation can take minutes to 48 hours. Re-run verify until verified is true; checking is free.
- Only domains the user controls: you must be able to edit their DNS records.

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "domainId"
  ],
  "properties": {
    "domainId": {
      "type": "string",
      "description": "Domain id returned by POST /v1/email/domains or GET /v1/email/domains."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{}
```

Example path params: `{"domainId":"email_domain_123"}`

## Remove Sending Domain

`DELETE /v1/email/domains/{domainId}`

Remove a custom sending domain and suspend the identities on it.

- Capability: `email.domains.delete`
- Scope: `email:send`
- Side effects: Deletes the domain, suspends its sender identities, and promotes another active identity as default when needed.
- Cost: Removal is free.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- Removing a domain suspends every sender identity on it; existing threads stop receiving replies there.
- Confirm with the user before removing a domain that is actively sending.

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "domainId"
  ],
  "properties": {
    "domainId": {
      "type": "string",
      "description": "Domain id returned by POST /v1/email/domains or GET /v1/email/domains."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example path params: `{"domainId":"email_domain_123"}`

## Create Email Identity

`POST /v1/email/identities`

Create a sender identity (optionally on a verified custom domain) and make it the workspace default.

- Capability: `email.identities.create`
- Scope: `email:send`
- Side effects: Starts a paid inbox period or switches the default to an existing address (free).
- Cost: A workspace's first inbox is a $0.10 seven-day trial (renewal off until enabled); later inboxes are $5 per 30 days and require purchased credits. Switching to an existing address is free.
- Idempotency-Key: required
- Polling: This route returns a terminal envelope directly.

Safety:
- Creating a new inbox requires the user's approval of the live price, then confirmInboxCharge=true. Promoting an existing address is free.
- A trial inbox expires at trialEndsAt unless renewal is enabled via PATCH /v1/email/identities/{emailIdentityId} — never enable it without the user's explicit approval.
- A custom domain must be verified first: GET /v1/email/domains shows status.
- The new identity becomes the workspace default sender; previous addresses keep receiving replies.

Request body schema:
```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "description": "Optional local part: 3-30 lowercase letters/digits, starting with a letter. Omit for deepagent001-deepagent999."
    },
    "displayName": {
      "type": "string",
      "description": "Optional sender display name. Omit for DeepAgent."
    },
    "confirmInboxCharge": {
      "type": "boolean",
      "default": false,
      "description": "Required when this creates a new inbox. Set true only after the user approves the live price (a first inbox is a $0.10 seven-day trial; later inboxes are $5 per 30 days)."
    },
    "domain": {
      "type": "string",
      "description": "Optional verified custom domain from GET /v1/email/domains. Omit to use the standard DeepAPI sending domain."
    },
    "dryRun": {
      "type": "boolean",
      "default": false,
      "description": "Zero-spend preview: validate this request and return the exact credit hold it would place (status dry_run plus an estimate object) without reserving, charging, or running anything."
    }
  },
  "additionalProperties": false
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{
  "username": "assistant",
  "displayName": "Assistant",
  "domain": "agent.example.com",
  "confirmInboxCharge": true
}
```

## Update Email Identity

`PATCH /v1/email/identities/{emailIdentityId}`

Update an email identity: change its sender display name, or enable the recurring renewal that keeps a trial inbox.

- Capability: `email.identities.update`
- Scope: `email:send`
- Side effects: Updates the sender display name (free), or arms the $5 every-30-days renewal on a trial inbox.
- Cost: Display-name updates and enabling renewal are free at call time; an enabled inbox then renews for $5 every 30 days.
- Idempotency-Key: not required
- Polling: This route returns a terminal envelope directly.

Safety:
- enableRenewal arms a recurring $5/30-day charge — set it only after the user explicitly approves.
- Use this route for display-name-only changes. Address changes use POST /v1/email/identities and may create a paid inbox.

Request body schema:
```json
{
  "type": "object",
  "properties": {
    "displayName": {
      "type": "string",
      "description": "New sender display name. The email address stays unchanged."
    },
    "enableRenewal": {
      "type": "boolean",
      "description": "Set true to keep a trial inbox: arms the $5 every-30-days renewal, billed from when the trial ends. Requires purchased credits. Never enable without the user's explicit approval."
    }
  },
  "additionalProperties": false
}
```

Path parameters schema:
```json
{
  "type": "object",
  "required": [
    "emailIdentityId"
  ],
  "properties": {
    "emailIdentityId": {
      "type": "string",
      "description": "Identity id returned by GET /v1/email/identities."
    }
  }
}
```

Response schema:
```json
{
  "$ref": "#/components/schemas/PublicEnvelope"
}
```

Example request body:
```json
{
  "displayName": "Research Assistant"
}
```

Example path params: `{"emailIdentityId":"email_identity_456"}`
