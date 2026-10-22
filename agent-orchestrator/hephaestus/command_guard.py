"""Mode gate for authenticated O decisions. Production R1 execution remains disabled."""
from nemesis.command_guard import Refused, context_valid
from event_pipeline.contract import validate


class ModeGate:
    @staticmethod
    def admit(context, decision, authenticated_source, initiator, fallback_decision=None):
        context_valid(context)
        if context["group"] == "B0":
            # Audit by the caller; even a GUARD_VERDICT event is forbidden in B0.
            raise Refused("MODE_B0", 409)
        if type(decision) is not dict or validate(decision, "O", authenticated_source):
            raise Refused("DECISION_INVALID", 409)
        if decision.get("event_type") != "DECISION" or any(decision.get(k) != context[k] for k in context):
            raise Refused("DECISION_CONTEXT", 409)
        p = decision["payload"]
        if p["stage"] != "PROPOSAL" or p["response_kind"] != "ACTION" or p["proposal"] is None:
            raise Refused("DECISION_NO_ACTION", 409)
        source, kind, group = decision["source_component"], p["decision_source"], context["group"]
        if source != authenticated_source:
            raise Refused("DECISION_PRINCIPAL", 403)
        allowed = ((group == "BM" and source == "operator_console" and kind == "MANUAL" and initiator == "OPERATOR") or
                   (group == "B1" and source == "decision_rules" and kind == "RULES" and initiator == "AUTO") or
                   (group == "B2" and source == "decision_llm" and kind == "LLM" and initiator == "AUTO") or
                   (group == "B3" and source == "decision_single_llm" and kind == "SINGLE_LLM" and initiator == "AUTO") or
                   (group in {"B2", "B3"} and source == "decision_rules" and kind == "RULES" and
                    p["fallback"] is True and p["fallback_of"] is not None and initiator == "AUTO"))
        if not allowed:
            raise Refused("MODE_SOURCE", 409)
        if p["fallback"]:
            expected = "decision_llm" if group == "B2" else "decision_single_llm"
            prior = fallback_decision
            if (type(prior) is not dict or validate(prior, "O", expected) or
                    prior.get("event_type") != "DECISION" or prior.get("decision_id") != p["fallback_of"] or
                    any(prior.get(k) != context[k] for k in context) or
                    prior["payload"]["stage"] != "PROPOSAL" or
                    prior["payload"]["response_kind"] not in {"TIMEOUT", "REFUSAL", "SCHEMA_INVALID"}):
                raise Refused("FALLBACK_EVIDENCE", 409)
        return p["proposal"]

    @classmethod
    def dispatch(cls, context, decision, authenticated_source, initiator, executor=None, fallback_decision=None):
        proposal = cls.admit(context, decision, authenticated_source, initiator, fallback_decision)
        if executor is None:
            raise Refused("R1_EXECUTOR_DISABLED", 409)
        # Tests supply a fake executor. Production never supplies an executor in R1.
        return executor(proposal)


class GuardedRules:
    """Run the locked rules adapter only for the trusted B1 trial context."""
    def __init__(self, client, rules):
        self.client, self.rules = client, rules
        self.skipped = None  # the group whose trusted context disabled auto-decision, for the ops audit

    def poll(self):
        ctx = self.client.context()
        context = {key: ctx.get(key) for key in ("run_id", "trial_id", "group")}
        context_valid(context)
        if context["run_id"] != self.client.run or context["trial_id"] != self.client.trial:
            raise Refused("RUN_CONTEXT", 409)
        if context["group"] == "B1":
            self.skipped = None
            return self.rules.poll()
        # B0/BM do not auto-decide; B2/B3 require a real LLM/fallback producer.
        self.skipped = context["group"]
        return None
