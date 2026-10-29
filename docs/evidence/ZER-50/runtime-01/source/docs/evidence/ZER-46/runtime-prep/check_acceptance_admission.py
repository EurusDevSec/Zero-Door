"""Offline admission and tighter bounds; no lab/HTTP/child process."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock,patch
spec=importlib.util.spec_from_file_location('zer46_acceptance_check',Path(__file__).with_name('run_acceptance.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Admission(unittest.TestCase):
    def setUp(self):
        self.patches=[patch.object(subprocess,x,side_effect=AssertionError('OFFLINE_NO_PROCESS')) for x in ('Popen','run')]
        self.patches.append(patch.object(m.parent.full,'measured_request',side_effect=AssertionError('OFFLINE_NO_HTTP')))
        for p in self.patches:p.start()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
    def test_tighter_budgets_stop_before_transport(self):
        lab=m.Lab();lab.fixture_http=29;lab.tcp_checks=4
        with self.assertRaisesRegex(RuntimeError,'AC_FIXTURE_HTTP_BUDGET'):lab.http('a')
        with self.assertRaisesRegex(RuntimeError,'AC_TCP_BUDGET'):lab.isolation({})
    def test_missing_approval_cannot_construct_lab(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(m,'OUT',Path(tmp)),patch.object(m,'AUTH',Path(tmp)/'missing'),patch.object(m.sys,'argv',['ac','--execute']),patch.object(m,'snapshot') as snapshot,patch.object(m.parent,'main') as parent:
            with self.assertRaises(FileNotFoundError):m.main()
            snapshot.assert_not_called();parent.assert_not_called()
    def test_consumed_attempt_does_not_touch_approval_or_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'acceptance.json').write_text('{}')
            with patch.object(m,'OUT',root),patch.object(m,'AUTH',root/'missing'):
                with self.assertRaisesRegex(RuntimeError,'ONE_ATTEMPT_ONLY'):m.verify_sources()
    def test_source_drift_rejected_and_snapshot_matches_approved_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'component.py';source.write_text('original')
            proposal=root/'proposal.md';proposal.write_text('reviewed')
            manifest=root/'manifest.json';lock={'files':{'component.py':hashlib.sha256(source.read_bytes()).hexdigest()}}
            manifest.write_text(json.dumps(lock))
            auth=root/'auth.json';auth.write_text(json.dumps({'status':'APPROVED','proposal':'proposal.md','proposalSha256':hashlib.sha256(proposal.read_bytes()).hexdigest(),'sourceManifestSha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}))
            with patch.object(m,'ROOT',root),patch.object(m,'OUT',root/'out'),patch.object(m,'AUTH',auth),patch.object(m,'MANIFEST',manifest),patch.object(m,'PROPOSAL',proposal):
                self.assertEqual(m.verify_sources(),lock);m.snapshot(lock)
                self.assertEqual((root/'out/source/component.py').read_bytes(),b'original')
                source.write_text('drift')
                with self.assertRaisesRegex(RuntimeError,'SOURCE_DRIFT'):m.verify_sources()
if __name__=='__main__':unittest.main()
