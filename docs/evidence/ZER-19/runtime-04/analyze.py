"""Offline replay of saved runtime-04 evidence; no subprocess, network or lab imports."""
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent; E=H.parent; ROOT=E.parents[2]
def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def spec(v):return {o['kind']+'/'+o['metadata']['namespace']+'/'+o['metadata']['name']:{'uid':o['metadata']['uid'],'spec':o['spec']} for o in v['items'] if o['kind'] in {'Deployment','PersistentVolumeClaim'} and o['metadata']['namespace']!='zd-sqli-lab'}
def restarts(v):return {o['metadata']['uid']+'/'+c['name']:c['restartCount'] for o in v['items'] if o['kind']=='Pod' and o['metadata']['namespace']!='zd-sqli-lab' for c in o.get('status',{}).get('containerStatuses',[])}
rows=[dict(file=p.name,**load(p)) for p in sorted((H/'raw').glob('*.json'))]
def labelled(name):return [r for r in rows if r['label']==name]
a=load(H/'acceptance.json'); c=load(H/'cleanup.json'); started=load(H/'started.json'); receipt=load(H/'live-receipt.json')
assert a['verdict']=='TECHNICAL_PASS_PENDING_REVIEW' and a['failure'] is None and not a['guard_failures']
assert c['verdict']=='CLEAN' and not c['problems'] and not c['topic_create_unknown'] and not c['topics_foreign_not_deleted']
assert a['fixture_http_reserved']==3 and a['provider_attempt_reserved'] and a['elapsed_s']<=1200
assert (H/'provider-attempt-reserved.json').exists() and not a['retry_allowed'] and not a['benchmark_eligible']
manifest=load(H/'source-manifest-at-invocation.json'); assert manifest==load(E/'runtime-prep/source-manifest-04.json')
assert len(manifest)==43 and all(sha(ROOT/p)==h for p,h in manifest.items())
products=load(E/'source-hashes.json'); assert len(products)==9 and all(sha(ROOT/p)==h for p,h in products.items())
for p,key in [('acceptance-04-proposal.md','proposal_sha256'),('acceptance-04-authorization.json','authorization_sha256'),('runtime-prep/source-manifest-04.json','source_manifest_sha256')]:assert sha(E/p)==started[key]
assert load(H/'preflight.json')['samples']==25 and load(H/'preflight.json')['verdict']=='READY_NOT_ISSUE_PASS'
netpol=load(H/'networkpolicy-preflight.json'); assert all(x['ok'] and not x['missing'] and not x['foreign'] for x in netpol['checks'].values())
assert len(labelled('netpol-node-firewall'))==2 and max(r['at'] for r in labelled('netpol-node-firewall'))<labelled('namespace-create')[0]['at']
assert labelled('tcp-denial')[0]['stdout'].strip()=='DIRECT_DENIED' and labelled('tcp-denial')[0]['returncode']==0
records=receipt['records']; events=[r['event'] for r in records]
assert events==['SESSION_STARTED','OBSERVATION','MODEL_TRACE','PLAN','GUARD_ACCEPTED','DISPATCH_INTENT','EXECUTOR_RESULT','SESSION_STOPPED']
t=records[2]['trace']; p=t['payload']; plan=records[3]; command=records[5]['command']; result=records[6]['raw']; send=result['details']['sqli']['sends']
assert p['outcome']=='OK' and p['provider']=='openai' and p['model']=='gpt-6-luna' and p['attempt_no']==1 and p['retry_reason'] is None
assert p['usage']=={'input_tokens':216,'output_tokens':26,'total_tokens':242,'status':'COMPLETE'}
assert p['latency_ms']<=20000 and p['cost']['status']=='ESTIMATE' and p['cost']['usd']<=.005
assert plan['decision_source']=='LLM' and plan['plan']=={'template':'benign-apparel','evidence_ids':['ev-health-01']}
assert command['commandId']==result['commandId']==records[4]['command_id'] and command['parameters']['customParams']['template']=='benign-apparel'
assert len(send)==1 and result['status']=='SUCCESS' and result['details']['requestsSent']==1 and send[0]['status']==200 and send[0]['restrictedRows']==0
assert receipt['stop_reason']=='MAX_ROUNDS' and receipt['completed_rounds']==1 and receipt['purpose']=='FUNCTIONAL_ONLY_NOT_BENCHMARK' and not receipt['benchmark_eligible']
budget=receipt['budget']; assert budget['attempts_dispatched']==1 and budget['known_input_tokens']==216 and budget['known_output_tokens']==26 and budget['cost_estimate_complete'] and budget['unknown_usage_attempts']==0
assert budget['known_cost_estimate_usd']==p['cost']['usd'] and budget['reserved_estimate_usd']<=.005
logs=[]
for line in load(H/'fixture-logs.json')['text'].splitlines():
 try:v=json.loads(line)
 except ValueError:continue
 if v.get('request_id'):logs.append(v)
assert len(logs)==3 and all(x['status']==200 and x['restricted_rows']==0 for x in logs)
joined=next(x for x in logs if x['request_id']==send[0]['responseId']); assert joined['correlation_id']==send[0]['requestId'] and joined['client_ip']==load(H/'raw-join.json')['worker_ip']
assert load(H/'raw-join.json')['status']=='MATCH'
for name in ('benign-before','benign-after'):
 probe=load(H/(name+'.json')); assert probe['status']==200 and any(x['request_id']==probe['request_id'] for x in logs)
capture=load(H/'session-file-capture.json'); assert json.loads(capture['receipt.json'])==receipt
assert load(H/'harvest.json')=={'errors':[],'before_namespace_delete':True,'status':'CAPTURED'}
uid=json.loads(labelled('namespace-owned')[0]['stdout'])['metadata']['uid']; assert uid==c['namespace_uid']
assert labelled('uid-delete')[0]['returncode']==0
for name in ('namespace-absence','final-namespace'):
 r=labelled(name)[-1]; assert r['returncode']==0 and not r['stdout'].strip()
assert len(labelled('topic-create'))==len(labelled('topic-delete'))==2
last_lists=labelled('topic-list')[-4:]; assert all(r['returncode']==0 for r in last_lists)
assert not last_lists[1]['stdout'].strip() and not last_lists[3]['stdout'].strip()
before=load(H/'before.json'); after=load(H/'after.json'); assert spec(before)==spec(after) and restarts(before)==restarts(after)
pvcs=[o for o in after['items'] if o['kind']=='PersistentVolumeClaim']; assert len(pvcs)==3 and all(o['status']['phase']=='Bound' for o in pvcs)
samples=load(H/'resource-samples.json'); assert len(samples)==33 and min(x['host_available'] for x in samples)>=1073741824 and min(x['wsl_available_kib'] for x in samples)>=1048576 and max(x['psi'] for x in samples)<=5
result={'verdict':'TECHNICAL_PASS_VERIFIED_SAVED_EVIDENCE','elapsed_s':a['elapsed_s'],'raw_receipts':len(rows),'provider':{'calls':1,'model':'gpt-6-luna','input_tokens':216,'output_tokens':26,'latency_ms':p['latency_ms'],'cost_estimate_usd':p['cost']['usd'],'billing_cost_verified':False},'functional':{'template':'benign-apparel','command_id':command['commandId'],'executor_sends':1,'fixture_http_total':len(logs),'http_statuses':[x['status'] for x in logs],'restricted_rows':[x['restricted_rows'] for x in logs],'direct_tcp':'DENIED','raw_join':'MATCH','stop_reason':'MAX_ROUNDS','completed_rounds':1},'resources':{'samples':len(samples),'min_windows_available_bytes':min(x['host_available'] for x in samples),'min_wsl_available_kib':min(x['wsl_available_kib'] for x in samples),'max_memory_psi_avg10':max(x['psi'] for x in samples),'guard_failures':[]},'cleanup':{'verdict':'CLEAN','namespace_uid':uid,'namespace_absent':True,'topics_deleted_and_absent':2,'shared_spec_uid_restart_unchanged':True,'bound_pvcs':3},'source':{'invocation_pins':len(manifest),'product_pins':len(products),'approval_hashes_match':True},'limits':['Functional ZER19 acceptance only; not SQLi effect/healing/KPI/G3/G4/formal benchmark','No live cancel claim; bounded cancellation behavior covered offline','Older runtime01-03 failures/UNKNOWN unchanged','Publication/CI/merge/Done remain separate gates']}
(H/'analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8'); print(json.dumps(result,indent=2))
