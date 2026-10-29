"""Read-only runtime evidence reconciliation; no external client or additional request."""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/evidence/ZER-50/runtime-01'
sys.path.insert(0, str(OUT / 'source' / 'agent-orchestrator'))
from event_pipeline.contract import canonical, validate
from hephaestus.sqli_action_state import SqliActionState

def load(name):
    return json.loads((OUT / name).read_bytes())
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

acceptance, work, clean = (load(p) for p in ('acceptance.json', 'work-result.json', 'cleanup.json'))
assert acceptance['status'] == 'RECONCILE_REQUIRED' and acceptance['failure'] is None
assert work['status'] == 'OBSERVED_PENDING_REVIEW' and not work['guard_failures']
assert clean['verdict'] == 'CLEAN' and not clean['errors']
assert all(clean[k] for k in ('namespace_absent', 'shared_specs_preserved', 'shared_restarts_preserved'))
for process in ('worker', 'cleanup_process'):
    assert acceptance[process]['exit_code'] == 0 and not acceptance[process]['timed_out']
    assert acceptance[process]['process_reaped'] and acceptance[process]['owned_tree_closed']
lock, auth = load('source-manifest.json'), load('authorization.json')
assert sha(OUT / 'source-manifest.json') == auth['source_manifest_sha256']
assert sha(OUT / 'proposal.md') == auth['proposal_sha256']
for relative, digest in lock['sha256'].items():
    assert sha(OUT / 'source' / relative) == digest, relative

raw = [load('raw/' + p.name) for p in sorted((OUT / 'raw').glob('*.json'))]
assert not [r for r in raw if r.get('error') or r.get('cancelled')]
http_commands = [r for r in raw if any('ZER46_STAGE' in a for a in r['args'])]
tcp_commands = [r for r in raw if any('s.connect((' in a for a in r['args'])]
assert len(http_commands) == work['fixture_http'] == 9
assert len(tcp_commands) == work['tcp_checks'] == 2
assert all(json.loads(r['stdout']) == {'denied': True} for r in tcp_commands)
logs = []
for r in raw:
    if 'logs' in r['args'] and 'sqli-fixture' in r['args']:
        for line in r['stdout'].splitlines():
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if 'request_id' in value:
                logs.append(value)

joins = []
state = load('state.json')
for i in range(1, 10):
    http, access = load('http-%03d.json' % i), load('join-%03d.json' % i)
    request, response = http['request'], http['response']
    assert len({canonical(v) for v in logs if v['request_id'] == access['request_id']}) == 1
    assert access in logs and response['request_id'] == access['request_id']
    assert request['correlation'] == access['correlation_id']
    assert urlsplit(request['path']).path == access['path'] and request['method'] == access['method']
    assert response['status'] == access['status'] and access.get('delivered', True) is True
    assert response['begin'] <= access['ts'] <= response['end']
    assert load('log-pod-target-%03d.json' % i)['uid'] == state['fixture_uid']
    command = next(r for r in http_commands if json.loads(r['stdout'])['request_id'] == response['request_id'])
    assert json.loads(command['stdout']) == response
    joins.append({'ref': 'http-%03d.json' % i, 'status': response['status'], 'request_id': response['request_id']})
assert len({r['request_id'] for r in joins}) == 9
assert all(load('http-%03d.json' % i)['response']['end'] <= load('http-%03d.json' % (i+1))['response']['begin']
           for i in range(1, 9))
cases = {}
post = None
for label, expected in (('C0', 'NO_ACTION'), ('C1', 'ACTION_COMPLETED')):
    receipt, evidence = load(label + '-receipt.json'), load(label + '-input.json')
    detection, access = evidence['detection'], evidence['access']
    assert receipt['status'] == expected and receipt['decision_source'] == 'LLM' and not receipt['fallback']
    assert not validate(receipt['decision']) and not validate(detection)
    assert access['run_id'] == state['run_id'] and access['trial_id'] == state['trial_id']
    assert access['fixture_uid'] == state['fixture_uid'] and access['detection_event_id'] == detection['event_id']
    assert evidence['http_sha256'] == sha(OUT / access['ref'])
    idx = int(access['ref'][5:8])
    assert evidence['raw_join_sha256'] == sha(OUT / ('join-%03d.json' % idx))
    assert len(receipt['model_events']) == 1
    event = receipt['model_events'][0]
    assert not validate(event) and event['payload']['outcome'] == 'OK' and event['payload']['attempt_no'] == 1
    assert event['causation_id'] == detection['event_id'] and event['decision_id'] == receipt['decision_id']
    assert event['payload']['usage']['status'] == 'COMPLETE' and event['payload']['usage']['output_tokens'] <= 256
    directory = OUT / label / state['run_id']
    records = [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
    guards = [r['event'] for r in records if r['kind'] == 'GUARD_VERDICT']
    assert len(guards) == 1 and not validate(guards[0])
    if label == 'C0':
        assert guards[0]['payload']['verdict'] == 'REJECT' and guards[0]['payload']['reason_code'] == 'MODEL_NO_ACTION'
        assert access['restricted_rows'] == 0 and receipt['api_result'] is None and receipt['action_id'] is None
        assert not [r for r in records if r['kind'] in ('DISPATCH_INTENT', 'API_ACCEPTED', 'ACTION_POSTCONDITION')]
    else:
        assert access['restricted_rows'] == access['rows'] == 3
        assert guards[0]['payload']['verdict'] == 'ACCEPT' and receipt['api_result']['replay'] is False
        assert len([r for r in records if r['kind'] == 'DISPATCH_INTENT']) == 1
        observation = next(r for r in records if r['kind'] == 'OBSERVATION')
        post = next(r for r in records if r['kind'] == 'ACTION_POSTCONDITION')
        machine = SqliActionState(receipt['api_result'], observation['pins'], fixture_uid=state['fixture_uid'],
            accepted_at=receipt['action_state']['api_accepted_at'], timeout_s=120)
        reconstructed = machine.observe(post['proof']['attacker'], post['proof']['benign'],
            fixture=post['proof']['fixture'], now=receipt['action_state']['completed_at'])
        assert reconstructed == receipt['action_state']
        assert reconstructed['terminal']['status'] == 'SUCCESS'
        assert receipt['api_result']['rule']['expires_at'] - receipt['api_result']['rule']['created_at'] == 180
    cases[label] = {'status': receipt['status'], 'reason': receipt['reason'],
        'action': receipt['plan']['action'], 'decision_latency_ms': receipt['decision_latency_ms']}
budget = load('model-budget.json')
assert budget['attempts_dispatched'] == 2 and budget['unknown_usage_attempts'] == 0
assert budget['cost_estimate_complete'] and not budget['blocked'] and budget['reserved_estimate_usd'] <= .01
assert load('functional-observed.json')['api_replace_attempts'] == 1
samples = load('resource-samples.json')
assert min(s['hostAvailable'] for s in samples) >= 1073741824
assert min(s['wslAvailableKiB'] for s in samples) >= 1048576
assert max(s['memoryPsiAvg10'] for s in samples) <= 5
result = {'status': 'TECHNICAL_FUNCTIONAL_PASS_PENDING_INDEPENDENT_REVIEW_PUBLICATION',
    'source_snapshots_verified': len(lock['sha256']), 'raw_command_receipts': len(raw),
    'http_count': 9, 'tcp_count': 2, 'dispatch_count': 1, 'api_replace_attempts': 1,
    'cases': cases, 'usage': budget, 'cleanup': 'CLEAN', 'postcondition_reconstructed': True,
    'native_processes_reaped': True, 'resource_samples': len(samples),
    'limits': ['nominated DETECTED wrapper, not deployed Gaia/Kafka integration',
               'containment postcondition, not H availability recovery or G3/G4/KPI',
               'publication/CI/merge/owner acceptance pending']}
print(json.dumps(result, indent=2))
