"""Formal M12 joins, including late proof and known no-action; no sockets or lab."""
from copy import deepcopy
import tempfile
from pathlib import Path
import unittest
from types import SimpleNamespace

from event_pipeline.contract import new_id
from measurement.clock import Instant,stamp
from measurement.containment_join import REFS,write_artifact
from measurement.formal_containment import evaluate


class FormalContainment(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.directory=Path(self.tmp.name)
        self.run,self.trial,self.aid=new_id('run'),new_id('trl'),new_id('act')
        self.expected={'source':'10.42.0.2','fixture_uid':'fixture-uid','policy_uid':'policy-uid',
            'policy_scope':'test-scope','benign_source':'10.42.0.3','boutique_flow':'boutique_purchase','ttl_s':180}
        self.inc={'id':new_id('inc'),'trial':self.trial,'containment':[],
             't_req':Instant(100000,'host',True,1,1),'actions':{self.aid:{
                 'HEAL_STARTED':[{'payload':{'action_type':'BLOCK_IP'}}],
                 'API_ACCEPTED':[{'at_ms':110000}]}},'conflicted':set()}
        model=SimpleNamespace(state=lambda clock:(clock=='host',[]),
                              at=lambda clock,ms:Instant(ms,clock,True,1,1))
        self.scorer=SimpleNamespace(group='B2',h=SimpleNamespace(run_id=self.run),
             trial={self.trial:{'clock':model}},
             stamp_of=lambda event:Instant(event['at_ms'],'host',True,1,1),
             effect_cache=lambda inc:('CONFIRMED',Instant(101000,'host',True,1,1),30))
        common={'run_id':self.run,'trial_id':self.trial,'clock_id':'host'}
        self.documents={
            'policy':dict(common,kind='policy',observed_at=stamp(120000),policy_uid='policy-uid',
                 scope='test-scope',fixture_uid='fixture-uid',rules=[{'action_id':self.aid,
                 'client_ip':'10.42.0.2','created_at':101,'expires_at':281}]),
            'blocked_source_probe':dict(common,kind='blocked_source_probe',observed_at=stamp(119000),
                 source='10.42.0.2',fixture_uid='fixture-uid',status=403,error='SOURCE_BLOCKED',action_ids=[self.aid]),
            'benign_fixture_probe':dict(common,kind='benign_fixture_probe',observed_at=stamp(119100),
                 source='10.42.0.3',fixture_uid='fixture-uid',status=200,restricted_rows=0),
            'boutique_probe':dict(common,kind='boutique_probe',observed_at=stamp(120100),
                 flow='boutique_purchase',ok=True)}
    def tearDown(self):self.tmp.cleanup()
    def entry(self):
        refs={REFS[k]:write_artifact(self.directory,v,run_id=self.run,trial_id=self.trial)
              for k,v in self.documents.items()}
        self.inc['containment']=[{'event_id':new_id('evt'),'action_id':self.aid,
            'clock':{'clock_id':'host'},'payload':dict(refs,t_contained=max(v['observed_at'] for v in self.documents.values()))}]
        return {'containment_directory':self.directory,'decision_coverage':True,
                'expected':{k:self.expected[k] for k in ('source','fixture_uid','ttl_s')},
                'containment':{'expected':deepcopy(self.expected),'claim':refs,'action_id':self.aid}}
    def evaluate(self,entry=None,**changes):
        return evaluate(self.scorer,self.inc,entry or self.entry(),audit_clean=changes.get('audit_clean',True))
    def test_joined_live_proof_counts_and_reports_effect_delay(self):
        result=self.evaluate()
        self.assertEqual('VERIFIED',result['status'])
        self.assertEqual(19100,result['since_effect_ms'])
    def test_late_boutique_cannot_verify_an_expired_block(self):
        self.documents['boutique_probe']['observed_at']=stamp(282000)
        self.assertEqual('NOT_VERIFIED',self.evaluate()['status'])
    def test_wrong_policy_uid_and_missing_action_never_count(self):
        self.documents['policy']['policy_uid']='another-policy'
        self.assertEqual('NOT_VERIFIED',self.evaluate()['status'])
        self.documents['policy']['policy_uid']='policy-uid';self.inc['actions']={}
        self.assertEqual('UNVERIFIED',self.evaluate()['status'])
    def test_missing_or_tampered_artifact_remains_unknown(self):
        entry=self.entry();digest=entry['containment']['claim']['boutique_probe_ref'][7:]
        path=self.directory/(digest+'.json');raw=path.read_bytes();path.write_bytes(raw+b' ')
        self.assertEqual('UNVERIFIED',self.evaluate(entry)['status'])
        path.unlink();self.assertEqual('UNVERIFIED',self.evaluate(entry)['status'])
    def test_unknown_audit_clock_or_large_clock_error_cannot_verify(self):
        self.assertEqual('UNVERIFIED',self.evaluate(audit_clean=False)['status'])
        model=self.scorer.trial[self.trial]['clock'];model.state=lambda clock:(False,['UNKNOWN_CLOCK'])
        self.assertEqual('UNVERIFIED',self.evaluate()['status'])
        model.state=lambda clock:(True,[]);self.inc['t_req'].resolution_ms=300
        self.assertEqual('UNVERIFIED',self.evaluate()['status'])
    def test_unanchored_no_action_observations_do_not_become_verified_claims(self):
        self.documents['policy']['rules']=[]
        self.documents['blocked_source_probe'].update(status=200,error=None,action_ids=[])
        self.inc['actions']={};entry=self.entry();entry['containment']['action_id']=None
        self.assertEqual('UNVERIFIED',self.evaluate(entry)['status'])
        entry['decision_coverage']=False
        self.assertEqual('UNVERIFIED',self.evaluate(entry)['status'])
    def test_positive_requires_the_matching_archived_h_claim(self):
        entry=self.entry();self.inc['containment']=[]
        self.assertEqual('UNVERIFIED',self.evaluate(entry)['status'])
    def test_malformed_action_and_unrepresentable_epoch_remain_unknown(self):
        entry=self.entry();entry['containment']['action_id']={}
        self.assertEqual('UNVERIFIED',self.evaluate(entry)['status'])
        self.documents['policy']['rules'][0].update(created_at=10**100,expires_at=10**100+180)
        self.assertEqual('UNVERIFIED',self.evaluate()['status'])
    def test_cap_checks_every_artifacts_clock_uncertainty(self):
        self.documents['policy'].update(clock_id='remote',observed_at=stamp(370800))
        self.documents['policy']['rules'][0].update(created_at=200,expires_at=380)
        self.documents['blocked_source_probe']['observed_at']=stamp(370700)
        self.documents['benign_fixture_probe']['observed_at']=stamp(370800)
        self.documents['boutique_probe']['observed_at']=stamp(370900)
        self.inc['actions'][self.aid]['API_ACCEPTED'][0]['at_ms']=210000
        model=self.scorer.trial[self.trial]['clock'];model.state=lambda c:(True,[])
        model.at=lambda c,ms:Instant(ms,c,True,400 if c=='remote' else 1,1)
        self.assertNotEqual('VERIFIED',self.evaluate()['status'])
    def test_b0_reports_control_without_a_containment_success(self):
        self.scorer.group='B0'
        result=self.evaluate()
        self.assertEqual('CONTROL',result['status'])
        self.assertTrue(result['same_source_blocked'])
    def test_unknown_effect_keeps_verified_source_proof_but_no_effect_latency(self):
        self.scorer.effect_cache=lambda inc:('UNKNOWN_EFFECT',None,30)
        result=self.evaluate()
        self.assertEqual('VERIFIED',result['status']);self.assertIsNone(result['since_effect_ms'])


if __name__=='__main__':unittest.main()
