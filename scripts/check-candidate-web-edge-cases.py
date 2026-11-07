import tempfile
import argparse,copy,importlib.util,json
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=Path(tempfile.mkdtemp(prefix='ayiti-web-ui-'))
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build-candidates.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r,e=m.load()
parser=argparse.ArgumentParser();parser.add_argument('--base');args=parser.parse_args()
class H(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(H,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start()
BASE=args.base or f'http://127.0.0.1:{server.server_port}';results=[]
def record(name,**details):results.append({'check':name,'result':'pass',**details});print(name+' passed',flush=True)
with sync_playwright() as p:
 b=p.chromium.launch();context=b.new_context(viewport={'width':390,'height':844},has_touch=True,permissions=['clipboard-read','clipboard-write']);page=context.new_page()
 route='/en/candidates/c-616382d917525405b2fa/'
 page.goto(BASE+route+'#information-web');page.locator('.web-node').last.wait_for();page.locator('.web-node').nth(3).click()
 expect(page.locator('.preview-candidate')).to_have_text('MULLER DEROSE')
 page.locator('.source-copy').click();expect(page.locator('.source-copy-status')).to_have_text('Link copied')
 saved=page.evaluate('navigator.clipboard.readText()');assert 'c-616382d917525405b2fa' in saved and 'source=' in saved and 'topic=campaign' in saved
 page.goto(saved);expect(page.locator('#web-preview-title')).to_have_text('MPH presents its candidates')
 page.locator('#web-close').click()
 if not page.locator('.lang-switch').is_visible():page.locator('.nav-toggle').click()
 page.locator('.lang-switch').click();assert '/en/' not in page.url and 'c-616382d917525405b2fa' in page.url and '#topic=campaign' in page.url
 page.locator('.source-node').first.click();expect(page.locator('#web-preview-title')).to_have_text('MPH prezante kandida li yo')
 page.locator('#web-close').click()
 record('mobile-source-copy-and-same-candidate-language-switch')
 # Nine synthetic sources test pagination without inventing public candidate content.
 person=copy.deepcopy(next(person for person in r['candidates'] if person['id']=='c-e8698b3339a756e88e60'));person['name']='UI pagination fixture'
 sources=[{'id':f'qa-{i}','title':{'ht':f'QA {i}','en':f'QA pagination item {i}'},'short_title':{'ht':f'QA {i}','en':f'QA item {i}'},'summary':{'ht':'QA','en':'Synthetic browser test data, never published as candidate information.'},'publisher':'QA fixture','type':'journalism','format':'article','categories':['articles'],'url':f'https://example.invalid/qa/{i}','reviewed_at':'2026-11-07','published_at':None,'review_status':'reviewed'} for i in range(1,10)]
 fixture={'profiles':{person['id']:{'sources':sources}}};html=m.profile_page('en',person,r,fixture)
 fixture_url=BASE+'/__web-ui-fixture__/'
 page.route(fixture_url+'**',lambda route:route.fulfill(status=200,content_type='text/html',body=html))
 page.goto(fixture_url+'#information-web');page.locator('.web-node').last.wait_for();page.locator('.web-node').first.click()
 assert page.locator('.source-node').count()==8;expect(page.locator('#web-page-count')).to_have_text('1 / 2')
 page.locator('.source-node').nth(7).click();expect(page.locator('#web-preview-title')).to_have_text('QA pagination item 8');page.locator('#web-close').click()
 page.locator('#web-next').click();assert page.locator('.source-node').count()==1;expect(page.locator('#web-page-count')).to_have_text('2 / 2')
 page.locator('.source-node').first.click();expect(page.locator('#web-preview-title')).to_have_text('QA pagination item 9')
 page.reload();expect(page.locator('#web-preview-title')).to_have_text('QA pagination item 9');page.locator('#web-close').click();page.locator('#web-previous').click();assert page.locator('.source-node').count()==8
 record('source-pagination-and-second-page-deep-link',fixture='Nine explicitly synthetic sources in a client-intercepted browser document; no public data changed.')
 context.close();context=b.new_context(viewport={'width':1280,'height':900});page=context.new_page();external=[]
 page.on('request',lambda req:external.append(req.url) if req.url.startswith('https://www.youtube-nocookie.com/') else None)
 rich='/en/candidates/c-e8698b3339a756e88e60/'
 page.goto(BASE+rich+'#source=etzer-priorities&topic=positions');expect(page.locator('#web-preview-title')).to_have_text('Etzer Emile’s campaign priorities')
 assert 'Proposals' in page.locator('#web-breadcrumb').inner_text()
 page.locator('.lang-switch').click();assert '#source=etzer-priorities&topic=positions' in page.url
 expect(page.locator('#web-breadcrumb')).to_contain_text('Pwopozisyon')
 record('language-switch-preserves-selected-source-and-topic')
 page.goto(BASE+rich+'#information-web');page.locator('.web-node').last.wait_for();page.locator('.web-node').nth(1).click();page.locator('.source-node').first.hover()
 assert page.locator('iframe').count()==0 and not external
 page.route('https://www.youtube-nocookie.com/**',lambda route:route.fulfill(status=200,content_type='text/html',body='<html><body><button>Explicit player request probe</button></body></html>'))
 page.locator('.source-node').first.click();page.get_by_role('button',name='Watch video').click();expect(page.locator('iframe')).to_have_count(1)
 assert 'autoplay=0' in page.locator('iframe').get_attribute('src');page.locator('.source-node').nth(1).hover();assert page.locator('iframe').count()==1
 page.locator('.source-node').nth(1).click();assert page.locator('iframe').count()==0
 page.get_by_role('button',name='Watch video').click();page.locator('#web-close').click();assert page.locator('iframe').count()==0
 record('explicit-player-request-pinning-and-cleanup',note='Player request intercepted by a stub. Actual YouTube streaming was not tested or claimed.')
 context.close();context=b.new_context(java_script_enabled=False);page=context.new_page();page.goto(BASE+'/en/candidates/c-318821d7c6585a15b714/')
 expect(page.locator('.candidate-source-list')).to_contain_text('publicly visible excerpt');expect(page.locator('.candidate-source-list .source-access-note')).to_be_visible()
 assert page.locator('.candidate-source-list a[href$=".pdf"]').count()==0
 record('native-archive-without-javascript-shows-excerpt-limit');context.close();b.close()
server.shutdown();(OUT/('live-edge-results.json' if args.base else 'local-edge-results.json')).write_text(json.dumps(results,indent=2),encoding='utf-8')

print("Browser evidence saved to:",OUT)
