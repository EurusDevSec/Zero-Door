from pathlib import Path
import difflib
r=Path.cwd()
for n in ('flows','probe','sink','clock'):
 p=Path('agent-orchestrator/measurement')/(n+'.py')
 a=(r/'docs/evidence/ZER-10/fix-03/before'/p).read_text().splitlines()
 b=(r/p).read_text().splitlines()
 print(chr(10).join(difflib.unified_diff(a,b,fromfile='before/'+str(p),tofile=str(p))))
