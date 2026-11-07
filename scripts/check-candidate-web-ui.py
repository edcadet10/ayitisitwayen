import tempfile
"""Rendered browser tasks; these are lab checks, not a human usability study."""
import argparse,importlib.util,json,time
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1];OUT=Path(tempfile.mkdtemp(prefix='ayiti-web-ui-'))
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build-candidates.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);registry,enrichment=m.load()
parser=argparse.ArgumentParser();parser.add_argument('--base');parser.add_argument('--quick',action='store_true');parser.add_argument('--ids',nargs='+');args=parser.parse_args()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def end_headers(self):
  for group in json.loads((ROOT/'vercel.json').read_text(encoding='utf-8'))['headers']:
   if group['source']=='/(.*)':
    for header in group['headers']:
     if header['key']=='Content-Security-Policy':self.send_header(header['key'],header['value'].replace('; upgrade-insecure-requests',''))
  super().end_headers()
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start()
BASE=args.base or f'http://127.0.0.1:{server.server_port}'
people=[p for p in registry['candidates'] if p['id'] in enrichment['profiles']]
for office in m.OFFICES.values():
 p=next((p for p in registry['candidates'] if p['office']==office and p['id'] not in enrichment['profiles']),None)
 if p:people.append(p)
if args.quick:people=[next(p for p in people if p['id']==ident) for ident in ['c-e8698b3339a756e88e60','c-616382d917525405b2fa','c-7308041793ef5e32b5ff']]+[next(p for p in people if p['office']=='senator')]
if args.ids:people=[p for p in people if p['id'] in args.ids]
results=[];source_previews=0;topic_visits=0
def overlap(page):
 return page.locator('.web-node').evaluate_all('els=>{const a=els.map(e=>e.getBoundingClientRect());let n=0;for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)if(a[i].x<a[j].right&&a[i].right>a[j].x&&a[i].y<a[j].bottom&&a[i].bottom>a[j].y)n++;return n}')
with sync_playwright() as p:
 browser=p.chromium.launch()
 for width in [390,1280]:
  context=browser.new_context(viewport={'width':width,'height':844},has_touch=width<900)
  for lang in ['ht','en']:
   for person in people:
    page=context.new_page();errors=[];requests=[]
    page.on('pageerror',lambda error:errors.append(str(error)));page.on('request',lambda request:requests.append(request.url))
    route=m.profile_url(person,lang);page.goto(BASE+route+'#information-web');page.locator('.web-node').last.wait_for()
    assert page.locator('.web-node').count()==8
    assert page.locator('.web-radius').count()==16 and page.locator('.web-loop').count()==8
    assert page.evaluate('getComputedStyle(document.body).backgroundColor')=='rgb(255, 255, 255)'
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert overlap(page)==0,(person['name'],lang,width,'overlap')
    sources=m.sources_for(person,registry,enrichment);visited=set()
    for index,(category,_) in enumerate(m.CATEGORIES):
     available=[source for source in sources if category in source['categories']]
     topic=page.locator('.web-node').nth(index)
     if not available:
      assert topic.is_disabled(),(person['name'],category,'empty topic enabled')
      continue
     topic.click();topic_visits+=1
     expect(page.locator('.source-node')).to_have_count(min(8,len(available)))
     assert overlap(page)==0
     ids=page.locator('.source-node').evaluate_all('els=>els.map(e=>e.dataset.sourceId)');assert len(ids)==len(set(ids))
     if page.locator('#web-mobile-preview').evaluate('e=>e.open'):page.locator('#web-close').click()
     displayed=[next(source for source in available if source['id']==ident) for ident in ids]
     for source_index,source in enumerate(displayed):
      if source['id'] in visited:continue
      point=page.locator('.source-node').nth(source_index);point.click()
      expect(page.locator('#web-preview-title')).to_have_text(source['title'][lang])
      expect(page.locator('#web-preview-summary')).to_have_text(source['summary'][lang])
      assert ' '.join(source['publisher'].split()) in ' '.join(page.locator('#web-preview-publisher').inner_text().split()),(person['name'],source['id'],'publisher attribution')
      link=page.locator('#web-preview-action>a');assert link.get_attribute('href')==('#registration' if source.get('native') else source['url'])
      if width<900:
       assert page.locator('#web-mobile-preview').evaluate('e=>e.open')
       box=link.bounding_box();assert box['y']>=0 and box['y']+box['height']<=844,(person['name'],source['id'],box)
       assert page.evaluate('document.activeElement.id')=='web-preview-title'
      if source.get('access')=='account':expect(page.locator('#web-preview-action .source-access-note')).to_be_visible()
      if source.get('native'):
       expect(page.locator('.web-record-facts')).to_contain_text(person['party'])
       expect(page.locator('.web-record-facts')).to_contain_text(m.COPY[person['status']][lang])
      visited.add(source['id']);source_previews+=1
      if width==390 and lang=='ht' and source_index==0 and len(visited)==1:page.screenshot(path=str(OUT/f'after-{person["id"]}.png'))
      page.locator('#web-close').click()
      assert not page.locator('#web-mobile-preview').evaluate('e=>e.open')
      assert page.evaluate('document.activeElement.classList.contains("source-node")')
      assert '#topic=' in page.url and '#source=' not in page.url
     page.locator('#web-back').click()
     assert page.url.endswith('#information-web')
     assert page.locator('.web-node').count()==8
     assert page.evaluate('Number(document.activeElement.dataset.index)')==index
     assert page.locator('#web-preview-content').is_hidden()
    assert visited and visited.issubset({source['id'] for source in sources}),(person['name'],visited)
    if len(sources)<=8:assert visited=={source['id'] for source in sources}
    if len(sources)==1:expect(page.locator('.web-coverage-note')).to_be_visible()
    assert not errors,(person['name'],errors)
    assert not [url for url in requests if urlparse(url).netloc!=urlparse(BASE).netloc]
    results.append({'id':person['id'],'office':person['office'],'lang':lang,'width':width,'sources_previewed':len(visited),'result':'pass'})
    page.close()
    if len(results)%10==0:print(f'UI profile cases passed: {len(results)}; source previews: {source_previews}',flush=True)
  context.close()
 # Narrow layouts, keyboard modal behavior, native registration and deep links.
 rich=next(p for p in registry['candidates'] if p['id']=='c-e8698b3339a756e88e60')
 for width,height in [(320,700),(390,560),(768,900),(1280,900)]:
  context=browser.new_context(viewport={'width':width,'height':height},has_touch=width<900)
  page=context.new_page();page.goto(BASE+m.profile_url(rich,'en')+'#information-web');page.locator('.web-node').last.wait_for();assert overlap(page)==0
  page.locator('.web-node').nth(3).click();page.locator('.source-node').first.focus();page.keyboard.press('Enter')
  if width<=900:
   assert page.locator('#web-mobile-preview').evaluate('e=>e.open')
   for _ in range(8):
    page.keyboard.press('Tab');assert page.evaluate('!!document.activeElement.closest("#web-mobile-preview")')
   page.keyboard.press('Escape');assert not page.locator('#web-mobile-preview').evaluate('e=>e.open')
   assert page.evaluate('document.activeElement.classList.contains("source-node")')
   assert page.locator('#web-preview-content').is_hidden()
  else:
   previous=page.locator('#web-preview-title').inner_text();page.locator('.source-node').nth(1).hover();assert page.locator('#web-preview-title').inner_text()==previous
   page.keyboard.press('Escape')
  page.locator('#web-back').click();page.locator('.web-node').nth(4).click()
  page.locator('#web-preview-action>a').click();assert page.url.endswith('#registration')
  assert not page.locator('#web-mobile-preview').evaluate('e=>e.open')
  page.locator('#candidate-open-web').click();assert page.url.endswith('#information-web')
  page.goto(BASE+m.profile_url(rich,'en')+'#source=etzer-priorities');page.locator('#web-preview-title').wait_for(state='visible');assert 'priorities' in page.locator('#web-preview-title').inner_text().lower()
  if width<=900:page.locator('#web-close').click()
  page.goto(BASE+m.profile_url(rich,'en')+'#source=missing-source');page.locator('.web-node').last.wait_for();expect(page.locator('#web-breadcrumb')).to_have_text(m.COPY['link_unavailable']['en'])
  assert page.locator('#web-preview-content').is_hidden()
  results.append({'check':'keyboard-native-record-and-deep-links','width':width,'height':height,'result':'pass'});context.close()
 browser.close()
server.shutdown()
report={'base':BASE,'environment':'Real Chromium rendered UI controlled through Playwright; not a human or physical-device usability study.','sampling':'All non-empty topics; first graph page per topic. Every source is checked by data invariants; the separate history audit checks older deep links, archive pagination and year discovery.','profile_count':len(people),'profile_ui_cases':sum('id' in row for row in results),'source_previews':source_previews,'topic_visits':topic_visits,'results':results}
out=OUT/('live-ui-results.json' if args.base else 'local-ui-results.json');out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))

print("Browser evidence saved to:",OUT)
