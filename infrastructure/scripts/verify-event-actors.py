"""Bounded ZER-9 real-pod transport proof. No fault, healing or model invocation.

Gaia uses its production query/publish functions with a declared synthetic alert;
Hephaestus runs its normal R1 startup/consumer. This is not detector/KPI evidence.
"""
import argparse
import ast
import base64
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("transport_verifier", Path(__file__).with_name("verify-event-pipeline.py"))
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
from event_pipeline.contract import Producer, canonical, new_id, now
from event_pipeline.client import Client
from event_pipeline.store import sha

command, post = old.command, old.post
NODE = "k3d-zero-door-server-0"
GATE = r'''
import json, socket, time, os
from urllib.request import Request,urlopen
keys=json.load(open('/keys/keys.json'))
assert set(keys) in ({'detector','reader'},{'decision_rules','reader'})
assert not os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/token')
assert not os.path.exists('/raw-h') and not os.path.exists('/raw-o')
history=[]; streak=0
for attempt in range(40):
 opened=[]
 try:
  r=urlopen(Request('http://events-o:8000/events?run_id='+os.environ['ZD_RUN_ID'],headers={'Authorization':'Bearer '+keys['reader']}),timeout=3)
  assert r.status==200
 except Exception: opened.append('O_NOT_READY')
 for host,port in [('events-h',8000),('kafka.zero-door.svc.cluster.local',9092),('elasticsearch.monitoring.svc.cluster.local',9200),('prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local',9090)]:
  assert socket.getaddrinfo(host,port), 'DNS must resolve for negative control'
  try:
   with socket.create_connection((host,port),timeout=1): opened.append(host)
  except (OSError,TimeoutError): pass
 history.append({'attempt':attempt,'open':opened})
 print(json.dumps(history[-1]),flush=True)
 streak=streak+1 if not opened else 0
 if streak==3:break
 time.sleep(1)
assert streak==3,history
print(json.dumps({'gate':'PASS','history':history,'roles':sorted(keys),'kube_token':False,'raw_mount':False}),flush=True)
'''


def ensure_owner(current, uid, nonce):
    if current['metadata']['uid'] != uid or current['metadata'].get('labels', {}).get('zero-door-verification') != nonce:
        raise RuntimeError('resource ownership changed; no cleanup')


def read_json(url, path='/readyz'):
    with urlopen(url + path, timeout=10) as response:
        return json.load(response)


def render(namespace, images, ctx, version):
    import yaml
    base = list(yaml.safe_load_all((ROOT / 'infrastructure/manifests/r1-event-pipeline.yaml').read_text()))
    overlay = list(yaml.safe_load_all((ROOT / 'infrastructure/manifests/r1-event-actors.yaml').read_text()))
    for doc in base:
        if doc['kind'] == 'Namespace':
            doc['metadata']['name'] = namespace
            doc['metadata']['labels']['zero-door-verification'] = namespace.removeprefix('zd-zer9-')
        else:
            doc['metadata']['namespace'] = namespace
        if doc['kind'] == 'Deployment':
            container = doc['spec']['template']['spec']['containers'][0]
            container['image'] = images['event_pipeline']
            if doc['metadata']['name'] == 'events-o':
                container['args'] += ['--topic', 'zd.events.o.' + namespace.removeprefix('zd-zer9-')]
    for doc in overlay:
        doc['metadata']['namespace'] = namespace
        if doc['kind'] == 'Pod':
            name = doc['metadata']['name']
            for container in doc['spec']['containers'] + doc['spec']['initContainers']:
                container['image'] = images[name]
                container['env'] = [{'name': k, 'value': v} for k, v in {
                    'ZD_EVENT_URL':'http://events-o:8000', 'ZD_O_KEYS_FILE':'/keys/keys.json',
                    'ZD_RUN_ID':ctx['run_id'], 'ZD_TRIAL_ID':ctx['trial_id'],
                    'ZD_PRODUCER_VERSION':version, 'ZD_CLOCK_ID':'clk_actor_transport',
                    'ZD_CLOCK_SOURCE':'UNKNOWN', 'PYTHONDONTWRITEBYTECODE':'1',
                }.items()]
            if name == 'hephaestus':
                # Transport-only fixture: persists across process/container restart,
                # NOT Pod replacement. Production integration must provide a durable volume.
                doc['spec']['securityContext']['fsGroup'] = 65532
                doc['spec']['volumes'].append({'name': 'decisions', 'emptyDir': {'sizeLimit': '16Mi'}})
                actor = doc['spec']['containers'][0]
                actor['env'].append({'name': 'ZD_RULES_STATE_FILE', 'value': '/state/decisions.sqlite'})
                actor['volumeMounts'] = [*actor['volumeMounts'], {'name': 'decisions', 'mountPath': '/state'}]
    return base, overlay


def verify_export(files, plane, seal):
    described = json.loads(files['export.json'])
    if described['seal'] != seal or sha(files[plane + '.jsonl']) != seal['sha256']:
        raise RuntimeError('export does not match seal')
    for name, info in described['files'].items():
        if name not in files or len(files[name]) != info['bytes'] or sha(files[name]) != info['sha256']:
            raise RuntimeError('export file mismatch: ' + name)
    return described


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--allow-temporary-es-ingress', action='store_true')
    parser.add_argument('--output', required=True, help='NEW directory inside checkout, including failure receipts')
    args = parser.parse_args()
    if not args.live or not __debug__:
        parser.error('--live required and assertions must be enabled')
    import yaml
    output = (ROOT / args.output).resolve()
    if ROOT not in output.parents:
        parser.error('output must be inside checkout')
    output.mkdir(parents=True, exist_ok=False)
    nonce = secrets.token_hex(6)
    ns, topic = 'zd-zer9-' + nonce, 'zd.events.o.' + nonce
    kube = ['kubectl', '--context', 'k3d-zero-door', '--request-timeout=15s']
    docker = ['docker', '--context', 'desktop-linux']
    checks, forwards = {}, []
    receipt = {'kind':'LIVE_ACTOR_TRANSPORT_SYNTHETIC_ALERT_NO_KPI', 'started_at':now(),
               'namespace':ns, 'topic':topic, 'checks':checks, 'verdict':'UNKNOWN'}
    started = time.monotonic()

    def save():
        (output / 'receipt.json').write_bytes(canonical(receipt) + b'\n')

    def k(*args, data=None, timeout=90):
        if time.monotonic() - started > 7200:
            raise TimeoutError('2h operation ceiling reached')
        return command(kube + list(args), data=data, timeout=timeout)

    def j(*args):
        return json.loads(k(*args))

    def execute(pod, code, interpreter='/usr/bin/python3'):
        return k('-n', ns, 'exec', pod, '--', interpreter, '-c', code, timeout=120)

    def stop(dep):
        k('-n', ns, 'scale', 'deployment/' + dep, '--replicas=0')
        deadline = time.monotonic() + 120
        while j('-n', ns, 'get', 'pods', '-l', 'app=' + dep, '-o', 'json')['items']:
            if time.monotonic() > deadline:
                raise TimeoutError('writer has not stopped: ' + dep)
            time.sleep(1)

    def wait_pod(name, completed=False):
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            pod = j('-n', ns, 'get', 'pod', name, '-o', 'json')
            phase = pod['status'].get('phase')
            if phase == 'Failed':
                raise RuntimeError('pod failed: ' + name)
            if completed and phase == 'Succeeded':
                return pod
            if not completed and any(c['type'] == 'Ready' and c['status'] == 'True' for c in pod['status'].get('conditions', [])):
                return pod
            time.sleep(1)
        raise TimeoutError('pod deadline: ' + name)

    def temporary_pod(name, code, plane=None):
        uid = 65533 if plane == 'H' else 65532
        container = {'name':'probe','image':images['event_pipeline'],'imagePullPolicy':'Never',
                     'command':['python','-c',code], 'resources':{'requests':{'cpu':'10m','memory':'16Mi'},'limits':{'cpu':'100m','memory':'64Mi'}},
                     'securityContext':{'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}}}
        pod = {'apiVersion':'v1','kind':'Pod','metadata':{'name':name,'namespace':ns,'labels':{'app':'events-o'}},
               'spec':{'restartPolicy':'Never','nodeSelector':{'kubernetes.io/hostname':NODE},'automountServiceAccountToken':False,
                       'serviceAccountName':'event-observer','securityContext':{'runAsNonRoot':True,'runAsUser':uid,'runAsGroup':uid,'fsGroup':uid},
                       'containers':[container]}}
        if plane:
            container['volumeMounts'] = [{'name':'raw','mountPath':'/source'},{'name':'output','mountPath':'/output'}]
            pod['spec']['volumes'] = [{'name':'raw','persistentVolumeClaim':{'claimName':'raw-' + plane.lower()}},
                                      {'name':'output','emptyDir':{'sizeLimit':'16Mi'}}]
            pod['metadata']['labels'] = {'role':'evaluator'}
        k('create','-f','-',data=canonical(pod))
        info = wait_pod(name, True)
        logs = k('-n',ns,'logs',name)
        k('-n',ns,'delete','pod',name,'--wait=true')
        return json.loads(logs), info

    try:
        if command(['docker','context','show']).decode().strip() != 'desktop-linux':
            raise RuntimeError('wrong Docker context')
        if command(['kubectl','config','current-context']).decode().strip() != 'k3d-zero-door':
            raise RuntimeError('wrong kube context')
        if ns in {n['metadata']['name'] for n in j('get','ns','-o','json')['items']}:
            raise RuntimeError('namespace already exists')
        receipt['preflight'] = {'nodes':j('get','nodes','-o','json'), 'metrics':k('top','nodes').decode(),
                               'monitoring_policies':j('-n','monitoring','get','networkpolicy','-o','json')}
        if any(int(line.split()[-1].strip('%')) > 80 for line in receipt['preflight']['metrics'].splitlines()[1:] if line.strip()):
            raise RuntimeError('node memory above 80%')
        source_paths = list((ROOT/'agent-orchestrator/event_pipeline').glob('*.py'))
        for name in ('gaia','hephaestus','event_pipeline'):
            source_paths += [ROOT/'agent-orchestrator'/name/'Dockerfile', ROOT/'agent-orchestrator'/name/'requirements.txt']
        source_paths += [ROOT/'agent-orchestrator'/name/'main.py' for name in ('gaia','hephaestus')]
        source_paths += [Path(__file__), ROOT/'infrastructure/manifests/r1-event-actors.yaml', ROOT/'infrastructure/manifests/r1-event-pipeline.yaml']
        receipt['source_hashes'] = {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in source_paths}
        version = sha(canonical(receipt['source_hashes']))[:16]
        images = {name:'zero-door/' + ('events' if name=='event_pipeline' else name) + ':zer-9-' + nonce for name in ('event_pipeline','gaia','hephaestus')}
        receipt['images'] = {}
        save()
        for name, image in images.items():
            log = command(docker + ['build','-f',str(ROOT/'agent-orchestrator'/name/'Dockerfile'),'-t',image,str(ROOT/'agent-orchestrator')], timeout=900)
            (output/('build-' + name + '.txt')).write_bytes(log)
            receipt['images'][name] = json.loads(command(docker + ['image','inspect',image,'--format','{{json .}}']))
            command(['k3d','image','import','-c','zero-door',image],timeout=240)
            save()
        ctx = {'run_id':new_id('run'),'trial_id':new_id('trl'),'incident_id':new_id('inc'),'group':'B1',
               'method_version':'zer9-real-actor-transport-not-kpi','config_ref':'sha256:' + version*4}
        receipt['context'] = ctx
        base, overlay = render(ns, images, ctx, version)
        (output/'rendered.yaml').write_text(yaml.safe_dump_all(base + overlay))
        # Policies precede all new pods, including actor init gates.
        k('create','-f','-',data=canonical(base[0]))
        ns_uid = j('get','ns',ns,'-o','json')['metadata']['uid']
        receipt['namespace_uid'] = ns_uid
        save()
        okeys = {r:secrets.token_hex(32) for r in ('harness','detector','decision_rules','reader','evaluator')}
        hkeys = {r:secrets.token_hex(32) for r in ('harness','evaluator')}
        private = output/'private'
        private.mkdir(mode=0o700)
        for name, keys in [('event-o-server',okeys),('event-h-server',hkeys)] + list(old.actor_key_files(okeys).items()):
            path = private/(name+'.json')
            path.write_bytes(canonical(keys)); path.chmod(0o600)
            k('-n',ns,'create','secret','generic',name,'--from-file=keys.json='+str(path))
        tree = ast.parse((ROOT/'agent-orchestrator/gaia/main.py').read_text())
        queries = [n.value.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)
                   and isinstance(n.value.value,str) and any(isinstance(t,ast.Name) and t.id.endswith('_query') and t.id!='query' for t in n.targets)]
        assert queries
        k('-n',ns,'create','configmap','event-queries','--from-literal=queries.json='+canonical(queries).decode())
        gate_file = private/'gate.py'; gate_file.write_text(GATE)
        k('-n',ns,'create','configmap','actor-verifier','--from-file=gate.py='+str(gate_file))
        k('create','-f','-',data=yaml.safe_dump_all([d for d in base[1:] if d['kind'] != 'Deployment'] + [d for d in overlay if d['kind'] != 'Pod']).encode())
        es_name = None
        if args.allow_temporary_es_ingress:
            es_name = 'zd-zer9-' + nonce
            policy = {'apiVersion':'networking.k8s.io/v1','kind':'NetworkPolicy','metadata':{'namespace':'monitoring','name':es_name,'labels':{'zero-door-verification':nonce}},
                      'spec':{'podSelector':{'matchLabels':{'app':'elasticsearch'}},'policyTypes':['Ingress'],
                              'ingress':[{'from':[{'namespaceSelector':{'matchLabels':{'kubernetes.io/metadata.name':ns}},'podSelector':{'matchLabels':{'app':'events-o'}}}], 'ports':[{'port':9200,'protocol':'TCP'}]}]}}
            assert j('-n','monitoring','get','pods','-l','app=elasticsearch','-o','json')['items']
            k('create','-f','-',data=canonical(policy))
            receipt['es_policy'] = {'name':es_name,'uid':j('-n','monitoring','get','networkpolicy',es_name,'-o','json')['metadata']['uid']}
            save()
        k('create','-f','-',data=yaml.safe_dump_all([d for d in base if d['kind']=='Deployment']).encode())
        urls = {}
        for dep in ('events-o','events-h'):
            k('-n',ns,'rollout','status','deployment/'+dep,'--timeout=180s',timeout=190)
            proc, urls[dep] = old.forward(kube,ns,dep); forwards.append(proc)
        o_url,h_url = urls['events-o'],urls['events-h']
        k('create','-f','-',data=yaml.safe_dump_all([d for d in overlay if d['kind']=='Pod']).encode())
        receipt['actors'] = {}
        for actor in ('gaia','hephaestus'):
            pod = wait_pod(actor)
            gate = json.loads(k('-n',ns,'logs',actor,'-c','access-gate').decode().splitlines()[-1])
            assert gate['gate']=='PASS' and all(not r['open'] for r in gate['history'][-3:])
            assert pod['spec']['nodeName']==NODE
            receipt['actors'][actor] = {'pod_uid':pod['metadata']['uid'],'spec':pod['spec'],'status':pod['status'],'gate':gate}
        checks['actual_actor_access_gates_before_trial'] = True
        save()
        for actor, own, other in [('gaia','detector','decision_rules'),('hephaestus','decision_rules','detector')]:
            code = """import json,os
from urllib.request import Request,urlopen
from urllib.error import HTTPError
keys=json.load(open('/keys/keys.json'))
assert set(keys)=={OWN,'reader'}
result={}
for role,path in [('reader','/events'),(OWN,'/seal')]:
 try: urlopen(Request('http://events-o:8000'+path,data=b'{}',headers={'Authorization':'Bearer '+keys[role],'Content-Type':'application/json'}),timeout=5);raise AssertionError(path)
 except HTTPError as e: assert e.code==403;result[role+path]=e.code
print(json.dumps(result))""".replace('OWN',repr(own))
            receipt['actors'][actor]['role_checks'] = json.loads(execute(actor,code))
        # HTTP source authority: structurally valid cross-role event must be refused.
        harness = Producer('harness',version,{'clock_id':'clk_harness_transport','clock_source':'UNKNOWN','resolution_ms':None})
        run = dict(ctx,trial_id=None);run.pop('incident_id')
        reader = Client(o_url,okeys['detector'],okeys['reader'],ctx['run_id'],ctx['trial_id'],harness)
        for event in [harness.event(run,'RUN_CONTEXT',{},'o.context'),harness.event(ctx,'TRIAL_CONTEXT',{},'o.context')]:
            post(o_url,okeys['harness'],event);old.wait_records(reader,{event['event_id']})
        canary = 'canary-'+secrets.token_hex(16)
        manifest = old.harness_manifest(ns,topic,images['gaia'],nonce)
        for name in ('gaia','hephaestus','evaluator-o','evaluator-h','actor-verifier'):
            manifest['entries'].append({'kind':'pod' if name!='actor-verifier' else 'configmap','value':name,'class':'NEUTRAL','o_visible':False})
        h_events = [harness.event(run,'RUN_STARTED',{'canary_token':canary,'protocol_ref':'transport-only','schedule_ref':'sha256:'+'0'*64,
                   'f01_params':{'delta_s':1,'k':3,'s_s':30,'l_ms':1000,'gap_s':2,'epsilon_s':0.1,'cap_det_s':60,'cap_rec_s':180},'reference_clock_id':'UNKNOWN'},'h.control'),
                    harness.event(ctx,'HARNESS_MANIFEST',manifest,'h.audit')]
        for event in h_events: post(h_url,hkeys['harness'],event)
        telemetry_code = """import asyncio,json,main,httpx
async def query():
 async with httpx.AsyncClient() as c:return await main.query_prometheus(c,QUERY)
m=asyncio.run(query());assert m and m['status']=='success' and m['data']['result']
logs=main.get_es_client().search(index='zero-door-logs-*',query={'match_all':{}},size=1)
l=dict(logs);assert l['hits']['hits'];assert all(h['_source']['kubernetes']['namespace_name']=='target-app' for h in l['hits']['hits'])
print(json.dumps({'metrics':m,'logs':l}))""".replace('QUERY',repr(queries[0]))
        receipt['telemetry_attempts'] = []
        for attempt in range(3):
            try:
                telemetry = json.loads(execute('gaia',telemetry_code))
                receipt['telemetry_attempts'].append({'attempt':attempt,'result':'PASS'});break
            except Exception as error:
                receipt['telemetry_attempts'].append({'attempt':attempt,'result':str(error)});save()
                if attempt==2:raise
                time.sleep(2)
        surfaces = [{'source_component':'detector','field':'query','text':queries[0]},
                    {'source_component':'detector','field':'query_result','text':canonical(telemetry).decode()}]
        receipt['query_surfaces'] = surfaces
        checks['real_gaia_telemetry_via_o'] = True
        execute('gaia',"import main;main.publish_alert('HIGH_CPU','frontend','transport_fixture',90.,80.,'Synthetic transport fixture; no workload effect','WARNING')")
        deadline = time.monotonic()+30
        while time.monotonic()<deadline:
            rows=list(reader.records())
            if any(r['envelope']['event_type']=='DECISION' for r in rows):break
            time.sleep(.5)
        detection=next(r['envelope'] for r in rows if r['envelope']['event_type']=='DETECTED')
        decision=next(r['envelope'] for r in rows if r['envelope']['event_type']=='DECISION')
        assert decision['causation_id']==detection['event_id'] and decision['incident_id']==ctx['incident_id']
        assert decision['payload']['inputs'][0]['event_id']==detection['event_id']
        assert decision['payload']['decision_source']=='RULES'
        for actor,event in [('gaia',decision),('hephaestus',detection)]:
            code="""import json,main
from urllib.error import HTTPError
try:main.r1_client.publish(json.loads(EVENT));raise AssertionError('cross-role accepted')
except HTTPError as e:assert e.code==422;print(json.dumps({'cross_role':e.code}))""".replace('EVENT',repr(canonical(event).decode()))
            receipt['actors'][actor]['cross_role'] = json.loads(execute(actor,code))
        guard_code="""import json
from urllib.request import Request,urlopen
from urllib.error import HTTPError
r={}
for p in ['/heal/trigger','/experiment/reset']:
 try:urlopen(Request('http://127.0.0.1:8000'+p,data=b'{}',headers={'Content-Type':'application/json'}),timeout=5);raise AssertionError(p)
 except HTTPError as e:assert e.code==409;r[p]=e.code
print(json.dumps(r))"""
        receipt['actors']['hephaestus']['execution_guard']=json.loads(execute('hephaestus',guard_code))
        # Redeliver same envelope from the detector pod; normal consumer must not re-decide.
        duplicate="import json,main;main.r1_client.publish(json.loads("+repr(canonical(detection).decode())+"))"
        execute('gaia',duplicate)
        time.sleep(3)
        rows=list(reader.records())
        assert sum(r['envelope']['event_type']=='DECISION' for r in rows)==1
        assert sum(r['envelope']['event_id']==detection['event_id'] for r in rows)==2
        checks['pod_gaia_to_kafka_to_pod_hephaestus_ids_dedup'] = True
        checks['role_keys_and_no_heal_reset'] = True
        assert all(r['transport']['kind']=='kafka' and r['transport']['http_request_id'] for r in rows)
        assert not any(r['envelope']['event_type'] in {'HEAL_STARTED','ACTION_COMPLETED','RECOVERY_VERIFIED'} for r in rows)
        checks['http_kafka_provenance_without_synthetic_recovery'] = True
        # Fifth pod: harness owns only the nonce topic; actors remain broker-denied.
        poison=b'not-json-zer9-transport'
        code="from kafka import KafkaProducer;import json;p=KafkaProducer(bootstrap_servers='kafka.zero-door.svc.cluster.local:9092',acks='all',retries=0);m=p.send("+repr(topic)+","+repr(poison)+").get(timeout=10);p.close();print(json.dumps({'partition':m.partition,'offset':m.offset}))"
        receipt['poison'],_ = temporary_pod('broker-probe',code)
        # Good envelope after poison, proving forward progress before restart.
        execute('gaia',duplicate)
        rows=list(reader.records())
        assert sum(r['envelope']['event_id']==detection['event_id'] for r in rows)==3
        assert read_json(o_url)['status']=='READY'
        before=[(r['envelope']['seq'],r['envelope_sha256']) for r in rows]
        for proc in forwards:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        forwards=[]
        k('-n',ns,'rollout','restart','deployment/events-o')
        k('-n',ns,'rollout','status','deployment/events-o','--timeout=180s',timeout=190)
        for dep in ('events-o','events-h'):
            proc,urls[dep]=old.forward(kube,ns,dep);forwards.append(proc)
        o_url,h_url=urls['events-o'],urls['events-h'];reader.url=o_url
        rows=list(reader.records())
        assert [(r['envelope']['seq'],r['envelope_sha256']) for r in rows]==before and read_json(o_url)['status']=='READY'
        checks['poison_good_next_restart_raw_and_readiness'] = True
        transport=[{'source_component':'recorder','field':'transport.'+key,'text':str(r['transport'][key])} for r in rows for key in ('topic','http_request_id')]
        controls=old.leak_controls(h_events,[r['envelope'] for r in rows],detection,surfaces+transport,all(checks.values()),harness,ctx)
        assert controls['clean']['result']=='CLEAN',controls
        assert controls['injected_stream_valid_ids']['findings']==['LABEL_IN_METADATA']
        assert controls['injected_target_valid_ids']['findings']==['LABEL_IN_METADATA']
        receipt['leak_audit']=controls;checks['clean_and_valid_id_label_controls']=True
        receipt['pods_before_stop']=j('-n',ns,'get','pods','-o','json')
        assert len(receipt['pods_before_stop']['items'])==4
        assert all(p['spec']['nodeName']==NODE for p in receipt['pods_before_stop']['items'])
        seals={}
        for plane,url,keys in [('O',o_url,okeys),('H',h_url,hkeys)]:
            seals[plane],pending=old.seal_with_retry(url,keys['evaluator'],ctx['run_id'])
            receipt.setdefault('seal_pending',{})[plane]=pending
        # Retest late ingress durability after seal, without changing sealed raw hash.
        late=json.loads(canonical(detection));late['event_id']=new_id('evt')
        try:post(o_url,okeys['detector'],late)
        except HTTPError as e:assert e.code==409
        else:raise AssertionError('late event accepted')
        for actor in ('gaia','hephaestus'):k('-n',ns,'delete','pod',actor,'--wait=true')
        for dep in ('events-o','events-h'):stop(dep)
        receipt['exports']={}
        for plane in ('O','H'):
            code="""import json,base64
from pathlib import Path
from event_pipeline.store import Archive
a=Archive('/source',PLANE)
try:a.export(RUN,'/output/export')
finally:a.close()
p=Path('/output/export');print(json.dumps({f.relative_to(p).as_posix():base64.b64encode(f.read_bytes()).decode() for f in p.rglob('*') if f.is_file()}))""".replace('PLANE',repr(plane)).replace('RUN',repr(ctx['run_id']))
            encoded,info=temporary_pod('evaluator-'+plane.lower(),code,plane)
            files={n:base64.b64decode(v,validate=True) for n,v in encoded.items()}
            receipt['exports'][plane]=verify_export(files,plane,seals[plane])
            for name,data in files.items():
                if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('unsafe export name')
                path=output/'export'/plane/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            if plane=='O':
                quarantined=[json.loads(line) for line in files['archive-scope/rejections.jsonl'].splitlines()]
                assert any(q['raw_sha256']==sha(poison) and q['transport']['offset']==receipt['poison']['offset'] for q in quarantined)
                assert 'late.jsonl' in files
        checks['sealed_real_pvc_export_hashes_quarantine_late']=True
        # Consumer committed beyond poison (checked from a new independent broker client).
        group='zd-recorder-'+__import__('hashlib').sha256(topic.encode()).hexdigest()[:16]
        code="""import json
from kafka import KafkaConsumer,TopicPartition
c=KafkaConsumer(bootstrap_servers='kafka.zero-door.svc.cluster.local:9092',group_id=GROUP,enable_auto_commit=False)
t=TopicPartition(TOPIC,0);o=c.committed(t);c.close();assert o>POISON;print(json.dumps({'committed':o}))""".replace('GROUP',repr(group)).replace('TOPIC',repr(topic)).replace('POISON',repr(receipt['poison']['offset']))
        receipt['committed_offset'],_=temporary_pod('offset-probe',code)
        checks['broker_commit_beyond_poison']=True
        receipt['topic_cleanup']=old.delete_owned_topic(kube,ns,images['gaia'],topic)
        # Runtime receipt now complete; cleanup must match the originally captured UIDs.
        ensure_owner(j('get','ns',ns,'-o','json'),ns_uid,nonce)
        if es_name:
            ensure_owner(j('-n','monitoring','get','networkpolicy',es_name,'-o','json'),receipt['es_policy']['uid'],nonce)
            k('-n','monitoring','delete','networkpolicy',es_name)
            assert not j('-n','monitoring','get','networkpolicy','-l','zero-door-verification='+nonce,'-o','json')['items']
            receipt['es_policy']['deleted']=True
        k('delete','namespace',ns,'--wait=true','--timeout=120s',timeout=130)
        assert ns not in {n['metadata']['name'] for n in j('get','ns','-o','json')['items']}
        checks['owned_topic_namespace_pvc_policy_cleanup_confirmed']=True
        receipt['verdict']='PASS'
    except Exception as error:
        receipt['verdict']='FAIL';receipt['error']=type(error).__name__+': '+str(error)
        receipt['resources_retained_for_diagnosis']=True
        save()
        raise
    finally:
        for proc in forwards:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        receipt['finished_at']=now();save()
        print(json.dumps({'receipt':str(output/'receipt.json'),'verdict':receipt['verdict'],'checks':len(checks)}))


if __name__=='__main__':
    main()
