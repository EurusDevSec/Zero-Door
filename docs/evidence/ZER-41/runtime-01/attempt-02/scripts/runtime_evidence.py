"""Local evidence helpers; no network or subprocess calls."""
import hashlib,ipaddress,json,sys,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'scratch/zer13/codex-completion'
OUT=ROOT/'docs/evidence/ZER-41/runtime-01/attempt-02'
mode=sys.argv[1]
def load(path):return json.loads(Path(path).read_text(encoding='utf8'))
def jsonlines(path):
 out=[]
 for line in Path(path).read_text(encoding='utf8').splitlines():
  try:out.append(json.loads(line))
  except ValueError: pass
 return out
if mode=='prepare':
 docs=list(yaml.safe_load_all((D/'runtime-owned02-final.yaml').read_text()))
 namespace=next(d for d in docs if d['kind']=='Namespace')
 deployment=next(d for d in docs if d['kind']=='Deployment' and d['metadata']['name']=='sqli-fixture')
 (D/'namespace.json').write_text(json.dumps(namespace),encoding='utf8')
 (D/'fixture-deployment.json').write_text(json.dumps(deployment),encoding='utf8')
 (D/'bootstrap.yaml').write_text(yaml.safe_dump_all([d for d in docs if d is not namespace and d is not deployment],sort_keys=False),encoding='utf8')
 hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['services/sqli-fixture/app.py','services/sqli-fixture/Dockerfile','services/sqli-fixture/seed.json','scratch/zer13/codex-completion/runtime-owned.yaml','scratch/zer13/codex-completion/runtime_probe.py']}
 (OUT/'source-manifest.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf8')
elif mode=='proxy':
 pods=load(sys.argv[2])['items']
 pod=next(p for p in pods if p['metadata']['labels'].get('app')=='zer41-private-ingress')
 ip=ipaddress.ip_address(pod['status']['podIP']);assert ip.version==4
 (D/'trust-patch.json').write_text(json.dumps({'data':{'ZD_SQLI_TRUSTED_PROXIES':str(ip)+'/32'}}),encoding='utf8')
 print(ip)
elif mode=='namespace':
 meta=load(sys.argv[2])['metadata'];run=(D/'run-id.txt').read_text().strip()
 assert meta['name']=='zd-sqli-lab' and meta['labels'].get('zero-door.io/run')==run
 if (D/'namespace-uid.txt').exists():assert (D/'namespace-uid.txt').read_text().strip()==meta['uid']
 else:(D/'namespace-uid.txt').write_text(meta['uid'],encoding='utf8')
 (D/'delete-options.json').write_text(json.dumps({'apiVersion':'v1','kind':'DeleteOptions','preconditions':{'uid':meta['uid']},'propagationPolicy':'Foreground'}),encoding='utf8')
elif mode=='reconcile':
 profile=sys.argv[2]
 pods=load(OUT/'raw'/('pods-'+profile+'.json'))['items']
 ips={p['metadata']['name']:p['status'].get('podIP') for p in pods}
 observed=jsonlines(OUT/'raw'/('fixture-'+profile+'.jsonl'))
 proxy=jsonlines(OUT/'raw'/'proxy.jsonl')
 records={r.get('request_id'):r for r in observed if r.get('request_id')}
 assertions=[]
 for source in ('a','b'):
  samples=jsonlines(OUT/'raw'/('window-'+profile+'-'+source+'.jsonl'))
  assert any(r.get('verdict')=='PASS_LOCAL_CASES' for r in samples),samples
  own=ips['zer41-source-'+source]
  for s in samples:
   if s.get('event')!='probe_sample':continue
   r=records.get(s['request_id']);assert r,('record missing',s['request_id'])
   assert r['correlation_id']==s['correlation_id'] and r['status']==s['status']
   assert r['client_ip']==own and r['client_ip']!='203.0.113.77',(r,own)
   assert r['source_confidence']!='UNKNOWN',r
   if s['method']=='GET' and s['path']=='/fixture/catalog/search':
    assert r['restricted_rows']==sum(x['visibility']!='public' for x in s['body']['results'])
   assert any(p.get('ClientHost')==own and p.get('DownstreamStatus')==s['status'] for p in proxy),('proxy source missing',own)
   assertions.append({'request_id':s['request_id'],'client_ip':own,'status':r['status']})
 assert ips['zer41-source-a']!=ips['zer41-source-b']
 result={'profile':profile,'verdict':'PASS_ROUTE_SOURCE_EFFECT_CRUD','matched_samples':len(assertions),'sources':ips,'matches':assertions,'fixture_access_records':len(records)}
 (OUT/('reconcile-'+profile+'.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in result.items() if k!='matches'}))
