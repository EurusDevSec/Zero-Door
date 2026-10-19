import sys,json,tempfile,errno,builtins
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'tests')
import test_event_pipeline_regressions as t
out={}
with tempfile.TemporaryDirectory() as d:
 broker=t.Broker();keys={role:role.ljust(64,'x') for role in ('harness','detector','reader','evaluator','decision_rules')}
 stack=t.Stack(d,broker,keys,kafka=False)
 try:
  ctx=t.context()
  for e in t.contexts(ctx):stack.archive.ingest(e,{'kind':'seed'},'harness')
  badpath=stack.archive.path(ctx['run_id'])/'O.jsonl';orig=builtins.open
  def broken_open(path,*args,**kwargs):
   if Path(path)==badpath and args and args[0]=='rb':raise OSError(errno.EIO,'simulated source read EIO')
   return orig(path,*args,**kwargs)
  with patch('builtins.open',broken_open):
   try:out['read_http']=stack.request('/events?run_id='+ctx['run_id'],'reader')
   except Exception as e:out['read_http_error']=type(e).__name__
  out['archive_failure']=stack.archive.failure
  out['ready_after_eio']=stack.request('/readyz')
  out['post_after_eio']=stack.request('/events','detector',t.detected(ctx))
 finally:stack.close()
print(json.dumps(out,indent=2))
