"""Read-only localhost ES verification, at most twelve HTTP queries."""
import json,time
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/evidence/ZER-41/runtime-01/attempt-02'
raw=OUT/'raw'
ids=[]
for profile,source in [('safe','a'),('vulnerable','b')]:
 samples=[json.loads(s) for s in (raw/('window-'+profile+'-'+source+'.jsonl')).read_text().splitlines()]
 ids.append(next(s['correlation_id'] for s in samples if s.get('event')=='probe_sample'))
opener=build_opener(ProxyHandler({}))
queries=0; found=[]
for identity in ids:
 for attempt in range(6):
  queries+=1
  body={'size':20,'query':{'query_string':{'query':'"'+identity+'"'}}}
  req=Request('http://127.0.0.1:19241/zero-door-logs-*/_search',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
  try:
   with opener.open(req,timeout=5) as r:result=json.loads(r.read(1048576))
  except Exception as error:
   (raw/('es-query-'+str(queries)+'.json')).write_text(json.dumps({'error_type':type(error).__name__}),encoding='utf8')
   time.sleep(2); continue
  (raw/('es-query-'+str(queries)+'.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
  hits=result.get('hits',{}).get('hits',[])
  matches=[h for h in hits if identity in json.dumps(h.get('_source',{})) and h.get('_source',{}).get('kubernetes',{}).get('namespace_name')=='zd-sqli-lab']
  if matches:found.append({'correlation_id':identity,'document_ids':[h['_id'] for h in matches]});break
  time.sleep(2)
report={'queries':queries,'found':found,'verdict':'PASS' if len(found)==len(ids) else 'MISSING_NAMESPACE_LOGS'}
(OUT/'elasticsearch.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
if len(found)!=len(ids):raise SystemExit(1)
