#!/usr/bin/env bash
# Read-only snapshot of node IPs, pod placement and netpol pod-firewall chains.
# Usage: snap.sh <label>   -> writes $OUT/<label>.json
set -u
OUT="$(dirname "$0")/netpol"
mkdir -p "$OUT"
D="docker --context desktop-linux"
K="kubectl --context k3d-zero-door --request-timeout=8s"
label="$1"
tmp="$OUT/$label.tmp"; mkdir -p "$tmp"
date -u +%Y-%m-%dT%H:%M:%SZ > "$tmp/at"
$D network inspect k3d-zero-door -f '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}' > "$tmp/bridge" 2>&1
$D inspect -f '{{.Name}} {{.State.Status}} {{.State.StartedAt}}' k3d-zero-door-agent-0 k3d-zero-door-server-0 > "$tmp/containers" 2>&1
$K get nodes -o json > "$tmp/nodes.json" 2>"$tmp/nodes.err"
$K get pods,pvc,deploy,statefulset,daemonset -A -o json > "$tmp/objs.json" 2>"$tmp/objs.err"
for n in agent server; do
  $D exec k3d-zero-door-$n-0 iptables-save -t filter > "$tmp/ipt-$n" 2>&1
  $D logs --since "$($D inspect -f '{{.State.StartedAt}}' k3d-zero-door-$n-0)" k3d-zero-door-$n-0 2>&1 \
    | grep -E 'Successfully retrieved node IP' | head -3 > "$tmp/nodeip-$n"
done
python -I - "$tmp" "$OUT/$label.json" <<'EOF'
import json, re, sys, pathlib
t = pathlib.Path(sys.argv[1])
rd = lambda f: (t / f).read_text(encoding='utf-8', errors='replace')
nodes = json.loads(rd('nodes.json'))
objs = json.loads(rd('objs.json'))
pods, pvcs, owners = [], [], []
for it in objs['items']:
    m, k = it['metadata'], it['kind']
    if k == 'Pod':
        sp, st = it['spec'], it.get('status', {})
        pods.append({'ns': m['namespace'], 'name': m['name'], 'node': sp.get('nodeName'),
                     'hostIP': st.get('hostIP'), 'podIP': st.get('podIP'),
                     'hostNetwork': sp.get('hostNetwork', False), 'phase': st.get('phase'),
                     'ready': all(c.get('ready') for c in st.get('containerStatuses', [])),
                     'restarts': sum(c.get('restartCount', 0) for c in st.get('containerStatuses', []))})
    elif k == 'PersistentVolumeClaim':
        pvcs.append({'ns': m['namespace'], 'name': m['name'], 'uid': m['uid'], 'phase': it['status'].get('phase')})
    else:
        owners.append({'kind': k, 'ns': m['namespace'], 'name': m['name'], 'uid': m['uid'],
                       'generation': m.get('generation')})
chains = {}
for n in ('agent', 'server'):
    s = rd(f'ipt-{n}')
    chains[n] = sorted(set(f'{b}/{a}' for a, b in re.findall(r'POD name:(\S+) namespace: (\S+) to chain', s)))
key = lambda p: f"{p['ns']}/{p['name']}"
host_of = {key(p): p['hostIP'] for p in pods}
ips = {}
for line in rd('bridge').splitlines():
    if line.strip():
        name, cidr = line.split()
        ips[name] = cidr.split('/')[0]
check = {}
for n in ('agent', 'server'):
    ip = ips.get(f'k3d-zero-door-{n}-0')
    expected = sorted(key(p) for p in pods if p['hostIP'] == ip and not p['hostNetwork'] and p['phase'] == 'Running')
    check[n] = {'container_ip': ip, 'startup_node_ip_log': rd(f'nodeip-{n}').strip(),
                'chains': len(chains[n]), 'expected_local_pods': len(expected),
                'missing': sorted(set(expected) - set(chains[n])),
                'foreign': sorted(c for c in chains[n] if host_of.get(c) != ip)}
    check[n]['ok'] = not check[n]['missing'] and not check[n]['foreign'] and ip in check[n]['startup_node_ip_log']
res = {'label': sys.argv[2], 'at': rd('at').strip(), 'bridge': ips, 'containers': rd('containers').strip().splitlines(),
       'nodes': [{'name': n['metadata']['name'],
                  'internal_ip': [a['address'] for a in n['status']['addresses'] if a['type'] == 'InternalIP'],
                  'ready': [c['status'] for c in n['status']['conditions'] if c['type'] == 'Ready']}
                 for n in nodes['items']],
       'check': check, 'pods': pods, 'pvcs': pvcs, 'owners': owners,
       'errors': {f: rd(f) for f in ('nodes.err', 'objs.err') if rd(f).strip()}}
pathlib.Path(sys.argv[2]).write_text(json.dumps(res, indent=1), encoding='utf-8')
print(json.dumps({'at': res['at'], 'bridge': ips, 'nodes': res['nodes'],
                  'check': {n: {k: v for k, v in c.items() if k != 'missing'} | {'missing_count': len(c['missing'])}
                            for n, c in check.items()},
                  'pods_not_ready': [key(p) for p in pods if not p['ready'] or p['phase'] != 'Running'],
                  'pvc_not_bound': [p['name'] for p in pvcs if p['phase'] != 'Bound']}, indent=1))
EOF
