import sys, json, tempfile, copy
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
sys.path[:0]=[str(ROOT/'agent-orchestrator'),str(ROOT/'tests'),str(ROOT/'tests/fixtures/zer10')]
from builder import Trace,e01,iso
from test_measurement_metrics import scored

def c0(group='B1'):
 t=Trace(group);t.run_started();t.trial_started();t.sync(10);t.sync(300);t.probe_run([(20,260,True)]);return t

def opts(t,full=False):
 b={'trial_ids':[t.trial],'slot_s':60,'episode_gap_s':90,'action_log_complete':True}
 if full:b['detector_coverage']={t.trial:[[iso(22),iso(300)]]}
 return {'benign':b}

def benign(t,o):
 t.trial_ended();return scored(t,o)['metrics']['M5_M6_benign']['trials'][t.trial]

out={}
t=c0();t.detected(50,incident=False);t.detected(51,service='cartservice',incident=False)
out['different_episode_keys']={'actual':benign(t,opts(t,True)),'expected':{'episodes_observed':2,'episodes_per_hour':round(2/(278/3600),6)}}
t=c0()
for at in [22,82,142,202,262]:t.detected(at,incident=False)
out['all_slots_hit_without_coverage']={'actual':benign(t,opts(t)),'expected':{'hit':5,'unknown':0,'bounds':[1.0,1.0],'episodes_per_hour':None,'verdict':'UNKNOWN for episode stream'}}
t=c0();a=t.detected(50,incident=False);dec=t.decision(51,a,incident=False);t.action(dec,started=52,api=53,done=None)
out['started_action_no_terminal']={'actual':benign(t,opts(t,True)),'expected':{'M6_actions_observed':1}}
t=c0('B0')
out['b0_detector_off']={'actual':benign(t,opts(t,True)),'expected':{'M5':'N/A','M6':'N/A'}}
t=e01();t.events=[x for x in t.events if x[1]['event_type']!='LLM_CALL']
out['llm_decision_with_no_call_records']={'actual':scored(t)['metrics']['M11_usage'],'expected':{'status':'MISSING','reason':'triggered LLM decision has no call/usage evidence'}}
t=e01();dec=next(e for _,e in t.events if e['event_type']=='DECISION');bad=t.llm_call(133.1,dec,attempt=2,retry_reason='SCHEMA');bad['payload']['usage']['input_tokens']=-1
r=scored(t)
out['invalid_second_llm_call']={'actual':r['metrics']['M11_usage'],'findings':r.get('findings'),'expected':{'raw_call_records':2,'call_coverage_status':'MISSING','usage_status':'MISSING','cost_lower_bound':0.01}}
print(json.dumps(out,indent=2))
