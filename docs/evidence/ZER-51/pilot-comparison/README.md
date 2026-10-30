# ZER-51 / ZER-21 AC02 — pilot evidence complete, one harness failure retained

One native observation per B0/B1/B2 × SQLi/C0. No statistical superiority claim.
Machine table:comparison.csv;full facts/IDs/budgets/limitations:reconciliation.json.

|Group|Case|Gaia|Proposed|Correct first action|Native containment|Business cycle|Whole trial|Calls|Cleanup|
|---|---|---|---|---|---|---|---|---|---|
|B0|C0|None|None|None|False|True|PASS|0|CLEAN|
|B1|SQLI|None|BLOCK_IP|True|True|True|NOT_MET_SHUTDOWN_RACE|0|CLEAN|
|B2|C0|ABSTAIN|None|False|False|True|PASS|1|CLEAN|
|B0|SQLI|None|None|None|False|True|PASS|0|CLEAN|
|B1|C0|None|NO_ACTION|True|False|True|PASS|0|CLEAN|
|B2|SQLI|OK|BLOCK_IP|True|True|True|PASS|2|CLEAN|

B0 has no decider/heal/model/key; first-action correctness isN/A. B1 uses actual
Healer observation/action guards,ModeGate/SqliContainment/SqliActionState and
same six-request native probe as B2. B2 uses realGaia/Hephaestus calls as admitted.
Ground truth is applied after decisions,not passed as case/answer to the models.
SQLi requiresBLOCK_IP;C0requiresNO_ACTION under the locked scoring rule. A valid
ABSTAIN is kept as abstention,not relabeled correctNO_ACTION or silently retried.

## Evidence quality and the preserved failure

Six planned cells all have nativeworker/request/log/probe evidence;fresh fixtureUID
percell. Paired operational-evidence hashes match for B0/B1/B2 in each case;
sharedDeployment/PVC/HPA/seed/CPU/memory/guard/executor/probe profiles match.
Ephemeral IDs/IP/timestamps remain distinct and unmodified in each actual input.

Whole-trial success is5/6. Originalpilot02 B1/SQLiworkNOT_MET staysfailed:
normalmainstop raced watcher read,while worker/guard/action/postcondition had
completed. Deterministic offline regression proves the oldshutdown race and
newdrain fix. The nativecontainment fact remains separate from fulltrialsucccess.
Onlyfournever-runcells were continued afterfix;no repeats or droppedfailure.
This is a disclosed pilotprotocoldeviation,not a cleanformaldataset or sixPASSclaim.

Allsixnamespace/topics cleanupsCLEAN,sharedspecsUID/restarts preserved against
cartprobe3sbaseline. The approvedcartrollout changed onlytwo probe timeouts;
noCPU/RAM/image/replica/PSIthreshold or otherworkload changes.

Usage total: {"model_calls": 3, "input_tokens": 1923, "output_tokens": 205, "cost_usd": 0.0002948, "http": 48, "tcp": 12, "worker_sends": 6, "sqli_sends": 3, "replaces": 2}. Cost is an estimate,not billing.
Recovery column means fixture sourcecontainment;businesscycle means benign
search/create/read/delete/absent. It doesnot establishexternalH/Boutique recovery,
MTTR/uptime or AI superiority. Clock/modelrevisionindependentlyUNKNOWN;archiveLOCAL.

AC01real3agenttrace remains ZER-21/runtime-07. AC02pilot evidence is nowpresent
with failure/abstention retained;requiredreview/publication/merge/Hoàngacceptance
remain before issueDone. No Linear mutation or Git publication performed here.
