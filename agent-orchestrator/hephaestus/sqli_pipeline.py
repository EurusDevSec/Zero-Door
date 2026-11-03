"""Gaia diagnosis -> authenticated transport -> Healer, without direct-alert APIs."""
import asyncio
from copy import deepcopy
import hashlib
import math
import re
from urllib.parse import urlsplit

from event_pipeline.contract import canonical
from event_pipeline.sqli_handoff import Handoff
from gaia.diagnosis import Diagnoser
from hephaestus.recovery import Healer


class SqliPipeline:
    def __init__(self, gaia, healer, handoff, exchange, sink):
        if (not isinstance(gaia, Diagnoser) or not isinstance(healer, Healer)
                or not isinstance(handoff, Handoff) or gaia.adapter is not healer.adapter
                or gaia.context != healer.context or handoff.context != healer.context
                or not callable(exchange) or not callable(sink)):
            raise ValueError("PIPELINE_CONFIG")
        self.gaia, self.healer, self.handoff = gaia, healer, handoff
        self.exchange, self.sink, self.started = exchange, sink, False

    async def record(self, kind, **values):
        task = asyncio.create_task(asyncio.to_thread(self.sink, {"kind":kind, **deepcopy(values)}))
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            await task
            raise

    async def run(self, observed):
        if self.started:
            raise ValueError("PIPELINE_ALREADY_STARTED")
        self.started = True
        # Validate native identity/freshness before spending provider budget.
        self.healer.observation(observed["detection"], observed["access"])
        diagnosis = await self.gaia.analyze(observed["detection"], observed["evidence"])
        await self.record("PIPELINE_GAIA", receipt=diagnosis)
        if (diagnosis["status"] != "OK" or diagnosis["decision_source"] != "LLM"
                or diagnosis["fallback"] or not diagnosis["budget"]["cost_estimate_complete"]
                or diagnosis["budget"]["blocked"]):
            return {"status":"NOT_RUN_GAIA", "diagnosis":diagnosis, "healer":None}
        packet = self.handoff.seal(observed)
        digest = hashlib.sha256(canonical(packet)).hexdigest()
        await self.record("HANDOFF_SEND_INTENT", packet_sha256=digest,
                          detection_event_id=observed["detection"]["event_id"])
        delivered = await self.exchange(deepcopy(packet))
        if (type(delivered) is not dict or set(delivered) != {"packet", "transport"}
                or canonical(delivered["packet"]) != canonical(packet)):
            raise ValueError("PIPELINE_TRANSPORT_MISMATCH")
        meta = delivered["transport"]
        topic = "zer19-" + self.healer.context["run_id"][4:16] + ".observations"
        expected = {"kind":"KAFKA", "topic":topic, "partition":0, "offset":0,
                    "consumed_topic":topic, "consumed_partition":0, "consumed_offset":0, "received_count":1}
        if (meta != expected or any(type(meta[k]) is not int for k in
                ("partition", "offset", "consumed_partition", "consumed_offset", "received_count"))):
            raise ValueError("PIPELINE_BROKER_RECEIPT")
        received = self.handoff.receive(delivered["packet"])
        await self.record("HANDOFF_RECEIVED", packet_sha256=digest, transport=delivered["transport"],
                          detection_event_id=received["detection"]["event_id"])
        # The only dispatch path consumes verified transported bytes, never the sender's object.
        receipt = await self.healer.run(received["detection"], received["access"])
        await self.record("PIPELINE_HEALER", receipt=receipt)
        return {"status":"COMPLETED", "diagnosis":diagnosis, "healer":receipt,
                "transport":delivered["transport"], "packet_sha256":digest}


def verify_benign_probe(proof, *, fixture_uid, attacker_ip, benign_ip, proxy_ip, not_before, at):
    """Validate native no-action controls; model abstention does not imply healthy service."""
    try:
        if proof['fixture'] != {'uid':fixture_uid,'ready':True} or len(proof['benign'])!=5:
            raise ValueError('BENIGN_FIXTURE')
        rows=[proof['attacker'],*proof['benign']]
        triples=[]
        for row,source in zip(rows,[attacker_ip]+[benign_ip]*5):
            request,response,access=row['http']['request'],row['http']['response'],row['access']
            begin,end,ts=response['begin'],response['end'],access['ts']
            if (row['pod_uid']!=fixture_uid or not row['ref']
                or not all(type(t) in (int,float) and math.isfinite(t) for t in (begin,end,ts,not_before,at))
                or not not_before<=begin<=ts<=end<=at
                or not re.fullmatch(r'[0-9a-f]{32}',response['request_id'])
                or response['request_id']!=access['request_id']
                or not re.fullmatch(r'[0-9a-f]{32}',request['correlation'])
                or request['correlation']!=access['correlation_id']
                or request['method']!=access['method'] or urlsplit(request['path']).path!=access['path']
                or response['status']!=access['status'] or access['client_ip']!=source
                or access['tcp_peer']!=proxy_ip or access['source_method']!='XFF_AFTER_TRUSTED'
                or access['source_confidence']!='PROXY_CHAIN' or access['blocked'] is not False
                or access['action_ids']!=[] or access['enforcement_point']!='sqli-fixture/trusted-client'
                or not re.fullmatch(r'[0-9a-f]{64}',access['policy_sha256'])):
                raise ValueError('BENIGN_NATIVE_JOIN')
            triples.append((request,response,access))
        a,*b=triples
        ref=b[1][1]['body']['order_ref']
        if not re.fullmatch(r'[0-9a-f]{32}',ref):raise ValueError('BENIGN_ORDER_REF')
        path='/fixture/orders/'+ref
        expected=[('GET','/fixture/catalog/search',200),('POST','/fixture/orders',201),
                  ('GET',path,200),('DELETE',path,200),('GET',path,404)]
        if (a[0]['method']!='GET' or a[2]['path']!='/fixture/catalog/search' or a[1]['status']!=200
            or a[1]['body'].get('count',0)<1
            or [(q['method'],j['path'],r['status']) for q,r,j in b]!=expected
            or b[0][1]['body'].get('count',0)<1 or b[1][1]['body']!=b[2][1]['body']
            or b[1][1]['body'].get('status')!='STORED'
            or any(b[1][0]['body'][k]!=b[1][1]['body'][k] for k in ('item','note'))
            or b[3][1]['body']!={'deleted':1} or b[4][1]['body']!={'error':'NOT_FOUND'}
            or any(left[1]['end']>right[1]['begin'] for left,right in zip(triples,triples[1:]))
            or len({r['http']['response']['request_id'] for r in rows})!=6
            or len({r['http']['request']['correlation'] for r in rows})!=6
            or len({r['access']['policy_sha256'] for r in rows})!=1):
            raise ValueError('BENIGN_CONTENT_OR_ORDER')
        return {'status':'PASS','fixture_uid':fixture_uid,'probe_refs':[r['ref'] for r in rows]}
    except (KeyError,TypeError,ValueError) as error:
        raise ValueError('BENIGN_PROBE_NOT_VERIFIED') from error
