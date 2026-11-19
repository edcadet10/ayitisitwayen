"""Publish only public assets; store pre-rendered candidate HTML in a compact pack.

The existing renderer remains the source of every HTML byte. The request handler
only looks up and decompresses a page; it does not depend on an external service.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PACK = ROOT / '.page-pack' / 'candidates.sqlite'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def public_files():
    # An allowlist keeps research inputs, build scripts and review material out
    # of public hosting, even if someone adds another source folder later.
    for suffix in ('html', 'css', 'js', 'png', 'webp', 'svg', 'ico', 'xml'):
        yield from ROOT.glob('*.' + suffix)
    yield ROOT / 'robots.txt'
    yield ROOT / 'f3a81c9e2b7d4f60a1c5e8d2b4f7a913.txt'
    yield from (ROOT / 'en').glob('*.html')
    for folder in ('assets', 'audio', '.well-known', 'data/candidate-public'):
        yield from (ROOT / folder).rglob('*')
    for folder in ('elections/analysis', 'en/elections/analysis'):
        for suffix in ('html', 'xml'):
            yield from (ROOT / folder).rglob('*.' + suffix)


def build():
    assert DIST.resolve() == ROOT.resolve() / 'dist'
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    PACK.parent.mkdir(exist_ok=True)
    temporary = PACK.with_suffix('.building')
    temporary.unlink(missing_ok=True)
    builder = module('candidate_builder', 'build-candidates.py')
    registry, enrichment = builder.load()
    dictionary = b'\n'.join(
        builder.profile_page(lang, registry['candidates'][-1], registry, enrichment).encode('utf-8')
        for lang in ('ht', 'en')
    )[-32768:]
    db = sqlite3.connect(temporary)
    db.execute('PRAGMA page_size=4096')
    db.execute('PRAGMA journal_mode=OFF')
    db.execute('PRAGMA synchronous=OFF')
    db.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY, value BLOB NOT NULL) WITHOUT ROWID')
    db.execute('INSERT INTO metadata VALUES(?,?)', ('dictionary', dictionary))
    # Large compressed pages belong in table leaves. WITHOUT ROWID also puts
    # their payload in index branches, increasing overflow and pack size.
    db.execute('CREATE TABLE pages(path TEXT PRIMARY KEY NOT NULL, content BLOB NOT NULL, sha256 TEXT NOT NULL, raw_bytes INTEGER NOT NULL)')
    count = raw_bytes = 0
    try:
        for path, content in builder.outputs(registry, enrichment):
            raw = content.encode('utf-8')
            if path.suffix == '.html':
                route = '/' + path.relative_to(ROOT).as_posix()
                route = route.removesuffix('index.html')
                compressor = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS, zdict=dictionary)
                compressed = compressor.compress(raw) + compressor.flush()
                decoder = zlib.decompressobj(zdict=dictionary)
                assert decoder.decompress(compressed) + decoder.flush() == raw, route
                db.execute('INSERT INTO pages VALUES(?,?,?,?)', (route, compressed, hashlib.sha256(raw).hexdigest(), len(raw)))
                count += 1
                raw_bytes += len(raw)
            else:
                # Public search/source catalogues and all existing sitemaps keep
                # their URLs. Do not materialize thousands of loose HTML files.
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        db.commit()
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    finally:
        db.close()
    temporary.replace(PACK)
    subprocess.run([sys.executable, str(ROOT / 'scripts/build-sitemaps.py')], check=True, cwd=ROOT)
    paths = set(public_files())
    for path in sorted(paths):
        if not path.is_file():
            continue
        destination = DIST / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    static_files = [p for p in DIST.rglob('*') if p.is_file()]
    static_bytes = sum(p.stat().st_size for p in static_files)
    report = {
        'format': 1, 'candidate_html_pages': count, 'candidate_html_bytes_before': raw_bytes,
        'candidate_pack_bytes': PACK.stat().st_size, 'static_files': len(static_files),
        'static_bytes': static_bytes, 'total_content_bytes': static_bytes + PACK.stat().st_size,
        'candidate_html_reduction_percent': round(100 * (1 - PACK.stat().st_size / raw_bytes), 2),
        'all_candidate_html_roundtrips_identical': True,
    }
    (ROOT / '.page-pack/build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    build()
