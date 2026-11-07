"""Historical archive tasks in rendered Chromium. No human usability-study claim."""
import argparse,importlib.util,json,tempfile,time
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=Path(tempfile.mkdtemp(prefix='ayiti-history-ui-'))
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build-candidates.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);registry,enrichment=m.load()
parser=argparse.ArgumentParser();parser.add_argument('--base');args=parser.parse_args()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start();BASE=args.base or f'http://127.0.0.1:{server.server_port}'
rich=next(p for p in registry['candidates'] if p['surname']=='MARTELLY');sources=m.sources_for(rich,registry,enrichment);results=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for width in [320,390,1280]:
  for lang in ['ht','en']:
   context=browser.new_context(viewport={'width':width,'height':844},has_touch=width<900);page=context.new_page();errors=[];requests=[]
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
   page.goto(BASE+m.profile_url(rich,lang)+'#information-web');expect(page.locator('.web-node')).to_have_count(8)
   assert not [url for url in requests if '/data/candidate-public/archives/' in url], 'Full catalog downloaded before intent'
   assert page.locator('.candidate-source-card').count()<=24
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.locator('#web-source-year').select_option('2011');expect(page.locator('#web-filter-status')).to_contain_text('2011')
   expected=[s for s in sources if '2011' in m.source_years(s)]
   expect(page.locator('#web-filter-status')).to_contain_text(str(len(expected)))
   page.locator('.web-node').nth(7).click();expect(page.locator('.source-node')).to_have_count(min(8,len(expected)))
   page.locator('.source-node').first.click();expect(page.locator('#web-preview-date')).to_contain_text('2011');page.locator('#web-close').click()
   # A source deep-link must reach older pages, with the correct topic and year.
   oldest=next(s for s in reversed(sources) if s.get('published_at','') and s['published_at'].startswith('2002'))
   page.goto(BASE+m.profile_url(rich,lang)+'#source='+oldest['id']+'&topic=history&year=2002')
   expect(page.locator('#web-preview-title')).to_have_text(oldest['title'][lang]);expect(page.locator('#web-preview-date')).to_contain_text('2002')
   assert page.locator('#web-preview-action>a').get_attribute('href')==oldest['url'];page.locator('#web-close').click()
   expect(page.locator('#web-source-year')).to_have_value('2002')
   page.locator('.web-archive-more summary').click();page.locator('.web-archive-more button').click();expect(page.locator('#web-source-year')).to_have_value('')
   page.locator('#source-archive-next').click();expect(page.locator('#source-archive-pagination')).to_contain_text('2 ')
   assert page.locator('.candidate-source-card').count()<=24
   page.locator('#web-source-query').fill('zzzz_no_candidate_source_zzzz');expect(page.locator('.candidate-archive-empty')).to_be_visible();assert page.locator('.web-node:not(:disabled)').count()==0
   page.locator('#web-source-query').fill('');expect(page.locator('.candidate-source-card')).to_have_count(24)
   page.locator('#web-source-relation').select_option('mention');expect(page.locator('#web-filter-status')).to_contain_text(m.t('sources',lang))
   expect(page.locator('.candidate-source-card').first.locator('.source-relationship')).to_be_visible()
   assert not errors,errors
   assert not [url for url in requests if urlparse(url).netloc!=urlparse(BASE).netloc]
   page.screenshot(path=str(OUT/f'archive-{lang}-{width}.png'),full_page=False)
   results.append({'check':'historical-year-deeplink-pagination-empty-search-mention','lang':lang,'width':width,'year_2011_sources':len(expected),'result':'pass'});context.close()
 # A failed catalog must leave the native archive usable and permit a retry.
 context=browser.new_context();page=context.new_page();page.route('**/data/candidate-public/archives/**',lambda route:route.fulfill(status=503,body='Unavailable'))
 page.goto(BASE+m.profile_url(rich,'en'));page.locator('#web-source-year').select_option('2011');expect(page.locator('#web-state-hint button')).to_be_visible();assert page.locator('.candidate-source-card').count()==24
 page.unroute('**/data/candidate-public/archives/**');page.locator('#web-state-hint button').click();expect(page.locator('#web-filter-status')).to_contain_text('2011');results.append({'check':'failed-catalog-keeps-native-cards-and-retry-recovers','result':'pass'});context.close()
 # Native year archives preserve original links without JavaScript.
 context=browser.new_context(java_script_enabled=False);page=context.new_page();page.goto(BASE+m.archive_url(rich,'en','2011'));expect(page.locator('h1')).to_contain_text('2011');assert 0<page.locator('.candidate-source-card').count()<=24
 assert page.locator('.source-preview-link:visible').count()==0
 assert page.locator('a[href$=".pdf"]').count()==0;results.append({'check':'historical-native-year-archive-without-javascript','result':'pass'});context.close()
 # Predeclared falsifiers: >350KB initial decoded resources, >24 archive cards,
 # >8 graph controls, remote requests, or >1.5s filter response with 6x CPU slowdown.
 context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page();session=context.new_cdp_session(page);session.send('Emulation.setCPUThrottlingRate',{'rate':6});requests=[];page.on('request',lambda r:requests.append(r.url))
 page.goto(BASE+m.profile_url(rich,'en')+'#information-web');expect(page.locator('.web-node')).to_have_count(8)
 initial=page.evaluate('performance.getEntriesByType("navigation").concat(performance.getEntriesByType("resource")).reduce((n,r)=>n+(r.decodedBodySize||0),0)')
 assert initial<=350000,initial;assert not any('/archives/' in url for url in requests)
 page.locator('#web-source-year').select_option('2011');expect(page.locator('#web-filter-status')).to_contain_text('2011')
 start=time.perf_counter();page.locator('#web-source-query').fill('zzzz_no_candidate_source_zzzz');expect(page.locator('.candidate-archive-empty')).to_be_visible();latency=round((time.perf_counter()-start)*1000)
 assert latency<=1500,latency
 assert page.locator('.web-node').count()<=8 and page.locator('.candidate-source-card').count()<=24
 results.append({'check':'largest-archive-initial-payload-and-throttled-filter','initial_decoded_bytes':initial,'cpu_slowdown':6,'filter_ms':latency,'result':'pass'});context.close();browser.close()
server.shutdown();(OUT/'results.json').write_text(json.dumps({'base':BASE,'results':results,'limits':'Browser automation, not a human or physical-device study.'},indent=2),encoding='utf-8');print(json.dumps({'checks':len(results),'evidence':str(OUT),'result':'pass'}))
