"""Offline integrity audit of this repair. Never launches processes or accesses lab/model."""
import difflib, hashlib, importlib.util, json
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
E=HERE.parent
ROOT=HERE.parents[3]
def load(p):return json.loads(p.read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
prior=load(HERE/'before-artifact-sha256.json.txt')
changed=[]
for p,expected in prior.items():
 b=(E/p).read_bytes()
 if {'sha256':sha(b),'bytes':len(b)}!=expected:changed.append(p)
assert sorted(changed)==['README.md','runtime-prep/check_runner.py','runtime-prep/run.py'],changed
product=load(E/'source-hashes.json')
assert all(sha((ROOT/p).read_bytes())==h for p,h in product.items())
historical=load(E/'runtime-02/source-manifest-at-invocation.json')
pin_delta=[p for p,h in historical.items() if sha((ROOT/p).read_bytes())!=h]
assert sorted(pin_delta)==sorted('docs/evidence/ZER-19/runtime-prep/'+p for p in ('run.py','check_runner.py'))
patches=[]
for name in ('run.py','check_runner.py'):
 before=(HERE/('before-'+name+'.txt')).read_bytes()
 expected=prior['runtime-prep/'+name]
 assert {'sha256':sha(before),'bytes':len(before)}==expected
 patches+=difflib.unified_diff(before.decode().splitlines(True),(E/'runtime-prep'/name).read_text(encoding='utf8').splitlines(True),fromfile='before/'+name,tofile='after/'+name)
(HERE/'delta.patch').write_text(''.join(patches),encoding='utf8')
preserved=load(HERE/'handoff-preservation.json')
for p,v in preserved.items():
 b=(ROOT/p).read_bytes()[v['prefix_bytes']:]
 assert len(b)==v['prior_bytes'] and sha(b)==v['prior_sha256']
 assert v['suffix_preserved']
# Old authorizations/manifest are kept, so the changed helper cannot silently
# consume them. The function only reads JSON/hashes, with all spawning denied.
spec=importlib.util.spec_from_file_location('runner_fix_audit',E/'runtime-prep/run.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with patch.object(module.subprocess,'Popen',side_effect=AssertionError('OFFLINE_EXTERNAL_CLIENT_FORBIDDEN')):
 try:module.authorize('runtime-02')
 except RuntimeError as error:
  assert str(error).startswith('SOURCE_DRIFT:'),str(error)
  gate=str(error)
 else:raise AssertionError('Old consumed authorization unexpectedly admitted changed helper')
assert not (E/'runtime-03').exists()
log=(HERE/'offline-tests.log').read_text(encoding='utf8')
assert 'Ran 30 tests' in log and '\nOK' in log
pins={str((E/'runtime-prep'/p).relative_to(ROOT)).replace('\\','/') : sha((E/'runtime-prep'/p).read_bytes()) for p in ('run.py','check_runner.py')}
result={'status':'OFFLINE_FIX_VERIFIED_RUNTIME_NOT_RUN','head_verified':'093e924000861da3096185427994d9ea736df36d','branch_verified':'codex/zer-19-nemesis-session','offline_tests':30,'test_native_client_boundary':'DENY_BEFORE_SPAWN_EXCEPT_LOCAL_PYTHON_CHILDREN','default_entrypoint':'PLAN_ONLY_0_CALLS_0_MUTATIONS','bash_syntax':'PASS','git_diff_check':'PASS','git_index':'EMPTY','prior_artifacts':len(prior),'unchanged_prior_artifacts':len(prior)-len(changed),'expected_current_artifact_delta':changed,'product_pins_unchanged':len(product),'historical_runtime02_pins':len(historical),'expected_current_helper_delta':pin_delta,'historical_helper_versions_archived':True,'historical_raw_verdicts_and_authorizations':'UNCHANGED','old_authorization_current_source_gate':gate,'source_hashes':pins,'review':'SELF_REVIEW_NO_NEW_INDEPENDENT_REVIEW_CLAIM','lab_stall_fixed':'NOT_VERIFIED','runtime03_exists':False,'runtime_calls':0,'fixture_http_tcp':0,'lab_mutations':0,'publication':'NOT_STARTED','issue_done':False}
(HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
