"""Read-only independent RT2 audit; does not import runtime assessor or host."""
import hashlib,json,subprocess,os,datetime
from pathlib import Path
P=Path('scratch/zer11/rt2-runtime-f8f94738'); A=P/'attempt-03'
load=lambda p: json.loads(p.read_text(encoding='utf-8'))
sha=lambda b: hashlib.sha256(b).hexdigest()
checks=[]
def ck(name, ok):
    checks.append({'check':name,'pass':bool(ok)})
    if not ok: raise AssertionError(name)
def kube(args):
    e=dict(os.environ,MSYS_NO_PATHCONV='1')
    p=subprocess.run(['kubectl','--context','k3d-zero-door','--request-timeout=20s']+args,capture_output=True,timeout=30,env=e)
    return p
baseline=load(A/'baseline.json'); live={}
for ns,deps in baseline.items():
    p=kube(['get','deployments','-n',ns,'-o','json']); ck('live read '+ns,p.returncode==0)
    live[ns]={d['metadata']['name']:d for d in json.loads(p.stdout)['items']}
    ck('same deployment set '+ns,set(deps)==set(live[ns]))
    for name,old in deps.items():
        now=live[ns][name]
        ck('UID/spec/ready '+ns+'/'+name,now['metadata']['uid']==old['metadata']['uid'] and now['spec']==old['spec'] and now['status'].get('availableReplicas',0)>=old['spec'].get('replicas',1))
p=kube(['get','namespace','zd-zer11-rt2-8320ed75','-o','json'])
ck('namespace explicitly absent',p.returncode!=0 and b'NotFound' in p.stderr)
(A/'independent-live.json').write_text(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deployments':live,'namespace_stderr':p.stderr.decode()},indent=2),encoding='utf-8')
for kind,filename,ns in [('resourcequota','quota-before.json','target-app'),('hpa','hpas-before.json',None),('networkpolicy','policies-before.json','target-app')]:
    args=['get',kind]+(['-n',ns] if ns else ['-A'])+['-o','json']; p=kube(args); ck('read '+kind,p.returncode==0)
    before=load(A/filename)['items']; after=json.loads(p.stdout)['items']
    proj=lambda items: sorted((o['metadata'].get('namespace',''),o['metadata']['name'],o['metadata']['uid'],json.dumps(o['spec'],sort_keys=True)) for o in items)
    ck('UID/spec unchanged '+kind,proj(before)==proj(after))
summary=load(A/'summary.json'); logs=load(A/'logs.json'); manual=load(A/'manual.json')
all_events=[]; counts={}
for g,c in summary['contexts'].items():
    root=A/'raw/work/exports'/g; raw=(root/'O.jsonl').read_bytes(); m=load(root/'manifest.json')
    rows=[json.loads(l) for l in raw.splitlines()]; es=[r['envelope'] for r in rows]
    ck(g+' raw manifest',m['sha256']==sha(raw) and m['bytes']==len(raw) and m['lines']==len(rows) and m['run_id']==c['run_id'])
    for i,row in enumerate(rows):
        canonical=json.dumps(row['envelope'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
        ck(g+' envelope hash '+str(i),sha(canonical)==row['envelope_sha256'])
    ck(g+' archive equals summary',es==summary['events'][g])
    ck(g+' run group isolation',all(e['run_id']==c['run_id'] and e['group']==g and e['plane']=='O' for e in es))
    ck(g+' trial isolation',all(e['trial_id']==c['trial_id'] for e in es if e['event_type']!='RUN_CONTEXT'))
    ck(g+' events bounded',all(e['event_type'] in ('RUN_CONTEXT','TRIAL_CONTEXT','DETECTED','DECISION') for e in es))
    d=[e for e in es if e['event_type']=='DETECTED']; dec=[e for e in es if e['event_type']=='DECISION']
    version='rt2-http-availability/1' if g=='BM' else 'rt2-synthetic-transport-control/1'
    ck(g+' detector attribution',len(d)==1 and d[0]['producer_version']==version and d[0]['payload']['rule_version']==version)
    if g in ('BM','B1'):
        kind,source=('MANUAL','operator_console') if g=='BM' else ('RULES','decision_rules')
        ck(g+' decision and causation',len(dec)==1 and dec[0]['payload']['decision_source']==kind and dec[0]['source_component']==source and dec[0]['causation_id']==d[0]['event_id'])
    else: ck(g+' no AI decision',not dec)
    audit=[json.loads(l.split('MODE_AUDIT ',1)[1]) for l in logs[g].splitlines() if 'MODE_AUDIT ' in l]
    if g!='B1':
        ctx={k:c[k] for k in ('run_id','trial_id','group')}
        ck(g+' live consumer audit',any(a.get('context')==ctx and a.get('route')=='consumer' and a.get('reason')=='AUTO_DECISION_DISABLED_FOR_GROUP' for a in audit))
    if g=='BM':
        ck('manual receipt',manual['status']==409 and manual['body']=={'detail':'R1_EXECUTOR_DISABLED'} and manual['decision_id']==dec[0]['decision_id'])
        ck('manual disabled executor audit',any(a.get('route')=='/heal/trigger' and a.get('reason')=='R1_EXECUTOR_DISABLED' for a in audit))
    for phase in ('before','after'):
        h=load(A/('health-'+phase+'-'+g+'.json'))
        ck(g+' '+phase+' real disabled health',h and h['status']=='UP' and h['execution']=='DISABLED_PENDING_GUARD' and h['k8s_connected'] is False)
    counts[g]=len(es); all_events+=es
ck('unique event IDs',len({e['event_id'] for e in all_events})==len(all_events)==14)
for pod in ('driver','console','bm','b1','b2','b3'):
    at=load(A/('rt2-'+pod+'-attest.json')); ck('source attestation '+pod,not at['errors'] and at['source_sha256']==summary['contexts']['BM']['config_ref'].split(':')[1])
ck('network boundaries',load(A/'boundary-network.json')=={'unauthenticated_o_status':401,'control_port_unreachable_from_console':True})
ck('console O only',load(A/'console-separation.json')['output'].strip()=='O_ONLY_KEYS')
ck('bad operator token refused',load(A/'wrong-token.json')['status']=='401')
samples=summary['samples']; failures=sum(s['ok'] is False for s in samples)
ck('full 180s and fail preserved',summary['finished'] and not summary['monitor_alive'] and not summary['failure'] and summary['monitor_reason']=='WINDOW_COMPLETE' and summary['monitor_duration_s']>=180 and 0<failures<len(samples))
first_fail=next(i for i,s in enumerate(samples) if s['ok'] is False)
ck('healthy before failed GET',first_fail>=10)
ck('tight interval and cap',summary['interval_s']==2 and summary['max_gets']==173 and len(samples)<=173)
warm=load(A/'warmup.json'); ck('warmup separate retained',warm['healthy_streak']==10 and len(warm['samples'])==10 and all(s['ok'] for s in warm['samples']))
budget=load(P/'request-budget.json'); upper=budget['prior_get_upper_bound']+len(warm['samples'])+len(samples)
ck('global frontend GET upper bound',upper<=360 and budget['prior_get_upper_bound']==167)
receipts=[load(P/'receipt.json'),load(P/'attempt-02/receipt.json'),load(A/'receipt.json')]
ck('exactly one frontend deletion all attempts',sum(r['frontend_pod_deletes'] for r in receipts)==1)
ck('all attempt cleanup clean',all(r['cleanup_verdict']=='CLEAN' for r in receipts))
ck('within single 45min authority',receipts[-1]['elapsed_s']<2700 and receipts[-1]['verdict']=='PASS_SCOPED_RT2')
image=load(P/'image-chain.json'); ck('OCI digest chain',image['rootfs_match'] and image['config_match'] and image['oci_index_hash_verified'] and image['platform_manifest_hash_verified'] and image['config_id']==image['node_config_id'])
result={'verdict':'PASS_INDEPENDENT_RAW_AND_CLEANUP','checks':checks,'check_count':len(checks),'events':counts,'monitor_samples':len(samples),'failed_samples':failures,'monitor_duration_s':summary['monitor_duration_s'],'frontend_get_upper_bound_all_attempts':upper,'limitations':['scripted MANUAL, not human blind BM','HTTP availability only; not business recovery','no Gaia/LLM quality or KPI claim','prior attempt exact request count unknown; conservative bound used']}
(A/'independent-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
