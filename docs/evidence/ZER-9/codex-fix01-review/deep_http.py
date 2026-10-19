import sys,json,hashlib,tempfile,time
from pathlib import Path
sys.path.insert(0,'tests')
import test_event_pipeline_regressions as t
keys={role:hashlib.sha256(role.encode()).hexdigest() for role in t.ROLES}
ctx=t.context(); ev=t.detected(ctx); v='x'
for _ in range(520):v=[v]
ev['payload']['extra']=v
out={}
with tempfile.TemporaryDirectory() as directory:
 broker=t.Broker(); stack=t.Stack(directory,broker,keys)
 try:
  for e in t.contexts(ctx):stack.archive.ingest(e,{},'harness')
  raw=t.canonical(ev)
  out['bytes']=len(raw);out['strict_decode_error']=t.store.decode(raw)[1]
  out['http_reply']=stack.request('/events','detector',raw=raw)
  out['quarantine_after_http']=len(t.lines(Path(directory)/'O'/ctx['run_id']/'rejections.jsonl'))+len(t.lines(Path(directory)/'O'/'rejections.jsonl'))
  broker.append(0,*t.signed(ev,keys));good=t.detected(ctx);broker.append(0,*t.signed(good,keys))
  t.eventually(lambda:stack.bridge.failure is not None,2)
  out['recorder_failure']=stack.bridge.failure;out['committed']=broker.committed;out['ready_reply']=stack.request('/readyz')
  out['good_recorded']=any(x['event_id']==good['event_id'] for x in stack.raw(ctx['run_id']))
 finally:stack.close()
print(json.dumps(out,indent=2))
