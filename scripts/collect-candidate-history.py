"""Collect a bounded, read-only publisher search for editorial identity review.

No automatic publishing. Only headlines/URLs/dates and match contexts enter the
local queue; full article bodies are discarded. HTTP denial or an incomplete
page set is recorded as incomplete, never as evidence of no historical coverage.
"""
import argparse,hashlib,json,re,time,unicodedata
from html import unescape
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
PUBLISHERS={'juno7':'https://www.juno7.ht','metropole':'https://metropole.ht','rezonodwes':'https://rezonodwes.com'}
def normal(value):return ''.join(c for c in unicodedata.normalize('NFD',value.lower()) if not unicodedata.combining(c))
def visible(html):return unescape(re.sub('<[^>]+>',' ',html))
def collect(candidate,query,publisher,max_pages):
 rows={};receipt={'candidate_id':candidate['id'],'query':query,'publisher':publisher,'status':'not_started','pages':0,'reported_total':None}
 for page in range(1,max_pages+1):
  params=urlencode({'search':query,'per_page':100,'page':page,'_fields':'id,date,link,title,content'})
  url=PUBLISHERS[publisher]+'/wp-json/wp/v2/posts?'+params
  try:
   with urlopen(Request(url,headers={'User-Agent':'AyitiSitwayen public archive research'}),timeout=30) as response:
    raw=response.read();items=json.loads(raw);total=int(response.headers.get('X-WP-Total','0'));pages=int(response.headers.get('X-WP-TotalPages','1'))
  except (HTTPError,URLError,TimeoutError,ValueError) as error:
   receipt.update(status='incomplete_request_error',error=str(error));break
  receipt.update(reported_total=total,pages=page)
  for item in items:
   title=visible(item['title']['rendered']).strip();text=visible(item['content']['rendered']);pattern=r'(?<!\w)'+re.escape(normal(query))+r'(?!\w)';hit=re.search(pattern,normal(text));headline_match=bool(re.search(pattern,normal(title)))
   context=text[max(0,hit.start()-100):hit.end()+160] if hit else ''
   rows[str(item['id'])]={'publisher_id':item['id'],'url':item['link'],'published_at':item['date'][:10],'title':title,'candidate_id':candidate['id'],'match':'headline' if headline_match else 'text_name' if hit else 'search_only','context_for_identity_review':context,'status':'needs_identity_and_context_review','response_sha256':hashlib.sha256(raw).hexdigest()}
  if page>=pages:
   receipt['status']='query_pages_complete' if len(rows)==total else 'incomplete_count_mismatch';break
  receipt['status']='incomplete_page_cap';time.sleep(.5)
 return {'receipt':receipt,'records':list(rows.values())}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--candidate',required=True);parser.add_argument('--alias',help='Explicit editorial alias, not an automatic identity assertion');parser.add_argument('--publisher',choices=PUBLISHERS,required=True);parser.add_argument('--max-pages',type=int,default=5);parser.add_argument('--output',type=Path,default=ROOT/'editorial/candidate-history-review-queue.json');args=parser.parse_args()
 if not 1<=args.max_pages<=100:parser.error('--max-pages must be between 1 and 100')
 registry=json.loads((ROOT/'data/candidates/registry.json').read_text(encoding='utf-8'));person=next((p for p in registry['candidates'] if p['id']==args.candidate),None)
 if not person:parser.error('Unknown registration ID')
 result=collect(person,args.alias or person['name'],args.publisher,args.max_pages);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result['receipt']))
if __name__=='__main__':main()
