"""Independent offline probes: source permission, changed copy stream, partial destination write."""
import builtins, errno, json, sys, tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'tests')
import test_event_pipeline_regressions as t
from event_pipeline import store
from event_pipeline.gateway import Gateway
rows=[]
class Wrapped:
 def __init__(self,f,kind): self.f,self.kind,self.once=f,kind,False
 def __getattr__(self,k): return getattr(self.f,k)
 def __enter__(self): return self
 def __exit__(self,*args): self.f.close()
 def read(self,*args):
  data=self.f.read(*args)
  if data and not self.once:
   self.once=True
   return bytes([data[0]^1])+data[1:]
  return data
 def write(self,data):
  self.f.write(data[:max(1,len(data)//2)])
  self.f.flush()
  raise OSError(errno.ENOSPC,'simulated destination partial write')
for plane in 'HO':
 for case in ('source_permission','source_stream_changes','destination_partial_write'):
  with tempfile.TemporaryDirectory() as directory:
   a=store.Archive(Path(directory)/plane,plane)
   try:
    ctx=t.context();run=ctx['run_id']
    for e in (t.contexts(ctx) if plane=='O' else [dict(t.manifest(),run_id=run)]):
     a.ingest(e,{'kind':'test'},'harness')
    raw=a.path(run)/(plane+'.jsonl');before=raw.read_bytes()
    if case!='source_permission':a.seal(run)
    dest=Path(directory)/'export';real=builtins.open;reads=[0]
    def opened(path,mode='r',*args,**kwargs):
     if Path(path)==raw and 'r' in mode:
      reads[0]+=1
      if case=='source_permission':raise PermissionError(errno.EACCES,'simulated source permission')
      if case=='source_stream_changes' and reads[0]==5:return Wrapped(real(path,mode,*args,**kwargs),'read')
     if case=='destination_partial_write' and Path(path)==dest/(plane+'.jsonl') and 'x' in mode:
      return Wrapped(real(path,mode,*args,**kwargs),'write')
     return real(path,mode,*args,**kwargs)
    caught=None
    with patch('builtins.open',opened):
     try:
      a.records(run) if case=='source_permission' else a.export(run,dest)
     except Exception as e:caught=type(e).__name__
    expected=(('ArchiveFailure','PermissionError') if case=='source_permission' else
              ('ArchiveFailure','INTEGRITY') if case=='source_stream_changes' else ('OSError',None))
    assert (caught,a.failure)==expected,(plane,case,caught,a.failure)
    assert raw.read_bytes()==before
    state=Gateway(a,{}).readiness()
    assert state['ready']==(case=='destination_partial_write'),state
    if case=='destination_partial_write':
     assert not (dest/'export.json').exists()
     a.export(run,Path(directory)/'complete')
     assert (Path(directory)/'complete/export.json').exists()
    else:
     try:a.ingest(dict(t.manifest(),run_id=run) if plane=='H' else t.detected(ctx),{'kind':'test'},'harness' if plane=='H' else 'detector')
     except store.ArchiveFailure:pass
     else:raise AssertionError('write after failure')
    assert raw.read_bytes()==before
    rows.append(dict(plane=plane,case=case,error=caught,failure=a.failure,ready=state['ready'],source_unchanged=True))
   finally:a.close()
print(json.dumps(dict(cases=rows,pass_count=len(rows)),indent=2))
