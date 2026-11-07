"""Check sitemap coverage against every generated canonical HTML page."""
import argparse,importlib.util,json,re,sys
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1];SITE='https://www.ayitisitwayen.org';NS='{http://www.sitemaps.org/schemas/sitemap/0.9}'
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
builder=module('candidate_builder','build-candidates.py');maps=module('site_sitemaps','build-sitemaps.py')
def page_head(content,path):
 head=maps.Head(content)
 assert head.title and head.description,(path,'Missing title/description')
 assert head.canonical and head.canonical.startswith(SITE+'/'),(path,'Missing canonical')
 assert not re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*noindex',content,re.I),(path,'Unexpected noindex')
 assert not urlparse(head.canonical).query and not urlparse(head.canonical).fragment,(path,'Query/fragment canonical')
 return head
def audit():
 registry,enrichment=builder.load();pages={};aliases=[];generated_maps={};titles={}
 for path,content in builder.outputs(registry,enrichment):
  if path.suffix=='.xml':generated_maps[path.name]=content;continue
  if path.suffix!='.html':continue
  route='/'+path.relative_to(ROOT).as_posix();route=route.removesuffix('index.html') if path.name=='index.html' else route
  head=page_head(content,route)
  expected=SITE+route
  if head.canonical!=expected:
   assert route in ['/candidates/president/','/en/candidates/president/'],route
   aliases.append(route);continue
  assert set(head.alternates)=={'ht','en','x-default'},route
  ht=route.removeprefix('/en') if route.startswith('/en/') else route
  assert head.alternates=={'ht':SITE+ht,'en':SITE+'/en'+ht,'x-default':SITE+ht},route
  blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',content,re.S)
  assert blocks,route
  metadata=json.loads(blocks[0]);assert metadata['url']==expected and metadata['description']==head.description,route
  assert 'jobTitle' not in metadata.get('about',{}),route
  assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',metadata['dateModified']),route
  pages[expected]=head;titles.setdefault(head.title,[]).append(route)
 for route,date in maps.base_pages():
  path=ROOT/route.strip('/')/'index.html' if route.endswith('/') else ROOT/route.strip('/')
  head=page_head(path.read_text(encoding='utf-8'),route);pages[SITE+route]=head;titles.setdefault(head.title,[]).append(route)
 duplicate_titles={title:routes for title,routes in titles.items() if len(routes)>1}
 assert not duplicate_titles,duplicate_titles
 all_urls=set();counts={}
 for name in ['sitemap-pages.xml','sitemap-candidates.xml','sitemap-candidate-directory.xml','sitemap-candidate-archives.xml']:
  content=generated_maps.get(name) or (ROOT/name).read_text(encoding='utf-8');root=ET.fromstring(content);entries=root.findall(NS+'url');urls=[e.findtext(NS+'loc') for e in entries]
  assert root.tag==NS+'urlset' and len(entries)<=50000 and len(content.encode())<=50000000,name
  assert len(urls)==len(set(urls)),(name,'Duplicate URL')
  assert not all_urls.intersection(urls),(name,'URL in multiple maps')
  for entry,url in zip(entries,urls):
   assert url in pages,(name,url,'Not an emitted canonical page')
   date=entry.findtext(NS+'lastmod')
   if date:assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',date),(url,date)
  all_urls.update(urls);counts[name]=len(urls)
 assert all_urls==set(pages),{'missing':list(set(pages)-all_urls)[:10],'unexpected':list(all_urls-set(pages))[:10]}
 root=ET.fromstring((ROOT/'sitemap.xml').read_text(encoding='utf-8'));assert root.tag==NS+'sitemapindex'
 assert {entry.findtext(NS+'loc') for entry in root.findall(NS+'sitemap')}=={SITE+'/'+name for name in counts}
 assert 'Sitemap: '+SITE+'/sitemap.xml' in (ROOT/'robots.txt').read_text(encoding='utf-8')
 headers=json.loads((ROOT/'vercel.json').read_text(encoding='utf-8'))['headers']
 noindex={group['source'] for group in headers if any(h['key'].lower()=='x-robots-tag' and 'noindex' in h['value'] for h in group['headers'])}
 assert noindex=={'/data/(.*)','/editorial/(.*)','/scripts/(.*)'},noindex
 return {'result':'pass','canonical_html_pages':len(pages),'canonical_aliases_excluded':aliases,'duplicate_titles':len(duplicate_titles),'sitemaps':counts,'scope':'Every generated candidate/directory/archive HTML page plus canonical static pages; no indexing/ranking guarantee.'}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args();report=audit()
 if args.output:args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=True))
