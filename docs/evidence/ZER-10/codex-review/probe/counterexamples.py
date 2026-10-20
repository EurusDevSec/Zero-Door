import sys,json,time,tempfile,threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
sys.path[:0]=[str(ROOT/'agent-orchestrator'),str(ROOT/'tests'),str(ROOT/'tests/fixtures/zer10')]
from test_measurement_probe import Boutique,Fixture,serve,stop,make_plan,run_probe,samples,PRODUCT,DEMO_FORM
from measurement.flows import Flow,boutique_spec,fixture_spec,Memory,request
from measurement.sink import HttpHSink
from measurement.__main__ import main as cli
from builder import e01
results={}
class DuplicateCart(Boutique):
    ordered=[]
    def handle_any(self,method):
        sid=self.session()
        if method=='POST' and self.path=='/cart':
            type(self).sessions.setdefault(sid,[]).append(PRODUCT)
        if method=='POST' and self.path=='/cart/checkout':
            type(self).ordered.append(list(type(self).sessions.get(sid,[])))
        return super().handle_any(method)
with tempfile.TemporaryDirectory() as tmp:
    server,cls,url=serve(DuplicateCart,ordered=[])
    try:
        p=make_plan(url,budget={'max_samples':1})
        summary,sink,_,_=run_probe(p,Flow(boutique_spec(PRODUCT,'Sunglasses',DEMO_FORM),url,[url]),tmp)
        got=samples(sink)[0]['payload']
        results['duplicate_cart']={'pass':got['pass'],'reason':got['detail']['reason'],'ordered':cls.ordered,'expected_quantity':1}
    finally: stop(server)
with tempfile.TemporaryDirectory() as tmp:
    server,cls,url=serve(Boutique,delay={'GET /':0.25})
    try:
        p=make_plan(url,budget={'max_samples':1},timeouts={'step_s':0.05,'transaction_s':1},f01={'l_ms':900})
        summary,sink,_,_=run_probe(p,Flow(boutique_spec(PRODUCT,'Sunglasses',DEMO_FORM),url,[url]),tmp)
        got=samples(sink)[0]['payload']
        results['step_timeout']={'step_s':p['timeouts']['step_s'],'pass':got['pass'],'home_ms':got['detail']['steps'][0]['ms'],'latency_ms':got['latency_ms']}
    finally: stop(server)
with tempfile.TemporaryDirectory() as tmp:
    server,cls,url=serve(Boutique,delay={'GET /':0.6})
    try:
        p=make_plan(url,budget={'max_samples':10,'max_duration_s':0.2},timeouts={'step_s':1,'transaction_s':1},f01={'l_ms':900})
        started=time.monotonic()
        summary,sink,_,_=run_probe(p,Flow(boutique_spec(PRODUCT,'Sunglasses',DEMO_FORM),url,[url]),tmp)
        results['max_duration']={'max_duration_s':p['budget']['max_duration_s'],'actual_s':round(time.monotonic()-started,3),'summary':summary,'sample_latency_ms':samples(sink)[0]['payload']['latency_ms']}
    finally: stop(server)
class Receive(BaseHTTPRequestHandler):
    got=[]
    def log_message(self,*a): pass
    def do_GET(self):
        type(self).got.append({'method':'GET','authorization':self.headers.get('Authorization'),'path':self.path})
        body=json.dumps({'status':'RECORDED','event_id':'evt_synthetic'}).encode()
        self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
recv=ThreadingHTTPServer(('127.0.0.1',0),Receive)
threading.Thread(target=recv.serve_forever,daemon=True).start()
class Redirect(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length',0)))
        self.send_response(302);self.send_header('Location',f'http://127.0.0.1:{recv.server_address[1]}/wrong-plane');self.send_header('Content-Length','0');self.end_headers()
redir=ThreadingHTTPServer(('127.0.0.1',0),Redirect)
threading.Thread(target=redir.serve_forever,daemon=True).start()
try:
    status=HttpHSink(f'http://127.0.0.1:{redir.server_address[1]}','SYNTHETIC_PROBE_TOKEN_01234567890123456789').deliver({'event_id':'evt_synthetic'})
    results['h_sink_redirect']={'status':status,'received_at_other_origin':Receive.got}
finally: stop(redir);stop(recv)
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp)
    h,o,_=e01().seal(base/'primary')
    other_h,other_o,_=e01().seal(base/'other')
    out=other_h/'score-inside-input'
    code=cli(['score','--h-export',str(h),'--o-export',str(o),'--other-export',str(other_h),'--output',str(out)])
    results['other_input_output']={'exit':code,'created_inside_other_export':(out/'score.json').exists()}
server,cls,url=serve(Boutique)
try:
    def interrupt_http(url_,method,headers,body,deadline,cancel):
        if method=='GET' and url_.endswith('/cart'):
            raise KeyboardInterrupt()
        return request(url_,method,headers,body,deadline,cancel)
    flow=Flow(boutique_spec(PRODUCT,'Sunglasses',DEMO_FORM),url,[url])
    try:
        flow.run(time.perf_counter_ns()+int(2e9),threading.Event(),Memory(),http=interrupt_http)
    except KeyboardInterrupt: pass
    results['keyboard_interrupt_cleanup']={'cart_sizes':[len(x) for x in cls.sessions.values()],'cleanup_requests':[x for x in cls.log if x[1]=='/cart/empty']}
finally: stop(server)
class StaleCreate(Fixture):
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length',0)))
        type(self).log.append(('POST',self.path))
        self.reply(201,type(self).table['pre-existing-order'])
server,cls,url=serve(StaleCreate,table={'pre-existing-order':{'order_ref':'pre-existing-order','item':'benign-catalog-item','note':'old-nonce','status':'STORED'}})
try:
    with tempfile.TemporaryDirectory() as tmp:
        p=make_plan(url,flow='fixture',budget={'max_samples':1})
        _,sink,_,_=run_probe(p,Flow(fixture_spec(),url,[url]),tmp)
        payload=samples(sink)[0]['payload']
        results['fixture_stale_cleanup']={'pass':payload['pass'],'reason':payload['detail']['reason'],'cleanup':payload['detail']['cleanup'],'pre_existing_still_exists':'pre-existing-order' in cls.table,'requests':cls.log}
finally: stop(server)
print(json.dumps(results,indent=2,sort_keys=True))
