import sys,json,tempfile,errno,builtins
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'tests')
import test_event_pipeline_regressions as t
from event_pipeline.store import Archive,Rejected,ArchiveFailure
from event_pipeline.gateway import Gateway
out=[]
for plane in ('H','O'):
 for operation in ('records','seal','export_late','export_global','export_destination'):
  with tempfile.TemporaryDirectory() as d:
   a=Archive(Path(d)/plane,plane);g=Gateway(a,{})
   try:
    ctx=t.context();run=ctx['run_id']
    initial=t.contexts(ctx) if plane=='O' else [dict(t.manifest(),run_id=run)]
    for e in initial:a.ingest(e,{'kind':'test'},'harness')
    raw=a.path(run)/(plane+'.jsonl')
    if operation.startswith('export'):
     a.seal(run)
     if operation=='export_late':
      ev=t.detected(ctx) if plane=='O' else dict(t.manifest(),run_id=run)
      try:a.ingest(ev,{'kind':'test'},ev['source_component'])
      except Rejected:pass
     if operation=='export_global':
      try:a.reject('INVALID',{'kind':'test'},None,raw=b'[]',attributable=False)
      except Rejected:pass
    target=a.path(run)/'late.jsonl' if operation=='export_late' else a.root/'rejections.jsonl' if operation=='export_global' else raw
    orig=builtins.open
    def broken(path,*args,**kwargs):
     if Path(path)==target and args and args[0]=='rb':raise OSError(errno.EIO,'simulated SOURCE read EIO')
     return orig(path,*args,**kwargs)
    error=None
    if operation=='export_destination':
     destination=Path(d)/'already-exists';destination.mkdir()
     try:a.export(run,destination)
     except Exception as e:error=type(e).__name__
    else:
     with patch('builtins.open',broken):
      try:
       if operation=='records':a.records(run)
       elif operation=='seal':a.seal(run)
       else:a.export(run,Path(d)/'export')
      except Exception as e:error=type(e).__name__
    out.append({'plane':plane,'operation':operation,'error':error,'failure':a.failure,'readiness':g.readiness()})
   finally:a.close()
print(json.dumps(out,indent=2))
