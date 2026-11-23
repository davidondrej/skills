# Browse Web — DeepAPI Endpoint Reference

Generated endpoint reference for the `browse-web` rows of the `deepapi` skill router. Bundle version: 528f2c511503.

Shared protocol (auth, CLI, polling, dry-run, errors) lives in `../SKILL.md`. All responses use the standard DeepAPI JSON envelope (`requestId`, `status`, `output`, `next`, `error`, `balance`).

## Workflow Guidance

Use this reference for interactive public-web work (clicking, navigating, and extracting dynamic pages).

### Recommended workflow

1. Prefer the scraping workflow for static reading and extraction.
2. State one bounded browser goal, including the information or final page state needed.
3. Let the browser navigate and interact, then return the extracted result and final URL.
4. Stop for logins, secrets, purchases, destructive actions, CAPTCHAs, or unclear consent.

## Endpoint Details

### Browser Task — `POST /v1/browser/act`
Give a real cloud browser a plain-English goal and get the result back. Built for pages an agent has to operate, not just read: filters and sortable tables, JavaScript pagination, dropdowns, date pickers and sliders, iframes and shadow DOM, infinite scroll, site search, store locators, and comparing several pages in one run. Public web only — no logins, purchases, or CAPTCHA solving. (`browser.act` · scope `browser:act` · idempotency required · async · ~$0.125-$0.75 per task depending on steps, cap $1.25)
- Body: `*task` (string), `startUrl` (string), `maxSteps` (integer=25), `outputSchema` (object), `allowedDomains` (array)
- Example: `{"task":"Find the support email address on example.com.","startUrl":"https://example.com","maxCostUsd":"1.25"}`
- Public web only: tasks that need logins, credentials, account creation, CAPTCHA solving, or purchases are rejected.
- Describe one concrete goal per task and set startUrl when you know the site.
