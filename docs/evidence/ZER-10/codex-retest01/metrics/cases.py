import sys,json,copy,traceback
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p / "agent-orchestrator").is_dir())
sys.path[:0]=[str(ROOT/'agent-orchestrator'),str(ROOT/'tests'),str(ROOT/'tests/fixtures/zer10')]
from builder import Trace,e01,iso
from test_measurement_metrics import scored
from event_pipeline.contract import new_id
from measurement.raw import load
from measurement.scorer import Scorer
import tempfile
out={}
def case(name,fn):
 try: out[name]=fn()
 except Exception as e: out[name]={'exception':type(e).__name__,'message':str(e),'trace':traceback.format_exc()}
def guard_bad():
 t=e01(); d=next(e for _,e in t.events if e['event_type']=='DECISION'); v=t.guard(133.2,d); del v['payload']['verdict'];r=scored(t);return {'M3':r['metrics']['decisions']['M3'],'findings':r['findings']}
def duplicate_call():
 t=e01(); d=next(e for _,e in t.events if e['event_type']=='DECISION'); old=next(e for _,e in t.events if e['event_type']=='LLM_CALL'); new=t.llm_call(134,d,attempt=2,retry_reason='SCHEMA');new['call_id']=old['call_id']; return scored(t)['metrics']['M11_usage']
def no_trial(bad):
 t=e01();t.events=[(p,e) for p,e in t.events if e['event_type'] not in ('TRIAL_STARTED','TRIAL_ENDED')];
 if bad: del next(e for _,e in t.events if e['event_type']=='ATTACK_REQUESTED')['payload']['target_services']
 with tempfile.TemporaryDirectory() as tmp:
  h,o,rejected=t.seal(tmp);sc=Scorer(*load(h,o));sc.intake();sc.classify();sc.trials();sc.incidents();
  intake={'rejected':rejected,'trial_contexts':len(sc.of('TRIAL_CONTEXT')),'trials':list(sc.trial),'incidents':[{k:v for k,v in i.items() if k in ('id','trial','missing','targets_unknown')} for i in sc.inc.values()]}
  intake['incidents']=[dict(i,missing=sorted(i['missing'])) for i in intake['incidents']]
  try: intake['result']=scored(t)
  except Exception as e:intake.update(exception=type(e).__name__,message=str(e),trace=traceback.format_exc())
  return intake
case('invalid_second_guard',guard_bad)
case('conflicting_call_coverage',duplicate_call)
case('missing_trial',lambda:no_trial(False))
case('invalid_request_missing_trial',lambda:no_trial(True))
print(json.dumps(out,indent=2))
