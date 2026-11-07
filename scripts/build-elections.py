"""Render reviewed election information into both static language versions.

Run after editing data/elections.json. --check verifies generated files in CI.
No source is fetched or automatically approved by this script.
"""
import argparse
import json
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/elections.json').read_text(encoding='utf-8'))
COPY = DATA['copy']
SITE = 'https://www.ayitisitwayen.org/'
MONTHS = {
    'ht': ['Janvye', 'Fevriye', 'Mas', 'Avril', 'Me', 'Jen', 'Jiyè', 'Out', 'Septanm', 'Oktòb', 'Novanm', 'Desanm'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
}
MILESTONES = {m['id']: m for m in DATA['milestones']}
TARGETS = ['index.html', 'voting.html', 'candidates.html', 'electoral-process.html', 'diaspora.html', 'voting-day.html', 'education.html', 'political-parties.html']


def text(key, lang):
    return escape(COPY[key][lang])


def date_text(value, lang):
    d = date.fromisoformat(value)
    return (f'{d.day} {MONTHS[lang][d.month - 1]} {d.year}' if lang == 'ht'
            else f'{MONTHS[lang][d.month - 1]} {d.day}, {d.year}')


def time(value, lang):
    return f'<time datetime="{value}">{date_text(value, lang)}</time>'


def anchor(url, label, cls=''):
    return f'<a href="{escape(url, quote=True)}"' + (f' class="{cls}"' if cls else '') + f'>{escape(label)}</a>'


def source_credit(lang, published=None):
    label = 'Sous' if lang == 'ht' else 'Source'
    name = 'Konsèy Elektoral Pwovizwa (KEP)' if lang == 'ht' else 'Conseil Électoral Provisoire (CEP)'
    return f'<p class="election-source-credit">{label}: {name}' + (f' · {time(published, lang)}' if published else '') + '</p>'


def freshness(lang):
    return f'''<div class="election-freshness" data-reviewed-date="{DATA['reviewed_at']}" data-stale-days="{DATA['stale_after_days']}">
<p class="election-review-date">{text('reviewed', lang)}: {time(DATA['reviewed_at'], lang)} · KEP / CEP</p>
<p class="election-stale" role="status" hidden>{text('stale', lang)}</p>
</div>'''


def summary(lang, home=False, candidate=False):
    hub = '/en/elections.html' if lang == 'en' else '/elections.html'
    label = 'Eleksyon 2026–2027' if lang == 'ht' else 'Elections 2026–2027'
    first = 'Premye tou' if lang == 'ht' else 'First round'
    second = 'Dezyèm tou + lokal' if lang == 'ht' else 'Second round + local'
    registration = 'Enskripsyon elektè' if lang == 'ht' else 'Voter registration'
    until = 'Dat limit nan kalandriye a' if lang == 'ht' else 'Scheduled deadline'
    dates = f'<p><span>{registration} · {until}</span><strong>{time(MILESTONES["voter-registration"]["date"], lang)}</strong></p><p><span>{first}</span><strong>{time(MILESTONES["first-round"]["date"], lang)}</strong></p><p><span>{second}</span><strong>{time(MILESTONES["second-round"]["date"], lang)}</strong></p>'
    if candidate:
        candidate_labels = {
            'ht': ['Enskripsyon sou entènèt: prezidan, senatè, depite', 'Depo dokiman: prezidan, senatè, depite', 'Enskripsyon sou entènèt: lokal', 'Depo dokiman: lokal'],
            'en': ['Online registration: president, senators, deputies', 'Document filing: president, senators, deputies', 'Online registration: local', 'Document filing: local'],
        }
        dates = ''.join(f'<p><span>{escape(label)}</span><strong>{time(MILESTONES[id]["date"], lang)}</strong></p>' for id, label in zip(['candidate-national', 'documents-national', 'candidate-local', 'documents-local'], candidate_labels[lang]))
    return f'''<section class="election-summary{' election-summary-home' if home else ''}" aria-label="{label}">
<p class="election-kicker">{label} · {text('scheduled', lang)}</p>
<div class="election-summary-dates{' election-candidate-dates' if candidate else ''}">{dates}</div>
<div class="election-actions">{anchor(hub, COPY['hub'][lang], 'election-button')} {anchor('/en/centres.html' if lang == 'en' else '/centres.html', COPY['find'][lang], 'election-button election-button-secondary')}</div>
{freshness(lang)}
</section>'''


def audio(lang):
    # Narration is Kreyòl in either language. Its transcript remains available.
    return f'''<div class="koute" role="group" aria-label="{text('audio', lang)}"><button type="button" class="koute-btn" aria-label="{text('audio', lang)}"><svg class="ic-play" viewBox="0 0 24 24" aria-hidden="true"><polygon points="6,4 20,12 6,20"/></svg><svg class="ic-pause" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg></button><div class="koute-main"><span class="koute-label">{text('audio', lang)}</span><div class="koute-track"><div class="koute-fill"></div></div></div><span class="koute-time">0:00</span><audio preload="none" src="/audio/11_eleksyon.mp3"></audio></div><p class="election-audio-note">{text('audio_label', lang)} · {anchor('/audio/election-transcripts.html', 'Tèks odyo yo / Audio transcripts')}</p>'''


def render_hub(lang):
    prefix = '/en/' if lang == 'en' else '/'
    local = lambda name: prefix + name
    nav = [('elections.html', 'Eleksyon' if lang == 'ht' else 'Elections'), ('education.html', 'Edikasyon' if lang == 'ht' else 'Education'), ('research.html', 'Rechèch' if lang == 'ht' else 'Research'), ('about.html#about', 'Konsènan' if lang == 'ht' else 'About'), ('about.html#contact', 'Kontak' if lang == 'ht' else 'Contact')]
    nav_html = ''.join(f'<a href="{local(path)}"' + (' aria-current="page" class="active"' if path == 'elections.html' else '') + f'>{label}</a>' for path, label in nav)
    resources = ''.join(f'''<article class="election-resource" data-audience="{r['audience']}"><h3>{anchor(local(r['url']), r['title'][lang])}</h3><p>{escape(r['description'][lang])}</p></article>''' for r in DATA['resources'])
    updates = ''.join(f'''<article class="election-update"><p class="election-kicker">{text('published', lang)}: {time(u['published_at'], lang)}</p><h3>{escape(u['title'][lang])}</h3><p>{escape(u['summary'][lang])}</p>{source_credit(lang)}</article>''' for u in DATA['updates'] if u['status'] == 'reviewed')
    rows = ''.join(f'<tr><td>{time(m["date"], lang)}</td><td>{escape(m["label"][lang])}</td></tr>' for m in DATA['milestones'])
    faqs = ''.join(f'<details><summary>{escape(f["question"][lang])}</summary><p>{text(f["answer_key"], lang)}</p>{source_credit(lang)}</details>' for f in DATA['faq'])
    options = ''.join(f'<option value="{key}">{text(key, lang)}</option>' for key in ['all', 'voter', 'candidate', 'diaspora', 'observer'])
    footer_source = (ROOT / ('en/candidates.html' if lang == 'en' else 'candidates.html')).read_text(encoding='utf-8')
    footer = re.search(r'<footer\b.*?</footer>', footer_source, re.S).group(0)
    structured = json.dumps({'@context': 'https://schema.org', '@type': 'WebPage', 'name': COPY['title'][lang], 'description': COPY['description'][lang], 'url': SITE + ('en/' if lang == 'en' else ''), 'inLanguage': lang, 'dateModified': DATA['reviewed_at'], 'publisher': {'@type': 'Organization', 'name': 'Ayiti Sitwayen'}}, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{text('title', lang)} | Ayiti Sitwayen</title><meta name="description" content="{text('description', lang)}">
<meta property="og:title" content="{text('title', lang)}"><meta property="og:description" content="{text('description', lang)}"><meta property="og:type" content="website"><meta property="og:url" content="{SITE}{'en/' if lang == 'en' else ''}"><meta property="og:image" content="{SITE}logo.png"><meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}{'en/' if lang == 'en' else ''}"><link rel="alternate" hreflang="ht" href="{SITE}"><link rel="alternate" hreflang="en" href="{SITE}en/"><link rel="alternate" hreflang="x-default" href="{SITE}">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@200..900&display=swap" rel="stylesheet"><meta name="theme-color" content="#ffffff"><link rel="stylesheet" href="/styles.css?v=3"><link rel="stylesheet" href="/theme.css?v=3"><link rel="stylesheet" href="/elections.css?v=2"><script type="application/ld+json">{structured}</script></head>
<body><a class="skip-link" href="#kontni">{'Ale dirèk nan kontni an' if lang == 'ht' else 'Skip to main content'}</a>
<nav class="navbar"><div class="container"><div class="nav-brand"><a href="{prefix}"><img src="/logo.webp" alt="Ayiti Sitwayen" class="logo" width="300" height="200"></a></div><button class="nav-toggle" aria-label="{'Meni navigasyon' if lang == 'ht' else 'Navigation menu'}" aria-expanded="false" aria-controls="navLinks">☰</button><div class="nav-links" id="navLinks">{nav_html}<button class="lang-switch">{'EN' if lang == 'ht' else 'HT'}</button></div></div></nav>
<main id="kontni" class="elections-page"><div class="container"><div class="election-intro"><p class="election-kicker">Ayiti Sitwayen · {text('independent', lang)}</p><h1>{text('heading', lang)}</h1><p class="election-lead">{text('intro', lang)}</p><div class="election-actions">{anchor(local('centres.html'), COPY['find'][lang], 'election-button')}{anchor('#enskri', COPY['register'][lang], 'election-button election-button-secondary')}</div>
{freshness(lang)}
<div class="election-registration" id="enskri"><h2>{escape(MILESTONES['voter-registration']['label'][lang])}: {time(MILESTONES['voter-registration']['date'], lang)}</h2><p>{text('registration', lang)}</p><p>{text('registration_note', lang)}</p>{source_credit(lang, '2026-10-26')}</div>
<div class="election-key-dates"><article><p class="election-kicker">{'Premye tou' if lang == 'ht' else 'First round'}</p><p class="election-big-date">{time(MILESTONES['first-round']['date'], lang)}</p><p>{'Prezidansyèl ak lejislatif' if lang == 'ht' else 'Presidential and legislative'}</p></article><article><p class="election-kicker">{'Dezyèm tou + lokal' if lang == 'ht' else 'Second round + local'}</p><p class="election-big-date">{time(MILESTONES['second-round']['date'], lang)}</p><p>{text('scheduled', lang)}</p></article></div><p class="election-muted">{text('caution', lang)} {anchor('#kalandriye', COPY['calendar_link'][lang])}</p>{audio(lang)}</div>
<section class="election-section" aria-labelledby="resous"><h2 id="resous">{text('audience', lang)}</h2><div class="election-filter" hidden><label for="election-audience">{text('audience_label', lang)}</label><select id="election-audience">{options}</select><p id="election-filter-status" role="status" aria-live="polite"></p></div><div class="election-resources">{resources}</div></section>
<section class="election-section" aria-labelledby="kalandriye"><h2 id="kalandriye">{text('timeline', lang)}</h2><p class="election-muted">{text('scheduled', lang)}. {text('caution', lang)}</p>{source_credit(lang, DATA['calendar']['published_at'])}<div class="election-table-wrap" role="region" aria-labelledby="kalandriye" tabindex="0"><table><thead><tr><th scope="col">{text('date', lang)}</th><th scope="col">{text('milestone', lang)}</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="election-section" aria-labelledby="aktyalite"><h2 id="aktyalite">{text('updates', lang)}</h2>{updates}</section>
<section class="election-section election-faq" aria-labelledby="kesyon"><h2 id="kesyon">{text('questions', lang)}</h2>{faqs}</section>
<section class="election-section"><h2>{text('learn', lang)}</h2><div class="election-actions">{anchor(local('voting.html'), 'Vòt' if lang == 'ht' else 'Voting')}{anchor(local('candidates.html'), 'Kandida' if lang == 'ht' else 'Candidates')}{anchor(local('electoral-process.html'), 'Pwosesis elektoral' if lang == 'ht' else 'Electoral process')}{anchor(local('diaspora.html'), 'Dyaspora' if lang == 'ht' else 'Diaspora')}{anchor(local('glossary.html'), 'Diksyonè politik' if lang == 'ht' else 'Political dictionary')}</div><div class="election-actions election-share"><button type="button" class="election-button election-button-secondary election-print" hidden>{text('print', lang)}</button>{anchor('https://wa.me/?text=' + quote(SITE + ('en/' if lang == 'en' else ''), safe=''), COPY['share'][lang], 'election-button election-button-secondary')}</div></section><p class="election-disclaimer">{text('disclaimer', lang)}</p></div></main>{footer}<script src="/script.js?v=7"></script><script src="/elections.js?v=2"></script><script src="/koute.js?v=2"></script></body></html>
'''


def render_directory(lang, kind):
    prefix = '/en/' if lang == 'en' else '/'
    centres = kind == 'centres'
    title = (('Sant enskripsyon ak vòt' if lang == 'ht' else 'Registration and voting centres') if centres
             else ('Estrikti politik ki gen apwobasyon KEP' if lang == 'ht' else 'Approved political structures'))
    search_label = 'Chèche' if lang == 'ht' else 'Search'
    count_label = 'sant' if centres and lang == 'ht' else 'centres' if centres else 'estrikti politik' if lang == 'ht' else 'political structures'
    if centres:
        records = json.loads((ROOT / 'data/voting-centres.json').read_text(encoding='utf-8'))['centres']
        filters = f'''<label>{'Depatman' if lang == 'ht' else 'Department'}<select data-directory-department><option value="">{'Tout depatman yo' if lang == 'ht' else 'All departments'}</option></select></label><label>{'Komin' if lang == 'ht' else 'Commune'}<select data-directory-commune><option value="">{'Tout komin yo' if lang == 'ht' else 'All communes'}</option></select></label>'''
        entries = ''.join(f'''<article class="election-directory-card" data-directory-row data-department="{escape(item['department'], quote=True)}" data-commune="{escape(item['commune'], quote=True)}"><h2>{escape(item['name'])}</h2><p>{escape(item['department'])} · {escape(item['commune'])}</p><p>{escape(item['section'])}</p><p>{escape(item['address'])}</p></article>''' for item in records)
        content = f'<div class="election-centre-results">{entries}</div>'
        intro = text('centre_note', lang)
    else:
        records = json.loads((ROOT / 'data/approved-parties.json').read_text(encoding='utf-8'))['parties']
        filters = ''
        entries = ''.join(f'<tr data-directory-row><td>{escape(item["name"])}</td><td>{escape(item["acronym"])}</td><td>{item["number"]}</td></tr>' for item in records)
        content = f'''<div class="election-table-wrap"><table><thead><tr><th scope="col">{'Non' if lang == 'ht' else 'Name'}</th><th scope="col">{'Sig' if lang == 'ht' else 'Acronym'}</th><th scope="col">{'Nimewo' if lang == 'ht' else 'Number'}</th></tr></thead><tbody>{entries}</tbody></table></div>'''
        intro = text('candidate_note', lang)
    body = f'''<main id="kontni" class="elections-page"><div class="container" data-directory data-result-noun="{count_label}"><p>{anchor(prefix, '← Eleksyon' if lang == 'ht' else '← Elections')}</p><div class="election-intro"><p class="election-kicker">Ayiti Sitwayen</p><h1>{title}</h1><p class="election-lead">{intro}</p>{source_credit(lang)}{freshness(lang)}</div><div class="election-directory-filters" hidden><label>{search_label}<input type="search" data-directory-search autocomplete="off"></label>{filters}</div><p data-directory-status role="status" aria-live="polite">{len(records)} {count_label}</p>{content}</div></main>'''
    shell = render_hub(lang)
    shell = re.sub(r'<main\b.*?</main>', lambda _: body, shell, count=1, flags=re.S)
    shell = re.sub(r'<title>.*?</title>', f'<title>{title} | Ayiti Sitwayen</title>', shell)
    shell = re.sub(r'(<meta (?:name="description"|property="og:description"|property="og:title") content=")[^"]*', lambda m: m[1] + escape(title, quote=True), shell)
    route = kind + '.html'
    shell = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m[1] + SITE + ('en/' if lang == 'en' else '') + route, shell)
    shell = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m[1] + SITE + ('en/' if lang == 'en' else '') + route, shell)
    for code, target in [('ht', SITE + route), ('en', SITE + 'en/' + route), ('x-default', SITE + route)]:
        shell = re.sub(r'(<link rel="alternate" hreflang="' + code + r'" href=")[^"]*', lambda m: m[1] + target, shell)
    structured = json.dumps({'@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'url': SITE + ('en/' if lang == 'en' else '') + route, 'inLanguage': lang, 'publisher': {'@type': 'Organization', 'name': 'Ayiti Sitwayen'}}, ensure_ascii=False)
    shell = re.sub(r'(<script type="application/ld\+json">).*?(</script>)', lambda m: m[1] + structured + m[2], shell, flags=re.S)
    return shell.replace('aria-current="page"', 'aria-current="location"')


def outputs():
    result = {}
    for lang in ['ht', 'en']:
        folder = ROOT / 'en' if lang == 'en' else ROOT
        result[folder / 'elections.html'] = render_hub(lang)
        result[folder / 'index.html'] = render_hub(lang)
        result[folder / 'centres.html'] = render_directory(lang, 'centres')
        result[folder / 'parties.html'] = render_directory(lang, 'parties')
        for name in TARGETS:
            if name == 'index.html':
                continue
            path = folder / name
            source = path.read_text(encoding='utf-8')
            marker = r'<!-- election-summary:start -->.*?<!-- election-summary:end -->'
            if re.search(marker, source, re.S):
                block = '<!-- election-summary:start -->\n' + summary(lang, name == 'index.html', name == 'candidates.html') + '\n<!-- election-summary:end -->'
                result[path] = re.sub(marker, lambda _: block, source, flags=re.S)
    scripts = json.loads((ROOT / 'data/election-audio.json').read_text(encoding='utf-8'))
    transcript = ''.join(f'<section><h2>{escape(item["title"])}</h2><p>{escape(item["text"])}</p><audio controls preload="none" src="/audio/{escape(item["file"], quote=True)}"></audio></section>' for item in scripts)
    result[ROOT / 'audio/election-transcripts.html'] = f'<!doctype html><html lang="ht"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tèks odyo eleksyon yo — Ayiti Sitwayen</title><link rel="stylesheet" href="/styles.css?v=3"><link rel="stylesheet" href="/theme.css?v=3"><link rel="stylesheet" href="/elections.css?v=2"></head><body><main class="container election-transcripts"><a href="/elections.html">← Eleksyon</a><h1>Tèks odyo eleksyon yo</h1><p>{COPY["audio_label"]["ht"]}. {COPY["reviewed"]["ht"]}: {date_text(DATA["reviewed_at"], "ht")}. Pou dat aktyèl yo, tcheke <a href="/elections.html">paj Eleksyon an</a>.</p>{transcript}</main></body></html>'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    for path, content in outputs().items():
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(content, encoding='utf-8', newline='\n')
    if args.check and changed:
        raise SystemExit('Election pages need regeneration: ' + ', '.join(changed))
    print(('Checked' if args.check else 'Generated') + ' shared election pages; ' + str(len(changed)) + ' changed.')
