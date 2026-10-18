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

  // iid_tail.expected_new_arrivals: fronts here by t0 + wait from galaxies neither
  // visible nor arrived at t0 (a Poisson process thinned by today's empty sky).
  const GL = legendre(128);
  function iidNewArrivals(p, sigma, z0, wait) {
    const c = C, v = p.v * C, delay = kernel(p, "visibility").delay;
    const loudBy = x => -Math.expm1(zones(p, T0 + x) * Math.log1p(-p.q * Math.min(phi(x / sigma - z0), 1 - 1e-15)));
    const cross = delay / (1 / v - 1 / c), rMax = (wait + delay) / (1 / v - 1 / c);
    const breaks = [...new Set([0, Math.min(cross, rMax), Math.min(v * wait, rMax), rMax])].sort((a, b) => a - b);
    let total = 0;
    for (let k = 0; k + 1 < breaks.length; k++) {
      const a = breaks[k], b = breaks[k + 1];
      for (let i = 0; i < GL.x.length; i++) {
        const r = 0.5 * (b - a) * GL.x[i] + 0.5 * (a + b);
        const pr = loudBy(wait - r / v) - loudBy(Math.max(-delay - r / c, -r / v));
        total += 0.5 * (b - a) * GL.w[i] * r * r * Math.max(pr, 0);
      }
    }
    return 4 * Math.PI * p.ng * total;
  }

  /* Independent normal durations with spread sigma (Gyr): fit the mean so the
   * external sky sits on the working line, then read off our position. */
  // Mean placement z0 (in sigma after today) that puts the external sky on the working line.
  const solveZ = (p, sigma) => bisect(z => iidVisible(p, sigma, z) > muStar(p), 0, 20, 50);

  function durationSpread(p, sigma) {
    const target = muStar(p);
    if (iidVisible(p, sigma, 0) < target) return null; // sky empty even with the mean at today
    const z0 = solveZ(p, sigma);
    const F = phi(-z0);
    const home = p.q * p.N * F;
    const base = iidArrived(p, sigma, z0, 0);
    let wait = NaN, waitArrivalOnly = NaN;
    if (p.v > 0) {
      const hi = 2 + 20 * sigma / Math.max(p.v, 0.01);
      waitArrivalOnly = bisect(w => iidArrived(p, sigma, z0, w) - base < Math.LN2, 0, hi, 40);
      wait = bisect(w => iidNewArrivals(p, sigma, z0, w) < Math.LN2, 0, hi, 40);
    }
    return { z0, F, home, pFirst: Math.exp(-home), meanAfter: z0 * sigma, wait, waitArrivalOnly };
  }

  /* observer_rates.py: observers like us under full non-indexical conditioning, as
   * emergences per galaxy per Gyr at t0 times the chance home is still quiet.  Every
   * branch sits on the same external sky boundary, so the sky factor cancels. */
  const npdf = z => Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI);
  const GL400 = legendre(400);

  // Largest q keeping the iid-tail sky on the boundary for a fixed mean placement z0.
  const qCeiling = (p, sigma, z0) =>
    10 ** bisect(l => iidVisible({ ...p, q: 10 ** l }, sigma, z0) <= muStar(p), -40, 0, 80);

  /* Hard-steps lottery on the linear ramp, loud on emergence: a planet of age a < W emerges
   * at rate k n a^(n-1).  Solves k for the sky; returns the galaxy's emergence rate and
   * expected emergences at t0. */
  function hardSteps(p, n, W) {
    const Wd = W || Infinity, birth = p.N / (T0 - S);
    const expectedAt = (t, k) => {
      const x = Math.max(t - S, 0), inside = Math.min(x, Wd);
      return birth * k * (inside ** (n + 1) / (n + 1) + (isFinite(Wd) ? Wd ** n * Math.max(x - Wd, 0) : 0));
    };
    const tEdge = T0 - HOST_MPC / (p.v * C), span = tEdge - S;
    const breaks = [...new Set([0, span, Math.min(Math.max(span - Wd, 0), span)])].sort((a, b) => a - b);
    const mu = k => {
      let total = 0;
      for (let j = 0; j + 1 < breaks.length; j++) {
        const a = breaks[j], b = breaks[j + 1];
        for (let i = 0; i < GL400.x.length; i++) {
          const u = 0.5 * (b - a) * GL400.x[i] + 0.5 * (a + b);
          total += 0.5 * (b - a) * GL400.w[i] * u * u * -Math.expm1(-expectedAt(tEdge - u, k));
        }
      }
      return 4 * Math.PI * p.ng * C ** 3 * total;
    };
    const k = 10 ** bisect(l => mu(10 ** l) <= muStar(p), -80, 10, 120);
    return { k, rate: birth * k * Math.min(T0 - S, Wd) ** n, emerged: expectedAt(T0, k) };
  }

  /* Each row: { rate, home, obs = rate * home }.  share is the emerged share of zones at t0
   * (our rank) where the branch has one.  Late filters put q at its sky ceiling. */
  function observerRates(p, sigma, opts) {
    const o = { n: 6, W: Infinity, z0s: [3, 1, 0], T: 4.6, ...opts };
    const row = (rate, home, extra) => ({ rate, home, obs: rate * home, ...extra });
    const L = T0 - S, N = p.N, p1 = { ...p, q: 1 };
    const z0 = solveZ(p1, sigma), F = phi(-z0);
    const processLoud = row(N * npdf(z0) / sigma, Math.exp(-N * F), { z0, share: F });
    const processFilter = o.z0s.map(z => {
      const q = qCeiling(p1, sigma, z);
      return row(N * npdf(z) / sigma, Math.exp(-q * N * phi(-z)), { z0: z, q });
    });
    const ceil = planetCeiling(p1, o.T), crossed = 1 - o.T / L, quiet = Math.exp(-ceil * crossed);
    const hs = hardSteps(p1, o.n, o.W);
    return {
      process: { loud: processLoud, filter: processFilter },
      planet: { loud: row(ceil / L, quiet), filter: row(N / L, quiet) },
      lottery: { loud: row(hs.rate, Math.exp(-hs.emerged), { share: hs.emerged / N }), filter: row(N / L, 1) },
    };
  }

  const api = { C, T0, S, HOST_MPC, BASELINE, zones, expected, planetCeiling, sharedLead,
    durationSpread, phi, muStar, solveZ, qCeiling, hardSteps, observerRates };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.LineageCap = api;
})(this);
