"""Portable release checks for the locked ZER-37 design, no network or lab."""
import copy, importlib.util, json, pathlib, re, sys
here=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('contract',here/'check_contract.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
doc=(here.parents[1]/'design/r1-event-contract.md').read_text(encoding='utf-8')
assert 'Trạng thái: LOCKED.' in doc
assert 'DRAFT_FOR_REVIEW' not in doc
assert m.SCHEMA=='zd-event/1.0.0'
fence=chr(96)*3
blocks=re.findall(re.escape(fence)+'json'+chr(10)+'(.*?)'+re.escape(fence),doc,re.S)
assert len(blocks)==2
count=0
for block in blocks:
 obj=json.loads(block)
 for rec in obj if isinstance(obj,list) else [obj]:
  e=rec.get('envelope',rec)
  errors,ok=m.validate(e,ctx={'l_ms':m.P['l_ms']})
  assert ok and not errors,(errors,e.get('event_type'))
  assert e['schema_version']==m.SCHEMA
  count+=1
for target in re.findall(r'\]\(([^)\s]+)\)',doc):
 target=target.split('#')[0]
 if target and not target.startswith(('https://','http://')):
  assert not re.match(r'^[A-Za-z]:',target),target
  assert (here.parents[1]/'design'/target).resolve().exists(),target
rows=[]
for cid,want in [('C1',dict(mttd=30,mttr=60,total=90,evaluator_mismatch=False)),('C3',dict(mttd=30,mttr=60,total=90,evaluator_mismatch=False)),('R1',dict(t_rec=191,mttr=60,evaluator_mismatch=True)),('W3',dict(reaction=19,orphans=0)),('L6',dict(leak='CLEAN',mode_violation=False)),('V1',dict(label='MISSING',reaction='MISSING')),('L7',dict(leak='LEAK_DETECTED')),('L8',dict(leak='LEAK_DETECTED')),('L9',dict(leak='UNKNOWN'))]:
 case=next(c for c in m.FIX['cases'] if c['id']==cid)
 sp=copy.deepcopy(m.FIX['base']);sp.update(case['over'])
 recs,prompts,meta=m.build(cid,sp);v=m.case_view(cid,m.analyse(recs,prompts),meta)
 actual={k:v.get(k) for k in want};assert actual==want,(cid,actual,want)
 rows.append(dict(case=cid,expected=want,actual=actual,passed=True))
print(json.dumps(dict(schema=m.SCHEMA,json_examples=count,focused_cases=rows,links='PASS'),ensure_ascii=False,indent=2))
