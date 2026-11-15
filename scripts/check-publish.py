"""Check lossless published pages, URL coverage and actual HTTP behavior."""
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('candidate_endpoint', ROOT / 'api/candidate-page.py')
endpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(endpoint)
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def check():
    db = endpoint.connection()
    routes = {row[0] for row in db.execute('SELECT path FROM pages')}
    db.close()
    expected = {'/candidates/president/', '/en/candidates/president/'}
    for name in ('candidates', 'candidate-directory', 'candidate-archives'):
        tree = ET.fromstring((ROOT / 'dist' / ('sitemap-' + name + '.xml')).read_bytes())
        expected.update(url.findtext(NS + 'loc').removeprefix('https://www.ayitisitwayen.org') for url in tree.findall(NS + 'url'))
    assert routes == expected, (len(routes), len(expected))
    # Every page, including retained candidates and deep archives, must restore
    # the build-time bytes and not require a request to the original source site.
    for path in sorted(routes):
        body, etag = endpoint.lookup(path)
        assert etag == '"' + hashlib.sha256(body).hexdigest() + '"', path
        assert body.startswith(b'<!doctype html>'), path
        assert b'<link rel="canonical"' in body, path
    invalid = ['/candidates/../data/', '/candidates/%2e%2e/', '/candidates//',
               '/api/candidate-page', '/api/candidate-page?route=',
               '/api/candidate-page?route=/candidates/&route=/en/candidates/',
               '/api/candidate-page?route=https://evil.invalid/', '/api/candidate-page?route=/candidates/%252e%252e/']
    for value in invalid:
        assert endpoint.route_for(value) is None, value
    assert endpoint.route_for('/candidates/?q=Etzer&route=/en/candidates/') == '/candidates/'
    assert endpoint.route_for('/api/candidate-page?route=/en/candidates/') == '/en/candidates/'
    class QuietHandler(endpoint.handler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    def request(path, method='GET', headers=None):
        try:
            with urlopen(Request(base + path, method=method, headers=headers or {})) as response:
                return response.status, response.headers, response.read()
        except HTTPError as error:
            return error.code, error.headers, error.read()
    try:
        probes = ['/candidates/', '/en/candidates/', '/candidates/c-73cb6b93ef8b5e7e9d1a/',
                  '/candidates/all/page-447.html', '/api/candidate-page?route=/candidates/']
        for path in probes:
            status, headers, body = request(path)
            assert status == 200, (path, status)
            assert body == endpoint.lookup(endpoint.route_for(path))[0]
            assert 's-maxage=86400' in headers['Vercel-CDN-Cache-Control']
            assert 'noindex' not in headers.get('X-Robots-Tag', '')
            assert request(path, 'HEAD')[2] == b''
            assert request(path, headers={'If-None-Match': headers['ETag']})[0] == 304
        status, headers, body = request('/candidates/does-not-exist/')
        assert status == 404 and headers['Cache-Control'] == 'no-store'
        assert request('/candidates/', 'POST')[0] == 405
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            assert all(status == 200 for status, _, _ in executor.map(request, probes * 8))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    forbidden = ['.github', 'scripts', 'editorial', 'data/candidates', 'data/candidate-editorial.json', '.page-pack', 'api']
    assert all(not (ROOT / 'dist' / name).exists() for name in forbidden)
    report = json.loads((ROOT / '.page-pack/build-report.json').read_text())
    assert report['candidate_pack_bytes'] < 100_000_000
    assert report['candidate_html_reduction_percent'] >= 80
    print(json.dumps({'result': 'pass', 'all_html_pages_restored_and_hashed': len(routes),
                      'sitemap_route_coverage': 'exact', 'http_get_head_304_404_405': 'pass',
                      'concurrent_requests': 40, 'ambiguous_or_invalid_routes_rejected': len(invalid),
                      'development_files_excluded': True}))


if __name__ == '__main__':
    check()
