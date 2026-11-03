"""Single-use bounded ZER-23 integration batch. Import/default are inert."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
PREP=Path(__file__).resolve().parent
ROOT=PREP.parents[3]
HEAD='d5b22414a66ddec3f02f549b4d18143f9b0c5880'
BATCH=PREP.parent/'runtime-02'
CASE=os.environ.get('ZD23_CASE')
if CASE not in (None,'SQLI','C0','CANCEL'):raise ValueError('CASE')
INDEX=2 if CASE=='C0' else 5
OUT=BATCH if CASE is None else BATCH/CASE
spec=importlib.util.spec_from_file_location('zer23_owned',ROOT/'docs/evidence/ZER-21/runtime-prep-07/run.py')
owned=importlib.util.module_from_spec(spec);spec.loader.exec_module(owned)
sha,save,run_child=owned.sha,owned.save,owned.run_child


def verify_sources(root=ROOT,prep=PREP):return owned.verify_sources(root,prep)


def admit(path):
    auth=json.loads(Path(path).read_bytes())
    if (auth.get('approved') is not True or auth.get('issue')!='ZER-23' or auth.get('attempt')!='runtime-02'
        or auth.get('proposal_sha256')!=sha(PREP/'proposal.md')
        or auth.get('source_manifest_sha256')!=sha(PREP/'source-manifest.json')
        or type(auth.get('expires_epoch')) not in (int,float)
        or not time.time()<auth['expires_epoch']<=time.time()+86400
        or CASE is not None and auth.get('case')!=CASE):raise ValueError('AUTHORIZATION_SCOPE_OR_PIN')
    verify_sources()
    baseline=json.loads((PREP.parent/'policy-recovery/result.json').read_bytes())
    process=json.loads((PREP.parent/'policy-recovery-process.json').read_bytes())
    if (baseline.get('status')!='BASELINE_READY' or process.get('exit_code')!=0
        or not process.get('owned_tree_closed') or not process.get('process_reaped')):
        raise ValueError('BASELINE_RECOVERY_NOT_VERIFIED')
    return auth


def execute(path):
    if CASE is not None:raise ValueError('BATCH_PARENT_REQUIRED')
    auth=admit(path);BATCH.mkdir()
    save(BATCH/'authorization.json',auth);save(BATCH/'started.json',{'at':time.time(),'head':HEAD,'restart_allowed':False})
    lock=verify_sources()
    for name in lock['sha256']:
        p=BATCH/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    save(BATCH/'source-manifest.json',lock);(BATCH/'proposal.md').write_bytes((PREP/'proposal.md').read_bytes())
    started=time.monotonic();rows=[]
    for case in ('SQLI','C0','CANCEL'):
        if time.monotonic()-started>2400:
            rows.append({'case':case,'status':'NOT_RUN_BATCH_DEADLINE'});break
        out=BATCH/case;out.mkdir();save(out/'authorization.json',dict(auth,case=case))
        save(out/'started.json',{'at':time.time(),'head':HEAD,'case':case,'restart_allowed':False})
        env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',MSYS_NO_PATHCONV='1',ZD23_CASE=case,
          PYTHONPATH=os.pathsep.join((str(ROOT/'agent-orchestrator'),str(Path(sys.prefix)/'Lib/site-packages'))))
        worker=cleanup={};error=None
        try:worker=run_child([sys.executable,'-B',str(PREP/'lab.py'),'--work'],env,out/'worker.log',timeout=900)
        except BaseException as failure:error=type(failure).__name__
        finally:
            env.pop('OPENAI_API_KEY',None)
            try:cleanup=run_child([sys.executable,'-B',str(PREP/'lab.py'),'--cleanup'],env,out/'cleanup.log',timeout=285)
            except BaseException as failure:error=error or 'CLEANUP_'+type(failure).__name__
        work=json.loads((out/'work-result.json').read_bytes()) if (out/'work-result.json').exists() else {}
        clean=json.loads((out/'cleanup.json').read_bytes()) if (out/'cleanup.json').exists() else {}
        passed=(not error and worker.get('exit_code')==0 and cleanup.get('exit_code')==0
          and not worker.get('timed_out') and not cleanup.get('timed_out')
          and work.get('status')=='OBSERVED_PENDING_REVIEW' and clean.get('verdict')=='CLEAN')
        row={'case':case,'status':'OBSERVED_PENDING_REVIEW' if passed else 'NOT_MET',
          'worker':worker,'cleanup_process':cleanup,'work':work,'cleanup':clean,'error':error}
        rows.append(row);save(out/'acceptance.json',row);save(BATCH/'progress.json',rows)
        if not passed:break
    result={'status':'REVIEW_REQUIRED' if len(rows)==3 and all(r['status']=='OBSERVED_PENDING_REVIEW' for r in rows) else 'NOT_MET',
      'elapsed_seconds':time.monotonic()-started,'rows':rows,'issue_done':False,'benchmark_eligible':False}
    save(BATCH/'acceptance.json',result);print(json.dumps(result));return 0 if result['status']=='REVIEW_REQUIRED' else 1


def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--authorization');a=p.parse_args()
    if not a.execute:print(json.dumps({'status':'PLAN_ONLY','lab_operations':0,'provider_calls':0}));return 0
    if not a.authorization:p.error('--authorization required')
    return execute(a.authorization)


if __name__=='__main__':raise SystemExit(main())
