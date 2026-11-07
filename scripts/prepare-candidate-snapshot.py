"""One-time reviewed registry import. Later changes require identity/status reconciliation."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import uuid

ROOT=Path(__file__).resolve().parents[1]
OFFICES={'Président':'president','Sénateur':'senator','Député':'deputy','Maire':'mayor','CASEC':'casec','ASEC':'asec'}
NAMESPACE=uuid.UUID('99cb3a6b-3088-42c4-83fb-422a339c0a8d')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('snapshot',type=Path);parser.add_argument('--reviewed-at',required=True);args=parser.parse_args()
    destination=ROOT/'data/candidates/registry.json'
    assert not destination.exists(), 'Initial import only. Reconcile later row, identity and status changes instead of replacing this registry.'
    data=json.loads(args.snapshot.read_text(encoding='utf-8'))
    assert data['status']=='preliminary' and data['total']==len(data['records'])
    candidates=[];seen=set()
    for row in data['records']:
        raw=json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':'))
        fingerprint=hashlib.sha256(raw.encode('utf-8')).hexdigest()
        assert fingerprint not in seen,'Identical source rows require editorial reconciliation.'
        seen.add(fingerprint)
        # UUID is assigned once and persisted, not recomputed by the site builder.
        record_id='c-'+uuid.uuid5(NAMESPACE,fingerprint).hex[:20]
        candidates.append({'id':record_id,'given_name':row['prenom'],'surname':row['nom'],'name':row['prenom']+' '+row['nom'],'office':OFFICES[row['poste']],'party':row['structure'],'locality':row['localite'],'position':row['position'],'status':'preliminary','source_fingerprint':fingerprint})
    candidates.sort(key=lambda p:(p['surname'],p['given_name'],p['office'],p['id']))
    counts=dict(Counter(p['office'] for p in candidates))
    assert counts=={OFFICES[k]:v for k,v in data['office_counts'].items()}
    out={'status':'reviewed','election':'2026-2027','reviewed_at':args.reviewed_at,'retrieved_at':data['retrieved_at'],'source_name':data['source_name'],'source_url':data['source_url'],'source_sha256':hashlib.sha256(args.snapshot.read_bytes()).hexdigest(),'total':len(candidates),'office_counts':counts,'identity_note':'Persistent registration IDs. Cross-election person links and changed source rows require explicit review; names alone do not establish identity.','candidates':candidates}
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'imported':len(candidates),'office_counts':counts},ensure_ascii=True))

if __name__=='__main__':main()
