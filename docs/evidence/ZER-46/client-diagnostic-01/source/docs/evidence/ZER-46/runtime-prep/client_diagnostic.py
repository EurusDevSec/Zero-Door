"""One separately approved benign client-readiness diagnostic. Inert import, no containment.
Never promotes a non-reproduced stall to a root-cause fix or full acceptance.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
PREP=Path(__file__).parent
OUT=ROOT/'docs/evidence/ZER-46/client-diagnostic-01'
AUTH=PREP/'client-diagnostic-authorization.json'
MANIFEST=PREP/'client-diagnostic-source-manifest.json'
spec=importlib.util.spec_from_file_location('zer46_client_diagnostic_agent',PREP/'run_agent_fixture.py')
agent=importlib.util.module_from_spec(spec); spec.loader.exec_module(agent)
full=agent.cached.parent.full
for module in (agent,agent.cached,agent.cached.parent,full,full.base): module.OUT=OUT


def admission():
    if (OUT/'started.json').exists() or (OUT/'acceptance.json').exists(): raise RuntimeError('ONE_ATTEMPT_ONLY')
    auth=json.loads(AUTH.read_text())
    if auth['status']!='APPROVED': raise RuntimeError('NOT_APPROVED')
    proposal=ROOT/auth['proposal']
    if proposal.resolve()!= (PREP/'client-diagnostic-proposal.md').resolve(): raise RuntimeError('PROPOSAL_PIN')
    if hashlib.sha256(proposal.read_bytes()).hexdigest()!=auth['proposalSha256']: raise RuntimeError('PROPOSAL_DRIFT')
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest()!=auth['sourceManifestSha256']: raise RuntimeError('MANIFEST_DRIFT')
    for path,expected in json.loads(MANIFEST.read_text())['files'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected: raise RuntimeError('SOURCE_DRIFT:'+path)
    return auth


def stages(text):
    result=[]
    for line in text.splitlines():
        match=re.fullmatch(r'ZER46_STAGE ([a-z_]+) ([0-9.]+)',line)
        if match: result.append({'stage':match[1],'at':float(match[2])})
    return result


def phase_deltas(text):
    timing=stages(text); counters={}
    for line in text.splitlines():
        parts=line.split(' ',3)
        if len(parts)!=4 or parts[0]!='ZER46_COUNTER': continue
        try: value=ast.literal_eval(parts[3])
        except (ValueError,SyntaxError): continue
        if isinstance(value,str) and len(value)<=4096: counters[(parts[1],parts[2])]=value
    def metric(stage,filename,key):
        value=counters.get((stage,filename),'')
        if filename=='memory.pressure':
            row=next((row for row in value.splitlines() if row.startswith('some ')), '')
            found=re.search(r'total=([0-9]+)',row)
        else: found=re.search(r'(?m)^'+re.escape(key)+r' ([0-9]+)$',value)
        return int(found[1]) if found else None
    deltas=[]
    for before,after in zip(timing,timing[1:]):
        row={'from':before['stage'],'to':after['stage'],'elapsed_seconds':after['at']-before['at']}
        for filename,key,name in [('memory.pressure','total','memory_some_stall_us'),('cpu.stat','throttled_usec','cpu_throttled_us'),('memory.events','oom_kill','oom_kill'),('memory.events','max','memory_max_events')]:
            a,b=metric(before['stage'],filename,key),metric(after['stage'],filename,key)
            row[name]=b-a if a is not None and b is not None and b>=a else None
        deltas.append(row)
    return deltas


class Lab(agent.Lab):
    def http(self,*args,**kwargs):
        if self.fixture_http>=1: raise RuntimeError('DIAGNOSTIC_ONE_HTTP_ONLY')
        return super().http(*args,**kwargs)

    def start_worker(self): raise RuntimeError('DIAGNOSTIC_NO_WRITER')
    def isolation(self,*args): raise RuntimeError('DIAGNOSTIC_NO_TCP_PROBES')

    def source_snapshot(self,label):
        pod=self.pod('zer46-source-a'); uid=pod['metadata']['uid']
        if (not re.fullmatch(r'[a-f0-9-]{36}',uid) or pod['spec']['nodeName']!=self.node or
                pod['metadata']['labels'].get('zero-door.io/run')!=self.owner): raise RuntimeError('DIAGNOSTIC_POD_OWNER')
        # Only this attempt's source-A Pod and descendant cgroups, no process memory or credentials.
        script='set -eu; found=0; for p in $(find /sys/fs/cgroup/kubepods -name memory.events); do case "$p" in *'+uid+'*|*'+uid.replace('-','_')+'*) found=1; d=$(dirname "$p"); for f in memory.current memory.max memory.high memory.events memory.pressure cpu.stat; do printf "@@ %s/%s\\n" "$d" "$f"; cat "$d/$f"; done;; esac; done; test "$found" = 1'
        row=self.command(['docker','--context','desktop-linux','exec',self.node,'sh','-c',script],timeout=4)
        self.save('source-a-'+label+'.json',{'at':time.time(),'uid':uid,'stdout':row.stdout.decode()})

    def run_fixture_protocol(self):
        self.addresses={who:self.pod('zer46-source-'+who)['status']['podIP'] for who in ('a','b')}
        pods=json.loads(self.kube('-n',full.NS,'get','pods','-o','json').stdout)['items']
        proxy=[p for p in pods if p['metadata']['labels'].get('app')=='zer46-private-ingress']
        if len(proxy)!=1: raise RuntimeError('PROXY_IDENTITY')
        self.addresses['proxy']=proxy[0]['status']['podIP']
        if len(set(self.addresses.values()))!=3: raise RuntimeError('SOURCE_SEPARATION')
        self.save('source-addresses.json',self.addresses)
        docs=full.renderer.render(self.owner,self.run_id,self.trial_id,self.addresses['proxy'],node=self.node)
        self.fixture_deployment_attempted=True
        self.kube('apply','-f',self.write_yaml('fixture.yaml',[d for d in docs if
            (d['kind'],d['metadata']['name']) in {('Deployment','sqli-fixture'),('ConfigMap','sqli-fixture-config')}]))
        self.save('fixture-initial.json',self.release())
        self.source_snapshot('before')
        self.expect('a',200)  # exactly one cold CLIENT invocation, no replay/warmup fallback
        self.source_snapshot('after')
        self.wait(time.monotonic()+30); self.resources()
        self.save('diagnostic-observed.json',{'at':time.time(),'http':1,'joined':True,'settle_seconds':30,
                  'claim':'ONE_SAMPLE_ONLY_NOT_CAUSAL_FIX_OR_AC_PASS'})


def summarize(error,cleanup):
    raw=[json.loads(p.read_text()) for p in sorted((OUT/'raw').glob('*.json'))]
    dispatches=[r for r in raw if 'exec' in r['args'] and any('X-Correlation-Id' in a and 'sys.argv[1]' in a for a in r['args'])]
    complete_stages=['interpreter','imports','request_ready','headers','response_end']
    complete=len(dispatches)==1 and [x['stage'] for x in stages(dispatches[0].get('stderr',''))]==complete_stages
    complete=complete and len(phase_deltas(dispatches[0].get('stderr','')))==4
    if complete:
        complete=all(value is not None for row in phase_deltas(dispatches[0]['stderr']) for key,value in row.items() if key in ('memory_some_stall_us','cpu_throttled_us','oom_kill','memory_max_events'))
    observed=OUT/'diagnostic-observed.json'
    complete=complete and observed.exists() and json.loads(observed.read_text()).get('joined') is True
    return {'at':time.time(),'error':error,'dispatches':len(dispatches),'diagnostic_receipts_complete':complete,
        'client_stages':[{'stages':stages(r.get('stderr','')),'cancelled':r.get('cancelled',False),
            'returncode':r.get('returncode'),'phase_deltas':phase_deltas(r.get('stderr','')),'http_result':'UNKNOWN' if r.get('cancelled') or r.get('error') else 'SEE_HTTP_AND_JOIN'} for r in dispatches],
        'cleanup':cleanup['component_resource_verdict'],'guard_failures':cleanup.get('guard_failures',[]),
        'status':'NOT_REPRODUCED_ONE_SAMPLE' if error is None and complete and cleanup['component_resource_verdict']=='CLEAN' else 'STOP_OR_INCONCLUSIVE',
        'root_cause_proven':False,'containment_run_authorized':False,'ac_pass':False,'issue_done':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--execute',action='store_true'); args=parser.parse_args()
    if not args.execute: parser.error('explicit separately approved --execute required')
    auth=admission(); lab=Lab(); lab.save('authorization.json',auth)
    error=None
    try: lab.execute(); lab.component()
    except Exception as failure:
        error=str(failure); lab.save('failure.json',{'at':time.time(),'reason':error})
    finally: cleanup=lab.cleanup()
    if lab.failure: error=error or 'GUARD_FAILURE:'+repr(lab.failure)
    receipt=summarize(error,cleanup); lab.save('acceptance.json',receipt)
    print(json.dumps(receipt)); return 0 if receipt['status']=='NOT_REPRODUCED_ONE_SAMPLE' else 1

if __name__=='__main__': sys.exit(main())
