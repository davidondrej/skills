---
name: domain-checker
description: Check domain registration in batches using public RDAP APIs, without keys or login. Use only when the user explicitly invokes /domain-checker.
disable-model-invocation: true
---

# Domain checker

Run the bundled Python 3 checker without packages, credentials or a browser. Resolve `scripts/check_domains.py` relative to this SKILL.md, regardless of the working directory.

```sh
python3 <skill-dir>/scripts/check_domains.py example.com example.dev example.ai --json
```

Use complete domains, not bare brand names or URLs; expand each name/TLD combination. Only domains directly under a TLD are supported (e.g. `.com`, `.dev`, `.ai`, `.cloud`), not multi-label suffixes such as `.co.uk`.

The script discovers endpoints through IANA and queries public registries, not registrar shopping carts. Use small batches; concurrency is capped at 4 requests.

## Read the results

JSON output is an array of `{domain, status, detail}` objects. Without `--json`, output is a short list and elapsed time.

- `REGISTERED`: matching registration record found.
- `NOT_FOUND`: registry reports no record. **Not confirmed available:** reservations, registration rules or premium pricing may prevent purchase.
- `UNAVAILABLE`: registry explicitly reports a reservation or registration restriction.
- `UNKNOWN`: unsupported registry, malformed response, timeout or HTTP error. Never treat as available.
- `INVALID`: malformed name or input outside the helper’s scope.

Report briefly as a live snapshot, preserving exact domains and statuses. Explain `UNKNOWN` reasons. On rate limits, wait before retrying; do not increase concurrency. Bootstrap failure exits nonzero: no checks completed.

Read registry error bodies: a 404 may report a reservation, while Verisign may return an empty RDAP 404. The helper handles both but detects only some reservation wording. Neither DNS absence nor RDAP redirect-service errors prove availability.

Use a registrar for final purchase availability or premium quotes. Registration checks do not establish whether another company uses the name or provide trademark clearance.

Sources: [IANA registry discovery](https://data.iana.org/rdap/dns.json), [RDAP HTTP semantics](https://www.rfc-editor.org/rfc/rfc7480.html), [RDAP.org status and rate-limit distinctions](https://about.rdap.org/).
