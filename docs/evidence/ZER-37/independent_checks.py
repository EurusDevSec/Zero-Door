"""Independent ZER-37 counterexamples. Reads Claude helper/fixtures unchanged; no network/lab."""
import copy, importlib.util, json, pathlib
s=importlib.util.spec_from_file_location('claude_contract',str(pathlib.Path(__file__).with_name('check_contract.py')))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
rows=[]
def make(cid='E01'):
 c=next(c for c in m.FIX['cases'] if c['id']==cid);sp=copy.deepcopy(m.FIX['base']);sp.update(c['over']);return m.build(cid,sp)
def score(rs,ps):
 for r in rs:r['envelope_sha256']='sha256:'+m.canon(r['envelope'])
 return m.analyse(rs,ps)
def save(name,observed,expected,passed):
 row=dict(case=name,observed=observed,expected=expected,expectation_met=bool(passed));rows.append(row);print(json.dumps(row,ensure_ascii=False))
def small(r):
 return {**{k:r[k] for k in ('orphans','leak','mode_violation')},'incidents':[{k:v for k,v in x.items() if k in ('label','t_det','t_rec','mttd','mttr','total','reaction','flags','evaluator_mismatch')} for x in r['incidents']]}
rs,ps,_=make();r=score(rs,ps);x=r['incidents'][0]
save('CONTROL_E01',small(r),'MTTD30 MTTR60 Total90 Reaction19',all(x[k]==v for k,v in dict(mttd=30,mttr=60,total=90,reaction=19).items()))
rs,ps,_=make()
for z in rs:
 e=z['envelope'];p=e['payload']
 if e['clock']['clock_source']=='OFF_HOST':
  e['ts_event']=m.iso(m.sec(e['ts_event'])+10)
  for k in ('t_start','t_end','t_eff','t_rec','recovery_verified_at'):
   if p.get(k):p[k]=m.iso(m.sec(p[k])+10)
 if e['event_type']=='CLOCK_SYNC':p['offset_ms']=10000
r=score(rs,ps);x=r['incidents'][0]
save('CLOCK_OFFSET_10S',small(r),'Corrected MTTD30 MTTR60 Total90',x['mttd']==30 and x['mttr']==60 and x['total']==90)
rs,ps,_=make()
for z in rs:
 e=z['envelope']
 if e['event_type']=='CLOCK_SYNC' and m.sec(e['payload']['measured_at'])>100:e['payload']['measured_at']=m.iso(101)
r=score(rs,ps)
save('SYNC_END_MISSING',small(r),'CLOCK_UNVERIFIED; sync10/101 does not bracket trial10..300','CLOCK_UNVERIFIED' in r['incidents'][0]['flags'])
rs,ps,_=make();ac=next(z['envelope'] for z in rs if z['envelope']['event_type']=='ACTION_COMPLETED');ac['payload']['postcondition']['satisfied']=False
ve=m.validate(ac);r=score(rs,ps)
save('SUCCESS_POSTCONDITION_FALSE',{'validate':ve,'score':small(r)},'Reject inconsistent SUCCESS; reaction19 cannot be justified',bool(ve[0]) or r['incidents'][0]['reaction']!=19)
rs,ps,_=make('BMC');rs=[z for z in rs if z['envelope']['event_type']!='DECISION'];r=score(rs,ps)
save('BM_MANUAL_DECISION_MISSING',small(r),'MODE_VIOLATION without actual MANUAL decision',r['mode_violation'])
rs,ps,_=make()
for z in rs:
 e=z['envelope']
 if e['event_type']=='PROBE_SAMPLE' and e['payload']['pass']:
  e['payload']['latency_ms']=5000;e['payload']['t_end']=m.iso(m.sec(e['payload']['t_start'])+5);e['payload']['error_class']='SLOW'
r=score(rs,ps)
save('PROBE_SLOW_PASS',small(r),'Cannot RECOVERED from inconsistent pass=true with latency5s>L2s',r['incidents'][0]['label']!='RECOVERED')
sp=copy.deepcopy(m.FIX['base']);sp['incidents']=[{k:sp[k] for k in ('t_req','t_stop','target','flow','effect')},{'t_req':1000,'t_stop':1140,'target':'frontend','flow':'checkout','effect':{'status':'CONFIRMED','t_eff':1001,'t':1060}}]
rs,ps,_=m.build('WAR_ACTIONS',sp)
for z in rs:
 e=z['envelope']
 if e['event_type'] in ('API_ACCEPTED','ACTION_COMPLETED'):e.pop('decision_id',None)
r=score(rs,ps)
save('ACTION_ID_ONLY_VALID_TERMINAL',small(r),'Known action_id links terminal; first reaction19, no orphans',r['orphans']==0 and r['incidents'][0]['reaction']==19)
rs,ps,_=make();rv=next(z['envelope'] for z in rs if z['envelope']['event_type']=='RECOVERY_VERIFIED');rv['ts_event']=m.iso(221)
ve=m.validate(rv);r=score(rs,ps)
save('PUBLISH_BEFORE_LAST_PROBE_FINISHED',{'validate':ve,'score':small(r),'event_at':221,'last_required_probe_end':221.25},'Reject/flag premature recovery publication',bool(ve[0]) or r['incidents'][0]['evaluator_mismatch'])
rs,ps,_=make();det=next(z['envelope'] for z in rs if z['envelope']['event_type']=='DETECTED');det['run_id']=m.gid('other','run','run');r=score(rs,ps)
save('EXPLICIT_CONTEXT_CONFLICT',small(r),'Wrong run_id must not score merely because incident_id matches','LINK_CONFLICT' in r['incidents'][0]['flags'] or r['incidents'][0]['mttd']!=30)
rs,ps,_=make()
for z in rs:
 if z['envelope']['event_type']=='RECOVERY_VERIFIED':z['envelope']['payload']['sample_seq_range']=[0,0]
r=score(rs,ps)
save('INVALID_RECOVERY_EVIDENCE_RANGE',small(r),'EVALUATOR_MISMATCH: sample0 cannot support recovery191..221',r['incidents'][0]['evaluator_mismatch'])
assert all(row["expectation_met"] for row in rows), "independent counterexample failed"
print('SUMMARY',len(rows),'cases;',sum(r['expectation_met'] for r in rows),'expectations met;',sum(not r['expectation_met'] for r in rows),'counterexamples reproduced')
