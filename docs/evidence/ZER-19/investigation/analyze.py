"""Offline analysis only. Reads saved receipts; no subprocess/network/lab imports."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent

def load(path):
    return json.loads(path.read_bytes())

def iso(t):
    return datetime.fromtimestamp(t, __import__('datetime').timezone.utc).isoformat()

def seconds(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()

def series(group, name):
    value = load(HERE / group / (name + '.json'))
    assert value['returncode'] == 0 and value['response']['status'] == 'success'
    return value['response']['data']['result']

# One exporter: both k3d nodes share the WSL kernel; never add duplicate host counters.
pressure = series('historical-metrics', 'pressure')
pressure_rows = []
for row in pressure:
    if row['metric']['instance'] != '172.19.0.5:9100':
        continue
    selected = [(t, float(v)) for t, v in row['values']
                if seconds('2026-10-28T15:55:00Z') <= t < seconds('2026-10-28T15:56:02Z')]
    for a, b in zip(selected, selected[1:]):
        pressure_rows.append({'metric': row['metric']['__name__'], 'from': iso(a[0]), 'to': iso(b[0]),
            'elapsed_s': b[0]-a[0], 'counter_delta_s': b[1]-a[1],
            'interval_stall_percent': 100*(b[1]-a[1])/(b[0]-a[0]),
            'not_avg10': True})

cart = series('historical-metrics', 'cart-throttling')
cart_old = [x for x in cart if x['metric']['name'].startswith('7895a60c')]
deltas = {}
for row in cart_old:
    a,b = row['values'][-2:]
    deltas[row['metric']['__name__']] = float(b[1])-float(a[1])
assert deltas['container_cpu_cfs_throttled_periods_total'] == 164
assert deltas['container_cpu_cfs_periods_total'] == 166
cart_summary = {'from': iso(a[0]), 'to': iso(b[0]), 'deltas': deltas,
    'throttled_active_periods_percent': 100*164/166,
    'not_wall_time_percent': True, 'cpu_limit_millicores': 200,
    'interpretation': 'Quota throttling corroborates cart scheduling pressure; does not identify the global stall initiator.'}

rpc = load(HERE / 'docker-exec-window.json')
exec_id='ff65663e2c5e017b4d2d1a253d211d97cd46a6cb6612b928455d4007cf5ad901'
rows=[x for x in rpc if exec_id+'/start' in x['msg']]
assert len(rows)==2 and rows[0]['msg'].startswith('>>') and rows[1]['msg'].startswith('<<')
exec_span={'exec_id':exec_id, 'request_at':rows[0]['time'], 'response_at':rows[1]['time'],
    'request_span_s':seconds(rows[1]['time'])-seconds(rows[0]['time']),
    'meaning':'Daemon/proxy exec-start transaction span, not an isolated cat CPU runtime.'}
assert 16.8 < exec_span['request_span_s'] < 17

scrapes=series('historical-metrics','scrapes')
slow_scrapes=[{'metric':s['metric'], 'at':iso(t), 'duration_s':float(v)}
    for s in scrapes if s['metric']['__name__']=='scrape_duration_seconds'
    for t,v in s['values'] if float(v)>5]
assert any(16 < x['duration_s'] < 17 for x in slow_scrapes)
vm=series('historical-attribution','vm-reclaim')
ooms=[x for x in vm if x['metric']['__name__']=='node_vmstat_oom_kill']
assert ooms and all(float(v)==0 for x in ooms for _,v in x['values'])
raw_samples=load(EVIDENCE/'runtime-02/resource-samples.json')
assert len(raw_samples)==28
source_pins=load(EVIDENCE/'source-hashes.json')
root=EVIDENCE.parents[2]
source_drift=[str(p) for p,h in source_pins.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
assert not source_drift
runtime_pins=load(EVIDENCE/'runtime-02/source-manifest-at-invocation.json')
runtime_drift=[p for p,h in runtime_pins.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
assert not runtime_drift

result={'scope':'OFFLINE_ANALYSIS_OF_SAVED_EVIDENCE_NOT_NEW_ACCEPTANCE',
    'docker_exec':exec_span, 'pressure_intervals':pressure_rows, 'cart':cart_summary,
    'slow_scrapes':slow_scrapes, 'oom_kill_counters_all_zero':True,
    'valid_guard_samples':len(raw_samples), 'product_pins_verified':len(source_pins),
    'runtime_invocation_pins_verified':len(runtime_pins), 'source_drift':source_drift+runtime_drift,
    'limits':['Cumulative PSI deltas do not reconstruct the missing avg10 guard sample.',
              'CPU, memory, and I/O stall intervals can overlap; do not sum them.',
              'No process-level Windows scheduling trace; ultimate triggering process remains unknown.',
              'Current Docker/WSL has restarted since incident; fresh counters are not historical proof.']}
(HERE/'analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'offline_analysis':'PASS','exec_span_s':exec_span['request_span_s'],
    'cart_throttled_period_ratio':164/166,'product_pins':len(source_pins),'runtime_pins':len(runtime_pins)}))
