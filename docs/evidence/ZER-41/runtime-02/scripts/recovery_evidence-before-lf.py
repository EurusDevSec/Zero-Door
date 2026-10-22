import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'docs/evidence/ZER-41/runtime-02'
def load(name):return json.loads((O/'raw'/name).read_text(encoding='utf8'))
def pvc(rows):return {p['metadata']['namespace']+'/'+p['metadata']['name']:(p['metadata']['uid'],p['spec'].get('volumeName')) for p in rows['items']}
mode=sys.argv[1]
if mode=='baseline':
 rows=load('workloads-before.json')['items']; found={p['metadata']['name']:p.get('spec',{}).get('replicas',1) for p in rows if p['metadata']['namespace']=='zero-door' and p['kind']=='Deployment' and p['metadata']['name'] in ('gaia','hephaestus')}
 assert set(found)=={'gaia','hephaestus'} and all(isinstance(v,int) and 0<=v<=10 for v in found.values())
 (O/'raw'/'agent-replicas.tsv').write_text(''.join(name+'\t'+str(n)+'\n' for name,n in sorted(found.items())),encoding='utf8')
 assert len(pvc(load('pvc-before.json')))==3
elif mode=='pvc':
 assert pvc(load('pvc-before.json'))==pvc(load('pvc-after-restart.json')),'PVC_IDENTITY_DRIFT'
 print('PVC_IDENTITY_PASS: three PVC UIDs and bound volume names unchanged')
elif mode=='final':
 assert pvc(load('pvc-before.json'))==pvc(load('pvc-final.json')),'PVC_IDENTITY_DRIFT'
 def desired(rows):return {(p['kind'],p['metadata']['namespace'],p['metadata']['name']):p['spec'].get('replicas',1) for p in rows['items']}
 assert desired(load('workloads-before.json'))==desired(load('workloads-final.json')),'REPLICA_DRIFT'
 protected=[]
 for p in load('workloads-final.json')['items']:
  if (p['metadata']['namespace'],p['metadata']['name']) in [('target-app','frontend'),('target-app','checkoutservice'),('monitoring','elasticsearch'),('zero-door','gaia'),('zero-door','hephaestus')]:
   ready=p.get('status',{}).get('availableReplicas',0);n=p['spec'].get('replicas',1)
   assert ready>=n,(p['metadata']['name'],ready,n)
   protected.append({'namespace':p['metadata']['namespace'],'name':p['metadata']['name'],'desired':n,'available':ready})
 result={'verdict':'RESTORE_PASS','pvc_identity':'3/3 unchanged','desired_replicas':'all unchanged','protected_availability':protected}
 (O/'restore-verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
