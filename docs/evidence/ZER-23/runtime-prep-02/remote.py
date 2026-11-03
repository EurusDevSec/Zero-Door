"""One command via the existing signed KafkaExecutor; provider credentials absent."""
import asyncio
import json
import sys

from nemesis.command_guard import CommandGuard, read_key, strict_json
from nemesis.session_cli import KafkaExecutor


def main():
    raw = sys.stdin.buffer.read(32769)
    if len(raw) > 32768:
        raise ValueError("REMOTE_COMMAND_SIZE")
    command = strict_json(raw)
    guard = CommandGuard.from_env()
    operator = read_key("/operator/key.json", "operator")
    guard.authorize("Bearer " + operator["secret"])
    # A private ledger claim precedes the Kafka send. Reinvocation cannot replay it.
    result = asyncio.run(KafkaExecutor(guard, guard.signer(), guard.ledger(),
        "kafka.zero-door.svc.cluster.local:9092")(command))
    print(json.dumps(result, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
