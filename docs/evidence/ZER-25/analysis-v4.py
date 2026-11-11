"""Offline descriptive reconciliation. Never fills failures or pools historical runs."""
import argparse
import json
import math
import re
from pathlib import Path
import statistics

TIMINGS=('worker_roundtrip_ms','observation_join_ms','response_workflow_ms','business_probe_ms','model_latency_ms')

def finite(value):return type(value) in (int,float) and math.isfinite(value) and value>=0

def integer(value,maximum):return type(value) is int and 0<=value<=maximum

def evidence_issues(data,cell,protocol=None):
    issues=[];budget=data.get('model_budget')
    if (type(budget) is not dict
        or not integer(budget.get('attempts_dispatched'),2 if cell['group']=='B2' else 0)
        or not integer(budget.get('reserved_tokens'),30000)
        or any(not integer(budget.get(k),1000000) for k in ('known_input_tokens','known_output_tokens','unknown_usage_attempts'))
        or any(not finite(budget.get(k)) for k in ('reserved_estimate_usd','known_cost_estimate_usd'))
        or budget.get('cost_estimate_complete') is not True or budget.get('blocked') is not False
        or budget.get('unknown_usage_attempts')!=0):issues.append('MODEL_BUDGET_MISSING_INVALID_OR_UNKNOWN')
    writes=data.get('api_replace_attempts')
    if not integer(writes,0 if cell['group']=='B0' else 1):issues.append('WRITE_COUNT_MISSING_OR_INVALID')
    if cell['case']=='C0' and writes!=0:issues.append('FALSE_ACTION_OR_UNKNOWN_WRITES')
    digest=data.get('observation_invariant_sha256')
    if type(digest) is not str or not re.fullmatch('[0-9a-f]{64}',digest):issues.append('OBSERVATION_HASH_MISSING_OR_INVALID')
    profile=data.get('workload_profile')
    expected={'source_cpu_limit':'500m','hpa_fixture':'OFF','duration_s':1,'concurrency':1,'rps':1,
      'max_worker_sends':1,'ttl_s':180,'probe':'native 6-request search/CRUD',
      'template':{'SQLI':'disclose-restricted','C0':'benign-apparel'}[cell['case']]}
    if (type(profile) is not dict or any(profile.get(k)!=v for k,v in expected.items())
        or any(type(profile.get(k)) is not str or not re.fullmatch('[0-9a-f]{64}',profile[k])
          for k in ('shared_specs_sha256','hpa_sha256','seed_sha256'))):issues.append('WORKLOAD_PROFILE_MISSING_OR_INVALID')
    if protocol and protocol.get('pre_measurement_preparation'):
        if (type(profile) is not dict or profile.get('fixed_quiet_s')!=protocol['pre_measurement_preparation']['fixed_quiet_seconds']
          or (data.get('context') or {}).get('method_version')!=protocol['version']):
            issues.append('METHOD_OR_FIXED_PREPARATION_MISMATCH')
    if protocol and protocol.get('native_setup'):
        expected_timeout=protocol['native_setup']['topic_create_cli_timeout_seconds']
        if (type(profile) is not dict or type(profile.get('topic_create_timeout_s')) is not int
          or profile.get('topic_create_timeout_s')!=expected_timeout):
            issues.append('TOPIC_SETUP_TIMEOUT_MISMATCH')
    metrics=data.get('metrics')
    if (type(metrics) is not dict or any(type(metrics.get(k)) is not bool
        for k in ('source_containment_verified','business_cycle_verified'))
        or (metrics.get('first_action_correct') is not None if cell['group']=='B0'
          else type(metrics.get('first_action_correct')) is not bool)):issues.append('METRIC_FACTS_MISSING_OR_INVALID')
    if type(data.get('fixture_uid')) is not str or not data['fixture_uid']:issues.append('FIXTURE_ID_MISSING')
    return issues

def stats(values):
    valid=[float(v) for v in values if type(v) in (float,int) and math.isfinite(v) and v>=0]
    return {'n':len(valid),'min':min(valid) if valid else None,'max':max(valid) if valid else None,
      'mean':statistics.mean(valid) if valid else None,
      'sample_sd':statistics.stdev(valid) if len(valid)>1 else None}

def read(path):
    try:return json.loads(path.read_bytes())
    except FileNotFoundError:return None

def expenditure(rows):
    """Known expenditure across all attempted cells; missing/unknown is explicit."""
    attempted=[r for r in rows if r['attempted']]
    ints=('attempts_dispatched','known_input_tokens','known_output_tokens','unknown_usage_attempts')
    floats=('known_cost_estimate_usd',)
    totals={k:0 for k in (*ints,*floats)}
    missing=invalid=0;complete=True
    for row in attempted:
        budget=row['model_budget']
        if budget is None:
            missing+=1;complete=False;continue
        if type(budget) is not dict:
            invalid+=1;complete=False;continue
        bad=False
        for key in ints:
            value=budget.get(key)
            if type(value) is int and value>=0:totals[key]+=value
            else:bad=True
        for key in floats:
            value=budget.get(key)
            if finite(value):totals[key]+=value
            else:bad=True
        if bad:invalid+=1
        complete=complete and not bad and budget.get('cost_estimate_complete') is True and budget.get('unknown_usage_attempts')==0
    return dict(totals,attempted_cells=len(attempted),reported_budget_cells=len(attempted)-missing,
      missing_budget_cells=missing,invalid_budget_cells=invalid,cost_estimate_complete=complete,
      scope='All attempted cells, including failed measurements; numeric totals are known amounts only')

def reconcile(batch,protocol):
    batch=Path(batch)
    retained=read(batch/'protocol.json')
    if retained is not None and retained!=protocol:raise ValueError('RETAINED_PROTOCOL_MISMATCH')
    acceptance=read(batch/'acceptance.json') or {}
    scheduled=protocol['schedule'];recorded=acceptance.get('rows',[])
    by_index={}
    for row in recorded:
        i=row['index']
        if type(i) is not int or i not in range(len(scheduled)) or i in by_index:
            raise ValueError('DUPLICATE_OR_FOREIGN_CELL')
        if any(row.get(k)!=scheduled[i][k] for k in ('block','group','case')):
            raise ValueError('CELL_SCHEDULE_MISMATCH')
        by_index[i]=row
    rows=[]
    for cell in scheduled:
        i=cell['index'];status=by_index.get(i,{}).get('status','MISSING')
        out=batch/('trial-%02d'%(i+1));data=read(out/'pilot-cell.json')
        final_budget=read(out/'model-budget.json')
        budget=final_budget if final_budget is not None else data.get('model_budget') if data else None
        gaia=(data.get('gaia') if data else None) or read(out/'gaia-receipt.json') or {}
        decision=(data.get('decision') if data else None) or read(out/'decision-receipt.json') or {}
        attempted=status not in ('NOT_RUN','MISSING') or bool(data) or final_budget is not None or (out/'started.json').exists()
        issues=[]
        if final_budget is not None and data and final_budget!=data.get('model_budget'):
            issues.append('FINAL_MODEL_BUDGET_MISMATCH')
        if status!='RECONCILE_REQUIRED':issues.append(status)
        if not data:issues.append('NATIVE_CELL_MISSING')
        else:
            if data.get('cell')!=cell:issues.append('CELL_IDENTITY')
            if data.get('http')!=8 or data.get('tcp')!=2:issues.append('PROBE_BUDGET')
            if any(type(data.get('timing',{}).get(k)) not in (int,float)
              or not math.isfinite(data['timing'][k]) or data['timing'][k]<0 for k in TIMINGS):issues.append('TIMING_INVALID')
            issues.extend(evidence_issues(data,cell,protocol))
        native=by_index.get(i,{})
        for k in ('work_elapsed_s','cleanup_elapsed_s'):
            if not finite(native.get(k)):issues.append(k.upper()+'_MISSING_OR_INVALID')
        if native.get('cleanup',{}).get('verdict')!='CLEAN':issues.append('CLEANUP_NOT_CLEAN')
        for name in ('worker','cleanup_process'):
            p=native.get(name,{})
            if not (p.get('exit_code')==0 and p.get('timed_out') is False):issues.append(name.upper()+'_UNSUCCESSFUL')
            if not (p.get('owned_tree_closed') is True and p.get('process_reaped') is True):issues.append(name.upper()+'_NOT_CLOSED')
        rows.append({**cell,'status':status,'measurement_issues':issues,'measurement_candidate':not issues,
          'timing':data.get('timing',{}) if data else {},'metrics':data.get('metrics') if data else None,
          'gaia_status':gaia.get('status'),'healer_status':decision.get('status'),
          'healer_action':(decision.get('plan') or {}).get('action'),
          'attempted':attempted,'model_budget':budget,
          'model_budget_source':'model-budget.json' if final_budget is not None else 'pilot-cell.json' if data else None,
          'workload_profile':data.get('workload_profile') if data else None,
          'observation_invariant_sha256':data.get('observation_invariant_sha256') if data else None,
          'fixture_uid':data.get('fixture_uid') if data else None})
        rows[-1].update({k:native.get(k) for k in ('work_elapsed_s','cleanup_elapsed_s')})
    # Same operational facts/profile within a case; identities remain distinct in originals.
    comparisons={}
    for case in protocol['cases']:
        peers=[r for r in rows if r['case']==case and r['measurement_candidate']]
        facts={r['observation_invariant_sha256'] for r in peers}
        profiles={json.dumps(r['workload_profile'],sort_keys=True) for r in peers}
        uids=[r['fixture_uid'] for r in peers]
        comparisons[case]={'observed_candidates':len(peers),'operational_facts_equal':len(facts)==1,
          'profiles_equal':len(profiles)==1,'distinct_fixture_uids':bool(uids) and len(set(uids))==len(uids)}
    summaries=[]
    for group in protocol['groups']:
        for case in protocol['cases']:
            chosen=[r for r in rows if r['group']==group and r['case']==case]
            valid=[r for r in chosen if r['measurement_candidate']]
            summaries.append({'group':group,'case':case,'planned':len(chosen),'candidate_n':len(valid),
              'failed_missing_or_not_run':len(chosen)-len(valid),
              'native_containment_true':sum(r.get('metrics',{}).get('source_containment_verified') is True for r in valid),
              'first_action_correct_true':None if group=='B0' else sum(r.get('metrics',{}).get('first_action_correct') is True for r in valid),
              'abstentions':sum(r['gaia_status']=='ABSTAIN' or r['healer_status']=='ABSTAIN' or r['healer_action']=='ABSTAIN' for r in chosen),
              'gaia_abstentions':sum(r['gaia_status']=='ABSTAIN' for r in chosen),
              'healer_abstentions':sum(r['healer_status']=='ABSTAIN' or r['healer_action']=='ABSTAIN' for r in chosen),
              'timing':{k:stats([r['timing'].get(k) for r in valid]) for k in TIMINGS},
              'work_s':stats([r['work_elapsed_s'] for r in valid]),
              'cleanup_s':stats([r['cleanup_elapsed_s'] for r in valid]),
              'full_cycle_s':stats([r['work_elapsed_s']+r['cleanup_elapsed_s'] for r in valid]),
              'usage_totals':expenditure(chosen)})
    complete=all(r['measurement_candidate'] for r in rows) and all(
      c['operational_facts_equal'] and c['profiles_equal'] and c['distinct_fixture_uids'] for c in comparisons.values())
    projected={key:sum(s['full_cycle_s'][key]*5 for s in summaries) if complete else None
      for key in ('min','mean','max')}
    return {'analysis_version':'zer52-descriptive-analysis/4','protocol_version':protocol['version'],'usage_totals':expenditure(rows),
      'status':'RAW_REVIEW_REQUIRED' if complete else 'INCOMPLETE_DO_NOT_LOCK',
      'planned':len(rows),'candidate_n':sum(r['measurement_candidate'] for r in rows),
      'rows':rows,'comparability':comparisons,'summary':summaries,
      'recommendation':{'minimum_formal_trials_per_cell_provisional':5 if complete else None,
        'basis':'Two pilot observations/cell and bounded exploratory minimum, not power or precision proof' if complete else 'Resolve missing/invalid measurement or safety failures before locking counts',
        'projected_30_cell_full_cycle_seconds':projected,
        'projection_limit':'Empirical pilot min/mean/max multiplied by5 per cell; not predictive bounds. BM/operator time and formal session overhead excluded, budget must be approved in ZER-53.',
        'independent_raw_review_required':True,'formal_lock_issue':'ZER-53'},
      'historical_pooling':False,'MTTD_MTTR_uptime':'NOT_ESTIMATED','issue_done':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('batch',type=Path);p.add_argument('--output',type=Path);p.add_argument('--protocol',type=Path);a=p.parse_args()
    selected=a.protocol or (a.batch/'protocol.json' if (a.batch/'protocol.json').exists() else Path(__file__).parent/'protocol.json')
    result=reconcile(a.batch,json.loads(selected.read_bytes()))
    if a.output:
        with a.output.open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    else:print(json.dumps(result,allow_nan=False))
if __name__=='__main__':main()
