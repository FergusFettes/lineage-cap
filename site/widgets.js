/* Widgets for blog.qmd: formatting, sliders, the parameter sidebar and stat cards.
 * The model itself is site/model.js (window.LineageCap); charts are drawn with Plot in the qmd. */

const SUP = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };
const sup = n => String(n).split("").map(c => SUP[c] || c).join("");

export function sci(x, digits) {
  if (!isFinite(x)) return "∞";
  if (x === 0) return "0";
  const e = Math.floor(Math.log10(Math.abs(x)));
  if (e >= -2 && e <= 3) return x.toPrecision(digits || 2).replace(/\.?0+$/, m => m.includes(".") ? "" : m);
  let m = x / 10 ** e, mm = m.toFixed((digits || 2) - 1);
  if (+mm >= 10) { mm = (1).toFixed((digits || 2) - 1); return mm === "1" ? `10${sup(e + 1)}` : `${mm} × 10${sup(e + 1)}`; }
  return +mm === 1 ? `10${sup(e)}` : `${mm} × 10${sup(e)}`;
}
export const pow10 = l => Math.abs(l - Math.round(l)) < 1e-9 ? ({ 0: "1", 1: "10" }[Math.round(l)] || `10${sup(Math.round(l))}`) : sci(10 ** l);
export function dur(g) {
  if (!isFinite(g)) return "∞";
  if (g < 1) { const m = g * 1000; return `${m < 10 ? m.toFixed(1) : Math.round(m)} Myr`; }
  return `${g.toFixed(g < 10 ? 2 : 1).replace(/0$/, "")} Gyr`;
}
export const pct = x => x >= 0.995 ? "100%" : x >= 0.1 ? `${Math.round(100 * x)}%` : x >= 0.001 ? `${(100 * x).toPrecision(2)}%` : `${sci(100 * x)}%`;
// "one in 3 × 10⁷" for small odds
export const oneIn = x => x >= 0.5 ? pct(x) : `1 in ${sci(1 / x)}`;

function h(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}

/* A styled range input whose .value is in model units.  spec: label, min, max, step (slider
 * units), to/from (slider <-> model units), fmt, ticks, help, cls, value.  Dispatches "input",
 * so it works with OJS viewof and Inputs.bind. */
export function slider(spec) {
  const to = spec.to || (x => x), from = spec.from || (x => x);
  const wrap = h("div", "lc-slider " + (spec.cls || ""));
  const id = "lc-" + Math.random().toString(36).slice(2, 9);
  wrap.innerHTML = `<div class="lc-slider-head"><label for="${id}" title="${(spec.help || "").replace(/"/g, "&quot;")}">${spec.label}</label><output></output></div>
    <input type="range" id="${id}" min="${spec.min}" max="${spec.max}" step="${spec.step}">
    <div class="lc-ticks">${(spec.ticks || []).map(t => `<span>${t}</span>`).join("")}</div>${spec.help ? `<p>${spec.help}</p>` : ""}`;
  const input = wrap.querySelector("input"), out = wrap.querySelector("output");
  let value = spec.value;
  const show = () => { input.value = from(value); out.textContent = spec.fmt(value); };
  Object.defineProperty(wrap, "value", { get: () => value, set: v => { value = v; show(); } });
  input.addEventListener("input", ev => { ev.stopPropagation(); value = to(+input.value); show(); wrap.dispatchEvent(new Event("input", { bubbles: true })); });
  show();
  return wrap;
}

const log = { to: l => 10 ** l, from: v => Math.log10(v) };

// The old site's sliders, keyed by model parameter.
export const SLIDERS = {
  N: { ...log, label: "Trajectories per galaxy, N", min: 2, max: 11, step: 0.1, fmt: v => pow10(Math.log10(v)),
    ticks: ["10²", "10⁵", "10⁸", "10¹¹"], help: "Effective Earth-equivalent trajectories in a galaxy today, our competitors in the race. Note: 10¹⁰." },
  q: { ...log, label: "Chance a lineage turns loud, q", min: -24, max: 0, step: 0.25, fmt: v => pow10(Math.log10(v)),
    ticks: ["10⁻²⁴", "10⁻¹²", "1"], help: "Probability that a lineage which crosses the threshold expands visibly. Note: 1." },
  v: { ...log, label: "Expansion front speed, v", min: -2, max: -0.01, step: 0.01, fmt: v => `${v < 0.1 ? v.toFixed(3) : v.toFixed(2)} c`,
    ticks: ["0.01c", "0.1c", "0.98c"], help: "How fast a loud lineage spreads. Note: 0.5c." },
  ng: { ...log, label: "Galaxy density", min: -3, max: -1, step: 0.05, fmt: v => `${sci(v)} /Mpc³`,
    ticks: ["0.001", "0.01", "0.1"], help: "Galaxies per cubic megaparsec. Note: 0.01." },
  pEmpty: { label: "An empty sky needs a chance of at least", min: 0.01, max: 0.6, step: 0.01,
    fmt: v => `${Math.round(100 * v)}% · μ ${(-Math.log(v)).toFixed(1)}`, ticks: ["1%", "30%", "60%"],
    help: "Lower is more permissive. Note: 5%, about three loud galaxies expected." },
  T: { cls: "planet-param", label: "Planet clock: time to emerge, T", min: 0.5, max: 13.5, step: 0.1, fmt: v => `${v.toFixed(1)} Gyr`,
    ticks: ["0.5", "4.6 (Earth)", "13.5 Gyr"], help: "Earth caps this at 4.6 Gyr for a history run on one planet." },
  W: { cls: "shared-param", label: "Shared start: window width, W", min: -2.1, max: 0.7, step: 0.05,
    to: l => l < -2 ? 0 : 10 ** l, from: v => v <= 0 ? -2.1 : Math.log10(v), fmt: v => v === 0 ? "one date" : dur(v),
    ticks: ["one date", "100 Myr", "5 Gyr"], help: "Galaxies' starts scattered uniformly over this window. The first-star case is 100–200 Myr." },
  sigma: { ...log, cls: "shared-param", label: "Spread of durations, σ", min: -2, max: 0.3, step: 0.02,
    fmt: v => `${dur(v)} · ${(100 * v / 13.6).toPrecision(2)}%`, ticks: ["10 Myr", "100 Myr", "2 Gyr"],
    help: "Standard deviation of independent normal durations, and its share of 13.6 Gyr." },
  n: { label: "Hard steps in the lottery, n", min: 3, max: 9, step: 1, fmt: v => `${v}`, ticks: ["3", "6", "9"],
    help: "Hanson et al. put n near 3 to 9." },
};

export const makeSlider = (key, value) => slider({ ...SLIDERS[key], value });

/* Live numbers for the sidebar: rows of [key, label]; .set({key: text}) updates them. */
export function resultRows(defs) {
  const rows = {};
  for (const [key, label] of defs) {
    const r = h("div", "lc-stat lc-item", `<span>${label}</span><output>–</output>`);
    r.dataset.key = key;
    rows[key] = r;
  }
  return { rows, set: values => { for (const k in values) if (rows[k]) rows[k].querySelector("output").textContent = values[k]; } };
}

/* The left sidebar: sliders and live numbers, each hidden until the text introduces it.
 * A span [phrase]{.lc-param data-param="T first"} reveals items T and first once it
 * scrolls into view; clicking it flashes them.  Docked in quarto's left sidebar on wide
 * screens, a collapsible bottom sheet otherwise. */
export function paramPanel(views, numbers) {
  const panel = h("aside", "lc-panel");
  panel.innerHTML = `<button class="lc-panel-toggle" type="button" aria-expanded="false">Parameters<small></small></button>
    <div class="lc-panel-body">
      <div class="lc-panel-card"><div class="lc-label">Parameters</div><div class="lc-panel-list" data-list="params"></div>
        <p class="lc-panel-empty">Sliders appear here as the text introduces them.</p></div>
      <div class="lc-panel-card" hidden><div class="lc-label">The numbers</div><div class="lc-panel-list" data-list="numbers"></div></div>
      <button class="lc-panel-all" type="button">Show everything</button>
    </div>`;
  const items = {};
  for (const k in views) { views[k].dataset.key = k; views[k].classList.add("lc-item"); items[k] = views[k]; }
  for (const k in numbers.rows) items[k] = numbers.rows[k];
  const markers = [...document.querySelectorAll(".lc-param[data-param]")];
  const keysOf = m => m.dataset.param.split(/\s+/).filter(k => items[k]);
  const order = [...new Set(markers.flatMap(keysOf))];
  for (const k of order) {
    items[k].hidden = true;
    panel.querySelector(`[data-list="${k in views ? "params" : "numbers"}"]`).appendChild(items[k]);
  }
  const shown = new Set(), count = panel.querySelector(".lc-panel-toggle small");
  function flash(k) {
    items[k].classList.remove("lc-new"); void items[k].offsetWidth; items[k].classList.add("lc-new");
  }
  function reveal(k, animate) {
    if (shown.has(k)) return;
    shown.add(k);
    items[k].hidden = false;
    items[k].closest(".lc-panel-card").hidden = false;
    if (animate) flash(k);
    panel.querySelector(".lc-panel-empty").hidden = [...shown].some(x => x in views) || false;
    panel.querySelector(".lc-panel-all").hidden = shown.size === order.length;
    count.textContent = ` · ${shown.size}/${order.length}`;
  }
  // Reveal everything whose marker has come within the lower part of the viewport.
  let first = true;
  function scan() {
    for (const m of markers) if (m.getBoundingClientRect().top < innerHeight * 0.85) keysOf(m).forEach(k => reveal(k, !first));
    first = false;
  }
  let queued = false;
  addEventListener("scroll", () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; scan(); }); } }, { passive: true });
  for (const m of markers) m.addEventListener("click", () => {
    keysOf(m).forEach(k => { reveal(k, false); flash(k); });
    panel.classList.add("open");
  });
  panel.querySelector(".lc-panel-all").addEventListener("click", () => order.forEach(k => reveal(k, false)));
  const toggle = panel.querySelector(".lc-panel-toggle");
  toggle.addEventListener("click", () => toggle.setAttribute("aria-expanded", panel.classList.toggle("open")));
  const wide = matchMedia("(min-width: 992px)");
  function place() {
    const host = document.getElementById("quarto-sidebar-toc-left");
    const dock = wide.matches && host;
    (dock ? host : document.body).appendChild(panel);
    panel.classList.toggle("docked", !!dock);
    panel.classList.toggle("sheet", !dock);
  }
  wide.addEventListener("change", place);
  place();
  scan();
  return panel;
}

/* A result card: { cls, title, sub, big, bigSub, verdict: {ok, text} | null, stats: [[label, value]] , chart } */
export function card(o) {
  const c = h("div", `lc-card ${o.cls || ""}`);
  if (o.title) c.appendChild(h("div", "lc-card-head", `<div class="lc-indicator"></div><div><h4>${o.title}</h4>${o.sub ? `<p>${o.sub}</p>` : ""}</div>`));
  if (o.big != null) c.appendChild(h("div", "lc-big", `<output>${o.big}</output><span>${o.bigSub || ""}</span>`));
  if (o.verdict) c.appendChild(h("div", `lc-verdict ${o.verdict.ok ? "ok" : "no"}`, o.verdict.text));
  if (o.stats && o.stats.length)
    c.appendChild(h("div", "lc-stats", o.stats.map(([k, v]) => `<div class="lc-stat"><span>${k}</span><output>${v}</output></div>`).join("")));
  if (o.chart) c.appendChild(o.chart);
  return c;
}

export function verdict(mu, pEmpty, prefix) {
  const p = Math.exp(-mu), ok = p >= pEmpty - 1e-12;
  const text = ok ? `Sky empty · P = ${pct(p)}` : `Sky not empty · P = ${p < 1e-4 ? sci(p) : pct(p)}`;
  return { ok, text: prefix ? `${prefix}${text.toLowerCase()}` : text };
}

export function row(...children) {
  const r = h("div", "lc-row");
  for (const c of children) r.appendChild(c);
  return r;
}

export function niceTicks(a, b) {
  const span = b - a, raw = span / 4, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map(k => k * mag).find(s => s >= raw);
  const r = [];
  for (let t = Math.ceil(a / step) * step; t <= b + 1e-9; t += step) r.push(Math.round(t / step) * step);
  return r;
}
export const decTicks = (a, b, every) => { const r = []; for (let e = Math.ceil(Math.log10(a)); e <= Math.floor(Math.log10(b)); e += every || 1) r.push(10 ** e); return r; };
