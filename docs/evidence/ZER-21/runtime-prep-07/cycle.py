"""One explicit functional cycle across the existing agents; inert on import.

The trusted caller owns native observation, signed execution, durable output and
process/cleanup limits. Completion here requires native reconciliation before any
runtime AC claim. This is not a benchmark runner or an authenticated O archive.
"""
import asyncio
from copy import deepcopy

from gaia.diagnosis import Diagnoser, observation_valid
from hephaestus.recovery import Healer
from nemesis.session import Session

CONTEXT = ("run_id", "trial_id", "incident_id", "group", "method_version", "config_ref")


class FunctionalCycle:
    """Reuse one adapter/budget and one incident; never replay a stage automatically.

    observe_result is a trusted native-reader port, not model/HTTP input. It must
    return detection/evidence/access after joining the worker's delivered result
    to the original fixture telemetry. No proposal grants dispatch authority.
    """
    def __init__(self, nemesis, gaia, healer, *, observe_result, sink):
        if (not isinstance(nemesis, Session) or not isinstance(gaia, Diagnoser)
                or not isinstance(healer, Healer) or not callable(observe_result)
                or not callable(sink)):
            raise ValueError("CYCLE_COMPONENTS")
        adapter = nemesis.adapter
        if (gaia.adapter is not adapter or healer.adapter is not adapter
                or any(nemesis.context.get(k) != gaia.context.get(k)
                       or nemesis.context.get(k) != healer.context.get(k) for k in CONTEXT)
                or adapter.budget.calls != 0 or adapter.budget.max_calls != 3
                or adapter.limits.attempts != 1 or adapter.limits.max_output_tokens > 256
                or adapter.limits.timeout_s > 20 or adapter.limits.deadline_s > 25
                or nemesis.limits.max_rounds != 1
                or nemesis.guard.policy["sqli"]["maxSends"] != 1
                or nemesis.task is not None or gaia.seen or healer.started):
            raise ValueError("CYCLE_CONTEXT_BUDGET_OR_REPLAY")
        self.nemesis, self.gaia, self.healer = nemesis, gaia, healer
        self.adapter, self.observe_result, self.sink = adapter, observe_result, sink
        self.context = deepcopy(healer.context)
        self.started = False
        self.stages = {}

    async def record(self, kind, **data):
        worker = asyncio.create_task(asyncio.to_thread(self.sink,
            {"kind": kind, "context": deepcopy(self.context), **deepcopy(data)}))
        try:
            await asyncio.shield(worker)
        except asyncio.CancelledError:
            await worker
            raise

    def join(self, observed):
        if type(observed) is not dict or set(observed) != {"detection", "evidence", "access"}:
            raise ValueError("CYCLE_OBSERVER_SCHEMA")
        detection, evidence, access = (observed[k] for k in ("detection", "evidence", "access"))
        observation_valid(detection, evidence)
        if access is None:
            raise ValueError("CYCLE_NATIVE_ACCESS_MISSING")
        self.healer.observation(detection, access)  # Same existing context/trust/freshness guard.
        records = self.stages["nemesis"]["records"]
        commands = [r["command"] for r in records if r["event"] == "DISPATCH_INTENT"]
        results = [r["raw"] for r in records if r["event"] == "EXECUTOR_RESULT"]
        if len(commands) != 1 or len(results) != 1 or results[0]["status"] != "SUCCESS":
            raise ValueError("CYCLE_EXECUTOR_JOIN")
        sends = results[0]["details"]["sqli"]["sends"]
        if (len(sends) != 1 or results[0]["commandId"] != commands[0]["commandId"]
                or sends[0].get("responseId") != access["request_id"]
                or sends[0]["requestId"] != commands[0]["commandId"] + "/1"
                or sends[0]["status"] != access["status"]
                or sends[0]["rows"] != access["rows"]
                or sends[0]["restrictedRows"] != access["restricted_rows"]
                or detection["payload"]["metric"] != "log_pattern_match"
                or detection["payload"]["value"] != int(access["restricted_rows"] > 0)):
            raise ValueError("CYCLE_NATIVE_RESULT_JOIN")
        return deepcopy(observed)

    async def run(self):
        if self.started:
            raise ValueError("CYCLE_ALREADY_STARTED")
        self.started = True
        status, reason, cancelled = "NOT_MET", "NEMESIS_NOT_COMPLETED", False
        try:
            await self.record("CYCLE_STARTED", benchmark_eligible=False)
            self.stages["nemesis"] = await self.nemesis.start()
            if (asyncio.current_task().cancelling()
                    or self.stages["nemesis"]["stop_reason"].startswith("CANCELLED")):
                # Session deliberately turns its cancellation into a durable receipt.
                # The parent cycle must still propagate the operator's cancellation.
                raise asyncio.CancelledError
            await self.record("NEMESIS_RESULT", receipt=self.stages["nemesis"])
            nemesis = self.stages["nemesis"]
            if (nemesis["stop_reason"] == "MAX_ROUNDS" and nemesis["completed_rounds"] == 1
                    and nemesis["budget"]["attempts_dispatched"] == 1
                    and nemesis["budget"]["cost_estimate_complete"]):
                observed = self.join(await self.observe_result(deepcopy(nemesis)))
                await self.record("OBSERVER_JOIN", observation=observed,
                    detection_source="RULES_TRUSTED_READER", archive_delivery="LOCAL_ONLY_NOT_AUTHENTICATED")
                self.stages["gaia"] = await self.gaia.analyze(observed["detection"], observed["evidence"])
                await self.record("GAIA_RESULT", receipt=self.stages["gaia"])
                gaia = self.stages["gaia"]
                reason = "GAIA_NOT_COMPLETED"
                if (gaia["status"] == "OK" and gaia["decision_source"] == "LLM" and not gaia["fallback"]
                        and gaia["budget"]["attempts_dispatched"] == 2
                        and gaia["budget"]["cost_estimate_complete"] and not gaia["budget"]["blocked"]):
                    # Diagnosis is recorded data, not an alternative to Healer's O evidence/guard.
                    self.stages["healer"] = await self.healer.run(observed["detection"], observed["access"])
                    await self.record("HEALER_RESULT", receipt=self.stages["healer"])
                    healer = self.stages["healer"]
                    reason = "HEALER_NOT_COMPLETED"
                    budget = self.adapter.budget.summary()
                    if (healer["status"] in {"NO_ACTION", "ABSTAIN", "ACTION_COMPLETED"}
                            and healer["decision_source"] == "LLM" and not healer["fallback"]
                            and budget["attempts_dispatched"] == 3 and budget["cost_estimate_complete"]
                            and not budget["blocked"]):
                        status, reason = "COMPLETED_PENDING_NATIVE_REVIEW", "THREE_AGENT_RECORDS_JOINED"
        except asyncio.CancelledError:
            self.nemesis.stop()
            reason, cancelled = "CANCELLED_OUTCOME_REQUIRES_RECONCILIATION", True
        except Exception as error:
            # No replay, inference retry, fabricated fallback or assumed remote cancellation.
            reason = ("HEALER_ACTION_RECONCILIATION_REQUIRED_" if self.healer.dispatched
                      else "STAGE_FAILED_") + type(error).__name__
        receipt = {"purpose": "THREE_AGENT_FUNCTIONAL_TRACE", "status": status, "reason": reason,
            "context": deepcopy(self.context), "stages": deepcopy(self.stages),
            "budget": self.adapter.budget.summary(), "benchmark_eligible": False,
            "healer_progress": {"started": self.healer.started, "dispatched": self.healer.dispatched,
                "api_result": deepcopy(self.healer.api_result),
                "action_state": self.healer.state.snapshot() if self.healer.state else None,
                "receipt_available": "healer" in self.stages,
                "journal_ref": str(self.healer.journal.directory / "events.jsonl"),
                "action_may_remain": self.healer.dispatched},
            "runtime_ac_verified": False, "recovery_verified": False, "restart_allowed": False,
            "archive_delivery": "LOCAL_ONLY_NOT_AUTHENTICATED"}
        await self.record("CYCLE_RECEIPT", receipt=receipt)
        if cancelled:
            raise asyncio.CancelledError
        return receipt
