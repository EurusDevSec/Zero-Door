"""Offline failure regressions from the stop audit; never starts a child or contacts the lab."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("zer46_stop_check", Path(__file__).with_name("run_fixture_only.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
full = m.full

class StopAudit(unittest.TestCase):
    def setUp(self):
        self.patches = [patch.object(subprocess, name, side_effect=AssertionError("OFFLINE_NO_PROCESS"))
                        for name in ("Popen", "run")]
        self.patches.append(patch.object(full, "measured_request", side_effect=AssertionError("OFFLINE_NO_HTTP")))
        for item in self.patches: item.start()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()

    def test_cancel_preserves_partial_streams_and_terminal_status(self):
        lab = full.Lab(); rows = {}; lab.save = lambda name, obj: rows.update({name: dict(obj)})
        lab.check = Mock(side_effect=[None, RuntimeError("GUARD_STOP")])
        class Child:
            pid = 123; returncode = None
            def poll(self): return self.returncode
            def terminate(self): self.returncode = -15
            def wait(self, timeout): return self.returncode
        def start(args, stdout, stderr, **kwargs):
            stdout.write(b'client-imported\n')
            stderr.write(b'--token=synthetic-secret\n')
            return Child()
        with patch.object(subprocess, 'Popen', side_effect=start):
            with self.assertRaisesRegex(RuntimeError, 'GUARD_STOP'):
                lab.command(['FAKE-NONEXECUTABLE'])
        receipt = rows['raw/0001.json']
        self.assertEqual(receipt.get('stdout'), 'client-imported\n')
        self.assertEqual(receipt.get('returncode'), -15)
        self.assertTrue(receipt.get('cancelled'))
        self.assertNotIn('synthetic-secret', receipt.get('stderr', ''))
        self.assertIn('[REDACTED]', receipt.get('stderr', ''))
        self.assertGreaterEqual(receipt['ended_at'], receipt['at'])

    def test_worker_stop_error_does_not_skip_owned_namespace_delete_or_receipt(self):
        lab = full.Lab(); lab.creation_attempted = True; lab.ns_uid = 'owned-uid'
        lab.before = {'items': []}; calls = []
        lab.save = Mock(); lab.logs = Mock(); lab.command = Mock()
        lab.snapshot = Mock(return_value={'items': []}); lab.resources = Mock()
        lab.probe = Mock(return_value={'healthy': True})
        lab.stop_worker = Mock(side_effect=RuntimeError('WRITER_EXIT_UNKNOWN'))
        def kube(*args):
            calls.append(args)
            if args[:3] == ('get', 'namespace', full.NS) and '--ignore-not-found' not in args:
                body = json.dumps({'metadata': {'uid': lab.ns_uid, 'labels': {'zero-door.io/run': lab.owner}}}).encode()
            else: body = b''
            return subprocess.CompletedProcess(args, 0, body, b'')
        lab.kube = kube
        report = lab.cleanup()
        self.assertTrue(any(args[:2] == ('delete', '--raw') for args in calls))
        self.assertTrue(report['namespace_absent'])
        self.assertEqual(report['verdict'], 'INCOMPLETE')
        self.assertTrue(any('WRITER_EXIT_UNKNOWN' in x for x in report['errors']))
        self.assertEqual(lab.save.call_args.args[0], 'cleanup.json')

    def test_late_guard_failure_vetoes_completed_protocol_in_both_entrypoints(self):
        for module in (m, full):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); proposal = root / 'proposal.md'; proposal.write_text('offline fake')
                auth = {'status': 'APPROVED', 'proposal': str(proposal),
                        'proposalSha256': hashlib.sha256(proposal.read_bytes()).hexdigest()}
                authpath = root / 'docs/evidence/ZER-46/runtime-prep/readiness-authorization.json'
                authpath.parent.mkdir(parents=True); authpath.write_text(json.dumps(auth))
                lab = Mock(); lab.validated = True; lab.started = 0; lab.failure = ['SHARED_INVENTORY_DRIFT']
                lab.cleanup.return_value = {'component_resource_verdict': 'CLEAN',
                                           'lab_readiness': 'NOT_VERIFIED', 'verdict': 'CLEAN'}
                context = patch.object(m, 'AUTHORIZATION_FILE', authpath)
                with patch.object(module, 'ROOT', root), patch.object(module, 'OUT', root / 'out'),                      patch.object(module, 'Lab', return_value=lab), patch.object(module.sys, 'argv', ['check', '--execute']), context:
                    result = module.main()
                self.assertEqual(result, 1)
                receipt = next(call.args[1] for call in lab.save.call_args_list if call.args[0] == 'acceptance.json')
                self.assertEqual(receipt['status'], 'NOT_MET')
                self.assertFalse(receipt['component_observed'])
                self.assertIn('SHARED_INVENTORY_DRIFT', receipt['error'])

if __name__ == '__main__': unittest.main()
