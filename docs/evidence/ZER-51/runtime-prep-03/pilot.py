"""Locked SQLi/C0 pilot policy and RULES controller; import has no effects."""
import asyncio
from copy import deepcopy
import hashlib
import time
from types import SimpleNamespace

from event_pipeline.contract import Producer, canonical, new_id, now
from hephaestus.command_guard import ModeGate
from hephaestus.recovery import Healer
from hephaestus.sqli_action_state import SqliActionState
from hephaestus.sqli_containment import SqliContainment

VERSION = 'zer51-pilot/1'
# Interleave case and treatment; one sample per cell, no statistical superiority claim.
SCHEDULE = (('B0','C0'),('B1','SQLI'),('B2','C0'),('B0','SQLI'),('B1','C0'),('B2','SQLI'))
CLOCK = {'clock_id':'host','clock_source':'UNKNOWN','resolution_ms':None}


def template(case):
    return {'C0':'benign-electronics','SQLI':'disclose-restricted'}[case]


def invariant_evidence(observed):
    """Compare observed facts across fresh native identities, never rewrite model input.

    Timestamps, run/request/event/Pod IDs and ephemeral IPs remain in raw observations.
    Group-specific runs cannot have byte-identical identity envelopes. Only these
    explicitly named operational values must match for paired B1/B2 comparability.
    """
    a=observed['access'];d=observed['detection']['payload']
    return {'detection':{k:d[k] for k in ('rule_id','rule_version','signature','metric','value','threshold','severity','description')},
            'access':{k:a[k] for k in ('method','path','status','rows','restricted_rows','delivered','source_method','source_confidence')},
            'source_role':'A','proxy_role':'trusted-private-proxy'}


def evidence_hash(observed):
    return hashlib.sha256(canonical(invariant_evidence(observed))).hexdigest()


def score(group,case,receipt,probe):
    """Ground truth is applied only after decision/effects; failures stay in denominator."""
    expected='NO_ACTION' if case=='C0' else 'BLOCK_IP'
    proposed=(receipt.get('plan') or {}).get('action')
    correct=None if group=='B0' else proposed==expected
    attacker=probe.get('attacker') if isinstance(probe,dict) else None
    benign=probe.get('benign',[]) if isinstance(probe,dict) else []
    business=(len(benign)==5 and [r['http']['response']['status'] for r in benign]==[200,201,200,200,404])
    state=receipt.get('action_state') or {};terminal=state.get('terminal') or {}
    condition=terminal.get('postcondition') or {}
    contained=bool(receipt.get('status')=='ACTION_COMPLETED'
        and state.get('phase')=='ACTION_COMPLETED' and terminal.get('status')=='SUCCESS'
        and condition.get('name')=='SQLI_SOURCE_CONTAINMENT'
        and condition.get('checked') is True and condition.get('satisfied') is True
        and receipt.get('action_id') and state.get('action_id')==receipt['action_id']
        and attacker and attacker['http']['response']['status']==403
        and attacker['access'].get('blocked') is True
        and attacker['access'].get('action_ids')==[receipt['action_id']])
    return {'expected_action':None if group=='B0' else expected,'proposed_action':proposed,
            'first_action_correct':correct,'false_action':bool(case=='C0' and proposed=='BLOCK_IP'),
            'guard_rejected':receipt.get('status')=='GUARD_REJECTED',
            'source_containment_verified':contained,'business_cycle_verified':business,
            'recovery':'FIXTURE_SOURCE_CONTAINMENT' if contained else 'NOT_CONTAINED' if case=='SQLI' else 'NO_FAULT',
            'external_H_recovery_verified':False,'benchmark_eligible':False}


class BaselineJournal:
    """B0 observer archive only; no decision/guard producer is constructed."""
    def __init__(self,output,context):
        from pathlib import Path
        self.directory=Path(output)/context['run_id'];self.directory.mkdir()
        self.stream=(self.directory/'events.jsonl').open('xb')
    def __call__(self,item):self.stream.write(canonical(item)+b'\n');self.stream.flush()
    def close(self):self.stream.close()


class RulesController:
    """B1 uses the actual Healer observation/action guards and backend/probe.

    The guard's budget view contains only deadline/blocked state. No Adapter,
    transport, model or provider credential is instantiated for RULES.
    """
    observation=Healer.observation
    action_guard=Healer.action_guard

    def __init__(self,context,*,api,pins,fixture_uid,journal,probe,budget,wall_clock=time.time):
        if context.get('group')!='B1' or journal.context!=context:
            raise ValueError('RULES_CONTEXT')
        self.context=deepcopy(context);self.fixture_uid=fixture_uid
        self.backend=SqliContainment(api,**pins,clock=wall_clock)
        self.pins,self.journal,self.probe=pins,journal,probe
        self.wall_clock=wall_clock
        self.adapter=SimpleNamespace(budget=budget)  # shared guard's deadline view; not an LLM Adapter
        self.started=False;self.dispatched=False;self.api_result=None;self.state=None
        self.producer=Producer('decision_rules',VERSION,CLOCK)
        self.guard_producer=Producer('guard',VERSION,CLOCK)

    async def run(self,detected,access):
        if self.started:raise ValueError('RULES_ALREADY_STARTED')
        self.started=True;self.journal.claim()
        access=self.observation(deepcopy(detected),deepcopy(access))
        if access is None:raise ValueError('RULES_ACCESS_MISSING')
        started=time.monotonic();decision_id=new_id('dec');action_id=new_id('act')
        action='BLOCK_IP' if access['restricted_rows']>0 and detected['payload']['value']>0 else 'NO_ACTION'
        plan={'action':action,'reason':'SQLI_DISCLOSURE' if action=='BLOCK_IP' else 'BENIGN',
              'evidence_ids':[detected['event_id']]}
        decision=self.producer.event(self.context,'DECISION',{
            'stage':'PROPOSAL','decision_source':'RULES',
            'inputs':[{'event_id':detected['event_id'],'received_at':now()}],
            'response_kind':'ACTION' if action=='BLOCK_IP' else 'NO_ACTION',
            'proposal':{'action_type':'BLOCK_IP','params':{'service':'sqli-fixture','ttl_sec':180}} if action=='BLOCK_IP' else None,
            'fallback':False,'fallback_of':None,'prompt_version':None,'prompt_sha256':None,
            'evidence_package_version':'hephaestus-joined-access/1',
            'access_sha256':hashlib.sha256(canonical(access)).hexdigest(),
            'decision_latency_ms':(time.monotonic()-started)*1000,'reason':plan['reason']},
            'o.decision',target=detected['target'],decision_id=decision_id,causation_id=detected['event_id'])
        self.journal({'kind':'DECISION','event':decision})
        status,reason='NO_ACTION','BENIGN'
        if action=='BLOCK_IP':
            try:
                ModeGate.admit({k:self.context[k] for k in ('run_id','trial_id','group')},decision,'decision_rules','AUTO')
                self.action_guard(detected,access,plan)
                verdict=self.guard_producer.event(self.context,'GUARD_VERDICT',{'verdict':'ACCEPT',
                    'reason_code':'SQLI_POLICY_ACCEPTED','guard_version':'zer50/1'},'o.guard',target=detected['target'],
                    decision_id=decision_id,causation_id=decision['event_id'])
                self.journal({'kind':'GUARD_VERDICT','event':verdict})
                self.journal({'kind':'DISPATCH_INTENT','action_id':action_id,'decision_id':decision_id})
                evidence={k:access[k] for k in ('client_ip','tcp_peer','source_method','source_confidence','request_id','ts')}
                evidence.update(run_id=self.context['run_id'],trial_id=self.context['trial_id'])
                self.dispatched=True
                def dispatch():
                    return ModeGate.dispatch({k:self.context[k] for k in ('run_id','trial_id','group')},
                        decision,'decision_rules','AUTO',executor=lambda _:self.backend.block(action_id=action_id,evidence=evidence,ttl_sec=180))
                task=asyncio.create_task(asyncio.to_thread(dispatch))
                try:self.api_result=await asyncio.shield(task)
                except asyncio.CancelledError:
                    try:self.api_result=await task
                    except Exception:pass
                    raise
                self.journal({'kind':'API_ACCEPTED','result':self.api_result,'action_id':action_id})
                self.state=SqliActionState(self.api_result,self.pins,fixture_uid=self.fixture_uid,
                    accepted_at=self.wall_clock(),timeout_s=120)
                proof=await asyncio.wait_for(self.probe(deepcopy(self.api_result)),timeout=120)
                snapshot=self.state.observe(proof['attacker'],proof['benign'],fixture=proof['fixture'],now=self.wall_clock())
                status='ACTION_COMPLETED' if snapshot['terminal'] and snapshot['terminal']['status']=='SUCCESS' else 'NOT_VERIFIED'
                reason='SQLI_CONTAINMENT_VERIFIED' if status=='ACTION_COMPLETED' else 'POSTCONDITION_NOT_MET'
                self.journal({'kind':'ACTION_POSTCONDITION','proof':proof,'state':snapshot,'action_id':action_id})
            except asyncio.CancelledError:raise
            except Exception as error:
                status='ACTION_OUTCOME_UNKNOWN' if self.dispatched else 'GUARD_REJECTED'
                reason=type(error).__name__+':'+str(error)
        receipt={'status':status,'reason':reason,'decision_source':'RULES','fallback':False,
            'plan':plan,'decision':decision,'detection_event_id':detected['event_id'],
            'action_id':action_id if self.dispatched else None,'api_result':deepcopy(self.api_result),
            'action_state':self.state.snapshot() if self.state else None,
            'model_events':[],'provider_calls':0,'decision_latency_ms':decision['payload']['decision_latency_ms'],
            'benchmark_eligible':False,'restart_allowed':False}
        self.journal({'kind':'RULES_RECEIPT','receipt':receipt})
        return receipt
