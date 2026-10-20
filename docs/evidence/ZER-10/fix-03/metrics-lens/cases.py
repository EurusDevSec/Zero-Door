import sys,json,copy,traceback
from pathlib import Path
ROOT=Path.cwd()
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'agent-orchestrator')]
from test_measurement_scorer import two_trials,score

results={}
for name in ['distinct','conflict','conflict_reverse','conflict_models','invalid_second']:
 tr=two_trials(False)
 calls=[e for _,e in tr.events if e['event_type']=='LLM_CALL']
 if name.startswith('conflict'):calls[1]['call_id']=calls[0]['call_id']
 if name=='conflict_models':calls[1]['payload']['model']='model-y'
 if name=='invalid_second':del calls[1]['payload']['usage']
 if name=='conflict_reverse':tr.events.reverse()
 r=score(tr)
 u=r['metrics']['M11_usage']
 expected={x['incident_id'] for x in r['incidents']}
 assert set(u['by']['incident'])==expected,(name,expected,u['by']['incident'])
 assert u['calls']==(1 if name.startswith('conflict') or name=='invalid_second' else 2),(name,u)
 if name.startswith('conflict'):
  assert u['status']=='MISSING' and u['calls_lower_bound']
  assert all(b['call_coverage_status']==b['usage_status']==b['cost_status']=='MISSING' for lv in u['by'].values() for b in lv.values())
  assert sum(b['calls'] for b in u['by']['incident'].values())==1
  assert sum(b['input_tokens']+b['output_tokens']+b['usd'] for b in u['by']['incident'].values())==0
 elif name=='distinct':
  assert u['status']=='OK' and not u['calls_lower_bound']
  assert all(b['call_coverage_status']==b['usage_status']==b['cost_status']=='COMPLETE' for lv in u['by'].values() for b in lv.values())
 else:
  assert u['status']=='MISSING' and u['calls_lower_bound']
  assert sorted(b['call_coverage_status'] for b in u['by']['incident'].values())==['COMPLETE','MISSING']
 results[name]={'N':r['metrics']['kpi']['counts']['N'],'incidents':sorted(expected),'usage':u,'labels':[x['label'] for x in r['incidents']]}
print(json.dumps({'verdict':'PASS','checks':len(results),'cases':results},indent=2))
