"""Render real data for local browser checks without writing every registration page."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build-candidates.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def prepare():
 r,e=m.load();people=[p for p in r['candidates'] if p['id'] in e['profiles']]
 for office in m.OFFICES.values():
  person=next((p for p in r['candidates'] if p['office']==office and p['id'] not in e['profiles']),None)
  if person:people.append(person)
 def write(route,html):
  path=ROOT/route.strip('/')/'index.html' if route.endswith('/') else ROOT/route.strip('/');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(html,encoding='utf-8',newline='\n')
 for person in people:
  sources=m.sources_for(person,r,e)
  if len(sources)>24:write('/data/candidate-public/archives/'+person['id']+'.json',m.compact({'id':person['id'],'sources':sources}))
  for lang in ['ht','en']:
   write(m.profile_url(person,lang),m.profile_page(lang,person,r,e))
   if len(sources)>24:
    years=sorted({year for source in sources for year in m.source_years(source)})
    for year in ['all']+years:
     pages=max(1,(sum(year=='all' or year in m.source_years(s) for s in sources)+23)//24)
     for page in {1,pages}:write(*m.archive_page(lang,person,sources,year,page))
 for lang in ['ht','en']:write(*m.directory_page(lang,r,e))
 print('Real profile fixtures:',len(people),'in both languages',flush=True)
if __name__=='__main__':prepare()
