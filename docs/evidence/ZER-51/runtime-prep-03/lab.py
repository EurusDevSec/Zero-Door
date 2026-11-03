"""Six-cell native SQLi/C0 pilot; all entry/cleanup gates retained from reviewed runner."""
import asyncio
import argparse
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time
import threading
import uuid

import run as supervisor
ROOT,PREP,OUT=supervisor.ROOT,supervisor.PREP,supervisor.OUT
sys.path.append(str(ROOT/"docs/evidence/ZER-21/runtime-prep-07"))
spec=importlib.util.spec_from_file_location('zer51_linked_fixture',ROOT/'docs/evidence/ZER-21/runtime-prep-07/lab.py')
linked=importlib.util.module_from_spec(spec);spec.loader.exec_module(linked)
from event_pipeline.contract import canonical,new_id
from event_pipeline.llm import Adapter,HttpxTransport,Limits,RunBudget
from gaia.diagnosis import Diagnoser
from hephaestus.recovery import Healer,Journal
from hephaestus.sqli_containment import NAMESPACE
from nemesis.command_guard import CommandGuard
from pilot import SCHEDULE,VERSION,RulesController,BaselineJournal,evidence_hash,invariant_evidence,score,template
kube_config_pin=linked.kube_config_pin


def make_lab():
    parent=linked.make_lab()
    class PilotLab(type(parent)):
        def __init__(self):
            super().__init__()
            if supervisor.INDEX is None:raise ValueError('TRIAL_INDEX_REQUIRED')
            self.group,self.case=SCHEDULE[supervisor.INDEX]
            self.context.update(group=self.group,method_version=VERSION)
            self.deadline=time.monotonic()+600;self.work_end=self.deadline-20
            self.last_probe=None
            self.watch_shutdown=threading.Event()

        def watch(self):
            due, snapshot_due = time.monotonic()+5, time.monotonic()+15
            while not self.stop.is_set() and not self.watch_shutdown.is_set():
                remaining=due-time.monotonic()
                if remaining>0:
                    self.watch_shutdown.wait(min(.2,remaining))
                    continue
                try:
                    self.resources()
                    if time.monotonic()>=snapshot_due:
                        observed=self.snapshot("watch-latest")
                        self.private_restarts(observed)
                        current=self.shared(observed)
                        if self.specs(current)!=self.specs(self.before) or self.restarts(current)!=self.restarts(self.before):
                            raise RuntimeError("SHARED_INVENTORY_DRIFT")
                        snapshot_due+=15
                except Exception as error:
                    # Genuine resource/deadline/identity errors still fail, even during shutdown.
                    self.failure.append(str(error));self.stop.set();self.capture_guard_stop()
                due+=5

        def finish_watch(self):
            # Signal normal watcher shutdown separately; keep the real guard stop clear
            # until the in-flight native read has drained. Never suppress its exceptions.
            self.watch_shutdown.set()
            if hasattr(self,"thread"):
                self.thread.join(timeout=20)
                if self.thread.is_alive():self.failure.append("WATCHER_SHUTDOWN_TIMEOUT")
            self.stop.set()

        def snapshot(self,label):
            result=super().snapshot(label)
            if label in {'before','after'}:
                raw=json.loads(self.kube('get','hpa','-A','-o','json').stdout)
                profile={x['metadata']['namespace']+'/'+x['metadata']['name']:
                    {'uid':x['metadata']['uid'],'spec':x['spec']} for x in raw['items']}
                self.save(label+'-hpa.json',profile)
                if label=='before' and any(k.startswith('zd-sqli-lab/') for k in profile):
                    raise ValueError('UNEXPECTED_FIXTURE_HPA')
                if label=='after' and profile!=json.loads((OUT/'before-hpa.json').read_bytes()):
                    raise ValueError('HPA_PROFILE_DRIFT')
            return result

        def native_api(self):
            if self.group=='B0':raise ValueError('B0_NO_HEAL_API')
            return super().native_api()

        def execute(self):
            supervisor.verify_sources()
            if self.context["group"] == "B2" and not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("PROVIDER_KEY_MISSING")
            # Verify endpoint and auth before kubectl or any dynamic credential/plugin invocation.
            kube_config_pin()
            if self.command(["git", "rev-parse", "HEAD"]).stdout.decode().strip() != supervisor.HEAD:
                raise ValueError("HEAD_DRIFT")
            if self.command(["docker", "context", "show"]).stdout.decode().strip() != "desktop-linux":
                raise ValueError("DOCKER_CONTEXT")
            nodes = json.loads(self.kube("get", "nodes", "-o", "json").stdout)["items"]
            if ({n["metadata"]["name"] for n in nodes} != {"k3d-zero-door-server-0", self.node}
                    or any(not any(c["type"] == "Ready" and c["status"] == "True"
                        for c in n["status"]["conditions"]) for n in nodes)):
                raise ValueError("NODE_PROFILE")
            if self.kube("get", "namespace", NAMESPACE, "--ignore-not-found", "-o", "name").stdout.strip():
                raise ValueError("NAMESPACE_ALREADY_EXISTS")
            self.before = self.snapshot("before")
            deployments = [x for x in self.before["items"] if x["kind"] == "Deployment"]
            target = [x for x in deployments if x["metadata"]["namespace"] == "target-app"]
            expected = {"cartservice", "checkoutservice", "currencyservice", "emailservice", "frontend",
                        "paymentservice", "productcatalogservice", "redis-cart", "shippingservice"}
            if ({x["metadata"]["name"] for x in target} != expected or any(x["spec"]["replicas"] != 1
                    or x.get("status", {}).get("availableReplicas", 0) != 1 for x in target)
                    or any(x["spec"]["replicas"] != 0 for x in deployments if x["metadata"]["namespace"] == "zero-door")):
                raise ValueError("SHARED_PROFILE_OR_READINESS")
            cart = next(x for x in target if x["metadata"]["name"] == "cartservice")
            server = next(x for x in cart["spec"]["template"]["spec"]["containers"] if x["name"] == "server")
            if any(server[p].get("timeoutSeconds") != 3 for p in ("livenessProbe", "readinessProbe")):
                raise ValueError("CART_PROBE_BASELINE_NOT_PREPARED")
            pvcs = [x for x in self.before["items"] if x["kind"] == "PersistentVolumeClaim"]
            if len(pvcs) != 3 or any(x.get("status", {}).get("phase") != "Bound" for x in pvcs):
                raise ValueError("PVC_PROFILE")
            start = time.monotonic()
            for i in range(25):
                self.wait(start + i * 5); self.resources()
            self.thread = threading.Thread(target=self.watch, daemon=True); self.thread.start()
            self.ensure_cache()  # Cached agent-node driver overrides build/import/pull.
            after = self.snapshot("after-preflight")
            if self.specs(after) != self.specs(self.before) or self.restarts(after) != self.restarts(self.before):
                raise ValueError("PREFLIGHT_DRIFT")
            self.save("preflight.json", {"status": "GATE_PASSED", "resource_samples": len(self.samples)})


        async def probe(self, result=None):
            self.action = result["rule"]["action_id"] if result else None
            self.probe_end = time.monotonic() + 115
            def collect():
                # Read-only projection wait precedes six sequential functional requests.
                self.wait_projection(self.cm(), seconds=85)
                a = self.row("a")
                b = [self.row("b")]
                nonce = uuid.uuid4().hex
                b.append(self.row("b", path="/fixture/orders", method="POST",
                    body={"item": "benign-lab-item", "note": nonce}))
                ref = b[-1]["http"]["response"]["body"]["order_ref"]
                if not re.fullmatch(r"[a-f0-9]{32}", ref):
                    raise ValueError("ORDER_REF")
                for method in ("GET", "DELETE", "GET"):
                    b.append(self.row("b", path="/fixture/orders/" + ref, method=method))
                pod = self.pod()
                ready = any(c["type"] == "Ready" and c["status"] == "True" for c in pod["status"]["conditions"])
                proof = {"attacker": a, "benign": b, "fixture": {"uid": pod["metadata"]["uid"], "ready": ready}}
                self.last_probe = proof
                self.save("postcondition-probe.json", proof)
                return proof
            task = asyncio.create_task(asyncio.to_thread(collect))
            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                await task  # Drain owned native operations; outer Job still supplies hard bound.
                raise
            finally:
                self.probe_end = None


        async def cases(self):
            # The operator replay plan is fixed before launch, not selected by the treatment.
            command=CommandGuard(self.command_policy).sqli_command(
                {'attackType':'SQLI','template':template(self.case),'durationSec':1},str(uuid.uuid4()))
            self.save('locked-command.json',{'plan_version':VERSION,'decision_source':'LOCKED_OPERATOR_PLAN','command':command})
            result=await self.execute_worker(command)
            receipt={'purpose':'LOCKED_WORKLOAD_NATIVE_REPLAY','records':[
                {'event':'DISPATCH_INTENT','command':command},{'event':'EXECUTOR_RESULT','raw':result}]}
            self.save('locked-worker-receipt.json',receipt)
            observed=await self.observe_worker(receipt)
            self.save('observer-input.json',observed)
            before=self.cm()
            budget=RunBudget(self.run_id,max_calls=2,max_reserved_tokens=15000,max_estimated_usd=.01,duration_s=300)
            output=OUT/'decisions';output.mkdir()
            journal=(BaselineJournal if self.group=='B0' else Journal)(output,self.context)
            api=connection=None;diagnosis=None;healer=None
            started=time.monotonic()
            try:
                if self.group=='B0':
                    if os.environ.get('OPENAI_API_KEY'):raise ValueError('B0_PROVIDER_KEY_PRESENT')
                    receipt={'status':'BASELINE_NO_DECIDER','decision_source':'NONE','plan':None,'model_events':[],
                        'fallback':False,'provider_calls':0,'action_id':None,'decision_latency_ms':None}
                    journal({'kind':'BASELINE_OBSERVATION','detection':observed['detection'],'access':observed['access'],
                        'automatic_decision':False,'automatic_heal':False})
                elif self.group=='B1':
                    if os.environ.get('OPENAI_API_KEY'):raise ValueError('B1_PROVIDER_KEY_PRESENT')
                    api,connection=self.native_api()
                    healer=RulesController(self.context,api=api,pins=self.target_pins,fixture_uid=self.fixture_uid,
                        journal=journal,probe=self.probe,budget=budget)
                    receipt=await healer.run(observed['detection'],observed['access'])
                else:
                    adapter=Adapter(HttpxTransport(os.environ['OPENAI_API_KEY']),budget,
                        limits=Limits(attempts=1,timeout_s=20,deadline_s=25,retry_delay_s=0,max_output_tokens=256))
                    diagnosis=await Diagnoser(adapter,self.context,lambda event:journal({'kind':'GAIA_EVENT','event':event})).analyze(
                        observed['detection'],observed['evidence'])
                    self.save('gaia-receipt.json',diagnosis)
                    api,connection=self.native_api()
                    healer=Healer(adapter,self.context,api=api,pins=self.target_pins,fixture_uid=self.fixture_uid,
                        journal=journal,probe=self.probe,ttl_sec=180,probe_timeout_s=120)
                    if (diagnosis['status']=='OK' and diagnosis['decision_source']=='LLM' and not diagnosis['fallback']
                            and diagnosis['budget']['cost_estimate_complete'] and not diagnosis['budget']['blocked']):
                        receipt=await healer.run(observed['detection'],observed['access'])
                    else:
                        receipt={'status':'NOT_RUN_GAIA_FAILURE','reason':diagnosis.get('reason'),
                            'decision_source':'NONE','fallback':True,'plan':None,'model_events':[],
                            'decision_latency_ms':None,'action_id':None}
                decision_elapsed_ms=(time.monotonic()-started)*1000
                self.save('decision-receipt.json',receipt)
                # Same six native probes even for no action. Never repeat a partially executed probe.
                if self.fixture_http==2:self.last_probe=await self.probe()
                if self.last_probe is None:
                    self.save('probe-incomplete.json',{'reason':'PARTIAL_OR_UNKNOWN','http_consumed':self.fixture_http})
                after=self.cm()
                if self.group=='B0' or not healer or not healer.dispatched:
                    if before!=after:raise ValueError('UNEXPECTED_POLICY_MUTATION')
                profile={'shared_specs_sha256':__import__('hashlib').sha256(canonical(self.specs(self.before))).hexdigest(),
                    'hpa_sha256':supervisor.sha(OUT/'before-hpa.json'),'fixture_hpa':'OFF','seed_sha256':supervisor.sha(ROOT/'services/sqli-fixture/seed.json'),
                    'template':template(self.case),'duration_s':1,'concurrency':1,'rps':1,'max_sends':1,
                    'guard':'Healer.observation+Healer.action_guard+ModeGate+SqliContainment',
                    'probe':'shared 6HTTP source+order cycle','ttl_s':180,'probe_timeout_s':120}
                row={'group':self.group,'case':self.case,'context':self.context,'observation_invariant_sha256':evidence_hash(observed),
                    'observation_invariants':invariant_evidence(observed),'identity_envelopes_byte_identical':False,
                    'workload_profile':profile,'decision':receipt,'gaia':diagnosis,
                    'decision_elapsed_ms':decision_elapsed_ms,'model_budget':budget.summary(),
                    'api_replace_attempts':api.writes if api else 0,'http_reserved_or_dispatched':self.fixture_http,
                    'metrics':score(self.group,self.case,receipt,self.last_probe),
                    'safety_or_protocol_failure':False,'benchmark_eligible':False}
                self.save('pilot-cell.json',row)
                self.save('functional-observed.json',{'status':'OBSERVED_PENDING_REVIEW','api_replace_attempts':row['api_replace_attempts'],
                    'fixture_http_reserved_or_dispatched':self.fixture_http,'tcp_checks':self.tcp_checks,
                    'model_budget':budget.summary(),'runtime_ac_verified':False,'recovery_verified':False,'benchmark_eligible':False})
            finally:
                self.save('model-budget.json',budget.summary());journal.close()
                if connection is not None:connection.close()
    return PilotLab()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--work",action="store_true");group.add_argument("--cleanup",action="store_true")
    args=parser.parse_args()
    if sys.stdin.buffer.readline(4)!=b"GO\n":raise ValueError("SUPERVISOR_GATE_REQUIRED")
    if args.work:linked.claim_work()
    supervisor.verify_sources();kube_config_pin();lab=make_lab()
    if args.cleanup:return 0 if lab.cleanup_owned()["verdict"]=="CLEAN" else 1
    error=None
    try:lab.execute();lab.component()
    except BaseException as failure:
        error=type(failure).__name__+":"+str(failure) if isinstance(failure,ValueError) else type(failure).__name__
    finally:
        lab.finish_watch()
        if lab.failure:error=error or "RESOURCE_OR_SHARED_GUARD"
        path=OUT/"model-budget.json";budget=json.loads(path.read_bytes()) if path.exists() else None
        lab.save("work-result.json",{"status":"NOT_MET" if error else "OBSERVED_PENDING_REVIEW",
            "error":error,"guard_failures":lab.failure,"provider_calls":budget["attempts_dispatched"] if budget else 0,
            "fixture_http":lab.fixture_http,"tcp_checks":lab.tcp_checks,"benchmark_eligible":False})
    return 1 if error else 0

if __name__=="__main__":raise SystemExit(main())
