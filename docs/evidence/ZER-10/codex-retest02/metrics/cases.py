import json,sys,traceback
from pathlib import Path
ROOT=Path.cwd()
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'agent-orchestrator')]
from test_measurement_scorer import two_trials,score,e01,HOST_CLOCK,without_trial_bounds,lost_request
from event_pipeline.contract import new_id
out={}
tr=two_trials(False)
calls=[e for p,e in tr.events if e['event_type']=='LLM_CALL']
calls[1]['call_id']=calls[0]['call_id']
res=score(tr)
out['cross_incident_conflict']={'expected_incidents':[i['incident_id'] for i in res['incidents']],'usage':res['metrics']['M11_usage'],'labels':[(r['incident_id'],r['label']) for r in res['incidents']]}
# Missing-trial variants: absent bounds, invalid start, duplicate starts/ends, bad request envelope, actions/stop.
rows=[]
for bounds in ['none','no_start','no_end','bad_start','duplicate_start','duplicate_end']:
 for bad in [False,True]:
  for stop in [None,240]:
   for action in [None,'SUCCESS','FAILED']:
    try:
     tr=e01(stop=stop,action_status=action,probe_clock=HOST_CLOCK)
     if bounds=='none':without_trial_bounds(tr)
     elif bounds in ['no_start','no_end']:tr.events=[(p,e) for p,e in tr.events if e['event_type']!=('TRIAL_STARTED' if bounds=='no_start' else 'TRIAL_ENDED')]
     else:
      typ='TRIAL_ENDED' if bounds=='duplicate_end' else 'TRIAL_STARTED'
      ev=next(e for p,e in tr.events if e['event_type']==typ)
      if bounds=='bad_start':del ev['payload']['planned_window']
      else:
       import copy
       dup=copy.deepcopy(ev);dup.update(event_id=new_id('evt'),seq=ev['seq']+1000);tr.events.append(('H',dup))
     if bad:lost_request(tr,'missing_targets')
     res=score(tr,{'required_flows':['checkout']})
     rows.append({'bounds':bounds,'bad_request':bad,'stop':stop,'action':action,'label':res['incidents'][0]['label'],'N':res['metrics']['kpi']['counts']['N'],'missing':res['incidents'][0]['missing_reasons']})
    except Exception as e:rows.append({'bounds':bounds,'bad_request':bad,'stop':stop,'action':action,'exception':repr(e),'trace':traceback.format_exc()})
out['trial_matrix']=rows
print(json.dumps(out,indent=2))
