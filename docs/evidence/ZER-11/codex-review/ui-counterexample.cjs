// Offline counterexample for the real results.js error handler; no browser/network.
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('agent-orchestrator/nemesis/static/results.js','utf8');
(async()=>{
 const results=[];
 for(const [status,detail] of [[503,'UPSTREAM_DOWN'],[422,'ARTIFACT_HASH_MISMATCH'],[401,'UNAUTHORIZED'],[404,'RUN_NOT_REGISTERED']]){
  const nodes = new Map();
  const element = id => { if(!nodes.has(id)) nodes.set(id,{textContent:'',dataset:{},addEventListener(){}}); return nodes.get(id); };
  const ctx=vm.createContext({document:{getElementById:element,body:{dataset:{run:'run_a'}}},window:{location:{origin:'http://fixture'}},Node:class{}, Date, console,
   fetch:async()=>({ok:false,status,json:async()=>({detail})})});
  vm.runInContext(source,ctx);
  vm.runInContext("S.selected='run_a'; S.view={run_id:'run_a'}; S.viewAt=Date.now();",ctx);
  element('kpi').textContent='PASS / rate=100%';
  await vm.runInContext("loadRun('run_a',true)",ctx);
  results.push({http:status,detail,state:element('state').textContent,kpi:element('kpi').textContent,
   expected:status===503?'STALE with cached values':'clear cached KPI; show integrity/access/unregistered error'});
 }
 console.log(JSON.stringify(results,null,2));
})();
