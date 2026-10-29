"""One full ZER-46 AC candidate. Inert import; fresh approval and exact source snapshot required.
No diagnostic retries, resource changes or image operations are introduced.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
PREP=Path(__file__).parent
OUT=ROOT/'docs/evidence/ZER-46/runtime-09'
AUTH=PREP/'acceptance-authorization.json'
MANIFEST=PREP/'acceptance-source-manifest.json'
PROPOSAL=PREP/'acceptance-proposal.md'
spec=importlib.util.spec_from_file_location('zer46_full_ac_agent',PREP/'run_agent_fixture.py')
agent=importlib.util.module_from_spec(spec);spec.loader.exec_module(agent)
parent=agent.cached.parent
for module in (agent,agent.cached,parent,parent.full,parent.full.base):module.OUT=OUT
parent.AUTHORIZATION_FILE=AUTH

class Lab(agent.Lab):
    def http(self,*args,**kwargs):
        if self.fixture_http>=29:raise RuntimeError('AC_FIXTURE_HTTP_BUDGET')
        return super().http(*args,**kwargs)
    def isolation(self,*args,**kwargs):
        if self.tcp_checks+2>4:raise RuntimeError('AC_TCP_BUDGET')
        return super().isolation(*args,**kwargs)

parent.Lab=Lab

def verify_sources():
    if (OUT/'started.json').exists() or (OUT/'acceptance.json').exists():raise RuntimeError('ONE_ATTEMPT_ONLY')
    auth=json.loads(AUTH.read_text(encoding='utf8'))
    if auth['status']!='APPROVED':raise RuntimeError('NOT_APPROVED')
    if (ROOT/auth['proposal']).resolve()!=PROPOSAL.resolve():raise RuntimeError('PROPOSAL_PIN')
    if hashlib.sha256(PROPOSAL.read_bytes()).hexdigest()!=auth['proposalSha256']:raise RuntimeError('PROPOSAL_DRIFT')
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest()!=auth['sourceManifestSha256']:raise RuntimeError('MANIFEST_DRIFT')
    lock=json.loads(MANIFEST.read_text(encoding='utf8'))
    for path,expected in lock['files'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:raise RuntimeError('SOURCE_DRIFT:'+path)
    return lock

def snapshot(lock):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'prepared-source-manifest.json').write_bytes(MANIFEST.read_bytes())
    scripts={}
    for path,expected in lock['files'].items():
        target=OUT/'source'/path;target.parent.mkdir(parents=True,exist_ok=True)
        content=(ROOT/path).read_bytes()
        if hashlib.sha256(content).hexdigest()!=expected:raise RuntimeError('SOURCE_DRIFT_DURING_SNAPSHOT:'+path)
        target.write_bytes(content)
        if path.startswith('docs/evidence/ZER-46/runtime-prep/') and Path(path).suffix in ('.py','.sh'):
            (OUT/'scripts').mkdir(exist_ok=True)
            (OUT/'scripts'/Path(path).name).write_bytes(content);scripts[path]=expected
    (OUT/'source-manifest.json').write_text(json.dumps({'files':lock['files'],'scripts':scripts},indent=2),encoding='utf8')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:parser.error('fresh separately approved --execute required')
    lock=verify_sources();snapshot(lock)
    return parent.main()

if __name__=='__main__':sys.exit(main())
