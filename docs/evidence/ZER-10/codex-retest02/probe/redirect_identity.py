from pathlib import Path
import sys,json,time,threading
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'agent-orchestrator')]
from test_measurement_probe import serve,stop,Boutique,PRODUCT,DEMO_FORM
from measurement.flows import Flow,Memory,boutique_spec
class SwitchCheckout(Boutique):
 def do_POST(self):
  if self.path=='/cart/checkout':
   self.rfile.read(int(self.headers.get('Content-Length',0)))
   type(self).log.append(('POST',self.path,self.session()))
   return self.send(307,b'', [('Set-Cookie','shop_session-id=foreign-user; Path=/'),('Location','/cart/empty')])
  self.handle_any('POST')
server,cls,url=serve(SwitchCheckout,sessions={'foreign-user':['foreign-product']})
try:
 result=Flow(boutique_spec(PRODUCT,None,DEMO_FORM),url,[url]).run(time.perf_counter_ns()+int(3e9),threading.Event(),Memory())
 print(json.dumps({'result':result,'log':cls.log,'sessions':cls.sessions},indent=2))
finally:stop(server)
