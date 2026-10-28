"""Offline raw reconciliation of the one approved benign diagnostic; no lab calls or old artifact writes."""
import hashlib
import ast
import json
from pathlib import Path
import re
import subprocess
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'docs/evidence/ZER-46/client-diagnostic-01'
PREP=ROOT/'docs/evidence/ZER-46/runtime-prep'

def read(name):return json.loads((OUT/name).read_text(encoding='utf8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def identity(doc):
    return {x['kind']+'/'+x['metadata']['namespace']+'/'+x['metadata']['name']:{'uid':x['metadata']['uid'],'spec':x['spec']}
        for x in doc['items'] if x['kind'] in ('Deployment','PersistentVolumeClaim') and x['metadata']['namespace']!='zd-sqli-lab'}
def restarts(doc):
    return {x['metadata']['uid']+'/'+c['name']:c['restartCount'] for x in doc['items'] if x['kind']=='Pod' and x['metadata']['namespace']!='zd-sqli-lab' for c in x.get('status',{}).get('containerStatuses',[])}
def main():
    auth=read('authorization.json'); lock=read('prepared-source-manifest.json')
    canonical=json.loads((PREP/'client-diagnostic-authorization.json').read_text(encoding='utf8'))
    assert canonical['status']=='APPROVED' and canonical['reply']=='Duyệt gói chẩn đoán một lần'
    # The run read its UTF-8 authorization using Windows cp1258. Preserve this raw defect;
    # only human display text differs, while every operative field and hash is identical.
    assert auth==canonical or auth==json.loads((PREP/'client-diagnostic-authorization.json').read_bytes().decode('cp1258'))
    for key in canonical.keys()-{'reply'}:assert auth[key]==canonical[key]
    assert sha(ROOT/auth['proposal'])==auth['proposalSha256']
    assert sha(OUT/'prepared-source-manifest.json')==auth['sourceManifestSha256']
    current_drift=[]
    for path,expected in lock['files'].items():
        assert sha(OUT/'source'/path)==expected
        if sha(ROOT/path)!=expected:current_drift.append(path)
    raw=[json.loads(p.read_text(encoding='utf8')) for p in sorted((OUT/'raw').glob('*.json'))]
    assert not any(r['args'][:4] in (['docker','--context','desktop-linux',op] for op in ('build','pull')) or r['args'][:3]==['k3d','image','import'] for r in raw)
    assert not list(OUT.glob('writer-*.json')) and not (OUT/'original-rule.json').exists()
    for r in raw:
        args=r['args']
        if args[0]=='kubectl' and any(verb in args for verb in ('apply','create','delete','patch','replace','scale')):
            assert not any(verb in args for verb in ('patch','replace','scale'))
            if '--raw' in args:assert args[args.index('--raw')+1]=='/api/v1/namespaces/zd-sqli-lab'
            file=Path(args[args.index('-f')+1]).resolve()
            assert file.parent==OUT.resolve()
    dispatches=[r for r in raw if 'exec' in r['args'] and any('X-Correlation-Id' in a and 'sys.argv[1]' in a for a in r['args'])]
    assert len(dispatches)<=1
    http='NOT_DISPATCHED'; joined=False; phase=[]; terminal=read('acceptance.json')
    source=OUT/'source/docs/evidence/ZER-46/runtime-prep/client_diagnostic.py'
    tree=ast.parse(source.read_text(encoding='utf8'))
    pure=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in ('stages','phase_deltas','summarize')]
    assert len(pure)==3
    helpers={'ast':ast,'json':json,'re':re,'time':time,'OUT':OUT}
    exec(compile(ast.Module(body=pure,type_ignores=[]),str(source),'exec'),helpers)
    if dispatches:
        sent=json.loads(dispatches[0]['args'][-1])
        assert sent['method']=='GET' and sent['path']=='/fixture/catalog/search?category=electronics' and sent['body'] is None and sent['headers']=={}
        assert 'zer46-source-a' in dispatches[0]['args']
        phase=helpers['phase_deltas'](dispatches[0].get('stderr',''))
        http='UNKNOWN'
        if (OUT/'http-001.json').exists():
            row=read('http-001.json'); assert row['request']==sent
            assert json.loads(dispatches[0]['stdout'])==row['response']
            http=row['response'].get('status','ERROR')
            if (OUT/'join-001.json').exists():
                record=read('join-001.json');target=read('log-pod-target-001.json');pod=read('fixture-initial.json')
                assert target['uid']==pod['metadata']['uid'] and target['name']==pod['metadata']['name']
                assert record['request_id']==row['response']['request_id'] and record['correlation_id']==sent['correlation'] and record['status']==http
                joined=any('logs' in r['args'] and 'pod/'+target['name'] in r['args'] and any(line==json.dumps(record) or _same(line,record) for line in r.get('stdout','').splitlines()) for r in raw)
                assert joined
    cleanup=read('cleanup.json')
    assert identity(read('before.json'))==identity(read('after.json'))
    assert restarts(read('before.json'))==restarts(read('after.json'))
    absent=[r for r in raw if r['args'][0]=='kubectl' and 'get' in r['args'] and 'namespace' in r['args'] and '--ignore-not-found' in r['args'] and r.get('returncode')==0 and not r['stdout'].strip()]
    assert absent and cleanup['namespace_absent'] is True
    namespace_uid=None
    if (OUT/'namespace-created.json').exists():
        namespace_uid=read('namespace-created.json')['metadata']['uid']
        assert read('namespace-delete-options.json')['preconditions']['uid']==namespace_uid
        assert any('delete' in r['args'] and '/api/v1/namespaces/zd-sqli-lab' in r['args'] and r.get('returncode')==0 for r in raw)
    assert cleanup['writer_processes']==0 and cleanup['fixture_http']<=1 and cleanup['boutique_http']<=32 and cleanup['tcp_checks']==0
    samples=read('resource-samples.json');violations=[r for r in samples if r['hostAvailable']<1073741824 or r['wslAvailableKiB']<1048576 or r['memoryPsiAvg10']>5]
    expected=helpers['summarize'](terminal['error'],cleanup)
    for key in ('status','dispatches','client_stages','diagnostic_receipts_complete','ac_pass','issue_done'):assert expected[key]==terminal[key]
    elapsed=terminal['at']-read('started.json')['at'];assert elapsed<=1200
    result={'status':'DIAGNOSTIC_RAW_RECONCILED','diagnostic_status':terminal['status'],'elapsed_seconds':elapsed,
        'at':terminal['at'],'source_snapshot_files_verified':len(lock['files']),'current_source_drift_after_run':current_drift,
        'authorization_display_encoding':'UNCHANGED' if auth==canonical else 'UTF8_READ_AS_CP1258; OPERATIVE_FIELDS_AND_HASHES_IDENTICAL',
        'dispatches':len(dispatches),'http_result':http,'joined':joined,'phase_deltas':phase,'guard_samples':len(samples),'violations':violations,
        'namespace_uid':namespace_uid,'namespace_uid_delete_verified_absent':True,'shared_spec_uid_restart_preserved':True,
        'pvc_count':sum(x['kind']=='PersistentVolumeClaim' for x in read('after.json')['items']),
        'fixture_http':cleanup['fixture_http'],'boutique_http':cleanup['boutique_http'],'owned_cleanup':cleanup['component_resource_verdict'],
        'builds':0,'imports':0,'pulls':0,'writers':0,'rules':0,'root_cause_proven':False,'full_containment_authorized':False,'ac_pass':False,'issue_done':False}
    (OUT/'raw-verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
def _same(line,record):
    try:return json.loads(line)==record
    except ValueError:return False
if __name__=='__main__':
    with patch.object(subprocess,'Popen',side_effect=AssertionError('OFFLINE_NO_PROCESS')),patch.object(subprocess,'run',side_effect=AssertionError('OFFLINE_NO_PROCESS')):main()
