"""Offline regressions. No lab, child process or HTTP; native handles are fake APIs."""
import ctypes
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

PREP = Path(__file__).parent
ROOT = PREP.parents[3]
def load(name, file):
    spec = importlib.util.spec_from_file_location(name, PREP / file)
    module = importlib.util.module_from_spec(spec)
    if os.environ.get('ZER46_FAIL_BEFORE') == '1' and file in ('run_component.py', 'reconcile_completed_protocol.py'):
        source = ROOT / 'scratch/zer46/runner-complete' / (file + '.before')
        exec(compile(source.read_text(), str(PREP / file), 'exec'), module.__dict__)
    else: spec.loader.exec_module(module)
    return module
m = load('complete_runner_test', 'run_component.py')
v = load('complete_verifier_test', 'reconcile_completed_protocol.py')
p = load('complete_process_test', 'writer_process.py')

class Complete(unittest.TestCase):
    def setUp(self):
        self.blocks = [patch.object(subprocess, name, side_effect=AssertionError('OFFLINE_NO_PROCESS')) for name in ('Popen', 'run')]
        self.blocks += [patch.object(m, 'measured_request', side_effect=AssertionError('OFFLINE_NO_HTTP'))]
        for b in self.blocks: b.start()
    def tearDown(self):
        for b in reversed(self.blocks): b.stop()
    def lab(self):
        lab = m.Lab(); lab.save = Mock(); return lab

    def test_ttl_schedule_reserves_successors_and_original_expiry(self):
        lab = self.lab(); lab.rule = {'created_at':1000, 'expires_at':1180}; clock = [10.]
        with patch.object(m.time,'time', side_effect=lambda:1000 + clock[0]-10), patch.object(m.time,'monotonic',side_effect=lambda:clock[0]):
            for name, budget in m.TTL_PHASES:
                lab.begin_phase(name)
                self.assertLessEqual(lab.phase_end + lab.phase_receipts[-1]['future_reserved_seconds'], 175)
                clock[0] += budget
                # End immediately before each boundary rather than silently crossing it.
                clock[0] -= .01
            lab.end_ttl_phases()
        self.assertIsNone(lab.phase_end)
        self.assertEqual(lab.rule['expires_at'],1180)

    def test_no_restart_phase_admission_after_budget_expired(self):
        lab = self.lab(); lab.rule = {'created_at':1000, 'expires_at':1180}
        with patch.object(m.time,'time',return_value=1180):
            with self.assertRaisesRegex(RuntimeError,'TTL_PHASE_NO_BUDGET'): lab.begin_phase('projection')
        lab.kube = Mock()
        with self.assertRaisesRegex(RuntimeError,'TTL_PHASE_ORDER'): lab.begin_phase('replacement')
        lab.kube.assert_not_called()

    def test_phase_overrun_cannot_be_erased_by_entering_next_phase(self):
        lab = self.lab(); lab.rule = {'created_at':1000,'expires_at':1180}; clock=[10.]
        with patch.object(m.time,'time',return_value=1000),patch.object(m.time,'monotonic',side_effect=lambda:clock[0]):
            lab.begin_phase('projection'); clock[0] = lab.phase_end
            with self.assertRaisesRegex(RuntimeError,'TTL_PHASE_TIMEOUT'): lab.begin_phase('blocked_before')
        self.assertEqual(lab.phase_name,'projection')

    def test_cancel_check_prevents_inflight_command_after_phase_deadline(self):
        lab = self.lab(); lab.phase_end=0; lab.phase_name='replacement'
        with self.assertRaisesRegex(RuntimeError,'TTL_PHASE_TIMEOUT'): lab.command(['FAKE'])

    def test_protocol_enters_restart_budget_before_uid_delete_and_keeps_expiry(self):
        lab=self.lab(); clock=[10.]; rule={'created_at':1000,'expires_at':1180}
        old={'metadata':{'uid':'old','name':'sqli-fixture-old'}}
        new={'metadata':{'uid':'new','name':'sqli-fixture-new'}}
        lab.release=Mock(side_effect=[old,new]); lab.command=Mock(); lab.write_yaml=Mock(return_value='fake.yaml')
        lab.pod=Mock(side_effect=lambda name:{'status':{'podIP':'10.42.1.1' if name.endswith('a') else '10.42.1.2'}})
        lab.addresses={}; lab.crud=Mock(); lab.isolation=Mock(); lab.wait_projection=Mock()
        lab.start_worker=Mock(); lab.stop_worker=Mock(); lab.wait_old_pod_absent=Mock()
        lab.rpc=Mock(side_effect=[{'replay':False,'containment_verified':False,'rule':rule},
                                {'replay':True,'rule':rule}])
        cm={'metadata':{'uid':'cm'},'data':{'policy.json':json.dumps({'rules':[rule]})}}
        lab.cm=Mock(return_value=cm); lab.wait=lambda until:clock.__setitem__(0,until)
        def kube(*args):
            if args[0]=='delete': self.assertEqual(lab.phase_name,'replacement')
            return subprocess.CompletedProcess(args,0,json.dumps({'items':[{'metadata':{'labels':{'app':'zer46-private-ingress'}},'status':{'podIP':'10.42.1.3'}}]}).encode(),b'')
        lab.kube=kube
        def expect(who,status,**kwargs):
            if status==403: self.assertIn(lab.phase_name,('blocked_before','blocked_after'))
            if status==200 and lab.phase_index==5: self.assertGreaterEqual(1000+clock[0]-10,1180)
            return {},{'observed_at':1000}
        lab.expect=Mock(side_effect=expect)
        with patch.object(m.renderer,'render',return_value=[]),patch.object(m.time,'time',side_effect=lambda:1000+clock[0]-10),patch.object(m.time,'monotonic',side_effect=lambda:clock[0]):
            lab.run_fixture_protocol()
        self.assertTrue(lab.validated); self.assertEqual(rule['expires_at'],1180)
        self.assertEqual([row['phase'] for row in lab.phase_receipts],[name for name,_ in m.TTL_PHASES])

    def test_delayed_log_delivery_reads_same_pod_without_http_replay(self):
        lab = self.lab(); pod={'metadata':{'uid':'pinned'}}; lab.wait=Mock()
        lab.logs=Mock(side_effect=[[],[],[{'request_id':'r','status':403}]])
        result=lab.join_access(pod,'r')
        self.assertEqual(result['status'],403); self.assertEqual(lab.fixture_http,0)
        self.assertEqual(lab.logs.call_count,3)
        self.assertTrue(all(call.args==(pod,) for call in lab.logs.call_args_list))

    def test_missing_duplicate_or_uid_drift_log_never_joins(self):
        for result in ([],[{'request_id':'r'},{'request_id':'r'}],RuntimeError('LOG_POD_IDENTITY')):
            lab=self.lab(); lab.wait=Mock()
            lab.logs=Mock(side_effect=result if isinstance(result,Exception) else None,return_value=result)
            with self.assertRaises(RuntimeError): lab.join_access({'metadata':{'uid':'pinned'}},'r')
            self.assertLessEqual(lab.logs.call_count,3); self.assertEqual(lab.fixture_http,0)

    def fake_worker(self, rpc_pid=22):
        lab=self.lab(); child=Mock(); child.pid=11; child.poll.return_value=0
        lab.worker=child; lab.worker_stderr=Mock(); lab.writer_identity={'pid':rpc_pid,'creation_ticks':123}
        lab.writer_handle=Mock(); lab.writer_handle.wait_exit.return_value='EXITED'; lab.worker_count=1
        return lab

    def test_actual_rpc_exit_proof_handles_distinct_launcher_pid(self):
        for rpc_pid in (11,22):
            lab=self.fake_worker(rpc_pid); handle=lab.writer_handle; lab.stop_worker()
            receipt=lab.writer_exits[0]
            self.assertEqual(receipt['writer']['pid'],rpc_pid); self.assertEqual(receipt['launcher_pid'],11)
            self.assertEqual(receipt['rpc_exit'],'EXITED'); handle.close.assert_called_once()
            self.assertIsNone(lab.worker)

    def test_missing_alive_or_unknown_rpc_exit_fails_even_if_launcher_exits(self):
        for status in ('ALIVE','UNKNOWN',None):
            lab=self.fake_worker()
            if status is None: lab.writer_handle=None; lab.writer_identity=None
            else: lab.writer_handle.wait_exit.return_value=status
            with self.assertRaisesRegex(RuntimeError,'WRITER_'): lab.stop_worker()
            self.assertNotEqual(lab.writer_exits[0]['rpc_exit'],'EXITED')
            self.assertIn('error',lab.writer_exits[0])

    def test_rpc_nonce_or_pid_drift_rejected_before_action_success(self):
        import queue
        lab=self.fake_worker(); lab.writer_instance='expected'; lab.replies=queue.Queue()
        lab.replies.put(json.dumps({'ok':True,'op':'block','pid':22,'instance':'foreign','result':{}}))
        with self.assertRaisesRegex(RuntimeError,'WRITER_RPC_ASSOCIATION'): lab.rpc('block')

    def api(self, executable='C:/Python/python.exe', ticks=None):
        api=Mock(); api.OpenProcess.return_value=77
        if ticks is None: ticks=int((1000+11644473600)*10000000)
        def times(handle,created,*args):
            created._obj.dwHighDateTime=ticks>>32; created._obj.dwLowDateTime=ticks&0xffffffff; return 1
        def image(handle,flags,buf,size): buf.value=executable; return 1
        api.GetProcessTimes.side_effect=times; api.QueryFullProcessImageNameW.side_effect=image
        api.WaitForSingleObject.return_value=0; return api

    def test_native_handle_is_retained_across_exit_not_reopened_by_pid(self):
        api=self.api()
        with patch.object(p.os,'name','nt'),patch.object(p.ctypes,'WinDLL',return_value=api,create=True),patch.object(p.time,'time',return_value=1001):
            handle=p.WriterProcess(22,'C:/Python/python.exe',1000)
            self.assertEqual(handle.wait_exit(1),'EXITED'); handle.close()
        api.OpenProcess.assert_called_once_with(0x100000|0x1000,False,22)
        api.WaitForSingleObject.assert_called_once_with(77,1000); api.CloseHandle.assert_called_once_with(77)

    def test_native_wrong_executable_or_old_creation_cannot_claim_owned_pid(self):
        for api in (self.api('C:/other.exe'),self.api(ticks=int((900+11644473600)*10000000))):
            with patch.object(p.os,'name','nt'),patch.object(p.ctypes,'WinDLL',return_value=api,create=True),patch.object(p.time,'time',return_value=1001):
                with self.assertRaisesRegex(RuntimeError,'WRITER_'): p.WriterProcess(22,'C:/Python/python.exe',1000)
            api.CloseHandle.assert_called_once_with(77)

    def terminal_fixture(self, root):
        def save(name,obj): (root/name).write_text(json.dumps(obj))
        self.put=save
        save('acceptance.json',{'component_observed':True,'error':None,'status':'COMPONENT_RECONCILE_REQUIRED'})
        raw=[]
        for n in range(1,30):
            req={'correlation':str(n)}; response={'status':200}
            save('http-%03d.json'%n,{'request':req,'response':response})
            raw.append({'args':['kubectl','exec','X-Correlation-Id sys.argv[1]',json.dumps(req)],'returncode':0,'stdout':json.dumps(response)})
        exits=[]
        for n in (1,2):
            identity={'pid':n+20,'creation_ticks':123+n,'method':'WINDOWS_RETAINED_PROCESS_HANDLE','instance':str(n),'executable':'python'}
            save('writer-%d-identity.json'%n,identity); save('writer-%d.json'%n,{'pid':n+10,'at':1000})
            for op in (['hello','block'] if n==1 else ['hello','block','cleanup']):
                save('writer-%d-%s.json'%(n,op),dict(identity,ok=True,op=op))
            exit_row={'writer':identity,'launcher_pid':n+10,'rpc_exit':'EXITED','launcher_exit':0,'at':1001,'ended_at':1002}
            save('writer-%d-exit.json'%n,exit_row); exits.append(exit_row)
        save('cleanup.json',{'errors':[],'guard_failures':[],'writer_exit_proofs':exits})
        phases=[]; now=10
        for i,(name,budget) in enumerate(m.TTL_PHASES):
            phases.append({'phase':name,'at':1000+now-10,'monotonic':now,'deadline_monotonic':now+budget,'future_reserved_seconds':sum(s for _,s in m.TTL_PHASES[i+1:]),'expiry':1180})
            now+=budget-.01
        ended=1000+now-10
        save('ttl-phases.json',phases); save('ttl-phases-completed.json',{'at':ended,'monotonic':now,'expires_at':1180,'remaining_seconds':1180-ended})
        save('original-rule.json',{'created_at':1000,'expires_at':1180})
        return raw

    def test_terminal_verifier_accepts_complete_proofs_without_claiming_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); raw=self.terminal_fixture(root)
            self.assertEqual(len(v.terminal_checks(root,raw)),2)

    def test_raw_join_requires_record_in_correct_pod_not_just_join_artifact(self):
        record={'request_id':'r','status':403}
        raw=[{'args':['kubectl','logs','pod/old'],'returncode':0,'stdout':json.dumps(record)}]
        self.assertFalse(v.log_contains(raw,'new',record))
        raw.append({'args':['kubectl','logs','pod/new'],'returncode':0,'stdout':json.dumps(record)})
        self.assertTrue(v.log_contains(raw,'new',record))

    def test_terminal_verifier_vetoes_failure_guard_unknown_exit_and_missing_proof(self):
        mutations=[lambda root,raw:self.put('failure.json',{'reason':'MEMORY_STOP'}),
            lambda root,raw:self.put('cleanup.json',{'errors':[],'guard_failures':['MEMORY_STOP'],'writer_exit_proofs':[]}),
            lambda root,raw:raw[0].update(cancelled=True),
            lambda root,raw:raw[0].pop('returncode'),
            lambda root,raw:(root/'writer-2-exit.json').unlink(),
            lambda root,raw:self.put('writer-2-exit.json',{'rpc_exit':'ALIVE'}),
            lambda root,raw:raw.append(raw[0]),
            lambda root,raw:self.put('ttl-phases-completed.json',{'at':1181,'monotonic':191,'expires_at':1180,'remaining_seconds':-1})]
        for mutate in mutations:
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); raw=self.terminal_fixture(root); mutate(root,raw)
                with self.assertRaises((AssertionError,KeyError,FileNotFoundError)): v.terminal_checks(root,raw)

class DiagnosticChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.d=load('complete_diagnostic_test','client_diagnostic.py')
    def setUp(self):
        self.blocks=[patch.object(subprocess,name,side_effect=AssertionError('OFFLINE_NO_PROCESS')) for name in ('Popen','run')]
        self.blocks.append(patch.object(self.d.full,'measured_request',side_effect=AssertionError('OFFLINE_NO_HTTP')))
        for b in self.blocks: b.start()
    def tearDown(self):
        for b in reversed(self.blocks): b.stop()
    def test_no_approval_or_consumed_attempt_cannot_admit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with patch.object(self.d,'AUTH',root/'missing'),patch.object(self.d,'OUT',root):
                with self.assertRaises(FileNotFoundError): self.d.admission()
                (root/'started.json').write_text('{}')
                with self.assertRaisesRegex(RuntimeError,'ONE_ATTEMPT_ONLY'): self.d.admission()
    def test_diagnostic_rejects_second_http_writer_and_tcp(self):
        lab=self.d.Lab(); lab.fixture_http=1
        for call in (lambda:lab.http('a'),lab.start_worker,lambda:lab.isolation({})):
            with self.assertRaisesRegex(RuntimeError,'DIAGNOSTIC_'):call()
    def test_execute_without_approval_cannot_construct_lab(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(self.d.sys,'argv',['diagnostic','--execute']):
            with patch.object(self.d,'AUTH',Path(tmp)/'missing'),patch.object(self.d,'OUT',Path(tmp)),patch.object(self.d,'Lab') as constructor:
                with self.assertRaises(FileNotFoundError):self.d.main()
                constructor.assert_not_called()
    def test_stage_deltas_expose_stall_and_missing_counters(self):
        text=''
        for name,at,total in [('interpreter',1,0),('imports',3,700000)]:
            text+='ZER46_STAGE '+name+' '+str(at)+'\n'
            for filename,value in [('memory.pressure','some avg10=1.00 total='+str(total)+'\n'),('cpu.stat','throttled_usec '+str(total//2)+'\n'),('memory.events','max 0\noom_kill 0\n')]:
                text+='ZER46_COUNTER '+name+' '+filename+' '+repr(value)+'\n'
        rows=self.d.phase_deltas(text)
        self.assertEqual(rows[0]['elapsed_seconds'],2)
        self.assertEqual(rows[0]['memory_some_stall_us'],700000)
        self.assertEqual(rows[0]['cpu_throttled_us'],350000)
        self.assertEqual(rows[0]['oom_kill'],0)
        self.assertIsNone(self.d.phase_deltas('ZER46_STAGE interpreter 1\nZER46_STAGE imports 3\n')[0]['memory_some_stall_us'])
    def test_missing_or_cancelled_receipt_is_inconclusive_never_ac_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'raw').mkdir()
            (root/'raw/0001.json').write_text(json.dumps({'args':['kubectl','exec','X-Correlation-Id sys.argv[1]','{}'],'cancelled':True,'stderr':'ZER46_STAGE interpreter 1\n'}))
            with patch.object(self.d,'OUT',root): row=self.d.summarize('MEMORY_STOP',{'component_resource_verdict':'CLEAN','guard_failures':['MEMORY_STOP']})
            self.assertEqual(row['status'],'STOP_OR_INCONCLUSIVE'); self.assertFalse(row['ac_pass'])
            self.assertFalse(row['root_cause_proven']); self.assertEqual(row['client_stages'][0]['http_result'],'UNKNOWN')

if __name__=='__main__': unittest.main()
