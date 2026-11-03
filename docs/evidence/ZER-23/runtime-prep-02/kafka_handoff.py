"""One real Kafka send/receive on an empty run-owned topic; no provider key."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from kafka import KafkaConsumer,KafkaProducer,TopicPartition
from nemesis.command_guard import CommandGuard
from event_pipeline.contract import canonical


def exchange(packet,topic,*,producer_factory=KafkaProducer,consumer_factory=KafkaConsumer):
    policy=CommandGuard.from_env().policy
    expected='zer19-'+policy['context']['run_id'][4:16]+'.observations'
    if topic!=expected or len(canonical(packet))>32768+512:
        raise ValueError('HANDOFF_TOPIC_OR_SIZE')
    with Path('/ledger/observation-send.claim').open('x') as claim:
        claim.write(hashlib.sha256(canonical(packet)).hexdigest());claim.flush();os.fsync(claim.fileno())
    consumer=producer=None
    try:
        consumer=consumer_factory(bootstrap_servers='kafka.zero-door.svc.cluster.local:9092',
          api_version=(2,5),enable_auto_commit=False,group_id=None,
          request_timeout_ms=6000,session_timeout_ms=5000,auto_offset_reset='earliest')
        tp=TopicPartition(topic,0);consumer.assign([tp])
        if consumer.beginning_offsets([tp])[tp]!=0 or consumer.end_offsets([tp])[tp]!=0:
            raise ValueError('HANDOFF_TOPIC_NOT_EMPTY')
        consumer.seek(tp,0)
        producer=producer_factory(bootstrap_servers='kafka.zero-door.svc.cluster.local:9092',
          api_version=(2,5),acks='all',retries=0,request_timeout_ms=5000,max_block_ms=5000)
        produced=producer.send(topic,canonical(packet),partition=0).get(timeout=6)
        end=time.monotonic()+8;records=[]
        while time.monotonic()<end and not records:
            for batch in consumer.poll(timeout_ms=500,max_records=2).values():records.extend(batch)
        if len(records)!=1:raise ValueError('HANDOFF_RECEIVE_CARDINALITY')
        row=records[0]
        if ((produced.topic,produced.partition,produced.offset)!=(topic,0,0)
                or (row.topic,row.partition,row.offset)!=(topic,0,0)
                or row.value!=canonical(packet)):
            raise ValueError('HANDOFF_BROKER_JOIN')
        return {'packet':json.loads(row.value),'transport':{'kind':'KAFKA','topic':produced.topic,
          'partition':produced.partition,'offset':produced.offset,'consumed_topic':row.topic,
          'consumed_partition':row.partition,'consumed_offset':row.offset,'received_count':1}}
    finally:
        if producer is not None:producer.close(timeout=2)
        if consumer is not None:consumer.close(autocommit=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--topic',required=True);args=p.parse_args()
    raw=sys.stdin.buffer.read(33281)
    if len(raw)>33280:raise ValueError('HANDOFF_SIZE')
    print(json.dumps(exchange(json.loads(raw),args.topic),allow_nan=False),flush=True)


if __name__=='__main__':main()
