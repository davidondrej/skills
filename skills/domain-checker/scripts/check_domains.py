#!/usr/bin/env python3
"""Keyless registry RDAP checks. NOT_FOUND does not guarantee registrability."""
import argparse
import concurrent.futures
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request


def get_json(url):
    request = urllib.request.Request(url, headers={"Accept": "application/rdap+json, application/json", "User-Agent": "domain-candidate-check/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def check(domain, services):
    try:
        domain = domain.strip().rstrip('.').encode('idna').decode('ascii').lower()
        labels = domain.split('.')
        if len(labels) != 2 or any(not label or len(label) > 63 or label.startswith('-') or label.endswith('-') or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in label) for label in labels):
            return domain, 'INVALID', 'Use a domain directly under a TLD, such as example.com'
        endpoints = services.get(labels[-1])
        if not endpoints:
            return domain, 'UNKNOWN', 'No IANA RDAP endpoint'
        url = endpoints[0].rstrip('/') + '/domain/' + urllib.parse.quote(domain)
        try:
            result = get_json(url)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raw = error.read()
                if not raw and 'application/rdap+json' in error.headers.get('Content-Type', ''):
                    return domain, 'NOT_FOUND', url
                try:
                    result = json.loads(raw)
                except (ValueError, UnicodeError):
                    return domain, 'UNKNOWN', 'Non-RDAP 404 response'
                if result.get('errorCode') == 404:
                    description = ' '.join(result.get('description', []))
                    if re.search(r'not available for registration|reserved for|reserved name', description, re.I):
                        return domain, 'UNAVAILABLE', description
                    return domain, 'NOT_FOUND', url
            return domain, 'UNKNOWN', 'HTTP ' + str(error.code)
        if result.get('objectClassName') == 'domain' and result.get('ldhName', '').lower() == domain:
            return domain, 'REGISTERED', url
        return domain, 'UNKNOWN', 'Unexpected registry response'
    except Exception as error:
        return domain, 'UNKNOWN', str(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('domains', nargs='+')
    parser.add_argument('--json', action='store_true', help='Include registry URLs')
    args = parser.parse_args()
    started = time.monotonic()
    try:
        bootstrap = get_json('https://data.iana.org/rdap/dns.json')
    except Exception as error:
        parser.exit(1, 'Could not load IANA registry list: ' + str(error) + '\n')
    services = {tld: urls for tlds, urls in bootstrap['services'] for tld in tlds}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda domain: check(domain, services), args.domains))
    if args.json:
        print(json.dumps([dict(domain=d, status=s, detail=e) for d, s, e in results], indent=2))
    else:
        for domain, status, detail in results:
            print(f'{domain:30} {status}' + (f' ({detail})' if status in {'UNKNOWN', 'INVALID', 'UNAVAILABLE'} else ''))
        print(f'\n{time.monotonic()-started:.1f}s. NOT_FOUND = no registry record; purchase availability and premium price are unverified.')


if __name__ == '__main__':
    main()
