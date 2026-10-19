import json,hashlib
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
folder=Path(__file__).parent
r=json.loads((folder/'receipt.json').read_bytes())
checks={}
checks['receipt_pass']=r['verdict']=='PASS' and all(r['checks'].values())
sha=lambda b:hashlib.sha256(b).hexdigest()
for p,d in r['source_hashes'].items():checks['source:'+p]=sha((root/p).read_bytes())==d
for name,image in r['images'].items():
 b=(folder/('oci-index-'+name+'.json')).read_bytes()
 checks[name+':oci_index']=sha(b)==image['Descriptor']['digest'].split(':')[1]
 index=json.loads(b)
 if name=='event_pipeline':
  pod=next(p for p in r['pods_before_stop']['items'] if p['metadata'].get('labels',{}).get('app')=='events-o')
  observed=pod['status']['containerStatuses'][0]['imageID']
 else:observed=r['actors'][name]['status']['containerStatuses'][0]['imageID']
 platform=next(m for m in index['manifests'] if m.get('platform',{}).get('architecture')=='amd64' and m.get('platform',{}).get('os')=='linux')
 b=(folder/('oci-manifest-'+name+'.json')).read_bytes()
 checks[name+':platform_manifest']=sha(b)==platform['digest'].split(':')[1]
 checks[name+':cri_config_digest']=json.loads(b)['config']['digest']==observed
raw={}
for plane in ['H','O']:
 d=folder/'export'/plane
 exp=json.loads((d/'export.json').read_bytes())
 for name,info in exp['files'].items():
  b=(d/name).read_bytes();checks[plane+':'+name]=len(b)==info['bytes'] and sha(b)==info['sha256']
 raw[plane]=[json.loads(l) for l in (d/(plane+'.jsonl')).read_bytes().splitlines()]
 checks[plane+':seal']=sha((d/(plane+'.jsonl')).read_bytes())==exp['seal']['sha256']
 for i,x in enumerate(raw[plane]):checks[plane+':envelope:'+str(i)]=sha(json.dumps(x['envelope'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())==x['envelope_sha256']
o=raw['O'];h=raw['H'];ctx=r['context']
detect=[x['envelope'] for x in o if x['envelope']['event_type']=='DETECTED'];decision=[x['envelope'] for x in o if x['envelope']['event_type']=='DECISION']
checks['single_decision']=len(decision)==1
checks['same_envelope_redelivery']=len(detect)==3 and len({json.dumps(x,sort_keys=True) for x in detect})==1
checks['causal_chain']=decision[0]['causation_id']==detect[0]['event_id'] and decision[0]['payload']['inputs'][0]['event_id']==detect[0]['event_id']
checks['incident_chain']=all(x['envelope'].get('incident_id')==ctx['incident_id'] for x in o if x['envelope']['event_type']!='RUN_CONTEXT')
checks['kafka_http_provenance']=all(x['transport']['kind']=='kafka' and x['transport']['http_request_id'] for x in o)
checks['offset_order']=all(b['transport']['offset']>a['transport']['offset'] for a,b in zip(o,o[1:]))
checks['no_recovery_claim']=not any(x['envelope']['event_type'] in {'HEAL_STARTED','ACTION_COMPLETED','RECOVERY_VERIFIED'} for x in o)
canary=h[0]['envelope']['payload']['canary_token']
checks['canary_absent_o']=canary not in (folder/'export/O/O.jsonl').read_text()
checks['audit_clean']=r['leak_audit']['clean']['result']=='CLEAN'
for actor,a in r['actors'].items():
 checks[actor+':gate']=len(a['gate']['history'])>=3 and all(not x['open'] for x in a['gate']['history'][-3:])
 checks[actor+':uid']=bool(a['pod_uid'])
 checks[actor+':source_denied']=a['cross_role']['cross_role']==422
 checks[actor+':no_token']=not a['spec']['automountServiceAccountToken']
 keys=[v['secret']['secretName'] for v in a['spec']['volumes'] if 'secret' in v]
 checks[actor+':own_key_mount']=keys==['event-o-'+actor]
 checks[actor+':no_raw']=not any('persistentVolumeClaim' in v for v in a['spec']['volumes'])
checks['distinct_actor_uid']=r['actors']['gaia']['pod_uid']!=r['actors']['hephaestus']['pod_uid']
result={'checks':checks,'passed':sum(checks.values()),'total':len(checks),'verdict':'PASS' if all(checks.values()) else 'FAIL'}

print(json.dumps(result,indent=2))
assert all(checks.values()),[k for k,v in checks.items() if not v]
