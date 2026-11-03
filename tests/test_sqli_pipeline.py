"""Real pipeline components; fake provider/Kafka/API, all outbound sockets denied."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent-orchestrator"))
from event_pipeline.sqli_handoff import Handoff
from event_pipeline.contract import canonical
from gaia.diagnosis import Diagnoser
from hephaestus.sqli_pipeline import SqliPipeline,verify_benign_probe
import test_hephaestus_recovery as recovery


class Model(recovery.Model):
    async def send(self,payload,timeout):
        observation=json.loads(payload["input"])
        if set(observation)!={"detection","evidence"}:
            return await super().send(payload,timeout)
        self.requests.append(deepcopy(payload))
        value={"classification":"NORMAL" if observation["detection"]["payload"]["value"]==0 else "SUSPICIOUS_ACTIVITY",
               "summary":"Observed native access", "confidence":0.9,
               "evidence_ids":[observation["detection"]["event_id"]]}
        if self.mode=="UNKNOWN":value["classification"]="UNKNOWN"
        return {"status":200,"request_id":"offline-gaia", "body":{"id":"resp_offline_gaia",
          "model":recovery.MODEL,"status":"completed","output":[{"type":"message","role":"assistant",
          "status":"completed","content":[{"type":"output_text","text":json.dumps(value)}]}],
          "usage":{"input_tokens":100,"output_tokens":40,"total_tokens":140}}}


class Pipeline(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.fixture=recovery.Recovery()
        self.fixture.setUp()
        self.native=patch.object(subprocess,'Popen',side_effect=AssertionError('OFFLINE_ONLY'))
        self.native.start();self.addCleanup(self.native.stop)
        self.healer=self.fixture.engine()
        self._cleanups.extend(self.fixture._cleanups)
        self.fixture._cleanups.clear()
        self.model=Model()
        self.healer.adapter.transport=self.model
        self.ctx=self.fixture.ctx
        self.observed={"detection":self.fixture.detected,"access":self.fixture.access,
          "evidence":{"metric":{"name":"log_pattern_match","value":1,"threshold":0},
                      "log":{"message":"Native observed disclosure","observed_at":None}}}
        self.codec=Handoff(b'x'*32,self.ctx,Path(self.fixture.tmp.name)/'claim.json',clock=lambda:self.fixture.wall)
        self.events=[]
        self.sent=[]

    async def exchange(self,packet):
        self.sent.append(deepcopy(packet))
        return {"packet":deepcopy(packet),"transport":{"kind":"KAFKA","topic":"zer19-"+self.ctx['run_id'][4:16]+".observations",
          "partition":0,"offset":0,"consumed_topic":"zer19-"+self.ctx['run_id'][4:16]+".observations","consumed_partition":0,"consumed_offset":0,"received_count":1}}

    def pipeline(self,exchange=None):
        gaia=Diagnoser(self.healer.adapter,self.ctx,self.events.append)
        return SqliPipeline(gaia,self.healer,self.codec,exchange or self.exchange,self.events.append)

    async def test_native_effect_transport_action_probe(self):
        flow=self.pipeline()
        result=await flow.run(self.observed)
        self.assertEqual('ACTION_COMPLETED',result['healer']['status'])
        self.assertEqual(1,len(self.sent));self.assertEqual(1,self.fixture.api.writes)
        self.assertTrue((Path(self.fixture.tmp.name)/'claim.json').exists())
        self.assertLess(next(i for i,x in enumerate(self.events) if x['kind']=='HANDOFF_RECEIVED'),
                        next(i for i,x in enumerate(self.events) if x['kind']=='PIPELINE_HEALER'))
        with self.assertRaisesRegex(ValueError,'ALREADY_STARTED'):await flow.run(self.observed)

    async def test_benign_no_action_keeps_policy(self):
        self.model.mode='NO_ACTION'
        self.observed['access']['restricted_rows']=0
        self.observed['detection']['payload']['value']=0
        self.observed['evidence']['metric']['value']=0
        result=await self.pipeline().run(self.observed)
        self.assertEqual('NO_ACTION',result['healer']['status']);self.assertEqual(0,self.fixture.api.writes)
        self.assertEqual(1,len(self.sent))

    async def test_gaia_abstain_retained_no_transport_or_heal(self):
        self.model.mode='UNKNOWN'
        result=await self.pipeline().run(self.observed)
        self.assertEqual('NOT_RUN_GAIA',result['status']);self.assertEqual('ABSTAIN',result['diagnosis']['status'])
        self.assertEqual([],self.sent);self.assertEqual(0,self.fixture.api.writes)

    async def test_transport_failure_never_direct_dispatch(self):
        async def fail(packet):raise TimeoutError('offline broker unavailable')
        with self.assertRaises(TimeoutError):await self.pipeline(fail).run(self.observed)
        self.assertEqual(0,self.fixture.api.writes);self.assertFalse(self.healer.started)
        with self.assertRaisesRegex(ValueError,'ALREADY_SENT'):self.codec.seal(self.observed)

    async def test_mutated_packet_never_reaches_healer(self):
        async def mutate(packet):
            result=await self.exchange(packet)
            result['packet']['payload']['observation']['access']['client_ip']='10.42.0.99'
            return result
        with self.assertRaises(ValueError):await self.pipeline(mutate).run(self.observed)
        self.assertFalse(self.healer.started);self.assertEqual(0,self.fixture.api.writes)

    async def test_foreign_or_missing_broker_receipt_never_dispatches(self):
        async def wrong(packet):
            result=await self.exchange(packet);result['transport']['offset']=1
            return result
        with self.assertRaisesRegex(ValueError,'BROKER_RECEIPT'):await self.pipeline(wrong).run(self.observed)
        self.assertFalse(self.healer.started);self.assertEqual(0,self.fixture.api.writes)

    async def test_invalid_native_evidence_rejected_before_provider(self):
        self.observed['access']['fixture_uid']='foreign'
        with self.assertRaises(ValueError):await self.pipeline().run(self.observed)
        self.assertEqual([],self.model.requests);self.assertEqual([],self.sent)

    async def test_cancel_during_transport_no_action_no_retry(self):
        started=asyncio.Event()
        async def stalled(packet):started.set();await asyncio.Event().wait()
        flow=self.pipeline(stalled);task=asyncio.create_task(flow.run(self.observed))
        await started.wait();task.cancel()
        with self.assertRaises(asyncio.CancelledError):await task
        self.assertFalse(self.healer.started);self.assertEqual(0,self.fixture.api.writes)
        with self.assertRaises(ValueError):await flow.run(self.observed)

    def test_auth_wrong_key_context_expiry_and_restart_replay(self):
        packet=self.codec.seal(self.observed)
        other=Handoff(b'y'*32,self.ctx,Path(self.fixture.tmp.name)/'other',clock=lambda:1001)
        with self.assertRaisesRegex(ValueError,'AUTH'):other.receive(packet)
        tampered=deepcopy(packet);tampered['payload']['observation']['access']['client_ip']='foreign'
        with self.assertRaisesRegex(ValueError,'AUTH'):self.codec.receive(tampered)
        self.fixture.wall=1062
        with self.assertRaisesRegex(ValueError,'FRESHNESS'):self.codec.receive(packet)
        self.fixture.wall=1001
        self.assertEqual(canonical(self.observed),canonical(self.codec.receive(packet)))
        restarted=Handoff(b'x'*32,self.ctx,Path(self.fixture.tmp.name)/'claim.json',clock=lambda:1001)
        with self.assertRaises(FileExistsError):restarted.receive(packet)


class BenignProbe(unittest.TestCase):
    def fixture(self):
        rows=recovery.probes()
        rows[0]['http']['response'].update(status=200,body={'count':1})
        rows[0]['access'].update(status=200,blocked=False,action_ids=[])
        return {'attacker':rows[0],'benign':rows[1:],'fixture':{'uid':recovery.POD,'ready':True}}

    def check(self,proof):
        return verify_benign_probe(proof,fixture_uid=recovery.POD,
          attacker_ip=recovery.PINS['attacker_ip'],benign_ip=recovery.PINS['benign_ip'],
          proxy_ip='10.42.0.12',not_before=1001,at=1010)

    def test_native_control_cycle(self):self.assertEqual('PASS',self.check(self.fixture())['status'])

    def test_failures_in_ready_trace_status_and_content_are_retained(self):
        for mutate in [lambda p:p['fixture'].update(ready=False),
          lambda p:p['fixture'].update(uid='foreign'),
          lambda p:p['attacker']['http']['response'].update(status=403),
          lambda p:p['benign'][-1]['http']['response'].update(status=200),
          lambda p:p['benign'][-1]['http']['response'].update(body={'error':'wrong'}),
          lambda p:p['benign'][2]['http']['response']['body'].update(note='wrong'),
          lambda p:p['benign'][3]['http']['response'].update(body={'deleted':0}),
          lambda p:p['benign'][0]['access'].update(client_ip='foreign'),
          lambda p:p['benign'][0]['access'].update(request_id='a'*32),
          lambda p:p['benign'][0]['access'].update(ts=999),
          lambda p:p['benign'][0]['access'].update(policy_sha256='b'*64)]:
            proof=self.fixture();mutate(proof)
            with self.subTest(mutate=mutate),self.assertRaisesRegex(ValueError,'NOT_VERIFIED'):self.check(proof)


if __name__=='__main__':unittest.main()
