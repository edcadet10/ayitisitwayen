"""Collect public CEP changes into an editorial artifact; never edit public copy."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
API = 'https://cephaiti.ht/wp-json/wp/v2/posts?per_page=30&_fields=id,date,modified,link,title,content'


def fetch(url):
    request = Request(url, headers={'User-Agent': 'AyitiSitwayen-ElectionReview/1.0', 'Accept': '*/*'})
    with urlopen(request, timeout=35) as response:
        if urlparse(response.url).hostname not in {'cephaiti.ht', 'www.cephaiti.ht'}:
            raise ValueError('Unexpected source host')
        body = response.read(12_000_001)
        if len(body) > 12_000_000:
            raise ValueError('Source exceeds the bounded collection size; review manually')
        return body


class CalendarLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        href = urljoin('https://cephaiti.ht/', attrs.get('href', ''))
        parsed = urlparse(href)
        if tag == 'a' and parsed.hostname in {'cephaiti.ht', 'www.cephaiti.ht'} and parsed.path.lower().endswith('.pdf') and 'calendrier' in parsed.path.lower():
            self.urls.add(href)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='editorial/cep-review-queue.json')
    parser.add_argument('--write-baseline', action='store_true', help='Only after an editor reviewed the sources; does not change reviewed dates.')
    args = parser.parse_args()
    baseline_path = ROOT / 'editorial/approved-sources.json'
    baseline = json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else {'posts': {}, 'documents': {}}
    result = {'fetched_at': datetime.now(timezone.utc).isoformat(), 'status': 'unreviewed', 'notices': [], 'documents': [], 'errors': [], 'publication': 'No public content changed.'}
    current = {'posts': {}, 'documents': {}}
    try:
        posts = json.loads(fetch(API))
        if not isinstance(posts, list) or not posts:
            raise ValueError('The public feed did not return a nonempty list')
        for post in posts:
            record = {'id': post['id'], 'modified': post['modified'], 'content_hash': digest(post['content']['rendered'].encode('utf-8'))}
            current['posts'][str(post['id'])] = record
            if baseline['posts'].get(str(post['id'])) != record:
                result['notices'].append({**record, 'published_metadata': post['date'], 'title': post['title']['rendered'], 'source_url': post['link'], 'source_html': post['content']['rendered'], 'review_status': 'unreviewed'})
    except Exception as error:
        result['errors'].append({'source': API, 'error_type': type(error).__name__, 'message': str(error)[:240]})
    try:
        links = CalendarLinks()
        links.feed(fetch('https://cephaiti.ht/').decode('utf-8', errors='replace'))
        if not links.urls:
            raise ValueError('No official calendar link was found')
        for url in sorted(links.urls):
            body = fetch(url)
            if not body.startswith(b'%PDF-'):
                raise ValueError('Calendar response is not a PDF')
            value = digest(body)
            current['documents'][url] = value
            if baseline['documents'].get(url) != value:
                result['documents'].append({'source_url': url, 'sha256': value, 'review_status': 'unreviewed', 'instruction': 'Review the PDF visually; a new URL or changed bytes do not approve new dates.'})
    except Exception as error:
        result['errors'].append({'source': 'official calendar', 'error_type': type(error).__name__, 'message': str(error)[:240]})
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.write_baseline:
        if result['errors']:
            raise SystemExit('Collection failed; the approved baseline was not changed.')
        baseline_path.parent.mkdir(exist_ok=True)
        baseline_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Unreviewed notices: {len(result['notices'])}; changed calendars: {len(result['documents'])}; collection errors: {len(result['errors'])}. Public content unchanged.")
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
