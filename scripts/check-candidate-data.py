"""Meaningful invariants for reviewed data and source/render safety, without a network dependency."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_builder',ROOT/'scripts/build-candidates.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class CandidateDataChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.registry,cls.enrichment=builder.load()
    def test_office_counts_and_source_uniqueness(self):
        self.assertEqual(self.registry['total'],sum(self.registry['office_counts'].values()))
        fingerprints=[p['source_fingerprint'] for p in self.registry['candidates']]
        self.assertEqual(len(fingerprints),len(set(fingerprints)))
        self.assertEqual(set(self.registry['office_counts']),set(builder.OFFICES.values()))
    def test_registration_is_not_approval(self):
        self.assertTrue(all(p['status']=='preliminary' for p in self.registry['candidates']))
        person=self.registry['candidates'][0]
        sources=builder.sources_for(person,self.registry,self.enrichment)
        self.assertTrue(sources[0]['native'])
        self.assertIn('preliminary',sources[0]['summary']['en'])
    def test_exact_names_preserved_and_not_merged(self):
        for person in self.registry['candidates']:
            self.assertEqual(person['name'],person['given_name']+' '+person['surname'])
        josephs=[p for p in self.registry['candidates'] if p['surname']=='JOSEPH']
        self.assertGreater(len(josephs),1)
        self.assertEqual(len(josephs),len({p['id'] for p in josephs}))
    def test_untrusted_url_schemes_are_rejected(self):
        for value in ['javascript:alert(1)','data:text/html,test','http://example.com','https://user:secret@example.com']:
            with self.assertRaises(AssertionError):builder.safe_url(value)
    def test_source_text_is_escaped_and_json_is_inert(self):
        source={'key':'</script><script>alert(1)</script>'}
        encoded=builder.compact(source)
        self.assertNotIn('</script>',encoded)
        self.assertEqual(json.loads(encoded),source)
        person={**self.registry['candidates'][0],'name':'<img src=x onerror=alert(1)>'}
        html=builder.card(person,self.enrichment,'en')
        self.assertNotIn('<img src=x',html)
        self.assertIn('&lt;img',html)
    def test_shared_publications_and_portrait_provenance(self):
        for entry in self.enrichment['profiles'].values():
            for source_id in entry['source_ids']:self.assertIn(source_id,self.enrichment['publications'])
            if entry.get('portrait'):
                self.assertTrue(entry['portrait']['source_url'])
                self.assertTrue(entry['portrait']['context']['en'])
                self.assertTrue(entry['portrait']['reuse_basis'])
        for source in self.enrichment['publications'].values():
            self.assertFalse(source['url'].lower().split('?')[0].endswith('.pdf'))
            self.assertEqual(source['review_status'],'reviewed')
    def test_both_languages_keep_profile_identity(self):
        person=self.registry['candidates'][0]
        for lang in ['ht','en']:
            html=builder.profile_page(lang,person,self.registry,self.enrichment)
            self.assertIn(builder.profile_url(person,'ht'),html)
            self.assertIn(builder.profile_url(person,'en'),html)
            self.assertIn(person['name'],html)
    def test_copy_review_fixes_are_present(self):
        self.assertEqual(builder.COPY['mayor']['ht'],'Majistra')
        self.assertEqual(builder.COPY['reviewed']['ht'],'Revize')
        self.assertIn('siwo myèl',self.enrichment['publications']['etzer-video-honey']['title']['ht'])

if __name__=='__main__':unittest.main()
