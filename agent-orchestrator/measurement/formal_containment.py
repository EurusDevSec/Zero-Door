"""Use the existing H artifact join in formal M12; never infer containment from a 403 alone."""
from .clock import duration,parse,stamp
from .containment_join import REFS,join,read_artifact
from event_pipeline.contract import valid_id


def bounded(a,b):
    value=duration(a,b)
    return value if value is not None and value[1] is not None and value[1]<=500 else None


def evaluate(scorer,inc,entry,*,audit_clean):
    base={'incident_id':inc['id'],'containment_event_ids':[e['event_id'] for e in inc['containment']]}
    unknown=lambda reason:dict(base,status='UNVERIFIED',reason=reason)
    spec=entry.get('containment');directory=entry.get('containment_directory')
    if not audit_clean:return unknown('AUDIT_UNVERIFIED')
    if not isinstance(spec,dict) or directory is None:return unknown('CONTAINMENT_ARTIFACTS_MISSING')
    expected,claim,aid=spec.get('expected'),spec.get('claim'),spec.get('action_id')
    if not isinstance(claim,dict) or not isinstance(expected,dict):return unknown('CONTAINMENT_FIELDS_MISSING')
    pinned=entry.get('expected')
    if not isinstance(pinned,dict) or any(pinned.get(k)!=expected.get(k) for k in ('source','fixture_uid','ttl_s')):
        return unknown('EXPECTED_TRIAL_SCOPE_MISMATCH')
    group=scorer.group;documents={}
    for kind,field in REFS.items():
        if group=='B0' and kind not in ('blocked_source_probe','boutique_probe'):continue
        doc,problem=read_artifact(directory,claim.get(field),kind=kind,run_id=scorer.h.run_id,trial_id=inc['trial'])
        if problem:return unknown(kind+':'+problem)
        documents[kind]=doc
    model=scorer.trial[inc['trial']]['clock']
    req=inc['t_req'];_,effect,_=scorer.effect_cache(inc)
    instants={}
    for kind,doc in documents.items():
        if not model.state(doc['clock_id'])[0]:return unknown('ARTIFACT_CLOCK_UNVERIFIED')
        point=model.at(doc['clock_id'],parse(doc['observed_at']))
        elapsed=bounded(req,point)
        if elapsed is None:return unknown('ARTIFACT_CLOCK_BOUND_UNVERIFIED')
        if elapsed[0]-elapsed[1]<0 or elapsed[0]+elapsed[1]>=330000:
            return dict(base,status='NOT_VERIFIED',reason='PROOF_OUTSIDE_OBSERVATION_WINDOW')
        instants[kind]=point
    if group=='B0':
        result=join(expected,None,claim,directory,run_id=scorer.h.run_id,trial_id=inc['trial'],group=group)
        return dict(base,**result)
    if type(expected.get('ttl_s')) is not int or expected['ttl_s']!=180:return unknown('EXPECTED_TTL_NOT_PINNED')
    if not valid_id(aid,'act'):return unknown('NO_VALID_ARCHIVED_ACTION_ID')
    claims=[e for e in inc['containment'] if e.get('action_id')==aid
            and all(e['payload'].get(field)==claim.get(field) for field in REFS.values())]
    if len(claims)!=1:return unknown('H_CLAIM_NOT_ARCHIVED_OR_AMBIGUOUS')
    action=inc['actions'].get(aid,{})
    if (len(action.get('HEAL_STARTED',[]))!=1 or len(action.get('API_ACCEPTED',[]))!=1
            or ('API_ACCEPTED',aid) in inc.get('conflicted',set())):
        return unknown('ARCHIVED_ACTION_MISSING_OR_CONFLICTED')
    started=action['HEAL_STARTED'][0];accepted=action['API_ACCEPTED'][0]
    if started['payload']['action_type']!='BLOCK_IP':return unknown('WRONG_ARCHIVED_ACTION')
    result=join(expected,aid,claim,directory,run_id=scorer.h.run_id,trial_id=inc['trial'],group=group)
    if result['status']!='VERIFIED':return dict(base,**result)
    policy=documents['policy'];rules=[r for r in policy['rules'] if r['action_id']==aid]
    if len(rules)!=1:return unknown('POLICY_ACTION_NOT_UNIQUE')
    rule=rules[0];clock_id=policy['clock_id']
    try:
        created=model.at(clock_id,parse(stamp(rule['created_at']*1000)))
        expires=model.at(clock_id,parse(stamp(rule['expires_at']*1000)))
        hclaim=claims[0]
        if not model.state(hclaim['clock']['clock_id'])[0]:return unknown('H_CLAIM_CLOCK_UNVERIFIED')
        claimed=model.at(hclaim['clock']['clock_id'],parse(hclaim['payload']['t_contained']))
    except (ValueError,OverflowError,TypeError,KeyError):return unknown('UNREPRESENTABLE_POLICY_OR_CLAIM_TIME')
    last=max(instants.values(),key=lambda t:t.ms)
    agreement=bounded(last,claimed)
    if agreement is None or abs(agreement[0])>agreement[1]:return unknown('H_CLAIM_TIME_MISMATCH')
    effect_delay=None
    for point in [*instants.values(),claimed]:
        since_api=bounded(scorer.stamp_of(accepted),point)
        until_expiry=bounded(point,expires)
        since_created=bounded(created,point)
        if None in (since_api,until_expiry,since_created):return unknown('ACTION_CLOCK_UNVERIFIED')
        if (since_api[0]-since_api[1]<0 or since_created[0]-since_created[1]<0
                or until_expiry[0]-until_expiry[1]<=0):
            return dict(base,status='NOT_VERIFIED',reason='PROOF_OUTSIDE_ACTION_LIFETIME')
        elapsed=bounded(req,point)
        if elapsed is None:return unknown('H_CLAIM_CLOCK_BOUND_UNVERIFIED')
        if elapsed[0]-elapsed[1]<0 or elapsed[0]+elapsed[1]>=330000:
            return dict(base,status='NOT_VERIFIED',reason='PROOF_OUTSIDE_OBSERVATION_WINDOW')
        delay=bounded(effect,point) if effect is not None else None
        if effect is not None and delay is None:return unknown('EFFECT_CLOCK_UNVERIFIED')
        if delay is not None and (delay[0]-delay[1]<0 or delay[0]+delay[1]>270000):
            return dict(base,status='NOT_VERIFIED',reason='PROOF_OUTSIDE_CONTAINMENT_CAP')
    effect_delay=bounded(effect,last) if effect is not None else None
    return dict(base,**result,verified_at_ms=last.ms,
                since_effect_ms=effect_delay[0] if effect_delay else None,
                time_bound_verified=True)
