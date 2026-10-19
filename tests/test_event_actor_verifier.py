"""Fail-closed checks for the live actor verifier without contacting the cluster."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('actor_verifier', ROOT/'infrastructure/scripts/verify-event-actors.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VerifierTests(unittest.TestCase):
    def test_cleanup_requires_uid_and_nonce(self):
        current={'metadata':{'uid':'a','labels':{'zero-door-verification':'n'}}}
        v.ensure_owner(current,'a','n')
        for uid,nonce in [('b','n'),('a','x')]:
            with self.assertRaises(RuntimeError):v.ensure_owner(current,uid,nonce)

    def test_export_checks_every_described_file(self):
        raw=b'{}\n';seal={'sha256':v.sha(raw)}
        manifest=b'{"seal":true}\n'
        d={'seal':seal,'files':{name:{'bytes':len(data),'sha256':v.sha(data)} for name,data in [('O.jsonl',raw),('manifest.json',manifest)]}}
        files={'O.jsonl':raw,'manifest.json':manifest,'export.json':json.dumps(d).encode()}
        v.verify_export(files,'O',seal)
        for name in ['O.jsonl','manifest.json']:
            bad=dict(files);bad[name]=b'edited'
            with self.assertRaises(RuntimeError):v.verify_export(bad,'O',seal)

    def test_actor_profiles_keep_keys_and_network_scope(self):
        ctx={'run_id':v.new_id('run'),'trial_id':v.new_id('trl')}
        images={n:'test/'+n for n in ['event_pipeline','gaia','hephaestus']}
        base,overlay=v.render('zd-zer9-abc',images,ctx,'ver')
        actors=[d for d in overlay if d['kind']=='Pod']
        self.assertEqual(len(actors),2)
        for pod in actors:
            name=pod['metadata']['name'];s=pod['spec']
            self.assertFalse(s['automountServiceAccountToken'])
            self.assertEqual(s['nodeSelector'],{'kubernetes.io/hostname':v.NODE})
            self.assertEqual([x.get('secret',{}).get('secretName') for x in s['volumes'] if 'secret' in x],['event-o-'+name])
            self.assertFalse(any('persistentVolumeClaim' in x for x in s['volumes']))
            self.assertEqual(s['initContainers'][0]['command'],['/usr/bin/python3','/verify/gate.py'])
            self.assertEqual(s['containers'][0]['image'],images[name])
        policy=next(d for d in overlay if d['metadata']['name']=='actors-to-o')
        self.assertEqual(policy['spec']['egress'],[{'to':[{'podSelector':{'matchLabels':{'app':'events-o'}}}],'ports':[{'port':8000,'protocol':'TCP'}]}])

    def test_gate_rejects_open_direct_connection(self):
        # Execute the actual gate with deterministic network doubles. An always-open H
        # connection must exhaust the gate, while a closed direct network passes at 3.
        from unittest.mock import patch, mock_open
        import socket
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*a):pass
        for opened in [False,True]:
            connect=(lambda *a,**k:Response()) if opened else (lambda *a,**k:(_ for _ in ()).throw(TimeoutError()))
            with patch('builtins.open',mock_open(read_data='{"detector":"x","reader":"r"}')),patch('os.path.exists',return_value=False),patch.dict('os.environ',{'ZD_RUN_ID':v.new_id('run')}),patch('urllib.request.urlopen',return_value=Response()),patch('socket.getaddrinfo',return_value=[1]),patch('socket.create_connection',side_effect=connect),patch('time.sleep'),patch('builtins.print') as output:
                if opened:
                    with self.assertRaises(AssertionError):exec(v.GATE,{})
                else:
                    exec(v.GATE,{})
                    result=json.loads(output.call_args[0][0]);self.assertEqual(len(result['history']),3)


if __name__=='__main__':unittest.main()
