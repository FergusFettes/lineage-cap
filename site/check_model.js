// Check site/model.js against numbers quoted in first-flush-likelihood.qmd.  Run: node site/check_model.js
const M = require("./model.js");
const B = M.BASELINE;
let failed = 0;
function near(name, got, want, rel) {
  const ok = Math.abs(got - want) <= rel * Math.abs(want);
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${name}: ${got.toPrecision(4)} (note ${want})`);
}
near("planet ceiling Lambda at T=4.6", M.planetCeiling(B, 4.6), 2.1e-8, 0.05);
near("saturated lead, visibility (Myr)", 1000 * M.sharedLead(B).delta, 13.7, 0.01);
near("saturated lead, arrival (Myr)", 1000 * M.sharedLead(B, "arrival").delta, 27, 0.03);
near("saturated lead, mu=1 (Myr)", 1000 * M.sharedLead({ ...B, pEmpty: Math.exp(-1) }).delta, 9.6, 0.01);
near("lead at Lambda=1 (Myr)", 1000 * M.sharedLead({ ...B, q: 1e-10 }).delta, 16, 0.04);
near("lead at Lambda=0.01 (Myr)", 1000 * M.sharedLead({ ...B, q: 1e-12 }).delta, 63, 0.04);
for (const [W, d] of [[0.1, 32], [0.2, 38], [0.5, 47], [5, 84]])
  near(`window ${W * 1000} Myr lead (Myr)`, 1000 * M.sharedLead(B, "visibility", W).delta, d, 0.03);
for (const [s, F, home, mean, wait] of [[0.03, 5.891824e-10, 5.891824, 182.5, 14.3],
  [0.136, 6.208437e-12, 0.06208437, 921.4, 33.5], [0.408, 2.715213e-13, 0.002715213, 2943.3, 93.9]]) {
  const r = M.durationSpread(B, s);
  near(`sigma ${s * 1000} Myr F(t0)`, r.F, F, 0.02);
  near(`sigma ${s * 1000} Myr MW ahead`, r.home, home, 0.02);
  near(`sigma ${s * 1000} Myr mean after (Myr)`, 1000 * r.meanAfter, mean, 0.01);
  near(`sigma ${s * 1000} Myr median arrival given empty sky (Myr)`, 1000 * r.wait, wait, 0.03);
}
// results/iid_tail/observer_rates.csv
const R = M.observerRates(B, 0.136);
near("FNC process loud, sigma 136 (rate)", R.process.loud.rate, 3.157651, 0.01);
near("FNC process loud, sigma 136 (home)", R.process.loud.home, 0.939804, 0.01);
near("FNC process late filter, mean 3 sigma after", R.process.filter[0].obs, 3.258712e8 * 0.991273, 0.05);
near("FNC process late filter, mean at today", R.process.filter[2].obs, 2.933399e10 * 0.999371, 0.05);
near("FNC planet loud", R.planet.loud.obs, 1.512933e-9, 0.05);
near("FNC planet late filter", R.planet.filter.obs, 7.352941e8, 0.01);
for (const [n, W, rate] of [[3, Infinity, 1.015566e-8], [9, Infinity, 2.074835e-7], [3, 5, 9.933589e-10], [9, 5, 1.425313e-9]])
  near(`FNC hard steps n=${n} W=${W}`, M.hardSteps(B, n, W).rate, rate, 0.02);
process.exit(failed ? 1 : 0);
