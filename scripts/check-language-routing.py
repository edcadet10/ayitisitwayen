"""Exercise the geographic language policy against every translated sitemap URL."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'vercel.json').read_text(encoding='utf-8'))
RULES = [r for r in CONFIG['redirects'] if ':page(' in r['source']]
assert len(RULES) == 4


def matches(condition, headers, cookies):
    values = cookies if condition['type'] == 'cookie' else headers
    value = values.get(condition['key'])
    return value is not None and re.fullmatch(condition.get('value', '.*'), value) is not None


def redirect(path, country, choice=None, destination='document'):
    headers = {'sec-fetch-dest': destination}
    if country is not None:
        headers['x-vercel-ip-country'] = country
    cookies = {'ayiti_lang': choice} if choice is not None else {}
    for rule in RULES:
        prefix, pattern = rule['source'].split(':page', 1)
        match = re.fullmatch(re.escape(prefix) + pattern, path)
        if not match:
            continue
        if not all(matches(c, headers, cookies) for c in rule.get('has', [])):
            continue
        if any(matches(c, headers, cookies) for c in rule.get('missing', [])):
            continue
        assert rule['permanent'] is False
        return rule['destination'].replace(':page', match[1])
    return None


def language(path):
    return 'en' if path.startswith('/en/') else 'ht'


def final(path, country, choice=None):
    visited = set()
    while path not in visited:
        visited.add(path)
        target = redirect(path, country, choice)
        if target is None:
            assert len(visited) <= 2, visited
            return path
        path = target
    raise AssertionError(('redirect loop', visited))


all_routes = set()
for filename in ('sitemap-pages.xml', 'sitemap-candidates.xml',
                 'sitemap-candidate-directory.xml', 'sitemap-candidate-archives.xml'):
    root = ET.parse(ROOT / filename).getroot()
    for entry in root:
        for element in entry:
            if element.tag.endswith('loc'):
                all_routes.add(urlsplit(element.text).path)
routes = {route for route in all_routes
          if (route.removeprefix('/en') if route.startswith('/en/') else '/en' + route) in all_routes}
assert len(routes) > 25000

checks = 0
for route in routes:
    assert language(final(route, 'HT')) == 'ht', route
    assert language(final(route, 'US')) == 'en', route
    assert language(final(route, 'HT', 'en')) == 'en', route
    assert language(final(route, 'US', 'ht')) == 'ht', route
    # A direct fetch remains the native URL in either language. Routing depends
    # on navigation context, never on a crawler name or user-agent allowlist.
    assert redirect(route, 'US', destination='empty') is None, route
    checks += 5

samples = ('/', '/education.html', '/about.html', '/elections.html', '/candidates/',
           '/candidates/c-e8698b3339a756e88e60/',
           '/elections/analysis/martelly-bodeau-sanctions-un-election-rule/')
for country in ('HT', 'US', 'FR', 'CA', None):
    for choice in (None, 'ht', 'en', 'invalid', 'en-US'):
        expected = choice if choice in ('ht', 'en') else ('ht' if country == 'HT' else 'en')
        for route in samples:
            for start in (route, '/en' + route):
                assert language(final(start, country, choice)) == expected
                checks += 1

for resource in ('/styles.css', '/script.js', '/assets/candidates/etzer-emile-320.webp',
                 '/audio/11_eleksyon.mp3', '/api/candidate-page', '/data/candidate-public/all.json',
                 '/sitemap-pages.xml', '/elections/analysis/feed.xml',
                 '/en/elections/analysis/feed.xml', '/robots.txt'):
    assert redirect(resource, 'US') is None, resource
    assert redirect(resource, 'HT', 'en') is None, resource

print(json.dumps({'result': 'pass', 'translated_routes': len(routes), 'policy_cases': checks,
                  'country': 'HT -> ht; other/unknown -> en', 'manual_choice': 'wins',
                  'native_fetches_and_assets': 'unchanged', 'redirect_loops': 0}))
