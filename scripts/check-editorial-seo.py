"""Audit published article HTML as a reader/crawler, including visible/schema parity."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://www.ayitisitwayen.org'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.title=''; self.h1=[]; self.meta={}; self.canon=[]
        self.alternates={}; self.hrefs=[]; self.ids=set(); self.breadcrumbs=[]
        self.paragraphs=[]; self.current=None; self.structured=[]; self.ld=None
        self.language=None; self.dates=[]; self.images=[]
        self.feed(text)
    def within(self, key, value):
        return any(a.get(key)==value for _,a in self.stack)
    def start(self, tag, attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag=='html': self.language=a.get('lang')
        if tag=='meta': self.meta.setdefault(a.get('name',a.get('property','')),[]).append(a.get('content',''))
        if tag=='link':
            if a.get('rel')=='canonical': self.canon.append(a['href'])
            if a.get('hreflang'): self.alternates[a['hreflang']]=a['href']
        if tag=='a' and a.get('href'):
            self.hrefs.append(a['href'])
            if self.within('class','editorial-breadcrumb'): self.breadcrumbs.append(a['href'])
        if tag=='time': self.dates.append(a.get('datetime'))
        if tag=='img': self.images.append(a)
        if tag=='h1': self.h1.append('')
        if tag=='p' and self.within('id','article-text'):
            self.paragraphs.append(''); self.current=len(self.paragraphs)-1
        if tag=='script' and a.get('type')=='application/ld+json': self.ld=''
        if tag not in VOID: self.stack.append((tag,a))
    handle_starttag=start
    def handle_startendtag(self, tag, attrs):
        self.start(tag,attrs)
        if tag not in VOID: self.handle_endtag(tag)
    def handle_data(self, data):
        if self.ld is not None: self.ld+=data
        if self.within('id','article-text') and self.current is not None and not self.within('class','editorial-citation'):
            self.paragraphs[self.current]+=data
        if any(t=='title' for t,_ in self.stack): self.title+=data
        if any(t=='h1' for t,_ in self.stack): self.h1[-1]+=data
    def handle_endtag(self, tag):
        if tag=='script' and self.ld is not None:
            self.structured.append(json.loads(self.ld)); self.ld=None
        if tag=='p': self.current=None
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:];break

def normal(text): return re.sub(r'\s+',' ',text).strip()
def absolute(href): return SITE+href if href.startswith('/') else href

def audit():
    d=json.loads((ROOT/'data/candidate-editorial.json').read_text(encoding='utf-8'))
    articles=[a for a in d['articles'] if a['status']=='published']
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap={x.text for x in ET.parse(ROOT/'sitemap-pages.xml').findall('.//s:loc',ns)}
    seen_titles=set();seen_descriptions=set();routes=[]
    for lang in ('ht','en'):
        prefix='/en/' if lang=='en' else '/'
        hub=Page((ROOT/(prefix+'elections/analysis/index.html').lstrip('/')).read_text(encoding='utf-8'))
        feed=ET.parse(ROOT/(prefix+'elections/analysis/feed.xml').lstrip('/'))
        feed_urls={x.text for x in feed.findall('./channel/item/link')}
        for a in articles:
            route=prefix+'elections/analysis/'+a['slug']+'/'
            url=SITE+route
            p=Page((ROOT/(route+'index.html').lstrip('/')).read_text(encoding='utf-8'))
            assert p.language==lang,(route,'wrong document language')
            assert p.canon==[url],(route,'canonical')
            ht=route.removeprefix('/en') if lang=='en' else route
            assert p.alternates=={'ht':SITE+ht,'en':SITE+'/en'+ht,'x-default':SITE+ht},(route,'language alternatives')
            assert p.h1==[a['title'][lang]],(route,'headline missing from native HTML')
            assert p.title==a['title'][lang]+' | Ayiti Sitwayen',(route,'title')
            assert p.title not in seen_titles,(route,'duplicate title')
            seen_titles.add(p.title)
            assert p.meta.get('description')==[a['description'][lang]],(route,'description')
            assert a['description'][lang] not in seen_descriptions,(route,'duplicate description')
            seen_descriptions.add(a['description'][lang])
            assert not re.search(r'\b(noindex|nosnippet|none)\b',' '.join(p.meta.get('robots',[])),re.I),(route,'index/snippet blocked')
            assert p.meta.get('og:url')==[url] and p.meta.get('og:type')==['article'],(route,'sharing metadata')
            graph=[item for block in p.structured for item in block.get('@graph',[])]
            item=next(x for x in graph if x.get('@type')=='Article')
            assert item['headline']==p.h1[0] and item['description']==a['description'][lang],(route,'schema copy differs')
            assert item['url']==url and item['inLanguage']==lang,(route,'schema identity')
            body='\n\n'.join(p.paragraphs)
            assert normal(item['articleBody'])==normal(body),(route,'schema/body differs or text requires JavaScript')
            assert len(p.paragraphs)>=3,(route,'missing native narrative')
            assert item['genre']==d['copy'][a['kind']][lang],(route,'opinion/analysis label')
            assert item['datePublished'] in p.dates and item['dateModified'] in p.dates,(route,'dates not visible')
            assert item['author']['@type']=='Organization' and item['author']['name']=='Ayiti Sitwayen',(route,'publisher attribution')
            assert all(u in p.hrefs for u in item['citation']),(route,'structured sources not visible')
            refs=[h.removeprefix('#') for h in p.hrefs if h.startswith('#source-')]
            assert refs and set(refs)<=p.ids,(route,'citation target missing')
            for person in item['about']:
                assert person['url'] in [absolute(h) for h in p.hrefs],(route,'candidate profile not linked')
            crumbs=next(x for x in graph if x.get('@type')=='BreadcrumbList')['itemListElement']
            assert [x['item'] for x in crumbs[:-1]]==[absolute(h) for h in p.breadcrumbs],(route,'structured breadcrumbs differ from navigation')
            assert crumbs[-1]['item']==url,(route,'breadcrumb identity')
            assert all(im.get('alt') for im in p.images),(route,'image description missing')
            assert url in sitemap and url in feed_urls and route in hub.hrefs,(route,'article undiscoverable')
            routes.append(route)
    return {'result':'pass','published_articles':len(articles),'language_pages':len(routes),'native_body_schema_parity':True,'unique_titles_and_descriptions':True,'visible_citations':True,'sitemap_feed_hub_coverage':True,'breadcrumb_navigation_parity':True,'limits':'Checks technical eligibility and discoverability; does not guarantee indexing, citations, traffic or ranking.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
