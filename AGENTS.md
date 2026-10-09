# Working in ZERO DOOR

- Read `.agent/rules/CONTEXT.md` and `.agent/workflows/session_memory.md` for project context; verify their claims against current source and Git state.
- Start current research work with `docs/plans/2026-10-09-research-recovery-roadmap.md` and its user-confirmed scope: Python/Go and Google Online Boutique are accepted; keep the original attack/healing/KPI commitments. `docs/plan_original_v3.md` is the internal research plan, `docs/plan.md` the later DevOps plan, and `docs/research/` the report. Read the linked user-supplied registration document for original commitments; do not treat lower internal KPI targets or old completion notes as approval.
- The active agents are Python FastAPI under `agent-orchestrator/{nemesis,gaia,hephaestus}`; the chaos executor is Go under `chaos-worker/`.

## Efficient code exploration with GitNexus

- Repository alias: `zero_door`. Local index: `.gitnexus/` (gitignored).
- Start code exploration with `gitnexus://repo/zero_door/context` via MCP; check freshness before relying on graph results.
- Use GitNexus `query` for related execution flows, then `context` for a specific symbol. Read only the relevant source ranges to verify conclusions.
- If MCP is unavailable in the current session, use `gitnexus query "<concept>" -r zero_door --limit 3` and `gitnexus context "<symbol>" -r zero_door --file <relative-path> --limit 5`.
- Refresh the index after code changes with `gitnexus analyze`. `.gitnexusrc` keeps analysis local, skips generated context/skills, and disables embeddings.
- Use `rg` and direct file reads for research prose, manifests, dynamic Kafka/HTTP relationships, or anything the graph does not resolve. Graph results are navigation aids, not runtime proof.
- Do not enable embeddings, generate a wiki, or publish an index unless requested.
