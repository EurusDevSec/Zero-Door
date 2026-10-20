import copy,json,sys,tempfile
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
sys.path[:0]=[str(ROOT/'agent-orchestrator'),str(ROOT/'tests/fixtures/zer10')]
from builder import e01,HOST
from measurement.raw import load
from measurement.scorer import Scorer
from measurement.metrics import run_metrics

def run(tr):
 with tempfile.TemporaryDirectory() as tmp:
  h,o,rej=tr.seal(tmp)
  s=Scorer(*load(h,o));r=s.run();r['metrics']=run_metrics(s,r,{})
  return {'incidents':r['incidents'],'findings':r['findings'],'kpi':r['metrics'].get('kpi'),'rejected':rej}

out={}
tr=e01(probe_clock=HOST);out['clean']=run(tr)
tr=e01(probe_clock=HOST)
for _,e in tr.events:
 if e['event_type']=='DETECTED':e['clock']={'clock_id':'clk_detector_ext','clock_source':'OFF_HOST','resolution_ms':16}
out['detector_unsynced']=run(tr)
tr=e01(probe_clock=HOST)
for _,e in tr.events:
 if e['event_type']=='ATTACK_REQUESTED':del e['payload']['target_services']
out['invalid_request']=run(tr)
tr=e01(probe_clock=HOST)
for _,e in tr.events:
 if e['event_type']=='RUN_STARTED':e['payload']['f01_params']['k']=0
out['invalid_params']=run(tr)
tr=e01(probe_clock=HOST)
for _,e in tr.events:
 if e['event_type']=='TRIAL_ENDED':e['ts_event']='2026-10-19T06:03:00.000Z'
out['samples_after_trial_end']=run(tr)
tr=e01(probe_clock=HOST)
tr2=e01(probe_clock=HOST)
for plane,e in tr2.events:
 if e['trial_id'] is None:continue
 e['run_id']=tr.run;e['seq']+=10000
 if e['event_type']=='ATTACK_REQUESTED':del e['payload']['target_services']
 tr.events.append((plane,e))
out['mixed_invalid_request']=run(tr)
tr=e01(probe_clock=HOST)
for _,e in tr.events:
 if e['event_type']=='PROBE_SAMPLE' and e['payload']['pass']: e['payload']['latency_ms']=-100
out['negative_latency']=run(tr)
print(json.dumps(out,indent=2))
