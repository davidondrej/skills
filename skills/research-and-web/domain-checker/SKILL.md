---
name: domain-checker
description: Check domain registration in batches through public registry RDAP APIs, without API keys or login. Use for domain availability checks, checking candidate domains, or keyless domain lookup from a CLI. Screens registration status, not brand conflicts, trademark clearance, or guaranteed purchase availability.
---

# Domain checker

Run the bundled Python 3 checker. No packages, credentials or browser needed.
Resolve `scripts/check_domains.py` relative to this SKILL.md, regardless of the current working directory.

```sh
python3 <skill-dir>/scripts/check_domains.py example.com example.dev example.ai --json
```

Pass complete domains, not bare brand names or URLs. For a name across several extensions, expand them into explicit domains. The helper supports domains directly under a TLD, including `.com`, `.dev`, `.ai` and `.cloud`; multi-label suffixes such as `.co.uk` are outside its scope.

The script discovers registry endpoints from IANA and runs up to 4 requests concurrently. Use small batches. It sends domain queries to public registries, not registrar shopping carts.

## Read the results

JSON output is an array of `{domain, status, detail}` objects. Without `--json`, output is a short list and elapsed time.

- `REGISTERED`: matching registration record found.
- `NOT_FOUND`: registry reports no record. **Do not call this confirmed available.** Reserved names, registration rules and premium pricing may still prevent purchase.
- `UNAVAILABLE`: registry explicitly reports a reservation or registration restriction.
- `UNKNOWN`: unsupported registry, malformed response, timeout or HTTP error. Never convert this to available.
- `INVALID`: malformed name or input outside the helper’s supported scope.

Report results briefly, noting they are a live snapshot. Keep exact domains with their statuses. For `UNKNOWN`, explain the returned reason; on rate limits, wait before retrying rather than increasing concurrency. Bootstrap failure exits nonzero and means no checks completed.

Read registry error bodies. A 404 can contain an explicit reservation; Verisign may return an empty RDAP 404. The helper handles both. It detects some explicit reservation messages, not every registry’s wording. DNS absence and RDAP redirect-service errors are not evidence of availability.

For final purchase availability or a premium quote, use a registrar check. Domain registration status does not establish whether another company uses the name.

Sources: [IANA registry discovery](https://data.iana.org/rdap/dns.json), [RDAP HTTP semantics](https://www.rfc-editor.org/rfc/rfc7480.html), [RDAP.org status and rate-limit distinctions](https://about.rdap.org/).
