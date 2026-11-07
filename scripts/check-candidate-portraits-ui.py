"""Rendered photo and registration-position tasks using browser protocol only."""
import argparse,importlib.util,json,tempfile
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--base');parser.add_argument('--output',type=Path);parser.add_argument('--ids',nargs='+');args=parser.parse_args()
OUT=args.output or Path(tempfile.mkdtemp(prefix='ayiti-portrait-ui-'));OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build-candidates.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);registry,enrichment=m.load()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start();BASE=args.base or f'http://127.0.0.1:{server.server_port}'
people=registry['candidates'];senators=[p for p in people if p['office']=='senator'];pictured=[p for p in senators if enrichment['profiles'].get(p['id'],{}).get('portrait')]
added=[p for p in people if enrichment['profiles'].get(p['id'],{}).get('portrait') and (not args.ids or p['id'] in args.ids)];results=[]
if args.ids:assert set(args.ids)=={p['id'] for p in added},'Every requested profile must have a verified portrait'
with sync_playwright() as pw:
 browser=pw.chromium.launch()
 for width in [320,390,1280]:
  for lang in ['ht','en']:
   context=browser.new_context(viewport={'width':width,'height':844},device_scale_factor=2 if width<900 else 1);page=context.new_page();requests=[];errors=[]
   page.on('request',lambda r:requests.append(r.url));page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(BASE+m.directory(lang)+'?office=senator&photo=available');expect(page.locator('.candidate-card')).to_have_count(min(24,len(pictured)));expect(page.locator('#candidate-count')).to_contain_text(str(len(pictured)))
   assert page.locator('.candidate-initials').count()==0
   expect(page.locator('#candidate-photo-count')).to_contain_text(str(len(senators)))
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.locator('.candidate-results-bar').scroll_into_view_if_needed()
   image=page.locator('.candidate-card .candidate-photo img').first;page.locator('.candidate-card .candidate-photo').first.scroll_into_view_if_needed();expect(image).to_have_attribute('src',enrichment['profiles'][pictured[0]['id']]['portrait']['path'])
   page.wait_for_function('()=>document.querySelector(".candidate-card .candidate-photo img").naturalWidth>0')
   assert page.locator('.candidate-card-position').count()==min(24,len(pictured))
   assert not [url for url in requests if urlparse(url).netloc!=urlparse(BASE).netloc]
   page.screenshot(path=str(OUT/f'senate-{lang}-{width}.png'),full_page=False)
   if len(pictured)>24:
    page.locator('#candidate-pagination button').last.click();expect(page.locator('.candidate-card')).to_have_count(min(24,len(pictured)-24));expect(page.locator('select[name=photo]')).to_have_value('available');assert page.locator('.candidate-initials').count()==0
    page.locator('#candidate-pagination button').first.click();expect(page.locator('.candidate-card')).to_have_count(24)
   # Clear photo-only mode, then activate the quick filter with a pending search.
   expect(page.locator('#candidate-filters')).to_be_hidden();page.locator('#candidate-show-portraits').click();expect(page.locator('#candidate-count')).to_contain_text(str(len(senators)))
   page.locator('input[name=q]').fill('cantave');page.locator('#candidate-show-portraits').click();expect(page.locator('.candidate-card')).to_have_count(1);expect(page.locator('.candidate-card h2')).to_have_text('CARL MURAT CANTAVE')
   # The card must reach the actual pictured web; Back must retain the filter.
   page.locator('.candidate-card-link').click();expect(page.locator('.web-centre img')).to_be_visible();expect(page.locator('.candidate-photo-credit a')).to_have_text('Juno7')
   page.locator('#candidate-back').click();expect(page.locator('.candidate-card')).to_have_count(1);expect(page.locator('select[name=photo]')).to_have_value('available');expect(page.locator('input[name=q]')).to_have_value('cantave')
   assert not errors,errors
   results.append({'check':'senate-coverage-filter-search-picture-web-back','width':width,'lang':lang,'photos':len(pictured),'total':len(senators),'result':'pass'});context.close()
 # Every new profile must display its own local portrait and linked publisher credit.
 context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page()
 for person in added:
  image=enrichment['profiles'][person['id']]['portrait']
  for lang in ['ht','en']:
   page.goto(BASE+m.profile_url(person,lang)+'#information-web');expect(page.locator('.web-centre img')).to_have_attribute('src',image['web_path']);page.wait_for_function('()=>document.querySelector(".web-centre img").naturalWidth===192')
   expect(page.locator('.candidate-photo-credit a')).to_have_attribute('href',image['source_url']);expect(page.locator('.candidate-photo-credit')).to_contain_text(image['context'][lang]);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert page.locator('a[href$=".pdf"]').count()==0
  results.append({'check':'new-profile-photo-web-credit-both-languages','id':person['id'],'result':'pass'})
 context.close()
 # Every registration slot remains understandable without JavaScript.
 for lang in ['ht','en']:
  context=browser.new_context(java_script_enabled=False);page=context.new_page();page.goto(BASE+m.directory(lang)+'senator/')
  expect(page.locator('#candidate-count')).to_contain_text(str(len(senators)));expect(page.locator('#candidate-photo-count')).to_contain_text(str(len(pictured)))
  assert page.locator('.candidate-photo noscript img').count()>0
  for position in m.POSITION_KEYS:
   person=next(p for p in people if p['position']==position);page.goto(BASE+m.profile_url(person,lang));expect(page.locator('.candidate-facts')).to_contain_text(m.registration_position(person,lang))
  results.append({'check':'native-senate-portraits-and-all-nine-position-labels','lang':lang,'result':'pass'});context.close()
 browser.close()
server.shutdown();report={'base':BASE,'environment':'Headless Chromium, browser protocol only; no OS input or focus control.','new_portraits':len(added),'results':results};(OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({'cases':len(results),'new_portraits':len(added),'screenshots':str(OUT),'result':'pass'}))
