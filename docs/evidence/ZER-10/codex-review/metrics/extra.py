from pathlib import Path
exec((Path(__file__).parent/'counterexamples.py').read_text().replace('print(json.dumps(out,indent=2))',''))

out={}
# Fully schema-valid raw GT with ill-typed action constraint must be UNKNOWN_GT, not crash.
t=e01()
gt=next(e for _,e in t.events if e['event_type']=='GROUND_TRUTH_LOCKED')
gt['payload']['constraints']['SCALE_UP']['max_replicas']='four'
try:out['malformed_gt_constraint']={'actual':scored(t)['metrics']['decisions']}
except Exception as e:out['malformed_gt_constraint']={'actual_exception':type(e).__name__+': '+str(e),'expected':'UNKNOWN_GT without exception'}
# Ingest order cannot decide between two contradictory guard verdicts for one decision_id.
t=e01()
dec=next(e for _,e in t.events if e['event_type']=='DECISION')
t.guard(133.2,dec,verdict='REJECT')
r=scored(t)
out['conflicting_guard_verdicts']={'actual_M3':r['metrics']['decisions']['M3'],'label':r['incidents'][0]['label'],'expected':'conflicting verdicts invalid/integrity, never accept_correct'}
guards=[(p,e) for p,e in t.events if e['event_type']=='GUARD_VERDICT']; positions=[i for i,(p,e) in enumerate(t.events) if e['event_type']=='GUARD_VERDICT']
for i,x in zip(positions,reversed(guards)):t.events[i]=x
out['conflicting_guard_reversed']={'actual_M3':scored(t)['metrics']['decisions']['M3']}
print(json.dumps(out,indent=2))
