"""Serve unchanged pre-rendered HTML from an immutable, read-only page pack."""
from functools import lru_cache
from http.server import BaseHTTPRequestHandler
from pathlib import Path
import re
import sqlite3
from urllib.parse import parse_qs, unquote, urlsplit
import zlib

PACK = Path(__file__).resolve().parents[1] / '.page-pack/candidates.sqlite'
ROUTE = re.compile(r'/(?:en/)?candidates/(?:[a-z0-9-]+/)*(?:page-[1-9][0-9]*\.html)?\Z')


def connection():
    return sqlite3.connect(PACK.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)


@lru_cache(maxsize=1)
def dictionary():
    db = connection()
    try:
        return db.execute('SELECT value FROM metadata WHERE key=?', ('dictionary',)).fetchone()[0]
    finally:
        db.close()


def route_for(target):
    request = urlsplit(target)
    if request.path.startswith(('/candidates', '/en/candidates')):
        path = request.path
    elif request.path == '/api/candidate-page':
        values = parse_qs(request.query, keep_blank_values=True).get('route', [])
        if len(values) != 1:
            return None
        path = values[0]
    else:
        return None
    # Only known ASCII URL shapes can reach a parameterized database lookup.
    # Reject encoded paths, traversal and ambiguous separators rather than
    # normalizing them into a different candidate's page.
    if unquote(path) != path or '..' in path or '//' in path:
        return None
    if path.endswith('/index.html'):
        path = path.removesuffix('index.html')
    if not path.endswith(('/', '.html')):
        path += '/'
    return path if ROUTE.fullmatch(path) else None


def lookup(path):
    db = connection()
    try:
        row = db.execute('SELECT content,sha256,raw_bytes FROM pages WHERE path=?', (path,)).fetchone()
    finally:
        db.close()
    if not row:
        return None
    decoder = zlib.decompressobj(zdict=dictionary())
    content = decoder.decompress(row[0]) + decoder.flush()
    if len(content) != row[2]:
        raise ValueError('Corrupt candidate page pack')
    return content, '"' + row[1] + '"'


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = route_for(self.path)
        page = lookup(path) if path else None
        if page is None:
            body = b'<!doctype html><html lang="en"><title>404 | Ayiti Sitwayen</title><h1>404</h1><p><a href="/candidates/">Kandida / Candidates</a></p></html>'
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Robots-Tag', 'noindex')
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(body)
            return
        content, etag = page
        unchanged = etag in [x.strip() for x in self.headers.get('If-None-Match', '').split(',')]
        self.send_response(304 if unchanged else 200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'public, max-age=0, must-revalidate')
        self.send_header('Vercel-CDN-Cache-Control', 'public, s-maxage=86400, stale-while-revalidate=604800')
        self.send_header('ETag', etag)
        self.end_headers()
        if not unchanged and self.command != 'HEAD':
            self.wfile.write(content)

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        self.send_response(405)
        self.send_header('Allow', 'GET, HEAD')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
