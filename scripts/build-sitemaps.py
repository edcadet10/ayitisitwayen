"""Generate a canonical-only sitemap index and base-page map; no network access."""
import argparse,json,re
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1];SITE='https://www.ayitisitwayen.org';NS='{http://www.sitemaps.org/schemas/sitemap/0.9}'
class Head(HTMLParser):
 def __init__(self,html):
  super().__init__();self.canonical=None;self.description=None;self.alternates={};self.title='';self.in_title=False;self.feed(html.split('</head>',1)[0])
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href')
  if tag=='link' and a.get('hreflang'):self.alternates[a['hreflang']]=a.get('href')
  if tag=='meta' and a.get('name')=='description':self.description=a.get('content')
  if tag=='title':self.in_title=True
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,text):
  if self.in_title:self.title+=text
def base_pages():
 dates=json.loads((ROOT/'data/site-page-dates.json').read_text(encoding='utf-8'))
 for path in sorted(list(ROOT.glob('*.html'))+list((ROOT/'en').glob('*.html'))+[ROOT/'audio/election-transcripts.html']):
  if re.fullmatch(r'google[a-f0-9]+\.html',path.name):continue
  route='/'+path.relative_to(ROOT).as_posix();route=route.removesuffix('index.html') if path.name=='index.html' else route
  head=Head(path.read_text(encoding='utf-8'))
  assert head.canonical and head.description and head.title,route
  assert head.canonical.startswith(SITE+'/') and '?' not in head.canonical and '#' not in head.canonical,route
  if head.canonical!=SITE+route:continue # Existing election/home aliases are not independent content.
  yield route,dates.get(route)
def outputs():
 pages=list(base_pages())
 rows=''.join('<url><loc>'+escape(SITE+route)+'</loc>'+('<lastmod>'+modified+'</lastmod>' if modified else '')+'</url>' for route,modified in pages)
 maps={'sitemap-pages.xml':'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+rows+'</urlset>\n'}
 entries=[]
 for name in ['sitemap-pages.xml','sitemap-candidates.xml','sitemap-candidate-directory.xml','sitemap-candidate-archives.xml']:
  content=maps.get(name) or (ROOT/name).read_text(encoding='utf-8');root=ET.fromstring(content);urls=root.findall(NS+'url');assert root.tag==NS+'urlset' and len(urls)<=50000 and len(content.encode())<=50000000,name
  modified=max((u.findtext(NS+'lastmod') or '' for u in urls),default='')
  entries.append('<sitemap><loc>'+SITE+'/'+name+'</loc>'+('<lastmod>'+modified+'</lastmod>' if modified else '')+'</sitemap>')
 maps['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(entries)+'</sitemapindex>\n'
 maps['robots.txt']='User-agent: *\nAllow: /\n\nSitemap: '+SITE+'/sitemap.xml\n'
 for name,content in maps.items():yield ROOT/name,content
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();changed=[]
 for path,content in outputs():
  if not path.exists() or path.read_text(encoding='utf-8')!=content:
   changed.append(path.name)
   if not args.check:path.write_text(content,encoding='utf-8',newline='\n')
 if args.check and changed:raise SystemExit('Sitemap files need regeneration: '+', '.join(changed))
 print('Canonical base pages:',len(list(base_pages())),'; sitemap index: 4 maps;',len(changed),'updated.')
if __name__=='__main__':main()
