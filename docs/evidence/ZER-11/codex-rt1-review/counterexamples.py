"""Independent H-RT1 review probes: fake kubectl/target only; no lab."""
import copy, errno, json, sys, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
sys.path.insert(0,str(ROOT/'tests'))
import test_dashboard_baseline_runtime as t

def row(name, **data):
    print(json.dumps(dict(case=name,**data),sort_keys=True,default=str),flush=True)

def case_managed_fields():
    c=unittest.TestCase(); r=t.Run(c)
    real=r.cluster
    def cli(argv,stdin=None,timeout=None):
        code,out,err=real(argv,stdin,timeout)
        # kubectl get's documented default: strip managedFields in JSON/YAML.
        if code==0 and argv[4]=='get' and '--show-managed-fields=true' not in argv:
            obj=json.loads(out)
            def strip(o):
                if isinstance(o,dict):
                    if isinstance(o.get('metadata'),dict): o['metadata'].pop('managedFields',None)
                    for v in o.values(): strip(v)
                elif isinstance(o,list):
                    for v in o: strip(v)
            strip(obj); out=json.dumps(obj).encode()
        return code,out,err
    r.kube.runner=cli
    try:
        res=r.go()
        row('real_kubectl_default',abort=res.get('abort'),cleanup=res.get('cleanup'),trials=list(r.orch.trials),attribution=r.orch.evidence.get('positive_control',{}).get('scale_attribution'))
        assert res.get('abort')=='ATTRIBUTION_CONTROL_FAILED' and not r.orch.trials
    finally:c.doCleanups()

def case_create_unknown():
    c=unittest.TestCase(); r=t.Run(c); real=r.cluster; fired=False
    def cli(argv,stdin=None,timeout=None):
        nonlocal fired
        ans=real(argv,stdin,timeout)
        if not fired and argv[4]=='create' and stdin and json.loads(stdin).get('kind')=='Namespace':
            fired=True
            return None,b'',b'TIMEOUT' # server created it; response was lost
        return ans
    r.kube.runner=cli
    try:
        res=r.go()
        row('namespace_create_lost_ack',abort=res.get('abort'),cleanup=res.get('cleanup'),namespace_left=r.orch.ns in real.namespaces,created=r.orch.created,final_diff=res.get('final_diff'))
        assert res['cleanup']=='CLEAN' and r.orch.ns in real.namespaces
    finally:c.doCleanups()

def case_disk_error():
    c=unittest.TestCase(); r=t.Run(c); original=Path.write_bytes
    def disk(path,data):
        if path.parent==r.out and path.name.startswith('delete-') and r.cluster.deploys[('zero-door','gaia')]['spec']['replicas']==0:
            raise OSError(errno.ENOSPC,'No space left on device')
        return original(path,data)
    try:
        error=None
        with patch.object(Path,'write_bytes',disk):
            try:r.go()
            except Exception as e:error=type(e).__name__+': '+str(e)
        row('host_disk_error',error=error,namespace_left=r.orch.ns in r.cluster.namespaces,gaia_replicas=r.cluster.deploys[('zero-door','gaia')]['spec']['replicas'],heph_replicas=r.cluster.deploys[('zero-door','hephaestus')]['spec']['replicas'],cleanup_steps=len(r.orch.cleanup_log),receipt=(r.out/'receipt.json').exists())
        assert error and len(r.orch.cleanup_log)==0 and r.cluster.deploys[('zero-door','gaia')]['spec']['replicas']==0
    finally:c.doCleanups()

if __name__=='__main__':
    case_managed_fields(); case_create_unknown(); case_disk_error()
