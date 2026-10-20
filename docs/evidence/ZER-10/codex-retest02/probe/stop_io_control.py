from pathlib import Path
import sys,json,time,threading,tempfile
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'agent-orchestrator')]
from test_measurement_probe import serve,stop,Boutique,DripAck,make_plan,CONTEXT,PRODUCT,DEMO_FORM
from measurement.clock import ProbeClock,HttpReference
from measurement.flows import Flow,boutique_spec
from measurement.probe import ProbeRunner
from measurement.sink import Publisher,Outbox,MemorySink,HttpHSink
from http.server import BaseHTTPRequestHandler
holder={}
class StopH(DripAck):
 def do_POST(self):
  threading.Timer(.1,holder['runner'].stop).start()
  return super().do_POST()
class StopRef(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  threading.Timer(.1,holder['runner'].stop).start()
  time.sleep(0.2)
  raw=json.dumps({'clock_id':'clk-host','utc_ms':time.time()*1000,'resolution_ms':1}).encode()
  self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
class StopCleanup(Boutique):
 def handle_any(self,method):
  if self.path=='/cart/empty':threading.Timer(.1,holder['runner'].stop).start()
  return super().handle_any(method)
out={}
for case in ['H_ACK','reference','cleanup']:
 servers=[]
 with tempfile.TemporaryDirectory() as tmp:
  bs,bc,url=serve(StopCleanup if case=='cleanup' else Boutique,mode='checkout_unconfirmed' if case=='cleanup' else 'ok',delay={'POST /cart/empty':0.2} if case=='cleanup' else {})
  servers.append(bs)
  plan=make_plan(url,budget={'max_duration_s':10,'grace_s':.3,'max_samples':1})
  flow=Flow(boutique_spec(PRODUCT,None,DEMO_FORM),url,[url])
  sink=MemorySink();reference=None
  if case=='H_ACK':
   hs,hc,hurl=serve(StopH,before=0.2,pause=0.0,got=[]);servers.append(hs)
   sink=HttpHSink(hurl,'SYNTHETIC_'+'0'*40,timeout_s=3)
  if case=='reference':
   rs,rc,rurl=serve(StopRef);servers.append(rs)
   reference=HttpReference(rurl,timeout_s=3)
   plan['clock_sync']={'method':'cristian-http/0','interval_s':5}
  runner=ProbeRunner(plan,flow,CONTEXT,ProbeClock('clk-host','HOST_SHARED'),Publisher(Outbox(Path(tmp)/'outbox.jsonl'),sink),reference=reference)
  holder['runner']=runner
  start=time.perf_counter_ns();summary=runner.run();end=time.perf_counter_ns()
  out[case]={'wall_s':(end-start)/1e9,'stop_to_end_s':(end-runner.stop_requested_ns)/1e9,'summary':summary}
 for server in servers:stop(server)
print(json.dumps(out,indent=2))
