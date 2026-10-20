import sys,time,json,tempfile,threading
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p / "agent-orchestrator").is_dir())
sys.path[:0]=[str(ROOT/'agent-orchestrator'),str(ROOT/'tests')]
from test_measurement_probe import Boutique,serve,stop,make_plan,run_probe,PRODUCT,DEMO_FORM,CONTEXT
from measurement.flows import Flow,boutique_spec,Memory
from measurement.sink import HttpHSink,Outbox,Publisher
from http.server import BaseHTTPRequestHandler
out={}

class CookieSwitch(Boutique):
    def do_POST(self):
        if self.path=='/cart':
            cls=type(self)
            self.rfile.read(int(self.headers.get('Content-Length','0')))
            sid=self.session()
            cls.log.append(('POST',self.path,sid))
            cls.sessions[sid].append(PRODUCT)
            return self.send(302,b'',[('Location','/cart'),('Set-Cookie','shop_session-id=foreign-user; Path=/')])
        return super().do_POST()
srv,cls,url=serve(CookieSwitch,sessions={'foreign-user':['foreign-product']})
try:
    flow=Flow(boutique_spec(PRODUCT,None,DEMO_FORM),url,[url])
    got=flow.run(time.perf_counter_ns()+2*10**9,threading.Event(),Memory())
    out['cookie_switch_cleanup']={'detail':got['detail'],'reason':got['reason'],'cleanup':got['cleanup'],'sessions':cls.sessions,'log':cls.log,'expected':'foreign-user cart retained; only original sample-owned cart cleaned or unresolved'}
finally:stop(srv)

# Owned loopback gateway slowly drips a fully valid ACK. Socket idle timeout is
# never reached, yet Publisher deadline and the declared grace expire meanwhile.
class DripAck(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def do_POST(self):
        event=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))))
        raw=json.dumps({'status':'RECORDED','event_id':event['event_id']}).encode()
        self.send_response(201);self.send_header('Content-Length',str(len(raw)));self.end_headers()
        try:
            for i in range(0,len(raw),5):
                self.wfile.write(raw[i:i+5]);self.wfile.flush();time.sleep(.02)
        except OSError:pass
srv,_,url=serve(DripAck)
try:
    with tempfile.TemporaryDirectory() as tmp:
        ob=Outbox(Path(tmp)/'outbox.jsonl');ob.add({'event_id':'evt_'+'1'*32})
        pub=Publisher(ob,HttpHSink(url,'SYNTHETIC_PROBE_TOKEN_'+'0'*30,timeout_s=.05))
        began=time.perf_counter();pending=pub.flush(max_attempts=1,deadline_ns=time.perf_counter_ns()+int(.05*1e9))
        out['sink_deadline_drip']={'deadline_s':.05,'sink_timeout_s':.05,'wall_s':time.perf_counter()-began,'pending':pending,'delivered':pub.counts['delivered'],'expected':'end by declared total deadline; undelivered event stays pending'}
finally:stop(srv)

# A valid coarse cadence reaches the next sample slot far beyond the run cap.
srv,cls,url=serve(Boutique)
try:
    with tempfile.TemporaryDirectory() as tmp:
        plan=make_plan(url,budget={'max_duration_s':.1,'grace_s':.05,'max_samples':2},f01={'delta_s':6.,'gap_s':12.})
        began=time.perf_counter();summary,_,_,_=run_probe(plan,Flow(boutique_spec(PRODUCT,None,DEMO_FORM),url,[url]),tmp)
        out['cadence_wait_over_cap']={'wall_s':time.perf_counter()-began,'summary':summary,'expected':'max_duration .1 + grace .05; waiting for slot must also be capped'}
finally:stop(srv)
# CLI uses an in-memory default journal, then prints only the aggregate summary.
import argparse,io,contextlib
from unittest.mock import patch
from measurement.__main__ import probe as cli_probe
from measurement.flows import request
from measurement.sink import MemorySink
class InterruptFlow(Flow):
    def run(self,*a,**kw):
        def interrupt_http(url_,method,headers,body,deadline,cancel):
            if method=='GET' and url_.endswith('/cart'):raise KeyboardInterrupt()
            return request(url_,method,headers,body,deadline,cancel)
        return super().run(*a,**dict(kw,http=interrupt_http))
srv,cls,url=serve(Boutique,delay={'POST /cart/empty':.3})
try:
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        plan=make_plan(url,budget={'max_duration_s':30,'grace_s':.05})
        for name,data in [('plan.json',plan),('context.json',CONTEXT),('keys.json',{'probe':'SYNTHETIC_'+'p'*40})]:(tmp/name).write_text(json.dumps(data))
        args=argparse.Namespace(plan=str(tmp/'plan.json'),context=str(tmp/'context.json'),h_keys=str(tmp/'keys.json'),outbox=str(tmp/'outbox.jsonl'),h_url='http://127.0.0.1:1',runtime_approval='OWNED_LOOPBACK_FAKE_ONLY')
        std=io.StringIO();began=time.perf_counter()
        with patch('measurement.__main__.flow_from',return_value=InterruptFlow(boutique_spec(PRODUCT,None,DEMO_FORM),url,[url])),patch('measurement.sink.HttpHSink',return_value=MemorySink()),contextlib.redirect_stdout(std):
            code=cli_probe(args)
        raw=[json.loads(line) for line in (tmp/'outbox.jsonl').read_text().splitlines()]
        stdout=json.loads(std.getvalue())
        out['cli_cancel_journal']={'wall_s':time.perf_counter()-began,'exit':code,'summary':stdout,'outbox_event_types':[x['event']['event_type'] for x in raw if x['op']=='event'],'cleanup_in_stdout_or_outbox':'cleanup' in std.getvalue() or any('cleanup' in json.dumps(x) for x in raw),'expected':'cancelled sample ownership/cleanup detail durably retained or included in CLI output; early-stop cleanup also respects .05s grace'}
finally:stop(srv)
print(json.dumps(out,indent=2))
