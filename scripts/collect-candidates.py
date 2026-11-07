"""Read only the public CEP dashboard endpoints. Discovery never publishes content."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import threading
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://tableau.cephaiti.ht'
lock = threading.Lock()
last_request = 0.0

def get_json(path):
    global last_request
    for attempt in range(3):
        with lock:
            delay = max(0, .3 - (time.monotonic() - last_request))
            if delay: time.sleep(delay)
            last_request = time.monotonic()
        request = Request(BASE + path, headers={'User-Agent': 'Mozilla/5.0 (compatible; AyitiSitwayen public registry review)', 'Accept': 'application/json', 'Referer': BASE + '/'})
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError):
            if attempt == 2: raise
            time.sleep(2 ** attempt)

def collect(cache):
    summary = get_json('/api/tableau')
    first = get_json('/api/tableau/candidats')
    total, size = first['total'], first['pageSize']
    assert total == summary['total'] and total > 0 and size > 0
    cache.mkdir(parents=True, exist_ok=True)
    marker = hashlib.sha256(json.dumps({p['title']: p['count'] for p in summary['postes']}, sort_keys=True).encode()).hexdigest()
    # Never reuse an old reading just because counts stayed the same.
    cache = cache / (marker[:16] + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
    cache.mkdir(exist_ok=True)
    def page(number):
        path = cache / f'{number}.json'
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else (first if number == 1 else get_json('/api/tableau/candidats?page=' + str(number)))
        assert data['page'] == number and data['pageSize'] == size and data['total'] == total, 'Registry changed during pagination; retain the old reviewed site.'
        assert len(data['items']) == min(size, total - (number - 1) * size)
        for item in data['items']:
            assert set(item) == {'nom', 'prenom', 'sexe', 'poste', 'position', 'structure', 'localite'}
            assert isinstance(item['localite'], list) and item['nom'] and item['prenom']
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return number, data['items']
    pages = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(page, n) for n in range(1, math.ceil(total / size) + 1)]
        for future in as_completed(futures):
            number, items = future.result(); pages[number] = items
            if len(pages) % 100 == 0: print(f'Collected {len(pages)} pages', flush=True)
    rows = [row for number in sorted(pages) for row in pages[number]]
    assert len(rows) == total
    expected = {p['title']: p['count'] for p in summary['postes']}
    observed = {office: sum(row['poste'] == office for row in rows) for office in expected}
    assert observed == expected, 'Office totals do not reconcile.'
    after = get_json('/api/tableau')
    assert {p['title']: p['count'] for p in after['postes']} == expected, 'Registry totals changed while collecting; retry before publication.'
    return {'source_name': 'Conseil Électoral Provisoire (CEP / KEP)', 'source_url': BASE + '/', 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'source_generated_at': summary.get('generatedAtUtc'), 'total': total, 'office_counts': observed, 'status': 'preliminary', 'records': rows}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'editorial/candidate-review-queue.json')
    parser.add_argument('--cache', type=Path, default=ROOT / '.candidate-collection-cache')
    args = parser.parse_args()
    try:
        result = collect(args.cache)
    except Exception as error:
        result = {'status': 'collection_failed', 'error': str(error), 'retrieved_at': datetime.now(timezone.utc).isoformat()}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        raise
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'total': result['total'], 'office_counts': result['office_counts'], 'output': str(args.output)}, ensure_ascii=True))

if __name__ == '__main__': main()
