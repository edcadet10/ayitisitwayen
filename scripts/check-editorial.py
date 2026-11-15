"""Publication checks for original articles; these do not certify factual truth."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('editorial_builder',ROOT/'scripts/build-editorial.py')
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class EditorialChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.about,cls.people,cls.portraits=builder.load()

    def test_word_ceiling_in_each_language(self):
        self.assertEqual(self.data['word_limit'],500)
        for article in self.data['articles']:
            for lang in builder.LANGUAGES:
                self.assertLessEqual(builder.word_count(article,lang),500,(article['slug'],lang))

    def test_overlong_article_is_rejected(self):
        data=copy.deepcopy(self.data)
        data['articles'][0]['paragraphs'][0]['text']['en']='word '*501
        with self.assertRaises(AssertionError):builder.validate(data,self.about,self.people)

    def test_unresolvable_citation_is_rejected(self):
        data=copy.deepcopy(self.data)
        data['articles'][0]['paragraphs'][0]['sources']=['no-such-document']
        with self.assertRaises(AssertionError):builder.validate(data,self.about,self.people)

    def test_documented_claim_requires_citation(self):
        data=copy.deepcopy(self.data)
        record=next(p for a in data['articles'] for p in builder.article_paragraphs(a) if p['kind']=='record')
        record['sources']=[]
        with self.assertRaises(AssertionError):builder.validate(data,self.about,self.people)

    def test_duplicate_slug_is_rejected(self):
        data=copy.deepcopy(self.data)
        data['articles'].append(copy.deepcopy(data['articles'][0]))
        with self.assertRaises(AssertionError):builder.validate(data,self.about,self.people)

    def test_stale_audio_is_rejected(self):
        data=copy.deepcopy(self.data)
        recorded=next((a for a in data['articles'] if a.get('audio')),None)
        if recorded is None:self.skipTest('No recording has been published')
        recorded['paragraphs'][0]['text']['ht']+=' Yon chanjman.'
        with self.assertRaises(AssertionError):builder.validate(data,self.about,self.people)

    def test_no_unverified_identity_can_be_attached(self):
        data=copy.deepcopy(self.data)
        data['articles'][0]['candidate_ids']=['c-not-a-verified-identity']
        with self.assertRaises(AssertionError):builder.validate(data,self.about,self.people)

    def test_draft_not_in_public_index(self):
        data=copy.deepcopy(self.data)
        data['articles'][0]['status']='draft'
        for lang in builder.LANGUAGES:
            rendered=builder.index_page(lang,data,self.people,self.portraits)
            self.assertNotIn(builder.route(lang,data['articles'][0]['slug']),rendered)

    def test_withdrawn_html_cannot_silently_remain_public(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            stale=root/'elections/analysis/withdrawn/index.html'
            stale.parent.mkdir(parents=True)
            stale.write_text('<h1>Withdrawn draft</h1>',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Unpublished or stale'):
                builder.reject_stale_routes(root,[])
            builder.reject_stale_routes(root,[stale])

    def test_inline_json_cannot_close_script(self):
        dangerous='</script><img src=x onerror=alert(1)>'
        encoded=builder.compact({'text':dangerous})
        self.assertNotIn('<',encoded)
        self.assertEqual(json.loads(encoded)['text'],dangerous)

    def test_native_article_and_visible_claims_match_metadata(self):
        for article in self.data['articles']:
            if article['status']!='published':continue
            for lang in builder.LANGUAGES:
                rendered=builder.article_page(lang,article,self.data,self.people,self.portraits)
                blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',rendered,re.S)
                graph=json.loads(blocks[0])['@graph']
                metadata=next(item for item in graph if item['@type']=='Article')
                self.assertEqual(metadata['author']['@type'],'Organization')
                self.assertEqual(metadata['author']['name'],'Ayiti Sitwayen')
                self.assertEqual(metadata['wordCount'],builder.word_count(article,lang))
                self.assertEqual(metadata['articleBody'],'\n\n'.join(p['text'][lang] for p in builder.article_paragraphs(article)))
                for paragraph in builder.article_paragraphs(article):
                    self.assertIn(builder.escape(paragraph['text'][lang]),rendered)
                    for sid in paragraph['sources']:
                        self.assertIn('href="#source-'+sid+'"',rendered)
                        self.assertIn('id="source-'+sid+'"',rendered)
                canonical=builder.SITE+builder.route(lang,article['slug'])
                self.assertIn('rel="canonical" href="'+canonical+'"',rendered)
                for code,url in [('ht',builder.SITE+builder.route('ht',article['slug'])),('en',builder.SITE+builder.route('en',article['slug'])),('x-default',builder.SITE+builder.route('ht',article['slug']))]:
                    self.assertIn('hreflang="'+code+'" href="'+url+'"',rendered)

    def test_published_routes_and_about_are_unique(self):
        paths=[path for path,_ in builder.outputs()]
        self.assertEqual(len(paths),len(set(paths)))
        for lang in builder.LANGUAGES:
            self.assertIn(ROOT/builder.route(lang).strip('/')/'index.html',paths)
            self.assertIn(ROOT/(builder.prefix(lang)+'about.html').strip('/'),paths)

    def test_candidate_records_link_back_to_published_pieces(self):
        spec=importlib.util.spec_from_file_location('candidate_builder_for_editorial',ROOT/'scripts/build-candidates.py')
        candidate_builder=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(candidate_builder)
        registry,enrichment=candidate_builder.load()
        published=[a for a in self.data['articles'] if a['status']=='published']
        linked_ids={cid for a in published for cid in a['candidate_ids']}
        for person in registry['candidates']:
            if person['id'] not in linked_ids:continue
            for lang in builder.LANGUAGES:
                rendered=candidate_builder.profile_page(lang,person,registry,enrichment)
                self.assertIn('id="candidate-editorial-title"',rendered)
                for article in published:
                    if person['id'] in article['candidate_ids']:
                        self.assertIn(builder.route(lang,article['slug']),rendered)


if __name__=='__main__':unittest.main()
