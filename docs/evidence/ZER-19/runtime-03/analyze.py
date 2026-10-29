"""Reproduce closed runtime-03 facts from saved files; no lab/model/process access."""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
E=HERE.parent
ROOT=E.parents[2]
def load(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
rows=[dict(file=p.name,**load(p)) for p in sorted((HERE/'raw').glob('*.json'))]
accept=load(HERE/'acceptance.json');cleanup=load(HERE/'cleanup.json');started=load(HERE/'started.json')
assert accept['verdict']=='NOT_MET' and accept['failure']['reason']=='POLICY_HOOK_MISSING'
assert cleanup['verdict']=='CLEAN' and not cleanup['problems'] and not accept['guard_failures']
assert not accept['provider_attempt_reserved'] and accept['fixture_http_reserved']==0
assert not (HERE/'provider-attempt-reserved.json').exists()
assert not (E/'runtime-04').exists()
labels={r['label'] for r in rows}
assert not labels.intersection({'session-once','benign-before','benign-after','tcp-denial','private-secrets','start-zer42-nemesis','start-zer42-worker','release-fixture'})
assert cleanup['topics_owned']==[] and cleanup['topic_create_unknown']==[]
ns=next(r for r in rows if r['label']=='namespace-owned')
uid=json.loads(ns['stdout'])['metadata']['uid']
assert uid==cleanup['namespace_uid']=='7cda8172-90b2-469d-8f55-ba99452cad6e'
assert next(r for r in rows if r['label']=='uid-delete')['returncode']==0
for label in ('final-namespace','namespace-absence'):
 receipt=[r for r in rows if r['label']==label][-1]
 assert receipt['returncode']==0 and not receipt['stdout'].strip()
before=load(HERE/'before.json');after=load(HERE/'after.json')
def specs(value):return {o['kind']+'/'+o['metadata']['namespace']+'/'+o['metadata']['name']:{'uid':o['metadata']['uid'],'spec':o['spec']} for o in value['items'] if o['kind'] in {'Deployment','PersistentVolumeClaim'} and o['metadata']['namespace']!='zd-sqli-lab'}
def restarts(value):return {o['metadata']['uid']+'/'+c['name']:c['restartCount'] for o in value['items'] if o['kind']=='Pod' and o['metadata']['namespace']!='zd-sqli-lab' for c in o.get('status',{}).get('containerStatuses',[])}
assert specs(before)==specs(after) and restarts(before)==restarts(after)
pvcs=[o for o in after['items'] if o['kind']=='PersistentVolumeClaim']
assert len(pvcs)==3 and all(p['status']['phase']=='Bound' for p in pvcs)
manifest=load(HERE/'source-manifest-at-invocation.json')
assert manifest==load(E/'runtime-prep/source-manifest-03.json')
assert len(manifest)==27 and all(sha(ROOT/p)==h for p,h in manifest.items())
products=load(E/'source-hashes.json');assert len(products)==9 and all(sha(ROOT/p)==h for p,h in products.items())
for file,key in [('acceptance-03-proposal.md','proposal_sha256'),('acceptance-03-authorization.json','authorization_sha256'),('runtime-prep/source-manifest-03.json','source_manifest_sha256')]:assert sha(E/file)==started[key]
policies=[r for r in rows if r['label']=='policy-hook']
pods=[p for r in rows if r['label']=='pod-wait' for p in json.loads(r['stdout']).get('items',[])]
fixture=[p for p in pods if p['metadata']['name'].startswith('sqli-fixture') and p['status'].get('podIP')][-1]
name=fixture['metadata']['name'];ip=fixture['status']['podIP']
assert fixture['spec']['nodeName']=='k3d-zero-door-agent-0'
assert len(policies)==80 and all(r['returncode']==0 and name not in r['stdout'] and ip not in r['stdout'] for r in policies)
assert all('namespace zd-sqli-lab' in r['stdout'] for r in policies)
comments=sorted(set((m[1],m[0]) for m in re.findall(r'POD name:([^ ]+) namespace: ([a-z0-9-]+)',policies[-1]['stdout'])))
comment_matches=[]
for namespace,podname in comments:
 pod=next((p for p in before['items'] if p['kind']=='Pod' and p['metadata']['namespace']==namespace and p['metadata']['name']==podname),None)
 if pod:comment_matches.append({'namespace':namespace,'pod':podname,'node':pod['spec']['nodeName'],'ip':pod['status'].get('podIP')})
identity=load(HERE/'node-identity-readonly.json');assert len(identity)==2 and all(r['returncode']==0 for r in identity)
containers=[json.loads(line) for line in identity[0]['stdout'].splitlines()]
nodes=json.loads(identity[1]['stdout'])['items'];identity_rows=[]
for container in containers:
 name_=container['name'].lstrip('/');node=next(n for n in nodes if n['metadata']['name']==name_)
 actual=container['networks']['k3d-zero-door']['IPAddress'];recorded=next(a['address'] for a in node['status']['addresses'] if a['type']=='InternalIP')
 assert actual==recorded
 identity_rows.append({'node':name_,'docker_ip':actual,'kubernetes_internal_ip':recorded,'match':True})
samples=load(HERE/'resource-samples.json');assert len(samples)==61
result={'verdict':'NOT_MET_POLICY_HOOK_MISSING_CLEANUP_CLEAN_NO_RETRY','elapsed_s':accept['elapsed_s'],'raw_receipts':len(rows),'preflight':load(HERE/'preflight.json'),'resources':{'samples':len(samples),'guard_failures':[],'min_host_available_bytes':min(r['host_available'] for r in samples),'min_wsl_available_kib':min(r['wsl_available_kib'] for r in samples),'max_memory_psi_avg10':max(r['psi'] for r in samples),'max_cpu_psi_avg10_diagnostic_only':max(r['pressure']['cpu']['some']['avg10'] for r in samples),'max_io_psi_avg10_diagnostic_only':max(r['pressure']['io']['some']['avg10'] for r in samples),'max_memory_read_elapsed_s':max(r['elapsed_s'] for r in rows if r['label']=='memory')},'fixture':{'name':fixture['metadata']['name'],'uid':fixture['metadata']['uid'],'ip':ip,'node':fixture['spec']['nodeName']},'policy_gate':{'queries':len(policies),'observed_span_s':policies[-1]['at']-policies[0]['at'],'max_query_elapsed_s':max(r['elapsed_s'] for r in policies),'all_returncode_zero':True,'namespace_policy_rules_seen':True,'fixture_name_or_ip_matches':0,'saved_firewall_comment_pod_associations':comment_matches,'interpretation':'Isolation of this fixture was not proven by the required dataplane gate; controller/programming cause remains unresolved. No direct denial probe was dispatched.'},'post_close_readonly_inventory':{'commands':2,'current_docker_kube_node_ips':identity_rows,'current_ip_swap_hypothesis':'NOT_SUPPORTED'},'cleanup':{'verdict':'CLEAN','namespace_uid':uid,'uid_delete_returned_zero':True,'namespace_absent_receipts':['0196-namespace-absence.json','0197-final-namespace.json'],'shared_spec_uid_unchanged':True,'shared_pod_restarts_unchanged':True,'bound_pvc_count':len(pvcs),'topics_created':0,'private_secrets_created':0},'activity':{'private_workloads_started':['proxy Deployment','gated safe fixture Deployment'],'worker_nemesis_started':False,'provider_attempts':0,'fixture_http':0,'tcp_denial_controls':0,'topics_created':0,'private_secrets_created':0,'build_import_pull':0},'harvest':load(HERE/'harvest.json'),'source':{'invocation_pins_verified':len(manifest),'product_pins_unchanged':len(products),'proposal_authorization_manifest_hashes_match':True},'publication':'BLOCKED','done':False,'runtime04_allowed':False,'limitations':['No Nemesis/model/executor functional verdict because that phase was not reached','No permanent resource stability fix proved by this one window','Current correct node IP mapping does not prove controller state or policy enforcement','Previous runtime01/02 failures/UNKNOWN/global cleanup verdicts unchanged']}
(HERE/'analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ('verdict','elapsed_s','raw_receipts','resources','cleanup','activity','source','publication')},indent=2))
