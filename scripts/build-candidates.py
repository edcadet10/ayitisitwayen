"""Generate native bilingual candidate pages from reviewed, versioned public data."""
import argparse
from collections import Counter
import hashlib
from html import escape as esc
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote, urlparse
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://www.ayitisitwayen.org'
COPY = json.loads((ROOT / 'data/candidate-copy.json').read_text(encoding='utf-8'))
OFFICES = {'Président': 'president', 'Sénateur': 'senator', 'Député': 'deputy', 'Maire': 'mayor', 'CASEC': 'casec', 'ASEC': 'asec'}
CATEGORIES = [('articles','▤'),('videos','▷'),('interviews','◉'),('campaign','◈'),('public_records','▥'),('social','@'),('positions','◇'),('history','⌁')]
PAGE_SIZE = 24
PORTRAIT_SIZES = '(max-width:360px) calc((100vw - 40px)/2), (max-width:650px) calc((100vw - 55px)/2), (max-width:1000px) calc((100vw - 90px)/3), (max-width:1200px) calc((100vw - 115px)/4), 272px'

def t(key, lang): return COPY[key][lang]
def normalize(value): return ''.join(c for c in unicodedata.normalize('NFD', value.casefold()) if not unicodedata.combining(c))
def compact(value): return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
def prefix(lang): return '/en/' if lang == 'en' else '/'
def directory(lang): return prefix(lang) + 'candidates/'
def profile_url(person, lang): return directory(lang) + person['id'] + '/'
def label(key, lang): return esc(t(key, lang))
def safe_url(value):
    parsed = urlparse(value)
    assert parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
    return value

def load():
    registry = json.loads((ROOT / 'data/candidates/registry.json').read_text(encoding='utf-8'))
    enrichment = json.loads((ROOT / 'data/candidates/enrichment.json').read_text(encoding='utf-8'))
    assert registry['status'] == 'reviewed' and registry['total'] == len(registry['candidates'])
    people = registry['candidates']; ids = set()
    for person in people:
        assert re.fullmatch('[a-z0-9-]{10,45}', person['id']) and person['id'] not in ids
        assert person['office'] in OFFICES.values() and person['status'] in ['preliminary','validated','withdrawn','rejected']
        ids.add(person['id'])
    assert Counter(p['office'] for p in people) == Counter(registry['office_counts'])
    for person_id, entry in enrichment['profiles'].items():
        assert person_id in ids
        entry['sources']=[enrichment['publications'][source_id] for source_id in entry.get('source_ids',[])]
        if entry.get('portrait'):
            p=entry['portrait']; assert p['path'].startswith('/assets/candidates/') and (ROOT / p['path'].lstrip('/')).resolve().is_relative_to(ROOT) and (ROOT / p['path'].lstrip('/')).is_file();safe_url(p['source_url'])
            assert re.fullmatch(r'\d{1,3}% \d{1,3}%',p.get('position','50% 30%'))
            for variant in p['variants']:
                asset=variant['path'];assert re.fullmatch(r'/assets/candidates/[a-z0-9-]+\.webp',asset) and (ROOT/asset.lstrip('/')).is_file()
                assert variant['width'] in [160,320,480] and variant['height']*4==variant['width']*5
            assert re.fullmatch(r'/assets/candidates/[a-z0-9-]+\.webp',p['web_path']) and (ROOT/p['web_path'].lstrip('/')).is_file()
        seen=set()
        for source in entry.get('sources',[]):
            assert re.fullmatch('[a-z0-9-]{3,80}',source['id']) and source['id'] not in seen and source['review_status']=='reviewed'
            seen.add(source['id']);safe_url(source['url'])
            assert source['type'] in ['journalism','official','campaign_source','social_source','opinion']
            assert all(category in dict(CATEGORIES) for category in source['categories'])
            for lang in ['ht','en']:assert source['title'][lang] and source['summary'][lang]
    return registry, enrichment

def portrait(person, enrichment, lang, hero=False):
    image=enrichment['profiles'].get(person['id'],{}).get('portrait')
    if image:
        path=esc(image['path'],quote=True)
        # Lazy gallery images load only when visible; a noscript copy preserves native access.
        srcset=esc(', '.join(f'{v["path"]} {v["width"]}w' for v in image['variants']),quote=True)
        sizes='(max-width:360px) 85px, (max-width:650px) 95px, 185px' if hero else PORTRAIT_SIZES
        attrs=f'srcset="{srcset}" sizes="{sizes}" src="{path}"' if hero else f'data-portrait-srcset="{srcset}" data-portrait-sizes="{sizes}" data-portrait-src="{path}"'
        tag=f'<img {attrs} alt="{esc(person["name"],quote=True)}" width="320" height="400" decoding="async" style="object-position:{esc(image.get("position","50% 50%"),quote=True)}"'+(' fetchpriority="high"' if hero else '')+'>'
        if not hero:tag+=f'<noscript><img srcset="{srcset}" sizes="{sizes}" src="{path}" alt="{esc(person["name"],quote=True)}" width="320" height="400" loading="lazy"></noscript>'
        return tag
    initials=''.join(part[0] for part in [person['given_name'],person['surname']] if part)
    return f'<span class="candidate-initials" aria-hidden="true">{esc(initials)}</span><span class="photo-pending">{label("photo_pending",lang)}</span>'

def shell(lang,title,description,path,body,profile=False):
    route=path.removeprefix('/en') if lang=='en' else path
    alternate=('/en'+route) if lang=='ht' else route
    ht=route;en='/en'+route
    nav=''.join(f'<a href="{url}"'+(' aria-current="page"' if key=='directory_title' else '')+f'>{label(key,lang)}</a>' for key,url in [('elections',prefix(lang)),('directory_title',directory(lang)),('education',prefix(lang)+'education.html'),('about',prefix(lang)+'about.html')])
    structured={'@context':'https://schema.org','@type':'WebPage','name':title,'url':SITE+path,'inLanguage':lang,'publisher':{'@type':'Organization','name':'Ayiti Sitwayen'}}
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Ayiti Sitwayen</title><meta name="description" content="{esc(description,quote=True)}"><meta name="theme-color" content="#ffffff"><meta property="og:title" content="{esc(title,quote=True)}"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:url" content="{SITE}{path}"><meta property="og:type" content="website"><meta property="og:image" content="{SITE}/logo.png"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="{SITE}{path}"><link rel="alternate" hreflang="ht" href="{SITE}{ht}"><link rel="alternate" hreflang="en" href="{SITE}{en}"><link rel="alternate" hreflang="x-default" href="{SITE}{ht}"><link rel="icon" href="/favicon.png"><link rel="stylesheet" href="/styles.css?v=3"><link rel="stylesheet" href="/theme.css?v=3"><link rel="stylesheet" href="/candidate-directory.css?v=4"><script type="application/ld+json">{compact(structured)}</script></head><body class="candidate-site"><a class="skip-link" href="#kontni">{label('skip',lang)}</a><nav class="navbar"><div class="container"><a class="nav-brand" href="{prefix(lang)}"><img src="/logo.webp" class="logo" alt="Ayiti Sitwayen" width="300" height="200"></a><button class="nav-toggle" aria-label="{label('menu',lang)}" aria-expanded="false" aria-controls="navLinks">☰</button><div class="nav-links" id="navLinks">{nav}<a class="lang-switch" href="{alternate}" lang="{'en' if lang=='ht' else 'ht'}">{'EN' if lang=='ht' else 'HT'}</a></div></div></nav>{body}<footer class="candidate-footer container"><a href="{prefix(lang)}">Ayiti Sitwayen</a><p>{label('independent',lang)}</p><a href="{prefix(lang)}about.html#contact">{label('correction',lang)}</a></footer><script type="application/json" id="candidate-copy">{compact({key:value[lang] for key,value in COPY.items()})}</script><script src="/candidate-common.js?v=4" defer></script><script src="/candidate-{'web' if profile else 'directory'}.js?v=4" defer></script></body></html>'''

def card(person,enrichment,lang):
    image=enrichment['profiles'].get(person['id'],{}).get('portrait')
    credit=f'<p class="candidate-card-photo-credit">{label("photo_credit",lang)}: {esc(image["credit"])}</p>' if image else ''
    return f'''<article class="candidate-card"><a class="candidate-card-link" href="{profile_url(person,lang)}#information-web" aria-label="{esc(person['name'],quote=True)} — {label('view_web',lang)}"><div class="candidate-photo">{portrait(person,enrichment,lang)}<span class="photo-open" aria-hidden="true">↗</span></div>{credit}<div class="candidate-card-info"><p class="candidate-card-office">{label(person['office'],lang)} · {esc(person['party'])}</p><h2>{esc(person['name'])}</h2><p class="candidate-card-place">{esc(' · '.join(person['locality']))}</p><span class="candidate-status">{label(person['status'],lang)}</span><span class="candidate-card-cta">{label('view_web',lang)} <span aria-hidden="true">↗</span></span></div></a></article>'''

def pagination(lang,office,page,total):
    count=max(1,(total+PAGE_SIZE-1)//PAGE_SIZE)
    base=directory(lang)+office+'/'
    return f'<nav class="candidate-pagination" aria-label="{label("page",lang)}">'+(f'<a href="{base}" class="candidate-button secondary">{label("previous",lang)}</a>' if page==2 else f'<a href="{base}page-{page-1}.html" class="candidate-button secondary">{label("previous",lang)}</a>' if page>2 else '')+f'<span>{label("page",lang)} {page} {label("of",lang)} {count}</span>'+(f'<a href="{base}page-{page+1}.html" class="candidate-button secondary">{label("next",lang)}</a>' if page<count else '')+'</nav>'

def directory_page(lang,registry,enrichment,office='president',page=1,main=True):
    people=[p for p in registry['candidates'] if office=='all' or p['office']==office]
    current=people[(page-1)*PAGE_SIZE:page*PAGE_SIZE]
    options=lambda pairs:''.join(f'<option value="{esc(value,quote=True)}">{esc(text)}</option>' for value,text in pairs)
    tabs=''.join(f'<a href="{directory(lang)}{key}/" data-office="{key}" class="office-tab'+(' active' if key==office else '')+'"'+(' aria-current="page"' if key==office else '')+f'>{label(key,lang)} <span>{registry["office_counts"].get(key,registry["total"]):,}</span></a>' for key in ['all']+list(OFFICES.values()))
    filters=f'''<form class="candidate-search" id="candidate-search" hidden><div class="candidate-search-line"><label for="candidate-query">{label('search',lang)}</label><div><input id="candidate-query" name="q" type="search" autocomplete="off"><button class="candidate-button" type="submit">{label('search_button',lang)} <span aria-hidden="true">↗</span></button></div></div><button class="candidate-clear" id="candidate-filter-toggle" type="button" aria-expanded="false" aria-controls="candidate-filters">{label('more_filters',lang)} +</button><div class="candidate-filters" id="candidate-filters" hidden><label>{label('department',lang)}<select name="department"><option value="">{label('all_departments',lang)}</option></select></label><label>{label('commune',lang)}<select name="place"><option value="">{label('all_communes',lang)}</option></select></label><label>{label('party',lang)}<select name="party"><option value="">{label('all_parties',lang)}</option></select></label><label>{label('status',lang)}<select name="status">{options([('',t('all_statuses',lang))]+[(k,t(k,lang)) for k in ['preliminary','validated','withdrawn','rejected']])}</select></label><button type="reset" class="candidate-clear">{label('clear',lang)}</button></div></form>'''
    fallback=''.join(f'<a href="{directory(lang)}{key}/">{label(key,lang)}</a>' for key in OFFICES.values())
    body=f'''<main id="kontni" class="candidate-main container" data-directory-office="{office}" data-directory-page="{page}"><div class="candidate-intro"><p class="candidate-kicker">AYITI SITWAYEN <span>—</span> {label('election',lang)}</p><h1>{label('heading',lang)}</h1><p class="candidate-lead">{label('intro',lang)}</p></div><aside class="candidate-registration-note"><span class="candidate-status">{label('preliminary',lang)}</span><p>{label('status_note',lang)}</p><small>{label('snapshot',lang)} <time datetime="{registry['reviewed_at']}">{registry['reviewed_at']}</time> · {registry['total']:,} {label('records',lang)} · {label('source',lang)}: KEP / CEP</small></aside><nav class="candidate-office-tabs" aria-label="{label('office',lang)}">{tabs}</nav>{filters}<div class="candidate-results-bar"><p id="candidate-count" role="status" aria-live="polite">{len(people):,} {label('results',lang)}</p><p class="candidate-web-prompt">◌ {label('view_web',lang)}</p></div><p id="candidate-load-error" role="alert" hidden>{label('load_error',lang)} <button type="button" class="candidate-clear" id="candidate-retry">{label('retry',lang)}</button></p><div class="candidate-grid" id="candidate-results">{''.join(card(p,enrichment,lang) for p in current)}</div><div id="candidate-pagination">{pagination(lang,office,page,len(people))}</div><details class="candidate-browse"><summary>{label('browse_office',lang)}</summary><p>{label('browse_note',lang)}</p><div>{fallback}</div></details><p class="candidate-coverage">{label('coverage',lang)}</p><a class="candidate-text-link" href="{prefix(lang)}candidates.html">{label('learn',lang)} ↗</a></main>'''
    path=directory(lang) if main else directory(lang)+office+('/' if page==1 else f'/page-{page}.html')
    return path,shell(lang,t('directory_title',lang),t('intro',lang),path,body)

def sources_for(person,registry,enrichment):
    official={'id':'cep-registration','type':'official','format':'record','categories':['public_records'],'title':COPY['registry_title'],'summary':COPY['registry_summary'],'publisher':'Conseil Électoral Provisoire (KEP / CEP)','url':registry['source_url'],'published_at':None,'reviewed_at':registry['reviewed_at'],'review_status':'reviewed','native':True}
    return [official]+enrichment['profiles'].get(person['id'],{}).get('sources',[])

def profile_page(lang,person,registry,enrichment):
    entry=enrichment['profiles'].get(person['id'],{});sources=sources_for(person,registry,enrichment)
    image=entry.get('portrait');credit=''
    if image:
        credit=f'<p class="candidate-photo-credit">{label("photo_credit",lang)}: <a href="{esc(safe_url(image["source_url"]),quote=True)}" target="_blank" rel="noopener noreferrer">{esc(image["credit"])}</a> · {esc(image["context"][lang])}</p>'
    position={'Titulaire':'titulaire','1er Adjoint':'first_deputy','2ème Adjoint':'second_deputy'}.get(person['position'])
    facts=[('office',t(person['office'],lang)),('party',person['party']),('position',t(position,lang) if position else person['position']),('place',' · '.join(person['locality']))]
    fact_html=''.join(f'<div><dt>{label(key,lang)}</dt><dd>{esc(value)}</dd></div>' for key,value in facts)
    archive=''.join(f'''<article class="candidate-source-card" data-source-id="{s['id']}" data-source-type="{s['type']}" data-source-date="{s.get('published_at') or ''}"><div><span class="source-type">{label(s['type'],lang)} · {label("format_"+s["format"],lang)}</span><span>{esc(s.get('published_at') or t('date_unknown',lang))}</span></div><h3>{esc(s['title'][lang])}</h3><p>{esc(s['summary'][lang])}</p><p class="source-publisher">{label('source',lang)}: {esc(s['publisher'])}</p>{f'<p class="source-access-note">{label("source_account_note",lang)}</p>' if s.get("access")=="account" else ""}{f'<a href="#registration">{label("registry_title",lang)} ↑</a>' if s.get('native') else f'<a href="{esc(safe_url(s["url"]),quote=True)}" target="_blank" rel="noopener noreferrer">{label("original",lang)} ↗</a>'}</article>''' for s in sources)
    types=''.join(f'<option value="{key}">{label(key,lang)}</option>' for key in ['official','journalism','campaign_source','social_source','opinion'])
    data={'id':person['id'],'name':person['name'],'registration':[{'label':t(key,lang),'value':value} for key,value in facts]+[{'label':t('status',lang),'value':t(person['status'],lang)}],'sources':sources,'categories':[{ 'key':key,'label':t(key,lang),'icon':icon} for key,icon in CATEGORIES]}
    body=f'''<main id="kontni" class="candidate-main candidate-profile container"><a class="candidate-back" href="{directory(lang)}" id="candidate-back">← {label('back',lang)}</a><section class="candidate-profile-intro" id="registration"><div class="candidate-profile-portrait"><div class="candidate-photo">{portrait(person,enrichment,lang,True)}</div>{credit}</div><div class="candidate-profile-heading"><p class="candidate-kicker">{label('election',lang)} · {label(person['office'],lang)}</p><h1>{esc(person['name'])}</h1><p class="candidate-status">{label(person['status'],lang)}</p><dl class="candidate-facts">{fact_html}</dl><p class="candidate-snapshot">{label('snapshot',lang)} <time datetime="{registry['reviewed_at']}">{registry['reviewed_at']}</time> · {label('source',lang)}: KEP / CEP</p><p class="candidate-status-explanation">{label('status_note',lang)}</p><a class="candidate-text-link" id="candidate-open-web" href="#information-web" hidden>{label("view_web",lang)} ↓</a><button class="candidate-clear" id="candidate-share" type="button" hidden>{label('share',lang)} ↗</button><span id="candidate-share-status" role="status"></span></div></section><section class="candidate-web-section" id="information-web" aria-labelledby="web-title" hidden><div class="candidate-web-heading"><div><p class="candidate-kicker">{esc(person['name'])} · {len(sources)} {label('sources',lang)}</p><p class="candidate-status">{label(person["status"],lang)}</p><h2 id="web-title">{label('the_web',lang)}</h2></div><a href="#source-archive" class="candidate-text-link">{label('archive',lang)} ↓</a></div><div class="candidate-web-toolbar"><button type="button" class="candidate-clear" id="web-back" hidden>← {label('topics',lang)}</button><p id="web-breadcrumb">{label('web_hint',lang)}</p><div id="web-pages" hidden><button type="button" id="web-previous" aria-label="{label('previous',lang)}">←</button><span id="web-page-count"></span><button type="button" id="web-next" aria-label="{label('next',lang)}">→</button></div></div><div class="candidate-web-layout"><div id="web-stage" role="group" aria-label="{label('web_label',lang)}"><svg id="web-threads" aria-hidden="true"></svg><a class="web-centre" href="#registration" aria-label="{esc(person['name'],quote=True)}">{f'<img src="{esc(image["web_path"],quote=True)}" alt="" width="192" height="192" decoding="async">' if image else '<span aria-hidden="true">'+esc(''.join(p[0] for p in [person['given_name'],person['surname']] if p))+'</span>'}</a><div id="web-nodes"></div></div><aside class="candidate-preview" id="web-preview" aria-live="polite" aria-label="{label('the_web',lang)}"><div id="web-preview-empty"><span class="preview-web-symbol" aria-hidden="true">✧</span><h3>{label('preview_empty',lang)}</h3><p>{label('preview_hint',lang)}</p></div><div id="web-preview-content" hidden><button type="button" id="web-close" aria-label="{label('close_preview',lang)}">×</button><p class="source-type" id="web-preview-type"></p><h3 id="web-preview-title"></h3><p id="web-preview-summary"></p><p class="source-publisher" id="web-preview-publisher"></p><p class="source-date" id="web-preview-date"></p><div id="web-preview-action"></div><div id="web-video"></div></div></aside></div></section><section class="candidate-archive" id="source-archive" aria-labelledby="archive-title"><div class="candidate-web-heading"><div><p class="candidate-kicker">{len(sources)} {label('sources',lang)}</p><h2 id="archive-title">{label('archive',lang)}</h2></div><div class="candidate-archive-filters" hidden><label>{label('source_type',lang)}<select id="source-type-filter"><option value="">{label('all_types',lang)}</option>{types}</select></label><label>{label('timeline',lang)}<select id="source-date-sort"><option value="newest">{label('newest',lang)}</option><option value="oldest">{label('oldest',lang)}</option></select></label></div></div><div class="candidate-source-list">{archive}</div><p class="candidate-coverage">{label('coverage',lang)}</p></section><script type="application/json" id="candidate-profile-data">{compact(data)}</script></main>'''
    return shell(lang,person['name']+' — '+t(person['office'],lang),t('registry_summary',lang),profile_url(person,lang),body,True)

def outputs(registry,enrichment):
    catalog=[]
    for p in registry['candidates']:
        image=enrichment['profiles'].get(p['id'],{}).get('portrait')
        catalog.append({**{key:p[key] for key in ['id','name','office','party','locality','status']},'initials':p['given_name'][0]+p['surname'][0],'portrait':{'path':image['path'],'position':image.get('position','50% 50%'),'variants':image['variants'],'sizes':PORTRAIT_SIZES,'credit':image['credit']} if image else None})
    yield ROOT/'data/candidate-public/catalog.json',compact({'reviewed_at':registry['reviewed_at'],'candidates':catalog})
    for office in OFFICES.values():
        yield ROOT/f'data/candidate-public/catalog-{office}.json',compact({'reviewed_at':registry['reviewed_at'],'candidates':[row for row in catalog if row['office']==office]})
    urls=[]
    for lang in ['ht','en']:
        path,html=directory_page(lang,registry,enrichment)
        urls.append(path);yield ROOT/path.strip('/')/'index.html',html
        for office in ['all']+list(OFFICES.values()):
            total=sum(office=='all' or p['office']==office for p in registry['candidates'])
            for page in range(1,max(1,(total+PAGE_SIZE-1)//PAGE_SIZE)+1):
                path,html=directory_page(lang,registry,enrichment,office,page,False)
                yield ROOT/path.strip('/')/('index.html') if path.endswith('/') else ROOT/path.strip('/'),html
        for person in registry['candidates']:
            path=profile_url(person,lang);urls.append(path)
            yield ROOT/path.strip('/')/'index.html',profile_page(lang,person,registry,enrichment)
    sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{xml_escape(SITE+url)}</loc><lastmod>{registry["reviewed_at"]}</lastmod></url>' for url in urls)+'</urlset>'
    yield ROOT/'sitemap-candidates.xml',sitemap

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    registry,enrichment=load();changed=[];count=0
    for path,content in outputs(registry,enrichment):
        count+=1
        if count % 2000 == 0: print(f'Candidate build: checked {count} artifacts',flush=True)
        if not path.exists() or path.read_text(encoding='utf-8')!=content:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content,encoding='utf-8',newline='\n')
    if args.check and changed:raise SystemExit(f'{len(changed)} candidate artifacts need regeneration: '+', '.join(changed[:8]))
    print(f'Candidate build: {count} artifacts; {registry["total"]} reviewed registrations; {len(changed)} updated.')

if __name__=='__main__':main()
