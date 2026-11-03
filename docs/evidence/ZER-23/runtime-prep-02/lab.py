"""ZER-23 native integration using the reviewed isolation/resource/cleanup supervisor."""
import asyncio
from datetime import datetime
import importlib.util
import json
import os
import sys
import time
import uuid
import run as supervisor
ROOT,PREP,OUT=supervisor.ROOT,supervisor.PREP,supervisor.OUT
sys.path.insert(0,str(ROOT/'agent-orchestrator'))
sys.path.append(str(ROOT/'docs/evidence/ZER-51/runtime-prep-03'))
spec=importlib.util.spec_from_file_location('zer23_pilot',ROOT/'docs/evidence/ZER-51/runtime-prep-03/lab.py')
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)
from event_pipeline.llm import Adapter,HttpxTransport,Limits,RunBudget
from event_pipeline.sqli_handoff import Handoff
from gaia.diagnosis import Diagnoser
from gaia.sqli_observer import observe_worker
from hephaestus.recovery import Healer,Journal
from hephaestus.sqli_pipeline import SqliPipeline,verify_benign_probe
from nemesis.command_guard import CommandGuard
from nemesis.session import Session,SessionLimits,PURPOSE


pilot_factory=pilot.make_lab


def make_lab():
    parent=pilot_factory()
    class Lab(type(parent)):
        def __init__(self):
            super().__init__()
            self.context['method_version']='zer23-sqli-integration/1'
            self.topics.append(self.prefix+'.observations')
            self.deadline=time.monotonic()+900;self.work_end=self.deadline-20

        def save(self,name,value):
            if name=='worker-transport-command.json' and '/current/handoff.py' in value.get('args',[]):
                name='handoff-transport-command.json'
            return super().save(name,value)

        async def probe(self,result=None):
            self.control_probe_started=time.time()
            return await super().probe(result)

        async def exchange(self,packet):
            self.save('handoff-send-intent.json',packet)
            def native():
                self.check_sources();self.pod()
                result=self.input_command(['kubectl','--context','k3d-zero-door','--request-timeout=25s',
                  '-n','zd-sqli-lab','exec','-i','zer46-source-a','-c','zer21-transport','--','python','-B',
                  '/current/handoff.py','--topic',self.topics[2]],json.dumps(packet,allow_nan=False).encode(),timeout=27)
                self.check_sources();self.pod()
                value=json.loads(result.stdout);self.save('handoff-native-receipt.json',value)
                return value
            task=asyncio.create_task(asyncio.to_thread(native))
            try:return await asyncio.shield(task)
            except asyncio.CancelledError:
                await task
                raise

        async def observe_worker(self,receipt):
            await super().observe_worker(receipt)
            native=json.loads((OUT/'worker-native-join.json').read_bytes())
            observed=observe_worker(self.context,receipt,native['raw_access'],fixture_uid=self.fixture_uid,
              pod_uid=native['pod_uid'],source_ip=self.addresses['a'],proxy_ip=self.addresses['proxy'],
              begin=self.worker_window[0],end=self.worker_window[1],at=time.time(),ref='worker-native-join.json')
            self.save('gaia-native-observation.json',observed)
            return observed

        async def cases(self):
            budget=RunBudget(self.run_id,max_calls=3 if supervisor.CASE=='SQLI' else 2,
              max_reserved_tokens=30000,max_estimated_usd=.015,duration_s=300)
            adapter=Adapter(HttpxTransport(os.environ['OPENAI_API_KEY']),budget,
              limits=Limits(attempts=1,timeout_s=20,deadline_s=25,retry_delay_s=0,max_output_tokens=256))
            output=OUT/'pipeline';output.mkdir();journal=Journal(output,self.context)
            api=connection=None
            try:
                async def health():
                    baseline=json.loads((OUT/'http-001.json').read_bytes())
                    if baseline['response']['status']!=200 or time.time()-baseline['response']['end']>60:
                        raise ValueError('HEALTH_BASELINE_STALE')
                    return {'observed_at':datetime.fromtimestamp(baseline['response']['end']).astimezone().isoformat(),
                      'evidence':[{'id':'ev-health-01','health':'HEALTHY'}]}
                if supervisor.CASE=='CANCEL':
                    entered=asyncio.Event()
                    async def wait_observation():entered.set();await asyncio.Event().wait()
                    session=Session(purpose=PURPOSE,guard=CommandGuard(self.command_policy),adapter=adapter,
                      observe=wait_observation,execute=self.execute_worker,context=self.context,
                      limits=SessionLimits(max_rounds=1,duration_s=90,command_s=1,required_rounds=1,
                        allowed_templates=('disclose-restricted',)))
                    task=session.start();await entered.wait();task.cancel()
                    try:receipt=await task
                    except asyncio.CancelledError:receipt={'stop_reason':'CANCELLED_PROPAGATED'}
                    self.save('cancel-receipt.json',receipt)
                    if not receipt['stop_reason'].startswith('CANCELLED') or budget.calls or self.fixture_http!=1:
                        raise ValueError('CANCEL_NOT_CLEAN')
                    return
                if supervisor.CASE=='SQLI':
                    session=Session(purpose=PURPOSE,guard=CommandGuard(self.command_policy),adapter=adapter,
                      observe=health,execute=self.execute_worker,context=self.context,
                      limits=SessionLimits(max_rounds=1,duration_s=90,command_s=1,required_rounds=1,
                        allowed_templates=('disclose-restricted',)))
                    receipt=await session.start();self.save('nemesis-receipt.json',receipt)
                    if receipt['completed_rounds']!=1 or receipt['stop_reason']!='MAX_ROUNDS':
                        raise ValueError('NEMESIS_NOT_COMPLETED')
                else:
                    command=CommandGuard(self.command_policy).sqli_command(
                      {'attackType':'SQLI','template':'benign-apparel','durationSec':1},str(uuid.uuid4()))
                    result=await self.execute_worker(command)
                    receipt={'records':[{'event':'DISPATCH_INTENT','command':command},{'event':'EXECUTOR_RESULT','raw':result}]}
                    self.save('locked-benign-receipt.json',receipt)
                observed=await self.observe_worker(receipt)
                before_policy=self.cm()
                api,connection=self.native_api()
                gaia=Diagnoser(adapter,self.context,lambda event:journal({'kind':'GAIA_EVENT','event':event}))
                healer=Healer(adapter,self.context,api=api,pins=self.target_pins,fixture_uid=self.fixture_uid,
                              journal=journal,probe=self.probe,ttl_sec=180,probe_timeout_s=120)
                handoff=Handoff(os.urandom(32),self.context,OUT/'handoff-claim.json')
                flow=SqliPipeline(gaia,healer,handoff,self.exchange,journal)
                result=await flow.run(observed);self.save('pipeline-receipt.json',result)
                if self.fixture_http==2:self.last_probe=await self.probe()
                if supervisor.CASE=='SQLI':
                    if result.get('healer',{}).get('status')!='ACTION_COMPLETED':
                        raise ValueError('SQLI_CONTAINMENT_NOT_MET')
                else:
                    if api.writes!=0 or self.cm()!=before_policy:raise ValueError('BENIGN_POLICY_CHANGED')
                    verdict=verify_benign_probe(self.last_probe,fixture_uid=self.fixture_uid,
                      attacker_ip=self.addresses['a'],benign_ip=self.addresses['b'],proxy_ip=self.addresses['proxy'],
                      not_before=self.control_probe_started,at=time.time())
                    self.save('benign-probe-verdict.json',verdict)
                if self.fixture_http!=8 or self.tcp_checks!=2:raise ValueError('PROBE_BUDGET')
                self.save('functional-observed.json',{'status':'OBSERVED_PENDING_REVIEW',
                  'case':supervisor.CASE,'fixture_http_reserved_or_dispatched':self.fixture_http,
                  'tcp_checks':self.tcp_checks,'api_replace_attempts':api.writes,'model_budget':budget.summary(),
                  'benchmark_eligible':False,'boutique_recovery_verified':False})
            finally:
                self.save('model-budget.json',budget.summary());journal.close()
                if connection is not None:connection.close()
    return Lab()


def main():
    pilot.make_lab=make_lab
    return pilot.main()


if __name__=='__main__':raise SystemExit(main())
