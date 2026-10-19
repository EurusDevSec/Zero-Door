import sys,json,copy,tempfile,hashlib
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'tests')
import test_event_pipeline_regressions as t
from event_pipeline.gateway import Gateway,server
from event_pipeline.store import Archive
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import threading
rows=[json.loads(x) for x in Path('docs/evidence/ZER-9/live-11/export/H/H.jsonl').read_bytes().splitlines()]
a=copy.deepcopy(rows[0]['envelope']);a['run_id']=t.new_id('run');a['event_id']=t.new_id('evt')
b=copy.deepcopy(a);b['event_id']=t.new_id('evt');b['seq']+=1
key='x'*64
with tempfile.TemporaryDirectory() as d:
 archive=Archive(d,'H');g=Gateway(archive,{'harness':key});http=server(g,('127.0.0.1',0));threading.Thread(target=http.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(http.server_port)
 def req(path,event=None):
  try:
   with urlopen(Request(url+path,data=t.canonical(event) if event else None,headers={'Authorization':'Bearer '+key}),timeout=5) as r:return r.status,json.load(r)
  except HTTPError as e:return e.code,json.load(e)
 original=Archive.append
 def partial(path,record):
  with open(path,'ab') as f:f.write(b'{"ingest_id":');f.flush()
  raise OSError('simulated partial disk write')
 out={'plane':'H'}
 try:
  with patch.object(Archive,'append',side_effect=partial):out['first']=req('/events',a)
  out['readiness_after_failure']=req('/readyz');out['next']=req('/events',b)
  try:archive.records(a['run_id']);out['raw_read']='OK'
  except Exception as e:out['raw_read']=type(e).__name__
 finally:http.shutdown();http.server_close();archive.close()
print(json.dumps(out,indent=2))
