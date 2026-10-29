"""Bounded decision outbox; never executes a proposal or claims recovery.

Use an explicitly mounted SQLite path for restart durability. The default memory
database is for existing transport fixtures only and reports PROCESS_ONLY.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time

from .contract import canonical


class DecisionJournal:
    MAX_ATTEMPTS = 3
    RETRY_WINDOW = 30
    COOLDOWN = 90
    CAPACITY = 10000

    def __init__(self, path=None, clock=time.time):
        self.path = str(path) if path is not None else ":memory:"
        self.durability = "PROCESS_ONLY" if self.path == ":memory:" else "PERSISTENT_PATH_REQUIRED"
        if self.path != ":memory:":
            p = Path(self.path)
            if p.is_symlink() or p.parent.is_symlink() or not p.parent.is_dir():
                raise ValueError("DECISION_STATE_PATH")
        self.clock = clock
        self.db = sqlite3.connect(self.path, timeout=2, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS decisions (input_id TEXT PRIMARY KEY, digest TEXT NOT NULL, "
                        "envelope TEXT NOT NULL, target TEXT NOT NULL, created REAL NOT NULL, "
                        "attempts INTEGER NOT NULL, status TEXT NOT NULL, reason TEXT)")

    def reserve(self, event, build):
        """Persist exact envelope BEFORE any send; ambiguous sends keep the same IDs."""
        digest = hashlib.sha256(canonical(event)).hexdigest()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.get(event["event_id"])
            if row:
                if row["digest"] != digest:
                    raise ValueError("DECISION_INPUT_CONFLICT")
                return row
            if self.db.execute("SELECT count(*) FROM decisions").fetchone()[0] >= self.CAPACITY:
                raise ValueError("DECISION_STATE_FULL")
            envelope = build()
            proposal = envelope["payload"]["proposal"]
            target = canonical([event["run_id"], event["trial_id"], event["target"],
                                proposal["action_type"] if proposal else None]).decode()
            current = self.clock()
            prior = self.db.execute("SELECT max(created) FROM decisions WHERE target=? AND "
                                    "status IN ('PENDING','RECORDED','UNKNOWN')", (target,)).fetchone()[0]
            status = "COOLDOWN" if proposal and prior is not None and current < prior + self.COOLDOWN else "PENDING"
            self.db.execute("INSERT INTO decisions VALUES (?,?,?,?,?,0,?,?)",
                            (event["event_id"], digest, canonical(envelope).decode(), target, current,
                             status, "COOLDOWN" if status == "COOLDOWN" else None))
            return self.get(event["event_id"])
        finally:
            if self.db.in_transaction:
                self.db.execute("COMMIT" if sys.exc_info()[0] is None else "ROLLBACK")

    def get(self, input_id):
        return self.db.execute("SELECT * FROM decisions WHERE input_id=?", (input_id,)).fetchone()

    def attempt(self, input_id):
        row = self.get(input_id)
        if row["status"] != "PENDING":
            return None
        if row["attempts"] >= self.MAX_ATTEMPTS or not 0 <= self.clock() - row["created"] < self.RETRY_WINDOW:
            self.finish(input_id, "UNKNOWN", "RETRY_BUDGET_EXHAUSTED")
            return None
        # A crash consumes this attempt; restart cannot reset its budget.
        self.db.execute("UPDATE decisions SET attempts=attempts+1 WHERE input_id=?", (input_id,))
        return json.loads(row["envelope"])

    def finish(self, input_id, status, reason=None):
        if status not in {"RECORDED", "REFUSED", "UNKNOWN"}:
            raise ValueError("DECISION_STATUS")
        self.db.execute("UPDATE decisions SET status=?,reason=? WHERE input_id=?", (status, reason, input_id))

    def summary(self):
        return {"durability": self.durability,
                "states": {r[0]: r[1] for r in self.db.execute("SELECT status,count(*) FROM decisions GROUP BY status")},
                "recovery_verification": "EXTERNAL_PROBE_REQUIRED"}

    def close(self):
        self.db.close()
