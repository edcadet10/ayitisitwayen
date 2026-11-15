"""Meaningful invariants for reviewed data and source/render safety, without a network dependency."""
import importlib.util
import json
import re
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
    def test_retained_registrations_keep_last_observed_dates(self):
        retained=self.registry.get('retained_candidates',[])
        self.assertTrue(retained)
        current_ids={p['id'] for p in self.registry['candidates']}
        current_fingerprints={p['source_fingerprint'] for p in self.registry['candidates']}
        for person in retained:
            self.assertNotIn(person['id'],current_ids)
            self.assertNotIn(person['source_fingerprint'],current_fingerprints)
            self.assertEqual(person['status'],'preliminary')
            self.assertLess(person['last_observed_at'],person['not_observed_at'])
            source=builder.sources_for(person,self.registry,self.enrichment)[0]
            self.assertEqual(source['reviewed_at'],person['last_observed_at'])
            for lang in ['ht','en']:
                self.assertIn(person['last_observed_at'],source['summary'][lang])
                self.assertIn(person['not_observed_at'],source['summary'][lang])
    def test_current_catalog_excludes_retained_registrations(self):
        path,content=next(builder.outputs(self.registry,self.enrichment))
        self.assertEqual(path.name,'catalog.json')
        catalog=json.loads(content)
        self.assertEqual(len(catalog['candidates']),self.registry['total'])
        self.assertEqual({p['id'] for p in catalog['candidates']},{p['id'] for p in self.registry['candidates']})
        self.assertFalse({p['id'] for p in self.registry.get('retained_candidates',[])} & {p['id'] for p in catalog['candidates']})
    def test_retained_profiles_keep_bilingual_urls_and_absence_notice(self):
        person=self.registry['retained_candidates'][0]
        for lang in ['ht','en']:
            html=builder.profile_page(lang,person,self.registry,self.enrichment)
            self.assertIn('candidate-retained-note',html)
            self.assertIn(f'<time datetime="{person["last_observed_at"]}">{person["last_observed_at"]}</time>',html)
            for other in ['ht','en']:self.assertIn(builder.profile_url(person,other),html)
    def test_portrait_profiles_have_person_specific_sharing_images(self):
        people=[person for person in self.registry['candidates'] if self.enrichment['profiles'].get(person['id'],{}).get('portrait')]
        for person in people:
            image=self.enrichment['profiles'][person['id']]['portrait']['path']
            html=builder.profile_page('en',person,self.registry,self.enrichment)
            self.assertIn(f'<meta property="og:image" content="{builder.SITE}{image}">',html)
            self.assertIn(f'<meta name="twitter:image" content="{builder.SITE}{image}">',html)
        missing=next(person for person in self.registry['candidates'] if not self.enrichment['profiles'].get(person['id'],{}).get('portrait'))
        self.assertIn(f'<meta property="og:image" content="{builder.SITE}/logo.png">',builder.profile_page('en',missing,self.registry,self.enrichment))
    def test_published_names_are_visible_sourced_and_in_person_metadata(self):
        by_id={p['id']:p for p in self.registry['candidates']}
        for ident,entry in self.enrichment['profiles'].items():
            if not entry.get('name_variants'):continue
            for lang in ['ht','en']:
                html=builder.profile_page(lang,by_id[ident],self.registry,self.enrichment)
                metadata=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',html).group(1))
                self.assertEqual(metadata['about']['alternateName'],[alias['name'] for alias in entry['name_variants']])
                visible=re.search(r'<p class="candidate-published-names">(.*?)</p>',html).group(1)
                for alias in entry['name_variants']:
                    self.assertIn(alias['name'],visible)
                    self.assertIn(self.enrichment['publications'][alias['source_id']]['url'].replace('&','&amp;'),visible)
    def test_presidential_name_index_links_beyond_first_gallery_page(self):
        presidents=[person for person in self.registry['candidates'] if person['office']=='president']
        self.assertGreater(len(presidents),builder.PAGE_SIZE)
        for lang in ['ht','en']:
            _,html=builder.directory_page(lang,self.registry,self.enrichment)
            index=re.search(r'<details class="candidate-name-index">(.*?)</details>',html).group(1)
            self.assertEqual(set(re.findall(r'<a href="([^"]+)">',index)),{builder.profile_url(person,lang) for person in presidents})
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
            self.assertIn(source['review_status'],['reviewed','indexed'])
            if source['review_status']=='indexed':
                self.assertEqual(source['editorial_level'],'index')
                self.assertIn(source['summary'],[builder.COPY['index_note'],builder.COPY['video_metadata_note']])
    def test_historical_records_and_candidate_identity_boundaries(self):
        history=json.loads((ROOT/'data/candidates/history-index.json').read_text(encoding='utf-8'))
        self.assertGreater(len(history['publications']),8000)
        self.assertGreater(sum(s['format']=='video' for s in history['publications'].values()),800)
        self.assertLessEqual(min(s['published_at'] for s in history['publications'].values() if s.get('published_at')),'2002-12-31')
        audit=json.loads((ROOT/'editorial/candidate-history-provenance.json').read_text(encoding='utf-8'))
        for ident in audit['withheld_profiles_due_to_identity_ambiguity']:
            self.assertNotIn(ident,history['profiles'])
        for ident in ['c-27353ad57d705ce8a375','c-a6829aac87da57bd8551','c-3a935f8354c358368920']:
            self.assertNotIn(ident,history['profiles'])
        for ident,entry in history['profiles'].items():
            self.assertEqual(len(entry['source_ids']),len(set(entry['source_ids'])))
            self.assertEqual(set(entry['source_ids']),set(entry['source_relations']))
        source=self.enrichment['publications'][next(iter(history['publications']))]
        self.assertNotIn('relation',source) # Per-candidate context must not mutate a shared publication.
    def test_individual_recordings_are_not_account_homepages(self):
        from urllib.parse import urlparse,parse_qs
        for source in self.enrichment['publications'].values():
            if source.get('format')!='video':continue
            parsed=urlparse(source['url'])
            if parsed.hostname in ['youtube.com','www.youtube.com']:
                self.assertEqual(parsed.path,'/watch')
                self.assertEqual(parse_qs(parsed.query).get('v'),[source['video_id']])
    def test_portrait_assets_are_small_local_and_auditable(self):
        audit=json.loads((ROOT/'editorial/candidate-portrait-provenance.json').read_text(encoding='utf-8'))
        reviewed={p['id']:p for p in audit['portraits']}
        for ident,entry in self.enrichment['profiles'].items():
            if not entry.get('portrait'):continue
            portrait=entry['portrait'];evidence=reviewed[ident]
            self.assertEqual(portrait['source_url'],evidence['source_url'])
            self.assertIn(portrait['source_url'],[self.enrichment['publications'][key]['url'] for key in entry['source_ids']])
            self.assertEqual(len(evidence['source_sha256']),64)
            self.assertEqual({v['width'] for v in portrait['variants']},{160,320,480})
            for variant in portrait['variants']:
                asset=ROOT/variant['path'].lstrip('/')
                self.assertLessEqual(asset.stat().st_size,35000)
                self.assertEqual(asset.read_bytes()[:4],b'RIFF')
                self.assertEqual(asset.read_bytes()[8:12],b'WEBP')
            web=ROOT/portrait['web_path'].lstrip('/')
            self.assertLessEqual(web.stat().st_size,18000)
    def test_both_languages_keep_profile_identity(self):
        person=self.registry['candidates'][0]
        for lang in ['ht','en']:
            html=builder.profile_page(lang,person,self.registry,self.enrichment)
            self.assertIn(builder.profile_url(person,'ht'),html)
            self.assertIn(builder.profile_url(person,'en'),html)
            self.assertIn(person['name'],html)
    def test_rejected_portrait_matches_do_not_reappear(self):
        # A headline can mention the candidate while picturing somebody else.
        # These rejected assets include Youri Latortue, Lean Colun and longer-name matches.
        rejected={
            'c-fdd715f3093f5e0e9c1f':'https://www.juno7.ht/wp-content/uploads/2020/12/5AF49516-7BC5-4811-9305-B2DD402C9E07.jpeg',
            'c-19a06a1d64595771bf1b':'https://www.juno7.ht/wp-content/uploads/2026/09/Jean-Junior-Jiha-demissionne-de-la-presidence-de-REKONSILYE-et-de-la-coordination-de-la-plateforme.jpg',
            'c-8bf29d122ade5423919a':'https://www.juno7.ht/wp-content/uploads/2020/12/Herve-Joseph.jpg',
            'c-1e903075c2db5a8db187':'https://www.juno7.ht/wp-content/uploads/2023/09/C6960CC0-FC18-44F0-A2CF-413109ABA410.png',
            'c-fd98f9247bf957ce81d6':'https://www.juno7.ht/wp-content/uploads/2023/03/B170969A-1A6D-4271-9861-E1FF1E5A0D6B.jpeg',
        }
        for ident,asset in rejected.items():
            self.assertNotEqual(self.enrichment['profiles'].get(ident,{}).get('portrait',{}).get('asset_url'),asset)
    def test_copy_review_fixes_are_present(self):
        self.assertEqual(builder.COPY['mayor']['ht'],'Majistra')
        self.assertEqual(builder.COPY['reviewed']['ht'],'Revize')
        self.assertIn('siwo myèl',self.enrichment['publications']['etzer-video-honey']['title']['ht'])

if __name__=='__main__':unittest.main()
