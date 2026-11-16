"""Render the reviewed bilingual Ayiti country and civic-resource guide."""
import argparse
import importlib.util
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def outputs():
    data = json.loads((ROOT / 'data/ayiti-guide.json').read_text(encoding='utf-8'))
    spec = importlib.util.spec_from_file_location('editorial_shell', ROOT / 'scripts/build-editorial.py')
    editorial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(editorial)
    copy = json.loads((ROOT / 'data/candidate-editorial.json').read_text(encoding='utf-8'))['copy']
    guide = data['guide']
    result = {}
    for lang in ('ht', 'en'):
        prefix = '/en/' if lang == 'en' else '/'
        path = prefix + 'ayiti.html'
        text = lambda key: escape(guide[key][lang])
        sections = []
        for section in guide['sections']:
            links = []
            for item in section['links']:
                assert item['url'].startswith('/') and not item['url'].startswith('//')
                local = prefix + item['url'].lstrip('/')
                target = ROOT / local.lstrip('/')
                packed_directory = local in ('/candidates/president/', '/en/candidates/president/')
                assert packed_directory or target.is_file() or (target / 'index.html').is_file(), local
                links.append('<li>' + editorial.link(local, item['label'][lang]) + '</li>')
            sections.append('<section class="editorial-about-section"><h3>' + escape(section['title'][lang])
                            + '</h3><p>' + escape(section['text'][lang]) + '</p><ul class="editorial-standards">'
                            + ''.join(links) + '</ul></section>')
        sources = ''.join('<li>' + editorial.link(source['url'], source['title'][lang]) + '</li>' for source in guide['sources'])
        body = f'''<main id="kontni" class="container editorial-main">
<nav class="editorial-breadcrumb" aria-label="{'Chemen paj la' if lang == 'ht' else 'Breadcrumb'}">{editorial.link(prefix, 'Ayiti Sitwayen')}<span aria-hidden="true">/</span><span aria-current="page">Ayiti</span></nav>
<header><p class="editorial-meta">{text('kicker')}</p><h1>{text('heading')}</h1><p>{text('intro')}</p><p class="editorial-meta">{text('reviewed_label')}: <time datetime="{data['reviewed_at']}">{data['reviewed_at']}</time></p></header>
<section class="editorial-about-section"><h2>{text('identity_heading')}</h2><p>{text('identity_text')} <a class="editorial-citation" href="#guide-sources">[1]</a></p></section>
<section class="editorial-about-section"><h2>{text('explore_heading')}</h2>{''.join(sections)}</section>
<section class="editorial-method" id="guide-sources"><h2>{text('sources_heading')}</h2><p>{text('sources_intro')}</p><ol>{sources}</ol></section></main>'''
        graph = [
            {'@type': 'Country', '@id': editorial.SITE + '/ayiti.html#country',
             'name': 'Ayiti' if lang == 'ht' else 'Haiti', 'alternateName': ['Ayiti', 'Haïti', 'Haiti'],
             'identifier': 'HT', 'subjectOf': {'@id': editorial.SITE + path + '#webpage'}},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Ayiti Sitwayen', 'item': editorial.SITE + prefix},
                {'@type': 'ListItem', 'position': 2, 'name': 'Ayiti', 'item': editorial.SITE + path}]},
        ]
        result[ROOT / path.lstrip('/')] = editorial.shell(lang, guide['title'][lang], guide['description'][lang], path,
                                                          body, data['reviewed_at'], copy, graph)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    for path, content in outputs().items():
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            changed.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.write_text(content, encoding='utf-8', newline='\n')
    if args.check and changed:
        raise SystemExit('Ayiti guide needs regeneration: ' + ', '.join(changed))
    print(f'Ayiti guide: 2 language pages; {len(changed)} changed.')
