import sys, json, copy, tempfile, hashlib, traceback
from pathlib import Path
sys.path[:0]=['tests','agent-orchestrator']
import test_dashboard_measurement as t
from nemesis import measurement_view as mv
from measurement.output import csv_bytes, INCIDENT_COLUMNS, USAGE_COLUMNS, incident_rows, usage_rows

def run_case(kind, fn):
 with tempfile.TemporaryDirectory() as d:
  root=Path(d)/'results';root.mkdir();t.score_case('b1_recovered',root)
  score=root/'b1_recovered'/'score.json'; doc=json.loads(score.read_text());fn(doc)
  score.write_text(json.dumps(doc),encoding='utf8')
  try:
   e=mv.register(root,'b1_recovered')
   v=mv.ResultsStore(root).view(e['run_id'])
   print(json.dumps({'case':kind,'result':'ACCEPT','kpi':v['kpi'],'data_time':v['data_time']}))
  except Exception as ex:
   print(json.dumps({'case':kind,'result':type(ex).__name__,'detail':str(ex)}))
for kind,fn in [
 ('missing_input_hashes',lambda d:d['inputs'].update(h_export_json_sha256=None,o_export_json_sha256=None)),
 ('missing_kpi_fields',lambda d:d['runs'][0]['metrics'].update(kpi={})),
 ('kpi_type',lambda d:d['runs'][0]['metrics']['kpi'].update(N='broken')),
 ('milestones_list',lambda d:d['runs'][0]['incidents'][0].update(milestones=['broken'])),
 ('bad_findings_types',lambda d:d['runs'][0]['findings'].update(mode_violations=1)),
 ('bad_leak_type',lambda d:d['runs'][0].update(leak=['bad']))]:
 run_case(kind,fn)
