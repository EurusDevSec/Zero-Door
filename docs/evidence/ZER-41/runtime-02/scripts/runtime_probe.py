"""One finite fixture-only probe window; run only after lab approval, inside an owned source pod."""
import json,re,sys,time,uuid
from urllib.request import Request,build_opener,ProxyHandler,HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import quote
ORIGIN='http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000'
EXPECTED={"seed_id":"zer41-catalog/1","catalog_rows":8,"public_rows":5,"restricted_rows":3,"by_category":{"apparel":{"public":2,"restricted":1},"home":{"public":2,"restricted":0},"electronics":{"public":1,"restricted":0},"internal":{"public":0,"restricted":2}},"benign":{"apparel":["PUB-APP-001","PUB-APP-002"],"home":["PUB-HOM-001","PUB-HOM-002"],"electronics":["PUB-ELE-001"],"internal":[],"nonexistent":[]},"injection":{"category":"zzz' OR visibility='restricted' --","vulnerable_returns_restricted":["RES-APP-900","RES-INT-001","RES-INT-002"],"safe_returns":[]}}
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs): raise RuntimeError('REDIRECT_REFUSED')
def main():
 profile,run_id,source=sys.argv[1:]
 if profile not in ('safe','vulnerable') or source not in ('a','b') or not re.fullmatch(r'zer41-[a-z0-9-]{1,40}',run_id): raise ValueError('SCOPE_REFUSED')
 opener=build_opener(ProxyHandler({}),NoRedirect())
 attempts=0; started=time.monotonic(); ids=[]; owned=None; window=uuid.uuid4().hex[:8]
 def req(method,path,body=None,headers=None,cleanup=False):
  nonlocal attempts
  if attempts>=(32 if cleanup else 28) or time.monotonic()-started>=(90 if cleanup else 70): raise RuntimeError('WINDOW_CAP')
  if not path.startswith('/fixture/'): raise ValueError('PATH_REFUSED')
  time.sleep(.2); attempts+=1
  correlation=f'{run_id}-{window}-{source}-{attempts}'
  values={'X-Correlation-Id':correlation,'Content-Type':'application/json',**(headers or {})}
  raw=None if body is None else json.dumps(body).encode()
  try: response=opener.open(Request(ORIGIN+path,data=raw,headers=values,method=method),timeout=5)
  except HTTPError as error: response=error
  with response:
   data=response.read(262145)
   if len(data)>262144: raise RuntimeError('RESPONSE_CAP')
   value=json.loads(data); identity=response.headers.get('X-Request-Id')
   if not identity or not re.fullmatch('[a-f0-9]{32}',identity): raise RuntimeError('MISSING_ID')
   ids.append(identity)
   print(json.dumps({'event':'probe_sample','run':run_id,'source':source,'profile':profile,'attempt':attempts,'correlation_id':correlation,'request_id':identity,'method':method,'path':path.split('?')[0],'status':response.status,'body':value}),flush=True)
   return response.status,value
 try:
  for category,skus in EXPECTED['benign'].items():
   status,body=req('GET','/fixture/catalog/search?category='+quote(category,safe=''))
   assert status==200 and sorted(r['sku'] for r in body['results'])==sorted(skus)
   assert all(r['visibility']=='public' for r in body['results'])
  status,body=req('GET','/fixture/catalog/search?category='+quote(EXPECTED['injection']['category'],safe=''))
  want=EXPECTED['injection']['safe_returns'] if profile=='safe' else EXPECTED['injection']['vulnerable_returns_restricted']
  assert status==200 and sorted(r['sku'] for r in body['results'])==sorted(want)
  # This synthetic address must never become the observed end-client identity.
  status,body=req('GET','/fixture/catalog/search?category=home',headers={'X-Forwarded-For':'203.0.113.77'})
  assert status==200
  nonce=uuid.uuid4().hex
  status,body=req('POST','/fixture/orders',{'item':'zer41-benign-item','note':nonce})
  assert status==201 and body.get('note')==nonce and body.get('item')=='zer41-benign-item'
  ref=body.get('order_ref')
  assert isinstance(ref,str) and re.fullmatch('[a-f0-9]{32}',ref)
  owned=(ref,nonce)
  status,body=req('GET','/fixture/orders/'+ref)
  assert status==200 and body.get('note')==nonce and body.get('item')=='zer41-benign-item'
 finally:
  if owned:
   ref,nonce=owned
   status,body=req('GET','/fixture/orders/'+ref,cleanup=True)
   if status!=200 or body.get('note')!=nonce: raise RuntimeError('UNRESOLVED_OWNERSHIP')
   status,body=req('DELETE','/fixture/orders/'+ref,cleanup=True)
   assert status==200 and body.get('deleted')==1
   status,body=req('GET','/fixture/orders/'+ref,cleanup=True)
   assert status==404
 assert len(ids)==len(set(ids))
 print(json.dumps({'event':'probe_window','verdict':'PASS_LOCAL_CASES','attempts':attempts,'run':run_id,'source':source,'profile':profile,'client_ip_verdict':'REQUIRES_LOG_RECONCILIATION'}),flush=True)
if __name__=='__main__':main()
