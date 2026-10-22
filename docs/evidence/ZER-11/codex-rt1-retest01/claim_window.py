"""Independent, pure-function attribution probes. No cluster or network."""
import copy
import json
import sys
from pathlib import Path

root = next(p for p in Path(__file__).resolve().parents if (p / 'agent-orchestrator').is_dir())
sys.path[:0] = [str(root / 'infrastructure/scripts'), str(root / 'agent-orchestrator')]
import r1_baseline_runtime as rt
from measurement.clock import stamp

t = 1_800_000_000_000
run = {'incidents': [{'trial_id': 'trial-1', 'label': 'RECOVERED_UNDETECTED',
                     'milestones': {'t_rec': {'t_ms': t + 20_000}, 't_stop': {'t_ms': t + 1}}}]}
receipt = {'trials': {'B0-CTRL': {'trial_id': 'trial-1', 'audit_coverage': {'complete': True}, 'stop_point': 'a'}}}
base = {'identity': {'t_req': stamp(t), 'deleted_uid': 'old-pod', 'owner_uids': ['rs-current'], 'pods_before': ['old-pod', 'surviving-pod']},
        'events': [{'reason': 'SuccessfulCreate', 'source': 'replicaset-controller', 'object': 'ReplicaSet/frontend-current',
                    'object_uid': 'rs-current', 't_ms': t + 1000, 'message': 'Created pod: frontend-replacement'}],
        'frontend_pods_after': [{'name': 'frontend-replacement', 'uid': 'new-pod', 'ready': True,
                                 'owner': [{'kind': 'ReplicaSet', 'uid': 'rs-current'}]}]}
rows = []
for name, at in [('current-before-recovery', t+1000), ('created-after-recovery', t+25000), ('missing-time', None), ('before-trial', t-60000)]:
    ev = copy.deepcopy(base)
    ev['events'][0]['t_ms'] = at
    actual = rt.interpret(run, receipt, {'trials': {'B0-CTRL': ev}})['B0-CTRL']['claim']
    rows.append({'case': name, 'event_t_ms': at, 't_req': t, 't_rec': t+20000, 'actual': actual,
                 'expected': 'CONTROLLER_RECOVERY_OBSERVED' if name == 'current-before-recovery' else 'RECOVERED_CONTROLLER_EVIDENCE_MISSING_OR_AMBIGUOUS'})
out = Path(__file__).with_suffix('.json')
out.write_text(json.dumps(rows, indent=1)+'\n')
print(json.dumps(rows, indent=1))
