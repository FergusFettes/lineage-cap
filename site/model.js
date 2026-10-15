/* Head-start cap model, ported from lineage_cap/ (expansion.py, start_spread.py, iid_tail.py).
 * Units: cosmic age in Gyr, distance in Mpc.  Flat space, Poisson galaxies, ideal detection.
 * Checked against the note's numbers by site/check_model.js (`make site-check`). */
(function (root) {
  "use strict";

  // Exact SI c, Julian Gyr and IAU parsec, in Mpc/Gyr (= 306.6014).
  const C = 299792458 * (365.25 * 86400 * 1e9) / (648000 / Math.PI * 149597870700 * 1e6);
  const T0 = 13.8;         // today
  const S = 0.2;           // ramp start
  const HOST_MPC = 0.03;   // host galaxy diameter, 30 kpc

  const BASELINE = {
    N: 1e10,       // effective trajectories per galaxy today
    q: 1,          // chance a crossed lineage turns loud
    v: 0.5,        // front speed, fraction of c
    ng: 0.01,      // galaxies per Mpc^3
    pEmpty: 0.05,  // working line: P(empty) at the edge
    T: 4.6,        // planet clock duration, Gyr
    W: 0,          // start window width, Gyr
    sigma: 0.136,  // duration spread, Gyr
  };

  // Gauss-Legendre nodes on [-1, 1] by Newton iteration.
  function legendre(n) {
    const x = new Float64Array(n), w = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      let z = Math.cos(Math.PI * (i + 0.75) / (n + 0.5)), dp = 0;
      for (let it = 0; it < 100; it++) {
        let p0 = 1, p1 = 0;
        for (let j = 1; j <= n; j++) { const p2 = p1; p1 = p0; p0 = ((2 * j - 1) * z * p1 - (j - 1) * p2) / j; }
        dp = n * (z * p0 - p1) / (z * z - 1);
        const dz = p0 / dp; z -= dz;
        if (Math.abs(dz) < 1e-15) break;
      }
      x[i] = z; w[i] = 2 / ((1 - z * z) * dp * dp);
    }
    return { x, w };
  }

  // z = r/R = 1 - u^2 resolves the thin partly-loud shell at the outer edge (as in expansion.py).
  const QUAD = (function (order) {
    const { x, w } = legendre(order);
    const z = new Float64Array(order), wz = new Float64Array(order);
    for (let i = 0; i < order; i++) { const u = (x[i] + 1) / 2; z[i] = 1 - u * u; wz[i] = w[i] * u; }
    return { z, w: wz };
  })(96);

  const zones = (p, t) => t < S ? 0 : p.N * Math.min(Math.max((t - S) / (T0 - S), 0), 1);

  // P(at least one loud lineage among m), stable for tiny q.
  function loud(m, q) {
    if (m <= 0 || q <= 0) return 0;
    if (q >= 1) return 1;
    return -Math.expm1(m * Math.log1p(-q));
  }

  const muStar = p => -Math.log(p.pEmpty);

  function kernel(p, kind) {
    const vis = kind === "visibility";
    return {
      delay: vis ? HOST_MPC / (p.v * C) : 0,
      prop: vis ? C : p.v * C,
    };
  }

  /* Expected galaxies showing themselves, for a lead delta (Gyr).
   * mode "planet": each trajectory crosses T = (t0 - delta) - s after its birth.
   * mode "inherited": one frontier at t0 - delta; with W > 0, galaxy starts spread
   * uniformly over a window of width W beginning at the frontier. */
  function expected(p, delta, mode, kind, W) {
    const { delay, prop } = kernel(p, kind);
    const avail = Math.max(delta - delay, 0);
    if (avail <= 0 || prop <= 0) return 0;
    const R = prop * avail, frontier = T0 - delta, Wd = W || 0;
    let sum = 0;
    const add = (z, w) => {
      const t = T0 - delay - avail * z;
      let pg;
      if (mode === "planet") {
        pg = loud(zones(p, t - (frontier - S)), p.q);
      } else if (Wd > 0) {
        const f = Math.min(Math.max(avail * (1 - z) / Wd, 0), 1);
        pg = f * loud(zones(p, t), p.q);
      } else {
        pg = t >= frontier ? loud(zones(p, t), p.q) : 0;
      }
      sum += pg * z * z * w;
    };
    if (mode === "inherited" && Wd > 0) {
      // Split the radial integral at the window kink, as in start_spread.py.
      const cut = Math.max(1 - Wd / avail, 0);
      for (let i = 0; i < QUAD.z.length; i++) add(cut * QUAD.z[i], cut * QUAD.w[i]);
      for (let i = 0; i < QUAD.z.length; i++) add(cut + (1 - cut) * QUAD.z[i], (1 - cut) * QUAD.w[i]);
    } else {
      for (let i = 0; i < QUAD.z.length; i++) add(QUAD.z[i], QUAD.w[i]);
    }
    return 4 * Math.PI * p.ng * R * R * R * sum;
  }

  function bisect(f, lo, hi, iters) {
    for (let i = 0; i < (iters || 60); i++) {
      const mid = 0.5 * (lo + hi);
      if (f(mid)) lo = mid; else hi = mid;
    }
    return 0.5 * (lo + hi);
  }

  /* Planet clock: largest loud yield Lambda = qN with an empty sky, for duration T.
   * Returns Infinity when even q = 1 leaves the sky empty enough. */
  function planetCeiling(p, T, kind) {
    const delta = T0 - S - T, target = muStar(p);
    if (expected({ ...p, q: 1 }, delta, "planet", kind || "visibility") <= target) return Infinity;
    const lq = bisect(l => expected({ ...p, q: 10 ** l }, delta, "planet", kind || "visibility") < target, -40, 0, 70);
    return 10 ** lq * p.N;
  }

  /* Shared start: largest lead delta (Gyr) of the first emergence over ours.
   * With a window W, delta is also our distance into the window, so it is capped at W.
   * Returns { delta, capped } where capped means the sky never binds inside the range. */
  function sharedLead(p, kind, W) {
    const target = muStar(p), k = kind || "visibility", Wd = W || 0;
    const hi = Wd > 0 ? Math.min(Wd, T0 - S) : T0 - S;
    if (expected(p, hi, "inherited", k, Wd) <= target) return { delta: hi, capped: false };
    return { delta: bisect(d => expected(p, d, "inherited", k, Wd) < target, 0, hi, 60), capped: true };
  }

  // Upper normal tail Phi(-x); erfc after Numerical Recipes, relative error < 1.2e-7.
  function erfc(x) {
    const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
    const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 +
      t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 +
      t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? r : 2 - r;
  }
  const phi = x => 0.5 * erfc(-x / Math.SQRT2);

  // iid_tail.expected_visible: mu when the mean emergence sits z0 sigma after today.
  function iidVisible(p, sigma, z0) {
    const { delay } = kernel(p, "visibility");
    const n = 1500, uMax = 5, h = uMax / n;
    let integral = 0;
    for (let i = 0; i <= n; i++) {
      const u = i * h, tau = u * sigma;
      const r = C * Math.max(tau - delay, 0);
      const f = phi(-z0 - u);
      const pg = -Math.expm1(zones(p, T0 - tau) * Math.log1p(-p.q * f));
      const y = r * r * pg * C * sigma;
      integral += (i === 0 || i === n ? 0.5 : 1) * y;
    }
    return 4 * Math.PI * p.ng * integral * h;
  }

  // iid_tail.expected_arrived: fronts physically here by t0 + wait.
  function iidArrived(p, sigma, z0, wait) {
    const vf = p.v * C, xMin = Math.max(-5 * sigma, S - T0), n = 1500, h = (wait - xMin) / n;
    let integral = 0;
    for (let i = 0; i <= n; i++) {
      const x = xMin + i * h, r = vf * (wait - x);
      const f = Math.min(phi(x / sigma - z0), 1 - 1e-15);
      const pg = -Math.expm1(zones(p, T0 + x) * Math.log1p(-p.q * f));
      integral += (i === 0 || i === n ? 0.5 : 1) * r * r * pg * vf;
    }
    return 4 * Math.PI * p.ng * integral * h;
  }

  /* Independent normal durations with spread sigma (Gyr): fit the mean so the
   * external sky sits on the working line, then read off our position. */
  function durationSpread(p, sigma) {
    const target = muStar(p);
    if (iidVisible(p, sigma, 0) < target) return null; // sky empty even with the mean at today
    const z0 = bisect(z => iidVisible(p, sigma, z) > target, 0, 20, 50);
    const F = phi(-z0);
    const home = p.q * p.N * F;
    const base = iidArrived(p, sigma, z0, 0);
    let wait = NaN;
    if (p.v > 0) {
      const hi = 2 + 20 * sigma / Math.max(p.v, 0.01);
      wait = bisect(w => iidArrived(p, sigma, z0, w) - base < Math.LN2, 0, hi, 40);
    }
    return { z0, F, home, pFirst: Math.exp(-home), meanAfter: z0 * sigma, wait };
  }

  const api = { C, T0, S, HOST_MPC, BASELINE, zones, expected, planetCeiling, sharedLead,
    durationSpread, phi, muStar };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.LineageCap = api;
})(this);
