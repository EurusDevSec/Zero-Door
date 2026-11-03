"""Runner admission/render/cancel and Kafka boundary tests; no lab/provider calls."""
import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
PREP=Path(__file__).resolve().parent
sys.path.insert(0,str(PREP));os.environ['ZD23_CASE']='SQLI'
with patch.object(platform,'system',return_value='Windows'):
    import run,lab,render,kafka_handoff
from event_pipeline.contract import canonical


class Runtime(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        for target,name in [(socket.socket,'connect'),(subprocess,'Popen')]:
            mock=patch.object(target,name,side_effect=AssertionError('OFFLINE_ONLY'))
            mock.start();self.addCleanup(mock.stop)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)

    def fixture(self):
        with patch.object(run,'sha',return_value='1'*64),patch.object(platform,'system',return_value='Windows'):
            native=lab.make_lab()
        docs,containers,volumes,policy=render.worker_documents(native.context,native.owner,'10.43.0.11')
        native.command_policy=policy
        return native,docs,containers,volumes

    def test_factory_context_three_topics_and_handoff_mount(self):
        native,docs,containers,volumes=self.fixture()
        self.assertEqual('B2',native.context['group']);self.assertEqual(3,len(set(native.topics)))
        source=next(d for d in docs if d['metadata']['name']=='zer21-transport-source')
        self.assertIn('handoff.py',source['data'])
        mount=next(v for v in volumes if v['name']=='zer21-source')
        self.assertIn({'key':'handoff.py','path':'handoff.py'},mount['configMap']['items'])
        self.assertFalse(any(e['name']=='OPENAI_API_KEY' for c in containers for e in c.get('env',[])))

    async def test_real_session_cancellation_before_model_and_worker(self):
        native,*_=self.fixture();native.fixture_http=1;native.tcp_checks=2
        saved={}
        with patch.object(run,'CASE','CANCEL'),patch.object(lab,'OUT',Path(self.tmp.name)),             patch.object(lab,'HttpxTransport',return_value=object()),             patch.dict(os.environ,{'OPENAI_API_KEY':'OFFLINE_PLACEHOLDER'}),             patch.object(native,'save',side_effect=lambda name,value:saved.update({name:deepcopy(value)})),             patch.object(native,'execute_worker',side_effect=AssertionError('NO_EXECUTOR')):
            await asyncio.wait_for(native.cases(),2)
        self.assertTrue(saved['cancel-receipt.json']['stop_reason'].startswith('CANCELLED'))
        self.assertEqual(0,saved['model-budget.json']['attempts_dispatched'])
        self.assertEqual(1,native.fixture_http)

    def test_worker_and_handoff_native_receipts_stay_separate(self):
        native,*_=self.fixture()
        base=type(native).__mro__[1]
        with patch.object(base,'save') as sink:
            native.save('worker-transport-command.json',{'args':['python','/current/remote.py']})
            native.save('worker-transport-command.json',{'args':['python','/current/handoff.py']})
        self.assertEqual(['worker-transport-command.json','handoff-transport-command.json'],
                         [c.args[0] for c in sink.call_args_list])

    def test_default_plan_and_invalid_authorization_never_spawn(self):
        with patch.object(sys,'argv',['run.py']),patch.object(run,'execute',side_effect=AssertionError('NO_WORK')):
            self.assertEqual(0,run.main())
        path=Path(self.tmp.name)/'auth.json';path.write_text(json.dumps({'approved':False}))
        with self.assertRaises(ValueError):run.admit(path)

    def test_actual_kafka_exchange_joins_one_record_and_claims_before_send(self):
        context={'run_id':'run_'+'1'*32}
        topic='zer19-'+context['run_id'][4:16]+'.observations';packet={'payload':{'native':'offline'},'mac':'offline'}
        calls=[]
        class Consumer:
            def __init__(self,**kw):self.topic=None;calls.append(('consumer',kw))
            def assign(self,rows):self.tp=rows[0];self.topic=self.tp.topic
            def beginning_offsets(self,rows):return {self.tp:0}
            def end_offsets(self,rows):return {self.tp:0}
            def seek(self,*a):pass
            def poll(self,**kw):return {self.tp:[SimpleNamespace(topic=topic,partition=0,offset=0,value=canonical(packet))]}
            def close(self,**kw):calls.append(('consumer_closed',kw))
        class Producer:
            def __init__(self,**kw):calls.append(('producer',kw))
            def send(self,name,value,partition):
                self.assertion=(name,value,partition);calls.append(('send',name))
                return SimpleNamespace(get=lambda timeout:SimpleNamespace(topic=topic,partition=0,offset=0))
            def close(self,**kw):calls.append(('producer_closed',kw))
        claim=Path(self.tmp.name)/'claim'
        with patch.object(kafka_handoff.CommandGuard,'from_env',return_value=SimpleNamespace(policy={'context':context})),             patch.object(kafka_handoff,'Path',return_value=claim):
            result=kafka_handoff.exchange(packet,topic,producer_factory=Producer,consumer_factory=Consumer)
            self.assertEqual(packet,result['packet']);self.assertEqual(0,result['transport']['consumed_offset'])
            with self.assertRaises(FileExistsError):
                kafka_handoff.exchange(packet,topic,producer_factory=Producer,consumer_factory=Consumer)
            with self.assertRaises(ValueError):
                kafka_handoff.exchange(packet,'foreign',producer_factory=Producer,consumer_factory=Consumer)
        self.assertEqual(1,len([r for r in calls if r[0]=='send']))
        self.assertIn(('consumer_closed',{'autocommit':False}),calls)


if __name__=='__main__':unittest.main()
