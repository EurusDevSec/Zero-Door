"""Offline renderer only: no subprocess, network, Kubernetes mutation or image build."""
import argparse, copy, re, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser()
p.add_argument('--run-id',required=True)
p.add_argument('--image',required=True)
p.add_argument('--proxy-image',required=True)
p.add_argument('--output',required=True,type=Path)
a=p.parse_args()
if not re.fullmatch(r'zer41-[a-z0-9-]{1,40}',a.run_id): p.error('invalid run id')
if not re.fullmatch(r'zer41-fixture:[a-f0-9]{12}',a.image): p.error('expected source-specific local image tag')
if not re.fullmatch(r'(docker.io/)?(library/)?traefik@sha256:[a-f0-9]{64}',a.proxy_image): p.error('expected observed Traefik digest')
ns='zd-sqli-lab'; owner={'zero-door.io/run':a.run_id}
docs=[d for d in yaml.safe_load_all((ROOT/'infrastructure/manifests/sqli-fixture.yaml').read_text()) if d and d['kind']!='Ingress']
def find(kind,name): return next(d for d in docs if d['kind']==kind and d['metadata']['name']==name)
for d in docs: d['metadata'].setdefault('labels',{}).update(owner)
dep=find('Deployment','sqli-fixture'); dep['spec']['strategy']={'type':'Recreate'}
dep['spec']['template']['metadata']['labels'].update(owner)
pod=dep['spec']['template']['spec']; pod['nodeSelector']={'kubernetes.io/hostname':'k3d-zero-door-server-0'}
find('Service','sqli-fixture')['spec']['ports'][0]['port']=9140
pod['initContainers']=[{'name':'policy-gate','image':a.image,'imagePullPolicy':'Never','command':['/usr/bin/python3','-c','import time; from pathlib import Path; p=Path("/data/.policy-release"); exec("while not p.exists(): time.sleep(0.2)")'],'securityContext':{'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}},'resources':{'requests':{'cpu':'5m','memory':'8Mi'},'limits':{'cpu':'50m','memory':'32Mi'}},'volumeMounts':[{'name':'data','mountPath':'/data'}]}]
pod['containers'][0]['image']=a.image; pod['containers'][0]['imagePullPolicy']='Never'
find('ConfigMap','sqli-fixture-config')['data']['ZD_SQLI_TOPOLOGY']='proxied'
allow=find('NetworkPolicy','allow-ingress-controller-and-dns')
allow['spec']['ingress'][0]['from']=[{'podSelector':{'matchLabels':{'app':'zer41-private-ingress'}}}]
def resource(kind,name,spec=None,**extra):
 d={'apiVersion':'v1' if kind in ('ConfigMap','Service','Pod') else 'apps/v1' if kind=='Deployment' else 'networking.k8s.io/v1', 'kind':kind,'metadata':{'name':name,'namespace':ns,'labels':dict(owner)},**extra}
 if spec is not None: d['spec']=spec
 docs.append(d); return d
static={'http':{'routers':{'fixture':{'entryPoints':['web'],'rule':'PathPrefix(`/fixture`)','service':'fixture'}},'services':{'fixture':{'loadBalancer':{'servers':[{'url':'http://sqli-fixture:9140'}]}}}}}
resource('ConfigMap','zer41-private-ingress',data={'dynamic.yaml':yaml.safe_dump(static,sort_keys=False)})
security={'runAsNonRoot':True,'runAsUser':65532,'runAsGroup':65532,'seccompProfile':{'type':'RuntimeDefault'}}
container_security={'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}}
proxy={'automountServiceAccountToken':False,'securityContext':security,'nodeSelector':{'kubernetes.io/hostname':'k3d-zero-door-server-0'},'containers':[{'name':'traefik','image':a.proxy_image,'imagePullPolicy':'IfNotPresent','args':['--global.checkNewVersion=false','--global.sendAnonymousUsage=false','--entrypoints.web.address=:8000','--providers.file.filename=/config/dynamic.yaml','--accesslog=true','--accesslog.format=json','--log.format=json','--log.level=ERROR'],'ports':[{'name':'web','containerPort':8000}],'readinessProbe':{'tcpSocket':{'port':'web'},'initialDelaySeconds':1,'periodSeconds':2},'securityContext':container_security,'resources':{'requests':{'cpu':'25m','memory':'32Mi'},'limits':{'cpu':'150m','memory':'96Mi'}},'volumeMounts':[{'name':'config','mountPath':'/config','readOnly':True}]}],'volumes':[{'name':'config','configMap':{'name':'zer41-private-ingress'}}]}
resource('Deployment','zer41-private-ingress',{'replicas':1,'strategy':{'type':'Recreate'},'selector':{'matchLabels':{'app':'zer41-private-ingress'}},'template':{'metadata':{'labels':{'app':'zer41-private-ingress',**owner}},'spec':proxy}})
resource('Service','zer41-private-ingress',{'type':'ClusterIP','selector':{'app':'zer41-private-ingress'},'ports':[{'name':'web','port':8000,'targetPort':'web'}]})
for name in ('zer41-source-a','zer41-source-b'):
 probe={'automountServiceAccountToken':False,'restartPolicy':'Never','activeDeadlineSeconds':1500,'securityContext':security,'nodeSelector':{'kubernetes.io/hostname':'k3d-zero-door-server-0'},'containers':[{'name':'source','image':a.image,'imagePullPolicy':'Never','command':['/usr/bin/python3','-c','import time; time.sleep(1500)'],'securityContext':container_security,'resources':{'requests':{'cpu':'5m','memory':'16Mi'},'limits':{'cpu':'50m','memory':'48Mi'}}}]}
 r=resource('Pod',name,probe);r['metadata']['labels']['app']='zer41-source'
dns={'to':[{'namespaceSelector':{'matchLabels':{'kubernetes.io/metadata.name':'kube-system'}},'podSelector':{'matchLabels':{'k8s-app':'kube-dns'}}}],'ports':[{'protocol':'UDP','port':53},{'protocol':'TCP','port':53}]}
def peer(app):return {'podSelector':{'matchLabels':{'app':app}}}
resource('NetworkPolicy','private-ingress',{'podSelector':{'matchLabels':{'app':'zer41-private-ingress'}},'policyTypes':['Ingress','Egress'],'ingress':[{'from':[peer('zer41-source')],'ports':[{'protocol':'TCP','port':8000}]}],'egress':[{'to':[peer('sqli-fixture')],'ports':[{'protocol':'TCP','port':9140}]},dns]})
resource('NetworkPolicy','private-sources',{'podSelector':{'matchLabels':{'app':'zer41-source'}},'policyTypes':['Egress'],'egress':[{'to':[peer('zer41-private-ingress')],'ports':[{'protocol':'TCP','port':8000}]},{'to':[peer('sqli-fixture')],'ports':[{'protocol':'TCP','port':9140}]},dns]})
sys.path.insert(0,str(ROOT/'tests'))
from check_guard_manifests import check
check(docs)
assert not any(d['kind']=='Ingress' for d in docs)
assert all(d['metadata']['labels']==owner or d['metadata']['labels'].get('zero-door.io/run')==a.run_id for d in docs)
assert all(d['spec'].get('type')=='ClusterIP' for d in docs if d['kind']=='Service')
assert sum(d['kind']=='Deployment' for d in docs)==2 and sum(d['kind']=='Pod' for d in docs)==2
assert find('ConfigMap','sqli-fixture-config')['data']['ZD_SQLI_PROFILE']=='safe'
with a.output.open('x',encoding='utf8',newline='\n') as out:yaml.safe_dump_all(docs,out,sort_keys=False)
print('OFFLINE_RENDER_PASS',len(docs),'resources; no public Ingress/NodePort/hostPort; safe profile')
