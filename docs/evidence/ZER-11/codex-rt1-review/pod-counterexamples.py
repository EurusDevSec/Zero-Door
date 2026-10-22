import sys,json,tempfile,time
from pathlib import Path
from unittest.mock import patch
root=next(p for p in Path(__file__).resolve().parents if (p/'agent-orchestrator').is_dir())
sys.path[:0]=[str(root/'agent-orchestrator'),str(root/'infrastructure/scripts'),str(root/'tests')]
import r1_baseline_runtime as rt
import test_dashboard_baseline_runtime as tt
from measurement.sink import HttpHSink,Retry
results={}
with tempfile.TemporaryDirectory() as tmp:
    a=rt.Agent(Path(tmp)/'agent')
    cfg=rt.config(tt.scaled_plan(),tt.OVERRIDES)
    cfg.update(protocol_ref='rt1 test',schedule_ref='sealed',config_ref='sha256:'+'a'*64)
    try:
        start=a.handle({'action':'start_run','config':cfg})
        assert start['ok'],start
        original=HttpHSink.deliver
        def fail_decision(self,event,deadline_ns=None):
            if event['event_type']=='DECISION': raise Retry('injected decision-only ACK outage')
            return original(self,event,deadline_ns)
        with patch.object(HttpHSink,'deliver',fail_decision):
            answer=a.handle({'action':'positive_control'})
        results['positive_control_lost_ack']={'handle_response':answer,'agent_saved_pc':a.pc}
        assert a.pc['ok'] is False and answer['ok'] is True
    finally: a.shutdown()
base={'incidents':[{'trial_id':'trl-1','label':'RECOVERED_UNDETECTED','milestones':{'t_rec':{'t_ms':200000},'t_stop':{'t_ms':210000}}}]}
for name,event in [
    ('B0-CTRL',{'reason':'SuccessfulCreate','object':'ReplicaSet/frontend-old','source':'replicaset-controller','t_ms':1000,'message':'historical pod created'}),
    ('B0-HPA',{'reason':'SuccessfulRescale','object':'HorizontalPodAutoscaler/frontend-hpa-r1','source':'horizontal-pod-autoscaler','t_ms':1000,'message':'New size: 1; reason: All metrics below target'})]:
    receipt={'trials':{name:{'trial_id':'trl-1','audit_coverage':{'complete':True},'stop_point':'a'}}}
    evidence={'trials':{name:{'events':[event],'frontend_pods_after':[]}}}
    results['historical_'+name]=rt.interpret(base,receipt,evidence)
assert results['historical_B0-CTRL']['B0-CTRL']['claim']=='CONTROLLER_RECOVERY_OBSERVED'
assert results['historical_B0-HPA']['B0-HPA']['claim']=='HPA_RECOVERY_OBSERVED'
print(json.dumps(results,indent=2))
