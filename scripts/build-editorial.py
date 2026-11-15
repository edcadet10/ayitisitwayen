"""Render bilingual editorial articles, their Elections hub, and the About page.

Only entries explicitly marked published are emitted. No external content is
fetched and no candidate, claim or draft is automatically approved.
"""
import argparse
import hashlib
from datetime import date
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://www.ayitisitwayen.org'
LANGUAGES = ('ht', 'en')


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', chr(92)+'u003c').replace('>', chr(92)+'u003e').replace('&', chr(92)+'u0026')


def article_paragraphs(article):
    if article.get('format') == 'narrative':
        return article['paragraphs']
    return [paragraph for section in article['sections'] for paragraph in section['paragraphs']]


def article_text(article, lang):
    values = [article['title'][lang], article['description'][lang]]
    if article.get('format') != 'narrative':
        values.append(article['takeaway'][lang])
        values.extend(section['heading'][lang] for section in article['sections'])
    values.extend(paragraph['text'][lang] for paragraph in article_paragraphs(article))
    return '\n\n'.join(values)


def word_count(article, lang):
    # Conservative space-separated count includes headline, deck, and narrative.
    # Shared navigation, references, byline, and related links are outside the piece.
    return len(article_text(article, lang).split())


def audio_url(recording):
    return recording['path'] + '?v=' + recording['file_sha256'][:12]


def prefix(lang):
    return '/en/' if lang == 'en' else '/'


def route(lang, slug=''):
    return prefix(lang) + 'elections/analysis/' + (slug + '/' if slug else '')


def bilingual(value):
    assert isinstance(value, dict) and set(value) == set(LANGUAGES)
    assert all(isinstance(value[lang], str) and value[lang].strip() for lang in LANGUAGES)


def validate(data, about, people):
    date.fromisoformat(data['updated_at'])
    date.fromisoformat(about['updated_at'])
    for value in data['copy'].values():
        bilingual(value)
    slugs = set()
    for source in data['sources'].values():
        parsed = urlparse(source['url'])
        assert parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
        bilingual(source['title'])
        bilingual(source['note'])
        date.fromisoformat(source['checked_at'])
        if source.get('published_at'):
            assert date.fromisoformat(source['published_at']) <= date.fromisoformat(source['checked_at'])
    for article in data['articles']:
        slug = article['slug']
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) and slug not in slugs
        slugs.add(slug)
        assert article['status'] in ('draft', 'published')
        assert article['kind'] in ('analysis', 'opinion')
        assert article['candidate_ids'] and len(article['candidate_ids']) == len(set(article['candidate_ids']))
        assert all(cid in people for cid in article['candidate_ids'])
        assert date.fromisoformat(article['published_at']) <= date.fromisoformat(article['updated_at']) <= date.fromisoformat(data['updated_at'])
        for key in ('title', 'description'):
            bilingual(article[key])
        if article.get('format') == 'narrative':
            assert article['paragraphs']
            for paragraph in article['paragraphs']:
                assert paragraph['kind'] in ('record', 'interpretation', 'argument', 'questions', 'scope')
                assert paragraph['kind'] != 'argument' or article['kind'] == 'opinion'
        else:
            bilingual(article['takeaway'])
            for section in article['sections']:
                bilingual(section['heading'])
                assert section['paragraphs']
        for paragraph in article_paragraphs(article):
            bilingual(paragraph['text'])
            assert all(sid in data['sources'] for sid in paragraph['sources'])
            if paragraph.get('kind') == 'record':
                assert paragraph['sources'], (slug, 'Documented claims require citations')
        assert any(paragraph['sources'] for paragraph in article_paragraphs(article)), (slug, 'No factual sources')
        for lang in LANGUAGES:
            assert word_count(article, lang) <= data['word_limit'] <= 500, (slug, lang, word_count(article, lang), 'Article exceeds word limit')
        if article.get('series'):
            assert article['series'] in data['series'] and article['series_position'] >= 1
        if article.get('audio'):
            audio=article['audio']
            assert audio['language']=='ht' and audio['provider']=='ElevenLabs'
            assert re.fullmatch(r'/audio/editorial/[a-z0-9-]+\.mp3',audio['path'])
            file=ROOT/audio['path'].lstrip('/')
            assert file.is_file() and file.stat().st_size>1000
            assert hashlib.sha256(file.read_bytes()).hexdigest()==audio['file_sha256']
            assert hashlib.sha256(article_text(article,'ht').encode('utf-8')).hexdigest()==audio['article_sha256'],(slug,'Narration is stale; regenerate after text changes')


def load():
    data = json.loads((ROOT / 'data/candidate-editorial.json').read_text(encoding='utf-8'))
    about = json.loads((ROOT / 'data/about.json').read_text(encoding='utf-8'))
    registry = json.loads((ROOT / 'data/candidates/registry.json').read_text(encoding='utf-8'))
    people = {person['id']: person for person in registry['candidates'] + registry.get('retained_candidates', [])}
    portraits = json.loads((ROOT / 'data/candidates/enrichment.json').read_text(encoding='utf-8'))['profiles']
    validate(data, about, people)
    return data, about, people, portraits


def link(url, text, css=''):
    return f'<a href="{escape(url, quote=True)}"' + (f' class="{css}"' if css else '') + f'>{escape(text)}</a>'


def time(value):
    return f'<time datetime="{value}">{value}</time>'


def shell(lang, title, description, path, body, modified, copy, graph=None, image=None, article=False):
    ht = path.removeprefix('/en') if lang == 'en' else path
    en = '/en' + ht
    alternate = en if lang == 'ht' else ht
    nav = ''.join(link(prefix(lang) + target, copy[key][lang]) for key, target in [('elections', 'elections.html'), ('candidates', 'candidates/'), ('education', 'education.html'), ('about', 'about.html')])
    org = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'Ayiti Sitwayen', 'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/logo.png'}}
    page = {'@type': 'WebPage', '@id': SITE + path + '#webpage', 'url': SITE + path, 'name': title, 'description': description, 'inLanguage': lang, 'dateModified': modified, 'isPartOf': {'@id': SITE + '/#website'}}
    metadata = {'@context': 'https://schema.org', '@graph': [org, page] + (graph or [])}
    image = image or SITE + '/logo.png'
    author_meta = '<meta name="author" content="Ayiti Sitwayen">' if article else ''
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Ayiti Sitwayen</title><meta name="description" content="{escape(description, quote=True)}">{author_meta}<meta name="theme-color" content="#ffffff"><meta name="robots" content="max-image-preview:large"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{escape(image, quote=True)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{escape(image, quote=True)}"><link rel="canonical" href="{SITE}{path}"><link rel="alternate" hreflang="ht" href="{SITE}{ht}"><link rel="alternate" hreflang="en" href="{SITE}{en}"><link rel="alternate" hreflang="x-default" href="{SITE}{ht}"><link rel="icon" href="/favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@200..900&display=swap" rel="stylesheet"><link rel="stylesheet" href="/styles.css?v=3"><link rel="stylesheet" href="/theme.css?v=3"><link rel="stylesheet" href="/editorial.css?v=2"><script type="application/ld+json">{compact(metadata)}</script></head><body class="editorial-site"><a class="skip-link" href="#kontni">{escape(copy['skip'][lang])}</a><nav class="navbar"><div class="container"><a class="nav-brand" href="{prefix(lang)}"><img class="logo" src="/logo.webp" alt="Ayiti Sitwayen" width="300" height="200"></a><button class="nav-toggle" aria-label="{escape(copy['menu'][lang], quote=True)}" aria-expanded="false" aria-controls="navLinks">☰</button><div class="nav-links" id="navLinks">{nav}<a class="lang-switch" href="{alternate}" lang="{'en' if lang == 'ht' else 'ht'}">{'EN' if lang == 'ht' else 'HT'}</a></div></div></nav>{body}<footer class="editorial-footer container"><a href="{prefix(lang)}">Ayiti Sitwayen</a><div>{link(prefix(lang)+'about.html#mission', 'Misyon nou' if lang == 'ht' else 'Our mission')} {link(prefix(lang)+'about.html#contact', copy['correction'][lang])} {link(prefix(lang)+'privacy.html', 'Konfidansyalite' if lang == 'ht' else 'Privacy')}</div></footer><script src="/editorial.js?v=2" defer></script></body></html>'''


def breadcrumb(lang, copy, article_title=None):
    return '<nav class="editorial-breadcrumb" aria-label="' + ('Chemen paj la' if lang == 'ht' else 'Breadcrumb') + '">' + link(prefix(lang) + 'elections.html', copy['elections'][lang]) + '<span aria-hidden="true">/</span>' + (link(route(lang), copy['title'][lang]) if article_title else '<span aria-current="page">' + escape(copy['title'][lang]) + '</span>') + ('<span aria-hidden="true">/</span><span aria-current="page">' + escape(article_title) + '</span>' if article_title else '') + '</nav>'


def picture(cid, lang, people, portraits, hero=False):
    image = portraits.get(cid, {}).get('portrait')
    if not image:
        return ''
    person = people[cid]
    srcset = ', '.join(f'{v["path"]} {v["width"]}w' for v in image['variants'])
    return '<figure class="editorial-portrait"><img src="' + escape(image['path'], quote=True) + '" srcset="' + escape(srcset, quote=True) + '" sizes="(max-width:650px) 140px, 260px" alt="' + escape(person['name'], quote=True) + '" width="320" height="400" style="object-position:' + escape(image.get('position', '50% 50%'), quote=True) + '" ' + ('fetchpriority="high"' if hero else 'loading="lazy"') + ' decoding="async"><figcaption>' + link(image['source_url'], image['credit']) + '</figcaption></figure>'


def card(article, lang, copy, people, portraits, featured=False):
    label = copy[article['kind']][lang]
    photos = ''.join(picture(cid, lang, people, portraits, featured) for cid in article['candidate_ids'])
    candidates = ' '.join(article['candidate_ids'])
    search = ' '.join([article['title'][lang], article['description'][lang]] + [people[cid]['name'] for cid in article['candidate_ids']])
    return f'''<article class="editorial-card{' editorial-featured' if featured else ''}" data-editorial-kind="{article['kind']}" data-editorial-candidates="{candidates}" data-editorial-search="{escape(search, quote=True)}"><div class="editorial-card-copy"><p class="editorial-meta"><span class="editorial-type {article['kind']}">{escape(label)}</span>{time(article['published_at'])}</p><h2>{link(route(lang, article['slug']), article['title'][lang])}</h2><p>{escape(article['description'][lang])}</p>{link(route(lang, article['slug']), copy['read'][lang]+' →', 'editorial-read')}</div><div class="editorial-card-portraits">{photos}</div></article>'''


def method(lang, copy):
    return f'''<aside class="editorial-method" id="method"><h2>{escape(copy['method'][lang])}</h2><p>{escape(copy['method_text'][lang])}</p><p>{escape(copy['ai_note'][lang])}</p>{link(prefix(lang)+'about.html#standards', copy['correction'][lang]+' / '+copy['method'][lang])}</aside>'''


def index_page(lang, data, people, portraits):
    copy = data['copy']
    articles = sorted([article for article in data['articles'] if article['status'] == 'published'], key=lambda a: a['published_at'], reverse=True)
    controls = ''.join(f'<button type="button" data-editorial-filter="{kind}" aria-pressed="{str(kind == "all").lower()}">{escape(copy[kind][lang])}</button>' for kind in ('all', 'analysis', 'opinion'))
    cards = ''.join(card(article, lang, copy, people, portraits, i == 0) for i, article in enumerate(articles))
    covered_ids = {cid for article in articles for cid in article['candidate_ids']}
    options = '<option value="">'+escape(copy['all_candidates'][lang])+'</option>'+''.join('<option value="'+cid+'">'+escape(people[cid]['name'])+'</option>' for cid in sorted(covered_ids,key=lambda cid:people[cid]['name']))
    tools = '<div class="editorial-tools" hidden><div class="editorial-search-fields"><label for="editorial-search">'+escape(copy['search_articles'][lang])+'<input id="editorial-search" type="search" autocomplete="off" maxlength="200"></label><label for="editorial-candidate">'+escape(copy['choose_candidate'][lang])+'<select id="editorial-candidate">'+options+'</select></label></div><div class="editorial-filters" role="group" aria-label="'+escape(copy['filter_label'][lang],quote=True)+'">'+controls+'</div></div>'
    body = f'''<main id="kontni" class="editorial-main container">{breadcrumb(lang, copy)}<header class="editorial-intro"><p class="editorial-kicker">Ayiti Sitwayen · {escape(copy['elections'][lang])}</p><h1>{escape(copy['title'][lang])}</h1><p class="editorial-lead">{escape(copy['intro'][lang])}</p><p class="editorial-status">{escape(copy['status_note'][lang])}</p></header><div class="editorial-definitions"><p><strong>{escape(copy['analysis'][lang])}</strong> {escape(copy['analysis_note'][lang])}</p><p><strong>{escape(copy['opinion'][lang])}</strong> {escape(copy['opinion_note'][lang])}</p></div>{tools}<p class="editorial-count" role="status" aria-live="polite" data-count-pattern="{escape(copy['result_count'][lang], quote=True)}">{escape(copy['result_count'][lang].format(count=len(articles)))}</p><div class="editorial-grid">{cards}</div><p class="editorial-empty" hidden>{escape(copy['no_results'][lang])}</p>{method(lang, copy)}</main>'''
    graph = [{'@type': 'CollectionPage', '@id': SITE + route(lang) + '#collection', 'url': SITE + route(lang), 'name': copy['title'][lang], 'hasPart': [{'@type': 'Article', 'url': SITE + route(lang, a['slug']), 'headline': a['title'][lang], 'genre': copy[a['kind']][lang]} for a in articles]}]
    return shell(lang, copy['title'][lang], copy['intro'][lang], route(lang), body, data['updated_at'], copy, graph)


def article_page(lang, article, data, people, portraits):
    copy = data['copy']
    source_ids = list(dict.fromkeys(sid for paragraph in article_paragraphs(article) for sid in paragraph['sources']))
    numbers = {sid: i for i, sid in enumerate(source_ids, 1)}
    sections = []
    groups = [{'kind':'record','paragraphs':article['paragraphs']}] if article.get('format') == 'narrative' else article['sections']
    for i, section in enumerate(groups, 1):
        paragraphs = []
        for paragraph in section['paragraphs']:
            citations = ''.join(' ' + link('#source-' + sid, '[' + str(numbers[sid]) + ']', 'editorial-citation') for sid in paragraph['sources'])
            paragraphs.append('<p>' + escape(paragraph['text'][lang]) + citations + '</p>')
        if article.get('format') == 'narrative':
            sections.append('<div class="editorial-story">'+''.join(paragraphs)+'</div>')
        else:
            sections.append(f'<section id="section-{i}" class="editorial-prose-section"><p class="editorial-kicker">{escape(copy[section["kind"]][lang])}</p><h2>{escape(section["heading"][lang])}</h2>{"".join(paragraphs)}</section>')
    sources = ''.join('<li id="source-' + sid + '"><p>' + link(data['sources'][sid]['url'], data['sources'][sid]['title'][lang]) + '</p><p class="editorial-source-meta">' + escape(data['sources'][sid]['publisher']) + (' · ' + time(data['sources'][sid]['published_at']) if data['sources'][sid].get('published_at') else '') + '</p><p>' + escape(data['sources'][sid]['note'][lang]) + '</p></li>' for sid in source_ids)
    profile_links = ''.join(link(prefix(lang) + 'candidates/' + cid + '/', people[cid]['name'] + ' →', 'editorial-profile-link') for cid in article['candidate_ids'])
    photos = ''.join(picture(cid, lang, people, portraits, True) for cid in article['candidate_ids'])
    others = [a for a in data['articles'] if a['status']=='published' and a['slug']!=article['slug']]
    others.sort(key=lambda a: (bool(set(a['candidate_ids']) & set(article['candidate_ids'])), a['published_at']), reverse=True)
    related = ''.join('<li>' + link(route(lang, other['slug']), copy[other['kind']][lang] + ' · ' + other['title'][lang]) + '</li>' for other in others[:6])
    related += '<li>' + link(route(lang), copy['browse_all'][lang]) + '</li>'

    count=word_count(article,lang)
    series=''
    if article.get('series'):
        siblings=sorted([a for a in data['articles'] if a.get('series')==article['series'] and a['status']=='published'],key=lambda a:a['series_position'])
        series='<nav class="editorial-series" aria-label="'+escape(copy['series'][lang],quote=True)+'"><h2>'+escape(data['series'][article['series']]['title'][lang])+'</h2><ol>'+''.join('<li>'+('<span aria-current="page">'+escape(a['title'][lang])+'</span>' if a['slug']==article['slug'] else link(route(lang,a['slug']),a['title'][lang]))+'</li>' for a in siblings)+'</ol></nav>'
    takeaway='' if article.get('format')=='narrative' else '<p class="editorial-takeaway">'+escape(article['takeaway'][lang])+'</p>'
    audio_html=''
    if article.get('audio'):
        recording=article['audio']
        audio_label='Koute atik la · Kreyòl' if lang=='ht' else 'Listen in Haitian Creole'
        audio_credit='Vwa jenere ak ElevenLabs.' if lang=='ht' else 'AI narration generated with ElevenLabs.'
        transcript_label='Li tèks atik la' if lang=='ht' else 'Read the Haitian Creole transcript'
        transcript_link='#article-text' if lang=='ht' else route('ht',article['slug'])+'#article-text'
        audio_html='<section class="editorial-audio" aria-labelledby="audio-title"><h2 id="audio-title">'+audio_label+'</h2><audio controls preload="none" aria-label="'+audio_label+'"><source src="'+audio_url(recording)+'" type="audio/mpeg"></audio><p>'+audio_credit+' '+link(transcript_link,transcript_label)+'</p></section>'
    body = f'''<main id="kontni" class="editorial-main container">{breadcrumb(lang, copy, article['title'][lang])}<article class="editorial-article" data-word-count="{count}"><header class="editorial-article-header"><div><p class="editorial-meta"><span class="editorial-type {article['kind']}">{escape(copy[article['kind']][lang])}</span><span>{escape(copy['published'][lang])}: {time(article['published_at'])}</span><span>{count} {escape(copy['words'][lang])}</span></p><h1>{escape(article['title'][lang])}</h1><p class="editorial-lead">{escape(article['description'][lang])}</p><p class="editorial-byline">{link(prefix(lang)+'about.html', 'Ayiti Sitwayen')} · {escape(copy['updated'][lang])}: {time(article['updated_at'])}</p><p class="editorial-kind-note">{escape(copy[article['kind']+'_note'][lang])}</p></div><div class="editorial-article-portraits">{photos}</div></header>{takeaway}{audio_html}<div class="editorial-prose" id="article-text">{''.join(sections)}</div></article><div class="editorial-prose">{series}<section class="editorial-sources" aria-labelledby="sources"><h2 id="sources">{escape(copy['sources'][lang])}</h2><ol>{sources}</ol></section><aside class="editorial-method"><p>{escape(copy['ai_note'][lang])}</p>{link(prefix(lang)+'about.html#contact', copy['correction'][lang])}</aside><section class="editorial-profile-records"><h2>{escape(copy['profile'][lang])}</h2><p class="editorial-status">{escape(copy['status_note'][lang])}</p>{profile_links}</section><section class="editorial-related"><h2>{escape(copy['related_articles'][lang])}</h2><ul>{related}</ul></section></div></main>'''
    path = route(lang, article['slug'])
    image = portraits.get(article['candidate_ids'][0], {}).get('portrait')
    image_url = SITE + image['variants'][-1]['path'] if image else SITE + '/logo.png'
    graph = [{'@type': 'Article', '@id': SITE + path + '#article', 'url': SITE + path, 'mainEntityOfPage': {'@id': SITE + path + '#webpage'}, 'headline': article['title'][lang], 'description': article['description'][lang], 'articleBody': '\n\n'.join(p['text'][lang] for p in article_paragraphs(article)), 'wordCount':count, 'image': [image_url], 'inLanguage': lang, 'genre': copy[article['kind']][lang], 'articleSection': copy['title'][lang], 'datePublished': article['published_at'], 'dateModified': article['updated_at'], 'author': {'@type': 'Organization', 'name': 'Ayiti Sitwayen', 'url': SITE + prefix(lang) + 'about.html'}, 'publisher': {'@id': SITE + '/#organization'}, 'about': [{'@type': 'Person', 'name': people[cid]['name'], 'identifier': cid, 'url': SITE + prefix(lang) + 'candidates/' + cid + '/'} for cid in article['candidate_ids']], 'citation': [data['sources'][sid]['url'] for sid in source_ids]}, {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': name, 'item': SITE + target} for i, (name, target) in enumerate([(copy['elections'][lang], prefix(lang)), (copy['title'][lang], route(lang)), (article['title'][lang], path)], 1)]}]
    if article.get('audio'):
        recording=article['audio']
        graph[0]['audio']={'@type':'AudioObject','contentUrl':SITE+audio_url(recording),'encodingFormat':'audio/mpeg','inLanguage':'ht','duration':'PT'+str(recording['duration_seconds'])+'S','transcript':article_text(article,'ht')}
    return shell(lang, article['title'][lang], article['description'][lang], path, body, article['updated_at'], copy, graph, image_url, True)


def about_page(lang, about, copy):
    pillars = ''.join('<article class="editorial-pillar"><h3>' + link(prefix(lang) + pillar['route'], pillar['title'][lang]) + '</h3><p>' + escape(pillar['text'][lang]) + '</p></article>' for pillar in about['pillars'])
    standards = ''.join('<li>' + escape(value[lang]) + '</li>' for value in about['standards'])
    labels = {'ht': ['Non ou', 'Imel ou', 'Mesaj ou', 'Prepare yon imel', 'Bouton sa a ouvri aplikasyon imel ou ak mesaj la pou ou ka verifye l epi voye l.'], 'en': ['Your name', 'Your email', 'Your message', 'Prepare an email', 'This opens your email application with the message so you can review and send it.']}[lang]
    body = f'''<main id="kontni" class="editorial-main editorial-about container"><header class="editorial-intro"><p class="editorial-kicker">Ayiti Sitwayen</p><h1>{escape(about['heading'][lang])}</h1><p class="editorial-lead">{escape(about['intro'][lang])}</p><div class="editorial-about-actions">{link(prefix(lang)+'candidates/', copy['candidates'][lang]+' →', 'editorial-read')} {link(route(lang), copy['title'][lang]+' →', 'editorial-read')}</div></header><section id="about" class="editorial-about-section"><h2>{escape(about['identity_title'][lang])}</h2><p>{escape(about['identity'][lang])}</p></section><section id="mission" class="editorial-about-section"><p class="editorial-kicker">{escape(about['mission_title'][lang])}</p><h2 class="editorial-mission">{escape(about['mission'][lang])}</h2><div class="editorial-pillars">{pillars}</div></section><section id="standards" class="editorial-about-section"><h2>{escape(about['standards_title'][lang])}</h2><ul class="editorial-standards">{standards}</ul></section><section id="research" class="editorial-about-section"><h2>{escape(about['origins_title'][lang])}</h2><p>{escape(about['origins'][lang])}</p>{link(prefix(lang)+'research.html', 'Gade travay rechèch la →' if lang == 'ht' else 'Explore the research →')}</section><section id="team" class="editorial-about-section"><h2>{escape(about['contribute_title'][lang])}</h2><p>{escape(about['contribute'][lang])}</p></section><section id="contact" class="editorial-about-section"><h2>{escape(about['contact_title'][lang])}</h2><div class="editorial-contact"><div><p>{link('mailto:'+about['email'], about['email'])}</p><p>{link('mailto:research@ayitisitwayen.org', 'research@ayitisitwayen.org')}</p><p>{link('mailto:partnerships@ayitisitwayen.org', 'partnerships@ayitisitwayen.org')}</p></div><form id="editorial-contact-form"><label for="contact-name">{labels[0]}</label><input id="contact-name" name="name" autocomplete="name" required maxlength="160"><label for="contact-email">{labels[1]}</label><input id="contact-email" type="email" name="email" autocomplete="email" required maxlength="254"><label for="contact-message">{labels[2]}</label><textarea id="contact-message" name="message" rows="5" required maxlength="12000"></textarea><button type="submit">{labels[3]}</button><p class="editorial-source-meta">{labels[4]}</p></form></div></section></main>'''
    return shell(lang, about['title'][lang], about['description'][lang], prefix(lang)+'about.html', body, about['updated_at'], copy)


def outputs():
    data, about, people, portraits = load()
    for lang in LANGUAGES:
        yield ROOT / route(lang).strip('/') / 'index.html', index_page(lang, data, people, portraits)
        for article in data['articles']:
            if article['status'] == 'published':
                yield ROOT / route(lang, article['slug']).strip('/') / 'index.html', article_page(lang, article, data, people, portraits)
        yield ROOT / (prefix(lang)+'about.html').strip('/'), about_page(lang, about, data['copy'])


def reject_stale_routes(root, expected):
    # A formerly published draft must not remain reachable in static hosting.
    # Withdrawal requires an explicit reviewed removal; never delete files here.
    existing = set()
    for lang in LANGUAGES:
        existing.update((root / route(lang).strip('/')).rglob('*.html'))
    stale = sorted(existing - set(expected))
    if stale:
        raise ValueError('Unpublished or stale editorial HTML remains: ' + ', '.join(str(path.relative_to(root)) for path in stale))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    count = 0
    pages = list(outputs())
    reject_stale_routes(ROOT, [path for path, _ in pages])
    for path, content in pages:
        count += 1
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8', newline='\n')
    if args.check and changed:
        raise SystemExit('Editorial/About pages need regeneration: ' + ', '.join(changed))
    print(f'Editorial/About pages: {count}; {len(changed)} changed.')
