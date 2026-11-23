# Send Email — DeepAPI Endpoint Reference

Generated endpoint reference for the `send-email` rows of the `deepapi` skill router. Bundle version: 528f2c511503.

Shared protocol (auth, CLI, polling, dry-run, errors) lives in `../SKILL.md`. All responses use the standard DeepAPI JSON envelope (`requestId`, `status`, `output`, `next`, `error`, `balance`).

## Workflow Guidance

Use this reference to draft, review, send, read, and organize agent email.

### Recommended workflows

- Draft for review: create with `send: false`, show the recipient, subject, and body, then send the saved draft only after approval.
- Explicit direct send: use `send: true` only when the user clearly asked to send now.
- Inbox work: list or read messages, draft a context-aware reply, and preserve the thread.
- Identity setup: use the default workspace identity unless the task requires a specific identity or sending domain.

Keep recipients intentional, avoid empty or low-context messages, and never claim delivery from a draft response.

## Endpoint Details

### Send Email — `POST /v1/email/send`
Create an email draft from a workspace email identity; set send=true to send it. (`email.send` · scope `email:send` · idempotency required)
- Body: `emailIdentityId` (string), `confirmInboxCharge` (boolean=false), `username` (string), `displayName` (string), `*to` (any), `cc` (any), `bcc` (any), `replyTo` (any), `*subject` (string), `text` (string), `html` (string), `labels` (array), `attachments` (any), `send` (boolean=false), `mode` (string=draft|send), `sendAt` (string), `clientId` (string), `inReplyTo` (string)
- Example: `{"to":"<email-address>","subject":"Quick hello","text":"Hi, this is a draft from my agent.","send":false}`
- If email_identity_confirmation_required is returned, show the user the live trial and recurring prices, ask for the sender name, and retry only after approval with confirmInboxCharge=true. Renewal never starts silently: a trial inbox expires unless the user enables renewal (Email page, or PATCH /v1/email/identities/{emailIdentityId} with enableRenewal true).
- Direct sending works out of the box with per-workspace daily/monthly caps that grow with clean sending history. When unsure, keep send=false (draft) and let the user review first.
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.
- Emails from the standard DeepAPI sending domain include a mandatory linked 'Sent via DeepAPI' footer. Verified customer-owned domains do not.
- Attachments, hidden HTML, image HTML, URL shorteners, and high-risk direct sends are blocked by policy.

### Receive Email — `GET /v1/email/messages`
Read messages for a workspace email identity. (`email.messages` · scope `email:read` · free)
- Query: `emailIdentityId` (string), `limit` (integer), `pageToken` (string), `labels` (string), `before` (string), `after` (string)
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.

### List Drafts — `GET /v1/email/drafts`
List pending email drafts for a workspace email identity. (`email.drafts` · scope `email:read` · free)
- Query: `emailIdentityId` (string), `limit` (integer), `pageToken` (string), `labels` (string), `before` (string), `after` (string)
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.

### Email Identities — `GET /v1/email/identities`
List the workspace email identities and the emailIdentityId values other email routes accept. (`email.identities` · scope `email:read` · free)
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.
- If the list is empty, create an inbox through the confirmed inbox flow or on the Email page. A disabled inbox must be re-enabled there.
- trial: true means the inbox expires at trialEndsAt unless renewal is enabled (PATCH /v1/email/identities/{emailIdentityId} with the user's approval).

### Send Draft — `POST /v1/email/drafts/{draftId}/send`
Approve and send an existing draft by draftId after review. (`email.drafts.send` · scope `email:send` · idempotency required)
- Body: `emailIdentityId` (string)
- Path: `*draftId` (string)
- Example: `{}`
- Send a draft only after it has been reviewed (by the user or a supervising agent).
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.
- Emails from the standard DeepAPI sending domain include a mandatory linked 'Sent via DeepAPI' footer. Verified customer-owned domains do not.
- Sending re-checks recipient and content policy against the stored draft; blocked drafts stay drafts.

### Add Sending Domain — `POST /v1/email/domains`
Add a customer-owned domain to send email from, and get the DNS records to publish. (`email.domains.create` · scope `email:send` · idempotency required)
- Body: `*domain` (string)
- Example: `{"domain":"agent.example.com"}`
- Adding a domain is a one-time charge. Publish the returned dnsRecords at the domain's DNS host, then call POST /v1/email/domains/{domainId}/verify.
- Verified customer-owned domains get 5x the automatic trust-tier send limits by default; explicit manual limits, including 0 (disabled), remain exact.
- Prefer a subdomain like agent.yourdomain.com when the root domain already sends email; the MX record is only required to RECEIVE mail on the domain.
- DNS propagation can take minutes to 48 hours. Re-run verify until verified is true; checking is free.
- Only domains the user controls: you must be able to edit their DNS records.

### Sending Domains — `GET /v1/email/domains`
List the workspace's customer-owned sending domains with status and pending DNS records. (`email.domains` · scope `email:read` · free)
- Do not pass inboxId or inbox_id; use emailIdentityId or the workspace default.

### Verify Sending Domain — `POST /v1/email/domains/{domainId}/verify`
Re-check the domain's DNS records and refresh its verification status. (`email.domains.verify` · scope `email:send` · free)
- Path: `*domainId` (string)
- Adding a domain is a one-time charge. Publish the returned dnsRecords at the domain's DNS host, then call POST /v1/email/domains/{domainId}/verify.
- Verified customer-owned domains get 5x the automatic trust-tier send limits by default; explicit manual limits, including 0 (disabled), remain exact.
- Prefer a subdomain like agent.yourdomain.com when the root domain already sends email; the MX record is only required to RECEIVE mail on the domain.
- DNS propagation can take minutes to 48 hours. Re-run verify until verified is true; checking is free.
- Only domains the user controls: you must be able to edit their DNS records.

### Remove Sending Domain — `DELETE /v1/email/domains/{domainId}`
Remove a custom sending domain and suspend the identities on it. (`email.domains.delete` · scope `email:send` · free)
- Path: `*domainId` (string)
- Removing a domain suspends every sender identity on it; existing threads stop receiving replies there.
- Confirm with the user before removing a domain that is actively sending.

### Create Email Identity — `POST /v1/email/identities`
Create a sender identity (optionally on a verified custom domain) and make it the workspace default. (`email.identities.create` · scope `email:send` · idempotency required)
- Body: `username` (string), `displayName` (string), `confirmInboxCharge` (boolean=false), `domain` (string)
- Example: `{"username":"assistant","displayName":"Assistant","domain":"agent.example.com","confirmInboxCharge":true}`
- Creating a new inbox requires the user's approval of the live price, then confirmInboxCharge=true. Promoting an existing address is free.
- A trial inbox expires at trialEndsAt unless renewal is enabled via PATCH /v1/email/identities/{emailIdentityId} — never enable it without the user's explicit approval.
- A custom domain must be verified first: GET /v1/email/domains shows status.
- The new identity becomes the workspace default sender; previous addresses keep receiving replies.

### Update Email Identity — `PATCH /v1/email/identities/{emailIdentityId}`
Update an email identity: change its sender display name, or enable the recurring renewal that keeps a trial inbox. (`email.identities.update` · scope `email:send` · free)
- Body: `displayName` (string), `enableRenewal` (boolean)
- Path: `*emailIdentityId` (string)
- Example: `{"displayName":"Research Assistant"}`
- enableRenewal arms a recurring $5/30-day charge — set it only after the user explicitly approves.
- Use this route for display-name-only changes. Address changes use POST /v1/email/identities and may create a paid inbox.

### Find Email — `POST /v1/email/find`
Find one person's professional email address from their name plus a company domain or company name. Returns the most likely address with a confidence score, catch-all status, verification result, and the public sources it was seen on. (`email.find` · scope `email:find` · ~$0.0735 per found address, nothing when none is found, cap $0.0735)
- Body: `*firstName` (string), `*lastName` (string), `domain` (string), `company` (string)
- Example: `{"firstName":"Avery","lastName":"Chen","domain":"example.com","maxCostUsd":"0.0735"}`
- Provide one company identifier: use domain whenever you know it; otherwise use company. A supplied domain controls the lookup and company is ignored. Neither field is individually mandatory, but at least one is required.
- One person per call. Loop over your list and keep each lookup separate.
- output.email is null when no address was found. That result is free and is not a failure — do not retry it with a different spelling more than once.
- Treat output.confidence as directional, not a guarantee. Verify the address before sending.
- Treat acceptAll true as unverified. The domain accepts mail for any address, so the mailbox itself is unproven.
- The full address is returned once. Replaying the original request returns it masked, because DeepAPI does not keep the address after answering.
- Only contact people for legitimate business reasons, and honour opt-outs. A 451 email_find_opted_out means never contact this person again.

### Verify Email — `POST /v1/email/verify`
Check one email address and return a standardized deliverability verdict, score, and compact evidence flags. (`email.verify` · scope `email:verify` · ~$0.03675 per conclusive result, cap $0.03675)
- Body: `*email` (string)
- Example: `{"email":"<email-address>","maxCostUsd":"0.03675"}`
- Process one email address or company domain per call.
- A deliverable verdict is evidence, not permission to contact someone.
- Treat verdict risky or acceptAll true as uncertain. Do not present it as a confirmed mailbox.
- Unknown and disposable results are successful free outcomes. Do not retry them repeatedly.

### Enrich Email — `POST /v1/email/enrich`
Enrich one known professional email with a compact person and employment profile. Personal phone, home-location, avatar, biography, and social-feed data are omitted. (`email.enrich` · scope `email:enrich` · ~$0.0147 per complete result, cap $0.0147)
- Body: `*email` (string)
- Example: `{"email":"<email-address>","maxCostUsd":"0.0147"}`
- Process one email address or company domain per call.
- Use professional enrichment only for a legitimate purpose and honour privacy requests.
- matchStatus partial or not_found is a successful free outcome. Do not invent missing fields.
- Do not infer sensitive traits from the returned professional profile.

### Enrich Company — `POST /v1/company/enrich`
Enrich one company domain with a compact company profile: identity, classification, location, size, and freshness. (`company.enrich` · scope `company:enrich` · ~$0.0147 per complete result, cap $0.0147)
- Body: `*domain` (string)
- Example: `{"domain":"example.com","maxCostUsd":"0.0147"}`
- Process one email address or company domain per call.
- Use the company's canonical public domain when possible. URLs are reduced to their hostname.
- matchStatus partial or not_found is a successful free outcome. Do not invent missing fields.
