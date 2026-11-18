"""Check public source/candidate associations and bilingual publication boundaries."""
import hashlib,importlib.util,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_social_builder',ROOT/'scripts/build-candidates.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class SocialPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/candidates/reviewed-social.json').read_text(encoding='utf-8'))
        cls.review=json.loads((ROOT/'editorial/social-material-publication-review-2026-11-18.json').read_text(encoding='utf-8'))
        cls.registry,cls.enrichment=builder.load()
        cls.people={p['id']:p for p in cls.registry['candidates']+cls.registry.get('retained_candidates',[])}

    def test_exact_source_coverage_and_identity_links(self):
        self.assertEqual(self.review['source_index_sha256'],hashlib.sha256((ROOT/'data/candidates/reviewed-social.json').read_bytes()).hexdigest())
        posts={sid:p for sid,p in self.data['publications'].items() if p['format']=='social_post'}
        self.assertEqual(len(posts),self.review['social_source_count'])
        self.assertEqual(len(posts),616)
        self.assertEqual(len({p['url'] for p in posts.values()}),616)
        linked=[]
        for cid,profile in self.data['profiles'].items():
            self.assertIn(cid,self.people)
            self.assertEqual(set(profile['source_ids']),set(profile['source_relations']))
            for sid in profile['source_ids']:
                self.assertIn(sid,self.data['publications'])
                self.assertIn(sid,self.enrichment['profiles'][cid]['source_ids'])
                if sid in posts:
                    linked.append(sid)
                    self.assertIn(profile['source_relations'][sid],['candidate_authored','candidate_coauthored'])
        self.assertEqual(len(linked),616)
        self.assertEqual(set(linked),set(posts))

    def test_source_indices_do_not_present_statements_as_verified_outcomes(self):
        for source in self.data['publications'].values():
            if source['format']!='social_post':continue
            self.assertEqual(source['review_status'],'indexed')
            self.assertEqual(source['editorial_level'],'index')
            self.assertEqual(source['summary'],builder.COPY['social_review_index_note'])
            self.assertEqual(source['date_basis'],'publication_time_in_Haiti_not_event_date')
            self.assertTrue(source['excerpt_is_original_language'])
            self.assertRegex(source['url'],r'^https://(?:x\.com/[^/]+/status/\d+|www\.instagram\.com/(?:[^/]+/)?p/[A-Za-z0-9_-]+/)')
            self.assertNotIn('event_date',source)
            for title in source['title'].values():
                if '« ' in title:self.assertLessEqual(len(title.split('« ',1)[1].rsplit(' »',1)[0].split()),12)

    def test_no_private_corpus_or_credentials_in_public_index(self):
        raw=(ROOT/'data/candidates/reviewed-social.json').read_text(encoding='utf-8')
        for marker in ['C:\\Users','social-review.sqlite','caption_evidence','proof_evidence','api_key','sk_','personal_identifier']:
            self.assertNotIn(marker,raw)

    def test_all_new_articles_are_reachable_as_source_nodes_and_profile_links(self):
        articles={a['slug']:a for a in builder.EDITORIAL['articles']}
        for slug in self.review['article_slugs']:
            article=articles[slug];self.assertEqual(article['status'],'published')
            source=next(s for s in self.data['publications'].values() if s['url'].endswith('/'+slug+'/'))
            self.assertEqual(source['title'],article['title'])
            self.assertEqual(source['summary'],article['description'])
            self.assertEqual(source['type']=='opinion',article['kind']=='opinion')
            for cid in article['candidate_ids']:
                self.assertIn(source['id'],self.data['profiles'][cid]['source_ids'])
                for lang in ['ht','en']:
                    page=builder.profile_page(lang,self.people[cid],self.registry,self.enrichment)
                    target=(' /en/' if lang=='en' else ' /').strip()+'elections/analysis/'+slug+'/'
                    self.assertIn('href="'+target+'"',page)

if __name__=='__main__':unittest.main()
