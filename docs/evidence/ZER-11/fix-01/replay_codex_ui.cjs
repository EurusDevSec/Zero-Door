// Replays Codex's docs/evidence/ZER-11/codex-review/ui-counterexample.cjs unchanged on the current
// results.js. The only addition: its VM context gets the browser's setInterval/clearInterval, which
// every browser provides and the fixed 401 path now calls (endSession). Run from the repo root.
"use strict";
const path = require("node:path");
const vm = require("node:vm");
const create = vm.createContext;
vm.createContext = sandbox => create(Object.assign({ setInterval: () => 0, clearInterval: () => {} }, sandbox));
require(path.join(__dirname, "../codex-review/ui-counterexample.cjs"));
