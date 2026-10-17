# Working in ZERO DOOR

- Read `.agent/rules/CONTEXT.md` and `.agent/workflows/session_memory.md` for project context; verify their claims against current source and Git state.
- Start current work with `docs/delivery/README.md`, then `docs/delivery/NOW.md`, the assigned Linear issue and its technical note under `docs/delivery/milestones/`. Read `docs/delivery/SCOPE.md` for user-confirmed commitments and `docs/delivery/WORKFLOW.md` for collaboration and QA/Done. Current units are Linear milestone / issue / sub-issue. Old plans and metadata live only in `docs/archive/planning/`; there are no parallel recovery/plans folders or redirect roadmap files.
- Python/Go and Google Online Boutique are accepted; keep the original attack/healing/KPI commitments. `docs/archive/planning/research-plan.md` is the internal research plan, `docs/archive/planning/devops-plan.md` the later DevOps plan, and `docs/research/` the report. Read the linked user-supplied registration document or its attributed excerpt for original commitments; do not treat lower internal KPI targets or old completion notes as approval.
- The active agents are Python FastAPI under `agent-orchestrator/{nemesis,gaia,hephaestus}`; the chaos executor is Go under `chaos-worker/`.

## Following delivery

- Linear Zero Door is the live authority for issue outcome/AC, state, assignment, priority, estimates, dates and relations. Repository scope, code and durable evidence remain authoritative in their domains. Read `docs/delivery/linear/README.md`; the named connection has verified workspace zero-door/team ZER; project P-ZER-1 has been created and verified; actual project/issue IDs and URLs are in docs/delivery/linear/mapping.json. Do not substitute EurusDevSec/S-cool metadata or claim a live status from Markdown.
- Issue notes hold technical requirements, file plans, verification and handoffs. Old status/owner/date tables are archived, not a live board. `NOW.md` is a session pointer. Preserve R*-T*-S* aliases only as provenance; verified Linear IDs are delivery identifiers after publication. Selective sub-issues live in Linear; do not create a Markdown mirror for each.
- Read only the assigned issue and relevant references. Before implementation record actual HEAD/dirty state and an exact file/action scope, including new tests/probes; use one writer per checkout. Close work with verification/evidence, not merely a code change or elapsed due date.
- End each work session with a technical handoff in the issue note; update live issue fields in Linear only within granted authority, and `NOW.md` only for checkpoint/next action. Code-changing issues require review, verification, merge and Hoang acceptance for Done; this does not authorize commit/push/merge. Do not mark legacy completion as runtime proof or operate lab/model/cloud merely because an item exists in tracking.

## Linear workspace routing

- For this repository / ZERO DOOR, reuse the configured MCP connection `linear_zero_door` and verify that returned workspace/project URLs belong to `linear.app/zero-door/` before writing. Configuration, OAuth and workspace/team read-back succeeded on 2026-10-17. Team ZER ID is 865d41a7-ef26-474c-a9f8-36e781569fc8; project P-ZER-1 ID is f6343559-080f-465f-aa7a-eda6074de51f; reuse the project and mapped issue IDs.
- The existing bundled Linear connector was observed on EurusDevSec/S-cool. Do not use it for ZERO DOOR merely because its generic tool names contain `linear`, and do not replace/re-authorize that connector to handle each project switch.
- Look up the existing named connection first. Missing tools in an already-running session is not evidence that the connection was deleted: reload tools/client and check before adding anything. Do not rerun `mcp add`, delete credentials or create duplicate server names on routine visits.
- A newly requested workspace needs its own verified access once; an existing workspace reuses saved configuration/authentication. Re-authenticate only when the actual connection requires it. Account/workspace switching does not authorize external writes, assignments or notifications.
- Keep workspace/project identity and actual IDs in `docs/delivery/linear/README.md` and mapping after read-back; do not store tokens or copy live issue state into the routing guide.

## Efficient code exploration with GitNexus

- Repository alias: `zero_door`. Local index: `.gitnexus/` (gitignored).
- Start code exploration with `gitnexus://repo/zero_door/context` via MCP; check freshness before relying on graph results.
- Use GitNexus `query` for related execution flows, then `context` for a specific symbol. Read only the relevant source ranges to verify conclusions.
- If MCP is unavailable in the current session, use `gitnexus query "<concept>" -r zero_door --limit 3` and `gitnexus context "<symbol>" -r zero_door --file <relative-path> --limit 5`.
- Refresh the index after code changes with `gitnexus analyze`. `.gitnexusrc` keeps analysis local, skips generated context/skills, and disables embeddings.
- Use `rg` and direct file reads for research prose, manifests, dynamic Kafka/HTTP relationships, or anything the graph does not resolve. Graph results are navigation aids, not runtime proof.
- Do not enable embeddings, generate a wiki, or publish an index unless requested.
