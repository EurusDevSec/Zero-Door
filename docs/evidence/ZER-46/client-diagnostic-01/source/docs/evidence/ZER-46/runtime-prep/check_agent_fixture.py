"""Offline regression: no process, API, fixture traffic or runtime admission is allowed."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("zer46_agent_check", Path(__file__).with_name("run_agent_fixture.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CHAIN = "KUBE-POD-FW-ABCDEFGHIJKLMNOP"
POD = {"metadata": {"name": "sqli-fixture-123-abc", "namespace": "zd-sqli-lab"},
       "spec": {"nodeName": "k3d-zero-door-agent-0"}, "status": {"podIP": "10.42.0.200"}}
TABLE = (":" + CHAIN + " - [0:0]\n"
    '-A FORWARD -j KUBE-ROUTER-FORWARD\n'
    '-A KUBE-ROUTER-FORWARD -d 10.42.0.200/32 -m comment --comment "rule to jump traffic destined to POD name:sqli-fixture-123-abc namespace: zd-sqli-lab to chain ' + CHAIN + '" -j ' + CHAIN + '\n'
    '-A ' + CHAIN + ' -m mark ! --mark 0x10000/0x10000 -j REJECT\n')


class AgentPlacement(unittest.TestCase):
    def setUp(self):
        self.patches = [patch.object(m.cached.subprocess, name, side_effect=AssertionError("offline no process"))
                        for name in ("Popen", "run")]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()

    def test_bound_hook_is_required_not_comment_or_chain_alone(self):
        self.assertTrue(m.hooked_policy(TABLE, POD))
        for table in (TABLE.replace('-A FORWARD -j KUBE-ROUTER-FORWARD', ''),
                      TABLE.replace('-j REJECT', '-j ACCEPT'),
                      TABLE.replace('10.42.0.200/32', '10.42.0.201/32'),
                      TABLE.replace('namespace: zd-sqli-lab', 'namespace: foreign'),
                      TABLE.replace('! --mark', '--mark'),
                      TABLE.replace(':' + CHAIN + ' - [0:0]', '')):
            self.assertFalse(m.hooked_policy(table, POD))

    def test_bad_identity_rejected(self):
        pod = copy.deepcopy(POD); pod['metadata']['name'] = "bad;name"
        with self.assertRaisesRegex(ValueError, 'policy identity'): m.hooked_policy(TABLE, pod)

    def test_node_mismatch_never_reads_or_releases(self):
        lab = m.Lab(); lab.command = Mock()
        pod = copy.deepcopy(POD); pod['spec']['nodeName'] = 'k3d-zero-door-server-0'
        with self.assertRaisesRegex(RuntimeError, 'POLICY_NODE_PIN'): lab.policy_installed(pod)
        lab.command.assert_not_called()

    def test_policy_reader_targets_only_pinned_node(self):
        lab = m.Lab(); lab.command = Mock(return_value=subprocess.CompletedProcess([], 0, TABLE.encode(), b''))
        self.assertTrue(lab.policy_installed(POD))
        self.assertEqual(lab.command.call_args.args[0], ['docker', '--context', 'desktop-linux', 'exec',
            'k3d-zero-door-agent-0', 'iptables-save', '-t', 'filter'])

    def test_cache_mismatch_does_not_admit_or_create(self):
        lab = m.Lab(); lab.kube = Mock(); lab.save = Mock()
        with patch.object(m.cached.Lab, 'ensure_cache', side_effect=RuntimeError('CACHED_NODE_DIGEST')):
            with self.assertRaisesRegex(RuntimeError, 'CACHED_NODE_DIGEST'): lab.ensure_cache()
        lab.kube.assert_not_called(); lab.save.assert_not_called()

    def test_existing_hook_missing_stops_before_fixture_or_observer(self):
        lab = m.Lab(); lab.save = Mock(); lab.policy_installed = Mock(return_value=False)
        pod = copy.deepcopy(POD); pod['status'].update(hostIP='172.19.0.4', phase='Running')
        nodes = {'items': [{'metadata': {'name': lab.node}, 'status': {'addresses': [
            {'type': 'InternalIP', 'address': '172.19.0.4'}]}}]}
        lab.kube = Mock(side_effect=[subprocess.CompletedProcess([], 0, json.dumps(x).encode(), b'')
                                    for x in (nodes, {'items': [pod]})])
        with patch.object(m.cached.Lab, 'ensure_cache'):
            with self.assertRaisesRegex(RuntimeError, 'EXISTING_POLICY_HOOK_MISSING'): lab.ensure_cache()
        self.assertEqual(lab.kube.call_count, 2); lab.save.assert_not_called()

    def test_all_owned_workloads_pinned_together_without_pull(self):
        renderer = m.cached.parent.full.renderer
        docs = renderer.render('zer46-0123456789ab', 'run_' + '1' * 32, 'trl_' + '2' * 32,
                               '10.42.0.200', node='k3d-zero-door-agent-0')
        count = 0
        for doc in docs:
            if doc['kind'] == 'Deployment': pod = doc['spec']['template']['spec']
            elif doc['kind'] == 'Pod': pod = doc['spec']
            else: continue
            count += 1
            self.assertEqual(pod['nodeSelector'], {'kubernetes.io/hostname': 'k3d-zero-door-agent-0'})
            self.assertTrue(all(c['imagePullPolicy'] == 'Never' for c in pod['containers']))
        self.assertEqual(count, 4)
        with self.assertRaisesRegex(ValueError, 'node pin'):
            renderer.render('zer46-0123456789ab', 'run_' + '1' * 32, 'trl_' + '2' * 32,
                            '10.42.0.200', node='foreign-node')

    def test_missing_hook_never_releases_application(self):
        lab = m.Lab(); lab.kube = Mock(); lab.pod = Mock(return_value={**copy.deepcopy(POD),
            'status': {'podIP': '10.42.0.200', 'containerStatuses': [{'restartCount': 0, 'state': {'running': {}}}]}})
        lab.policy_installed = Mock(return_value=False)
        lab.wait = Mock(side_effect=RuntimeError('GUARD_STOP'))
        with self.assertRaisesRegex(RuntimeError, 'GUARD_STOP'): lab.release()
        lab.kube.assert_not_called()


    def test_prepared_manifest_drift_stops_before_execution(self):
        with patch.object(m.Path, 'read_text', return_value='{"sourceManifestSha256":"wrong"}'), \
             patch.object(m.Path, 'read_bytes', return_value=b'changed'):
            with self.assertRaisesRegex(RuntimeError, 'PREPARED_MANIFEST_DRIFT'): m.verify_prepared_sources()


if __name__ == '__main__': unittest.main()
