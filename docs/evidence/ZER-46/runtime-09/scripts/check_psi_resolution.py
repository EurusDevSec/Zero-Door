"""Offline regressions from independent PSI-resolution review. No actor, network or native process."""
import importlib.util
import json
from pathlib import Path
import queue
import subprocess
import sys
import unittest
from unittest.mock import Mock,patch

spec=importlib.util.spec_from_file_location('zer46_psi_tests',Path(__file__).with_name('run_component.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.process_observer

class Resolution(unittest.TestCase):
    def setUp(self):
        self.block=[patch.object(subprocess,name,side_effect=AssertionError('OFFLINE_NO_PROCESS')) for name in ('Popen','run')]
        self.block.append(patch.object(m,'measured_request',side_effect=AssertionError('OFFLINE_NO_HTTP')))
        for b in self.block:b.start()
    def tearDown(self):
        for b in reversed(self.block):b.stop()
    def lab(self):
        lab=m.Lab();lab.save=Mock();return lab

    def test_watchdog_read_survives_foreground_phase_transition_and_log_deadline(self):
        lab=self.lab();clock=[99.8];owner=m.threading.get_ident();lab.phase_end=100;lab.phase_name='projection';lab.log_read_end=100
        class Child:
            pid=123;returncode=None
            def poll(self):
                if clock[0]>=100.3:self.returncode=0
                return self.returncode
            def terminate(self):self.returncode=-15
            def wait(self,timeout):return self.returncode
            def kill(self):self.returncode=-9
        def sleep(seconds):
            clock[0]+=seconds
            if clock[0]>=99.9:lab.phase_end=130;lab.phase_name='blocked_before'
        with patch.object(m.threading,'get_ident',return_value=owner+1),patch.object(m.time,'monotonic',side_effect=lambda:clock[0]),patch.object(m.time,'sleep',side_effect=sleep),patch.object(subprocess,'Popen',return_value=Child()):
            result=lab.command(['FAKE_READ_ONLY_RESOURCE'],timeout=4)
        self.assertEqual(result.returncode,0)
        receipt=lab.save.call_args.args[1]
        self.assertFalse(receipt.get('cancelled',False));self.assertEqual(lab.failure,[])

    def test_foreground_deadline_and_global_guard_remain_enforced(self):
        lab=self.lab();owner=m.threading.get_ident();lab.phase_name='projection';lab.phase_end=0
        with self.assertRaisesRegex(RuntimeError,'TTL_PHASE_TIMEOUT'):lab.check()
        with patch.object(m.threading,'get_ident',return_value=owner+1):
            lab.check()
            lab.stop.set()
            with self.assertRaisesRegex(RuntimeError,'GUARD_OR_CLEANUP_RESERVE'):lab.check()
            lab.stop.clear();lab.deadline=0
            with self.assertRaisesRegex(RuntimeError,'GLOBAL_BUDGET'):lab.check()

    def rpc_lab(self):
        lab=self.lab();lab.worker=Mock();lab.worker_count=1;lab.writer_started_at=1;lab.writer_instance='nonce';lab.replies=queue.Queue()
        return lab
    def reply(self,**change):
        row={'ok':True,'op':'hello','pid':22,'instance':'nonce','executable':sys.executable,'kernel_executable':'C:/Python/python.exe','result':{'identity_only':True}}
        row.update(change);return json.dumps(row)

    def test_venv_logical_path_and_native_image_are_both_validated(self):
        lab=self.rpc_lab();lab.replies.put(self.reply())
        handle=Mock();handle.identity={'pid':22,'creation_ticks':123,'executable':'C:/Python/python.exe','method':'WINDOWS_RETAINED_PROCESS_HANDLE'}
        with patch.object(p,'WriterProcess',return_value=handle) as native:
            self.assertEqual(lab.rpc('hello'),{'identity_only':True})
        native.assert_called_once_with(22,'C:/Python/python.exe',1)
        self.assertEqual(lab.writer_identity['rpc_executable'],sys.executable)
        self.assertEqual(lab.writer_identity['executable'],'C:/Python/python.exe')

    def test_unpinned_logical_path_or_drifted_native_image_is_rejected(self):
        lab=self.rpc_lab();lab.replies.put(self.reply(executable='C:/foreign/python.exe'))
        with patch.object(p,'WriterProcess') as native:
            with self.assertRaisesRegex(RuntimeError,'WRITER_LOGICAL_EXECUTABLE_PIN'):lab.rpc('hello')
            native.assert_not_called()
        for changed in ({'pid':23},{'kernel_executable':'C:/foreign/python.exe'},{'executable':'C:/foreign/venv/python.exe'}):
            lab=self.rpc_lab();lab.writer_identity={'pid':22,'creation_ticks':123,'executable':'C:/Python/python.exe','rpc_executable':sys.executable}
            lab.replies.put(self.reply(op='block',**changed))
            with self.assertRaisesRegex(RuntimeError,'WRITER_IDENTITY_DRIFT'):lab.rpc('block')

    def test_current_kernel_image_uses_self_native_handle_not_python_alias(self):
        api=Mock();api.GetCurrentProcess.return_value=42
        def image(handle,flags,buf,size):buf.value='C:/Physical/python3.11.exe';return 1
        api.QueryFullProcessImageNameW.side_effect=image
        with patch.object(p.os,'name','nt'),patch.object(p.ctypes,'WinDLL',return_value=api,create=True):
            self.assertEqual(p.current_image(),'C:/Physical/python3.11.exe')
        self.assertEqual(api.QueryFullProcessImageNameW.call_args.args[0],42)

if __name__=='__main__':unittest.main()
