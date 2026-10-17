"""Note figures: clocks, light cone, planet ceiling, head-start cap,
saturation, start window, first flush.

Run from the repo root::

    MPLCONFIGDIR=.mplconfig uv run python figures/make_note.py

Outputs ``figures/note_fig{1..7}_*.{png,svg}``, numbered in the order
they appear in first-flush-likelihood.qmd.

Design rules (shared by every figure)
-------------------------------------
* Drawn at final print size (6.3 in = the A4 text width with 2.5 cm
  margins) and included at ``width=100%``, so 8-9 pt here is 8-9 pt on
  the page.  No in-figure titles: captions carry the message.
* Ink for text, never series colour.  Hairline solid grids.
* Colour is semantic and fixed across figures: blue = visibility (the
  baseline condition) and the empty-sky-compatible wash; orange =
  physical arrival; aqua = the looser mu = 1 line; neutral grey wash =
  excluded by the sky.  Ordered quantities (Lambda, sigma_T) use a
  one-hue blue ramp, light -> dark with magnitude.
* Categorical slots validated with the dataviz skill's
  validate_palette.js (all-pairs, light): CVD dE 9.2, normal dE 24.0.
  Aqua is below 3:1 contrast on white, so every aqua mark is also
  direct-labelled and dashed.

Variable language
-----------------
``Lambda = q * N`` is the mean number of lineages per galaxy that turn
loud.  ``N = 1e10`` zones per galaxy today (baseline config).  The lead
``delta = t0 - f`` is called "lead" everywhere, matching the text.

Data provenance (per figure)
----------------------------
Fig. 1  Schematic from closed-form Appendix-A counts: N(t) linear ramp
        from s = 0.2 Gyr, planet clock m = N(t - T) at T = 4.6 Gyr,
        inherited clock m = 1[t >= f] N(t) at f = s + T = t0.
Fig. 2  Saved grid ``results/inference/head_start_bounds.csv``
        (planet_linked, remote_visibility, zones_now=1e10, v=0.5c,
        mu=-log 0.05); axes swapped to put duration on x.  Earth-age
        crossing from ``results/inference/earth_origin_q_ceilings.csv``.
Fig. 3  Same saved grid, inherited mode: visibility at mu=-log 0.05
        and mu=1, arrival at mu=-log 0.05.
Fig. 4  Closed-form deadlines t_vis(r) = t0 - D/v - r/c and
        t_arr(r) = t0 - r/v; plateau radius and leads from the
        saturated formula in Appendix A (agrees with the saved grid).
Fig. 5  mu(delta) at fixed Lambda recomputed with
        ``lineage_cap.expansion.expected_count`` and anchored to the
        saved delta_max per q (asserted to return mu_ref there).
Fig. 6  ``lineage_cap.start_spread.spread_bound`` on
        ``configs/start_spread.json`` (q=1, visibility), as in
        figures/make.py.
Fig. 7  Normal-tail shares F(t0 + tau) = Phi(tau/sigma - z0), with z0
        read from ``results/iid_tail/normal_tail_estimate.csv``.
Fig. 8  ``results/iid_tail/n_sweep.csv`` (F(t0) and N F(t0) against N).
Fig. 9  ``results/iid_tail/observer_rates.csv`` (FNC 2x2; the lottery's
        late-filter cell is the planet birth-rate bound).

Fig. 5 now sits in the note's appendix; file numbers no longer follow
page order exactly.
"""

import csv
import json
import math
from pathlib import Path
from statistics import NormalDist
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, LogLocator, NullFormatter
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lineage_cap.expansion import C_MPC_PER_GYR, Geometry, expected_count, galaxy_probability
from lineage_cap.history import History
from lineage_cap.start_spread import spread_bound

OUT = ROOT / "figures"
GRID = ROOT / "results/inference/head_start_bounds.csv"
EARTH_CSV = ROOT / "results/inference/earth_origin_q_ceilings.csv"
TAIL_CSV = ROOT / "results/iid_tail/normal_tail_estimate.csv"
NSWEEP_CSV = ROOT / "results/iid_tail/n_sweep.csv"
RATES_CSV = ROOT / "results/iid_tail/observer_rates.csv"
PEAK_CSV = ROOT / "results/iid_tail/fnc_peak.csv"
CONFIG = json.loads((ROOT / "configs/baseline.json").read_text())
SPREAD_CONFIG = json.loads((ROOT / "configs/start_spread.json").read_text())

N_ZONES = 1e10
SPEED = 0.5
MU_REF = CONFIG["inference"]["reference"]["mu_threshold"]   # -log(0.05)
EARTH_AGE = CONFIG["time"]["earth_age_gyr"]                 # 4.6 Gyr
RAMP_START = CONFIG["time"]["ramp_start_gyr"]               # 0.2 Gyr
NOW = CONFIG["time"]["now_gyr"]                             # 13.8 Gyr
N_G = CONFIG["abundance"]["galaxy_density_mpc3"]            # 0.01 / Mpc^3
HOST_D = CONFIG["expansion"]["host_galaxy_diameter_kpc"] / 1000.0   # Mpc
C_MYR = C_MPC_PER_GYR / 1e3                                 # Mpc / Myr

# Tokens (dataviz reference palette, light surface).
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID_C, AXIS_C, WASH = "#e1e0d9", "#c3c2b7", "#efeeea"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
RAMP = {250: "#86b6ef", 400: "#3987e5", 550: "#1c5cab", 700: "#0d366b"}

WIDTH = 6.3   # in; A4 text width at 2.5 cm margins
LAM_LABEL = "Loud yield  $\\Lambda = qN$  (mean loud lineages per galaxy)"
WHITE_BOX = {"facecolor": "white", "edgecolor": "none", "pad": 1.2, "alpha": .92}


def setup():
    plt.rcParams.update({
        "font.family": "Arial", "font.size": 8.5,
        "mathtext.fontset": "custom", "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": AXIS_C, "axes.linewidth": .8,
        "axes.labelcolor": INK, "axes.labelsize": 9, "text.color": INK,
        "xtick.color": AXIS_C, "ytick.color": AXIS_C,
        "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "xtick.major.size": 3, "ytick.major.size": 3,
        "xtick.minor.size": 1.6, "ytick.minor.size": 1.6,
        "axes.grid": True, "grid.color": GRID_C, "grid.linewidth": .6,
        "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 8,
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
        "svg.fonttype": "none", "svg.hashsalt": "lineage-cap",
    })


def save(fig, name):
    for suffix in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{suffix}", dpi=300, facecolor="white",
                    bbox_inches="tight", pad_inches=.04,
                    metadata={"Date": None} if suffix == "svg" else None)
    plt.close(fig)
    print(f"wrote figures/{name}.png / .svg")


def dot(ax, x, y, color, size=5.5, hollow=False, z=6):
    """Marker with a 1.5 pt white ring so it reads where it crosses lines."""
    ax.plot([x], [y], "o", color=color, markersize=size, zorder=z,
            markerfacecolor="white" if hollow else color,
            markeredgecolor=color if hollow else "white",
            markeredgewidth=1.5 if hollow else 1.2)


def leader(ax, text, xy, xytext, **kw):
    kw.setdefault("fontsize", 8)
    kw.setdefault("color", INK)
    ax.annotate(text, xy=xy, xytext=xytext,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .6,
                            "shrinkA": 2, "shrinkB": 3}, **kw)


def grid_rows(mode, kernel, mu):
    """Saved head-start grid slice: (Lambda, min duration Gyr, lead Myr, constrained)."""
    with GRID.open() as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["clock_kind"] == "elapsed_time"
                and r["lineage_mode"] == mode
                and r["kernel"] == kernel
                and float(r["zones_now"]) == N_ZONES
                and float(r["speed_c"]) == SPEED
                and math.isclose(float(r["mu_threshold"]), mu, rel_tol=1e-9)]
    rows.sort(key=lambda r: float(r["q"]))
    return (np.array([float(r["q"]) * N_ZONES for r in rows]),
            np.array([max(float(r["earliest_duration_min_gyr"]), 0.0) for r in rows]),
            np.array([float(r["head_start_max_gyr"]) * 1e3 for r in rows]),
            np.array([r["constrained_within_history"] == "True" for r in rows]))


def earth_crossing():
    with EARTH_CSV.open() as fh:
        for r in csv.DictReader(fh):
            if (r["clock_kind"] == "elapsed_time" and r["kernel"] == "remote_visibility"
                    and float(r["zones_now"]) == N_ZONES
                    and float(r["speed_c"]) == SPEED
                    and math.isclose(float(r["mu_threshold"]), MU_REF, rel_tol=1e-9)):
                return float(r["q_max"]) * N_ZONES
    raise LookupError("Earth-case ceiling row not found")


def saturated_delta_max_myr(mu, kernel="remote_visibility"):
    """Closed-form plateau (Appendix A); returns (delta_max Myr, radius Mpc)."""
    delay = HOST_D / (SPEED * C_MPC_PER_GYR) if kernel == "remote_visibility" else 0.0
    c_k = C_MPC_PER_GYR if kernel == "remote_visibility" else SPEED * C_MPC_PER_GYR
    radius = (3 * mu / (4 * math.pi * N_G)) ** (1 / 3)
    return (delay + radius / c_k) * 1e3, radius


def rare_ceiling(duration, start):
    """Rare-expander planetary ceiling 3 L mu / (pi n_g c^3 (L - T - D/v)^4)."""
    span = NOW - start
    lead = span - np.asarray(duration) - HOST_D / (SPEED * C_MPC_PER_GYR)
    return 3 * span * MU_REF / (math.pi * N_G * C_MPC_PER_GYR**3 * lead**4)


def sci(x):
    """1.2e-12 -> 1.2x10^-12 in mathtext."""
    mant, exp = f"{x:.1e}".split("e")
    return f"{mant}$\\times$10$^{{{int(exp)}}}$"


def zone_share(t):
    """N(t)/N0 for the linear ramp from s to t0, held flat after t0."""
    return np.clip((np.asarray(t) - RAMP_START) / (NOW - RAMP_START), 0, 1)


# ---------------------------------------------------------------- fig 1
def fig1_clocks():
    t = np.linspace(0, 16, 1601)
    zones = zone_share(t)
    planet = zone_share(t - EARTH_AGE)
    f = NOW                                   # inherited frontier f = s + T, delta = 0
    inherited = np.where(t >= f, zones, 0.0)

    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.55), sharey=True,
                             layout="constrained")
    for ax, emerged, name in ((axes[0], planet, "Planet clock,  $T$ = 4.6 Gyr"),
                              (axes[1], inherited, "Inherited clock,  $f = s + T$")):
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 1.08)
        ax.set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16])
        ax.set_yticks([0, .25, .5, .75, 1], labels=["0", "25%", "50%", "75%", "100%"])
        ax.fill_between(t, zones, color=WASH, linewidth=0, zorder=1)
        ax.plot(t, zones, color=INK2, linewidth=1.0, zorder=2)
        ax.plot(t, emerged, color=BLUE, linewidth=2.0, zorder=4)
        ax.axvline(NOW, color=INK2, linewidth=.7, zorder=3)
        ax.text(NOW + .15, 1.02, "today", fontsize=7.5, color=INK2, va="bottom")
        ax.set_title(name, loc="left", fontsize=9, fontweight="bold", pad=10)
        ax.set_xlabel("Cosmic age (Gyr)")
    axes[0].set_ylabel("Share of today's trajectories")

    # Planet clock: two thirds emerged; first ones 9 Gyr before us.
    share_now = float(zone_share(NOW - EARTH_AGE))
    dot(axes[0], NOW, share_now, BLUE)
    leader(axes[0], f"{share_now:.0%} emerged\nby today", (NOW, share_now), (9.6, .78),
           ha="right")
    first = RAMP_START + EARTH_AGE
    axes[0].annotate("", xy=(first, .09), xytext=(NOW, .09),
                     arrowprops={"arrowstyle": "<->", "color": INK2, "lw": .7,
                                 "shrinkA": 0, "shrinkB": 0})
    axes[0].text(11.0, .12, "first emergences\n9 Gyr before ours",
                 ha="center", fontsize=7.5, color=INK2)
    axes[0].text(1.0, .40, "in play", fontsize=7.5, color=INK2)
    axes[0].text(12.0, .36, "emerged", fontsize=7.5, color=INK)

    # Inherited clock: nobody before f, everybody at f.
    dot(axes[1], NOW, 1.0, BLUE)
    leader(axes[1], "every trajectory in play\nemerges together at $f$", (NOW, .62),
           (1.0, .86), ha="left", va="center")
    leader(axes[1], "none emerged before $f$", (9.0, 0.0), (2.0, .2), va="center")
    save(fig, "note_fig1_clocks")


# ---------------------------------------------------------------- fig 2
def fig2_planetary():
    lam, duration, _, constrained = grid_rows("planet_linked", "remote_visibility", MU_REF)
    crossing = earth_crossing()
    keep = constrained & (duration > 0)
    lam, duration = lam[keep], duration[keep]
    # The saved grid stops at its smallest Lambda (T ~ 1.2 Gyr).  Below that
    # the rare-expander closed form (Appendix A) continues the curve to T = 0.
    short = np.linspace(0.0, duration[0], 40, endpoint=False)
    lam = np.concatenate((rare_ceiling(short, RAMP_START), lam))
    duration = np.concatenate((short, duration))
    i = np.searchsorted(lam, crossing)
    lam = np.insert(lam, i, crossing)
    duration = np.insert(duration, i, EARTH_AGE)
    t_at_one = float(np.interp(0.0, np.log10(lam), duration))

    fig, ax = plt.subplots(figsize=(WIDTH, 3.15), layout="constrained")
    ax.set_yscale("log")
    ax.set_xlim(0, 14)
    ax.set_ylim(1e-10, 1e2)
    ax.yaxis.set_major_locator(FixedLocator([10.0 ** k for k in range(-10, 3, 2)]))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(1.0,), numticks=30))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(range(0, 15, 2))

    ax.fill_between(duration, lam, 1e-10, color=BLUE, alpha=.10, linewidth=0, zorder=1)
    ax.fill_between(duration, lam, 1e2, color=WASH, linewidth=0, zorder=0)
    ax.plot(duration, lam, color=BLUE, linewidth=2.0, zorder=4)

    # Later ramp starts with today's count fixed: shorter head starts, looser
    # ceilings.  Rare limit only, so drawn up to Lambda = 1e-2.
    for start, color in ((2.0, RAMP[400]), (4.0, RAMP[250])):
        t = np.linspace(0.0, NOW - start - 1.0, 400)
        ceiling = rare_ceiling(t, start)
        ax.plot(t, ceiling, color=color, linewidth=1.3, linestyle=(0, (4, 2.5)), zorder=3)
        ax.annotate(f"ramp from\n{start:g} Gyr", xy=(t[-1], ceiling[-1]), xytext=(3, 0),
                    textcoords="offset points", fontsize=7.2, color=INK2,
                    ha="left", va="center", linespacing=.95)

    ax.axhline(1.0, color=INK2, linewidth=.7, zorder=2)
    dot(ax, t_at_one, 1.0, BLUE)
    leader(ax, f"$\\Lambda$ = 1 needs $T \\gtrsim$ {t_at_one:.1f} Gyr:\n"
               "nearly all of cosmic history", (t_at_one, 1.0), (12.6, 1.5e-2),
           ha="right", va="center")

    ax.axvline(EARTH_AGE, color=INK2, linewidth=.8, linestyle=(0, (4, 3)), zorder=3)
    ax.plot([EARTH_AGE], [crossing], marker="*", color=INK, markersize=11,
            markeredgecolor="white", markeredgewidth=.8, zorder=6)
    leader(ax, f"Earth's age, 4.6 Gyr:  $\\Lambda \\lesssim$ 2.1$\\times$10$^{{-8}}$,\n"
               "under one loud lineage per 50 million galaxies",
           (EARTH_AGE, crossing), (1.0, 2e-5), va="center",
           bbox={"facecolor": WASH, "edgecolor": "none", "pad": 1.5})
    ax.text(EARTH_AGE - .15, 20, "fits in Earth's history", ha="right", va="center",
            fontsize=7.5, color=INK2)
    ax.text(EARTH_AGE + .15, 20, "longer than Earth's history", ha="left", va="center",
            fontsize=7.5, color=INK2)

    ax.text(.3, 1e-2, "excluded: earlier lineages\nwould be visible", fontsize=8,
            color=INK2, va="center")
    ax.text(13.6, 3e-10, "compatible with the empty sky", fontsize=8, color=INK2,
            ha="right", va="center")

    ax.set_xlabel("Duration every planet needs,  $T$  (Gyr from the planet's birth)")
    ax.set_ylabel("Largest loud yield  $\\Lambda = qN$")
    top = ax.secondary_xaxis("top", functions=(lambda x: RAMP_START + x,
                                               lambda x: x - RAMP_START))
    top.set_xticks([2, 4, 6, 8, 10, 12])
    top.set_xlabel("First emergences at cosmic age (Gyr)", fontsize=8, color=INK2)
    top.spines["top"].set_visible(True)
    top.spines["top"].set_color(AXIS_C)
    save(fig, "note_fig2_planetary")
    print(f"  fig2: Earth crossing Lambda={crossing:.3e}; T(Lambda=1)={t_at_one:.3f} Gyr")


# ---------------------------------------------------------------- fig 3
def fig3_headstart():
    series = [
        (*grid_rows("inherited", "physical_arrival_diagnostic", MU_REF),
         ORANGE, "-", 1.6, "Arrival, $P$(empty) = 5%",
         saturated_delta_max_myr(MU_REF, "physical_arrival_diagnostic")[0]),
        (*grid_rows("inherited", "remote_visibility", 1.0),
         AQUA, (0, (5, 2.5)), 1.6, "Visibility, $\\mu$ = 1",
         saturated_delta_max_myr(1.0)[0]),
        (*grid_rows("inherited", "remote_visibility", MU_REF),
         BLUE, "-", 2.2, "Visibility, $P$(empty) = 5%  (reference)",
         saturated_delta_max_myr(MU_REF)[0]),
    ]
    _, radius = saturated_delta_max_myr(MU_REF)

    fig, ax = plt.subplots(figsize=(WIDTH, 3.6), layout="constrained")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-9, 1e10)
    ax.set_ylim(6, 2.4e4)
    ax.xaxis.set_major_locator(FixedLocator([10.0 ** k for k in range(-8, 11, 2)]))
    ax.xaxis.set_minor_locator(FixedLocator([10.0 ** k for k in range(-9, 11, 2)]))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks([10, 30, 100, 300, 1000, 3000, 10000],
                  labels=["10", "30", "100", "300", "1,000", "3,000", "10,000"])
    ax.yaxis.set_minor_formatter(NullFormatter())

    ax.axvspan(10, 1e10, color=WASH, linewidth=0, zorder=0)
    ax.axvline(10, color=INK2, linewidth=.6, zorder=1)
    ax.text(16, 1.3e4, "saturated, $\\Lambda \\gtrsim$ 10:\nevery galaxy in reach is loud,\n"
            f"so only reachable volume counts\n(radius {radius:.1f} Mpc, ~3 galaxies)",
            fontsize=7.8, color=INK2, va="top")

    history_myr = (CONFIG["time"]["now_gyr"] - CONFIG["time"]["ramp_start_gyr"]) * 1e3
    handles, first_lams = [], []
    for lam, _, lead, con, color, ls, lw, label, plateau in series:
        y = np.where(con, lead, np.nan)
        first = int(np.flatnonzero(con)[0])
        if first > 0:  # join the curve to the history cap at the last unbounded grid point
            y[first - 1] = history_myr
            first -= 1
        ax.plot(lam, y, color=color, linestyle=ls, linewidth=lw, zorder=4)
        # nudge the close 13.7 / 9.6 plateau labels apart
        y_lab = plateau * {AQUA: .9, BLUE: 1.1}.get(color, 1.0)
        ax.text(1.4e10, y_lab, (f"{plateau:.1f}" if plateau < 20 else f"{plateau:.0f}") + " Myr",
                fontsize=8, color=color, va="center", ha="left", fontweight="bold")
        handles.append(Line2D([], [], color=color, linestyle=ls, linewidth=lw, label=label))
        first_lams.append(lam[first])
        if color == BLUE:
            lam_v, lead_v = lam, lead

    # Below these yields no lead within the history is excluded: the cap is the history itself.
    ax.plot([1e-9, max(first_lams)], [history_myr, history_myr], color=INK2, linestyle=":",
            linewidth=1.2, zorder=3)
    ax.text(1.3e-9, history_myr * 1.12, "whole history, 13.6 Gyr: no bound at smaller $\\Lambda$",
            fontsize=7.5, color=INK2, va="bottom")

    for target, xytext, ha in ((0.01, (1.5e-4, 22), "right"), (1.0, (0.04, 8.5), "right")):
        j = int(np.argmin(np.abs(np.log10(lam_v / target))))
        dot(ax, lam_v[j], lead_v[j], BLUE, hollow=True)
        leader(ax, f"$\\Lambda$ = {target:g}:  {lead_v[j]:.0f} Myr", (lam_v[j], lead_v[j]),
               xytext, ha=ha, va="center")

    ax.legend(handles=handles[::-1], loc="center", bbox_to_anchor=(0.75, 0.42),
              handlelength=2.6, facecolor=WASH, framealpha=1, frameon=True,
              edgecolor="none")
    ax.set_xlabel(LAM_LABEL)
    ax.set_ylabel("Largest lead of the frontier,  $\\delta_{\\max}$  (Myr)")
    save(fig, "note_fig3_headstart")


# ---------------------------------------------------------------- fig 5
def fig5_saturation():
    history = History.from_config(CONFIG)
    geometry = Geometry.from_config(CONFIG)
    lam_grid, _, head_grid, con_grid = grid_rows("inherited", "remote_visibility", MU_REF)
    delay_myr = geometry.delay(SPEED, "remote_visibility") * 1e3
    deltas = np.linspace(0, 80, 321)
    mu_sat = (4 * math.pi / 3) * N_G * (
        C_MYR * np.maximum(deltas - delay_myr, 0)) ** 3

    fig, ax = plt.subplots(figsize=(WIDTH, 3.0), layout="constrained")
    ax.set_xlim(0, 80)
    ax.set_ylim(0, 6)
    ax.set_xticks(range(0, 81, 10))
    ax.axhspan(MU_REF, 6, color=WASH, linewidth=0, zorder=0)
    ax.axhline(MU_REF, color=INK2, linewidth=.8, zorder=2)
    ax.text(79, MU_REF - .1, "$\\mu$ = 3,  $P$(empty) = 5%", ha="right", va="top",
            fontsize=8, color=INK2)
    ax.text(79, MU_REF + .1, "excluded", ha="right", va="bottom", fontsize=8, color=INK2)

    panels = [(0.01, RAMP[250]), (1.0, RAMP[400]), (100.0, RAMP[550]), (1e4, RAMP[700])]
    handles = []
    for lam, color in panels:
        q = lam / N_ZONES
        mu = np.asarray(expected_count(history, geometry, deltas / 1e3, q, SPEED,
                                       "inherited", "elapsed_time", "remote_visibility"),
                        dtype=float)
        j = int(np.argmin(np.abs(np.log10(lam_grid / lam))))
        assert con_grid[j] and math.isclose(lam_grid[j], lam, rel_tol=1e-9)
        delta_saved = head_grid[j]
        mu_at = float(np.interp(delta_saved, deltas, mu))
        assert abs(mu_at - MU_REF) < .02, (lam, mu_at)
        p_g = float(galaxy_probability(N_ZONES, q))
        print(f"  fig5: Lambda={lam:<7g} delta_max={delta_saved:.2f} Myr, "
              f"mu there={mu_at:.4f}, p_g={p_g:.4g}")
        ax.plot(deltas, mu, color=color, linewidth=2.0, zorder=4)
        dot(ax, delta_saved, MU_REF, color, z=7)
        lam_txt = "10$^4$" if lam == 1e4 else f"{lam:g}"
        handles.append(Line2D([], [], color=color, linewidth=2.0,
                              label=f"$\\Lambda$ = {lam_txt}   ({p_g:.0%} of galaxies loud)"))
        if lam == 0.01:
            leader(ax, f"$\\Lambda$ = 0.01:  $\\delta_{{\\max}}$ = {delta_saved:.0f} Myr",
                   (delta_saved, MU_REF), (66, 1.4), ha="center", va="center")
        if lam == 1.0:
            leader(ax, f"$\\Lambda$ = 1:  {delta_saved:.0f} Myr", (delta_saved, MU_REF),
                   (22, 2.2), ha="left", va="center")
        if lam == 1e4:
            leader(ax, f"$\\Lambda$ = 100, 10$^4$:\n{delta_saved:.1f} Myr", (delta_saved, MU_REF),
                   (1.0, 4.7), ha="left", va="center")

    ax.plot(deltas, mu_sat, color=INK, linewidth=1.0, linestyle=(0, (3, 2.5)), zorder=6)
    handles.append(Line2D([], [], color=INK, linewidth=1.0, linestyle=(0, (3, 2.5)),
                          label="saturated limit: every galaxy loud"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(.28, .995),
              handlelength=2.6, fontsize=7.6, labelspacing=.35)
    # Keep legend clear of the curves by placing it in the excluded band's middle.
    ax.set_xlabel("Lead of the frontier over us,  $\\delta$  (Myr)")
    ax.set_ylabel("Expected visible loud galaxies,  $\\mu$")
    save(fig, "note_fig5_saturation")


# ---------------------------------------------------------------- fig 6
def fig6_window():
    h = History.from_config(SPREAD_CONFIG)
    g = Geometry.from_config(SPREAD_CONFIG)
    marks = [.1, .2, .5, 1, 5]
    spans = np.unique(np.concatenate((np.geomspace(.01, 5, 100), marks)))
    bounds = [spread_bound(h, g, 1, .5, "remote_visibility", float(w), 1, MU_REF)
              for w in spans]
    frac = np.array([float(b.percentile_max) for b in bounds])

    fig, ax = plt.subplots(figsize=(WIDTH, 2.9), layout="constrained")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10, 5000)
    ax.set_ylim(.01, 1.3)
    ax.set_xticks([10, 30, 100, 200, 500, 1000, 5000],
                  labels=["10", "30", "100", "200", "500", "1,000", "5,000"])
    ax.set_yticks([.01, .02, .05, .1, .2, .5, 1],
                  labels=["1%", "2%", "5%", "10%", "20%", "50%", "100%"])
    ax.minorticks_off()
    ax.axvspan(100, 200, color=WASH, linewidth=0, zorder=0)
    ax.text(141, .0125, "first-star\nwindow?", ha="center", va="bottom", fontsize=7.5,
            color=INK2)
    ax.fill_between(spans * 1e3, frac, .01, color=BLUE, alpha=.10, linewidth=0, zorder=1)
    ax.plot(spans * 1e3, frac, color=BLUE, linewidth=2.0, zorder=4)
    for w in marks:
        f = frac[np.flatnonzero(spans == w)[0]]
        dot(ax, w * 1e3, f, BLUE)
        txt = f"{f:.1%}".replace(".0%", "%") if f < .1 else f"{f:.0%}"
        if w == max(marks):
            ax.annotate(txt, xy=(w * 1e3, f), xytext=(-3, -11), textcoords="offset points",
                        fontsize=8, ha="right", va="top", color=INK,
                        bbox={"facecolor": "white", "alpha": .75, "edgecolor": "none", "pad": 1.0})
        else:
            ax.annotate(txt, xy=(w * 1e3, f), xytext=(6, 5), textcoords="offset points",
                        fontsize=8, ha="left", va="bottom", color=INK)
    ax.text(11, 1.08, "short windows: any position allowed", fontsize=7.5, color=INK2)
    ax.text(600, .45, "later starts excluded", fontsize=8, color=INK2, ha="left")
    ax.text(14, .05, "our start must lie\nin this front share", fontsize=8, color=INK2)
    ax.set_xlabel("Width of the start window,  $W$  (Myr, log)")
    ax.set_ylabel("Latest permitted position\nof our start in the window (log)")
    save(fig, "note_fig6_window")
    print("  fig6:", {w: round(float(frac[np.flatnonzero(spans == w)[0]]), 4) for w in marks})


# ---------------------------------------------------------------- fig 7
def fig7_flush():
    with TAIL_CSV.open() as fh:
        rows = {round(float(r["sigma_T_myr"])): r for r in csv.DictReader(fh)}
    norm = NormalDist()
    tau = np.linspace(-400, 3600, 2001)          # Myr after today

    fig, ax = plt.subplots(figsize=(WIDTH, 3.7), layout="constrained")
    ax.set_yscale("log")
    ax.set_xlim(-400, 3600)
    ax.set_ylim(1e-16, 3)
    ax.yaxis.set_major_locator(FixedLocator([10.0 ** k for k in range(-16, 1, 2)]))
    ax.yaxis.set_minor_locator(FixedLocator([10.0 ** k for k in range(-15, 1, 2)]))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(range(0, 3601, 500), labels=["today", "+0.5", "+1", "+1.5", "+2",
                                              "+2.5", "+3", "+3.5"])

    one_zone = 1 / N_ZONES
    ax.axhline(one_zone, color=INK2, linewidth=.7, zorder=2)
    ax.text(3550, one_zone * 2.2, "one zone per galaxy at $N = 10^{10}$", fontsize=7.8,
            color=INK2, ha="right", va="bottom")
    ax.axvline(0, color=INK2, linewidth=.7, zorder=2)
    ax.axhline(.5, color=INK2, linewidth=.8, linestyle=(0, (3, 2)), zorder=2)
    ax.text(3550, .4, "half emerged", fontsize=7.5, color=INK2, ha="right", va="top")

    cases = [(30, RAMP[250]), (136, RAMP[400]), (408, RAMP[700])]
    handles = []
    for sigma, color in cases:
        r = rows[sigma]
        z0 = float(r["z0"])
        share = np.array([norm.cdf(x / sigma - z0) for x in tau])
        share = np.where(share > 0, share, np.nan)
        ax.plot(tau, share, color=color, linewidth=2.0, zorder=4)
        f_now = float(r["F_t0"])
        mean_after = float(r["mean_completion_after_t0_myr"])
        dot(ax, 0, f_now, color, z=7)
        dot(ax, mean_after, .5, color, z=7)
        mw = float(r["expected_mw_finishers_by_t0"])
        pct = "1%" if sigma == 136 else ("3%" if sigma == 408 else "0.2%")
        home = "  (home check fails)" if float(r["p_first_in_mw"]) < .05 else ""
        handles.append(Line2D([], [], color=color, linewidth=2.0,
                              label=f"$\\sigma_T$ = {sigma} Myr ({pct}):  at most {mw:.2g} loud ahead"
                                    f" in the Milky Way,  $F(t_0)$ = {sci(f_now)}{home}"))
    leader(ax, "today: the sky caps the count ahead of us;\n"
               "the share $F(t_0)$ scales nearly as $1/N$", (0, 6e-12),
           (500, 2e-14), va="center")
    leader(ax, "mean emergence still to come\n(dots on the 50% line)", (2940, .5),
           (2940, 1e-6), va="center", ha="center")
    fig.legend(handles=handles, loc="outside lower center",
               fontsize=7.4, handlelength=2.2, labelspacing=.3)
    ax.set_xlabel("Time from today (Gyr)")
    ax.set_ylabel("Share of zones emerged,  $F$")
    save(fig, "note_fig7_flush")


# ---------------------------------------------------------------- fig 8
def fig8_nsweep():
    with NSWEEP_CSV.open() as fh:
        rows = list(csv.DictReader(fh))
    cases = [(30, RAMP[250]), (136, RAMP[400]), (408, RAMP[700])]
    fig, (left, right) = plt.subplots(1, 2, figsize=(WIDTH, 2.6), layout="constrained")
    for ax in (left, right):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(5e5, 2e11)
        ax.xaxis.set_major_locator(FixedLocator([1e6, 1e7, 1e8, 1e9, 1e10, 1e11]))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.axvline(N_ZONES, color=INK2, linewidth=.7, linestyle=(0, (4, 3)), zorder=2)
        ax.set_xlabel("Zones per galaxy today,  $N$")
    left.set_ylim(1e-14, 1e-5)
    left.yaxis.set_major_locator(FixedLocator([10.0 ** k for k in range(-14, -4, 2)]))
    right.set_ylim(1e-3, 30)
    right.yaxis.set_major_locator(FixedLocator([1e-3, 1e-2, 1e-1, 1, 10]))
    right.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    for ax in (left, right):
        ax.yaxis.set_minor_formatter(NullFormatter())
    for sigma, color in cases:
        sub = [r for r in rows if round(float(r["sigma_T_myr"])) == sigma]
        n = np.array([float(r["N_t0"]) for r in sub])
        f = np.array([float(r["F_t0"]) for r in sub])
        nf = np.array([float(r["N_F_t0"]) for r in sub])
        left.plot(n, f, color=color, linewidth=2.0, marker="o", markersize=3.5,
                  markeredgecolor="white", markeredgewidth=.8, zorder=4)
        right.plot(n, nf, color=color, linewidth=2.0, marker="o", markersize=3.5,
                   markeredgecolor="white", markeredgewidth=.8, zorder=4)
        right.annotate(f"{sigma} Myr", xy=(n[-1], nf[-1]), xytext=(4, 0),
                       textcoords="offset points", fontsize=7.5, color=INK2, va="center")
        if sigma == 136:
            k = float(sub[0]["exponent_vs_N"])
            left.text(1.5e6, 3e-13, f"$F(t_0) \\propto N^{{-{k:.2f}}}$ at 136 Myr",
                      fontsize=8, color=INK)
    left.set_ylabel("Most emerged by today,  $F(t_0)$")
    right.set_ylabel("Loud ahead in the Milky Way,  $NF(t_0)$")
    right.text(1.2e6, 18, "home check fails above 1", fontsize=7.5, color=INK2, va="center")
    right.axhline(1.0, color=INK2, linewidth=.7, zorder=2)
    handles = [Line2D([], [], color=c, linewidth=2.0, label=f"$\\sigma_T$ = {s} Myr")
               for s, c in cases]
    fig.legend(handles=handles, loc="outside lower center", ncols=3, fontsize=7.6)
    save(fig, "note_fig8_nsweep")


# ---------------------------------------------------------------- fig 9
def fig9_fnc():
    with RATES_CSV.open() as fh:
        rows = {r["scenario"]: float(r["emergences_per_galaxy_per_gyr_at_t0"]) * float(r["p_quiet_home"])
                for r in csv.DictReader(fh)}
    hard = [v for k, v in rows.items() if k.startswith("hard steps")]
    process_late = [v for k, v in rows.items() if "late filter q=" in k]
    planet_late = rows["planet clock, late filter at q ceiling"]
    process = rows["process clock, sigma_T=136 Myr, q=1"]
    cells = [  # (row, loud low, loud high, late low, late high, late is a bound)
        ("Hard-steps lottery,\n$n$ = 3-9", min(hard), max(hard), planet_late, planet_late, True),
        ("Planet clock,\n$T$ = 4.6 Gyr", rows["planet clock, improbability before emergence"],
         rows["planet clock, improbability before emergence"], planet_late, planet_late, False),
        ("Process clock,\n$\\sigma_T$ = 136 Myr", process, process, min(process_late), max(process_late), False),
    ]
    loud_c, late_c = RAMP[700], RAMP[250]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.5), layout="constrained")
    ax.set_xscale("log")
    ax.set_xlim(1e-11, 1e11)
    ax.xaxis.set_major_locator(FixedLocator([10.0 ** k for k in range(-10, 11, 2)]))
    ax.xaxis.set_minor_locator(FixedLocator([10.0 ** k for k in range(-11, 12, 2)]))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_ylim(-.6, 3.1)
    ax.set_yticks(range(3), labels=[c[0] for c in cells])
    ax.tick_params(axis="y", length=0, labelcolor=INK)
    ax.grid(axis="y", visible=False)
    for y, (_, lo, hi, late_lo, late_hi, bound) in enumerate(cells):
        for a, b, color, hollow in ((lo, hi, loud_c, False), (late_lo, late_hi, late_c, True)):
            if b > a:
                ax.plot([a, b], [y, y], color=color, linewidth=5, solid_capstyle="round", zorder=3)
            else:
                dot(ax, a, y, color, size=7, hollow=hollow, z=5)
        if bound:
            ax.annotate("", xy=(late_lo / 30, y), xytext=(late_lo / 1.4, y),
                        arrowprops={"arrowstyle": "-|>", "color": late_c, "lw": 1.4})
            ax.text(late_lo, y + .28, "at most", fontsize=7.2, color=INK2, ha="center")
    # Gap from the lottery's best loud case (its near edge) to the process clock.
    top = 2.62
    for x, y0 in ((max(hard), 0.0), (process, 2.0)):
        ax.plot([x, x], [y0 + .12, top], color=MUTED, linestyle=":", linewidth=.9, zorder=2)
    ax.annotate("", xy=(process, top), xytext=(max(hard), top),
                arrowprops={"arrowstyle": "<->", "color": MUTED, "lw": .8, "shrinkA": 0, "shrinkB": 0})
    ax.text(math.sqrt(process * max(hard)), top + .08,
            f"loud expansion: process clock ahead by at least {process / max(hard):.0e}".replace("e+0", "$\\times10^{") + "}$",
            fontsize=7.5, color=INK, ha="center", va="bottom")
    ax.set_xlabel("Observers like us per galaxy per Gyr at $t_0$, with home still quiet")
    handles = [Line2D([], [], color=loud_c, linewidth=5, label="loud expansion ($q$ = 1, improbability before emergence)"),
               Line2D([], [], color=late_c, marker="o", markerfacecolor="white", linestyle="none",
                      markersize=6, label="late filter ($q$ at its sky ceiling)")]
    fig.legend(handles=handles, loc="outside lower center", ncols=2, fontsize=7.4)
    save(fig, "note_fig9_fnc")


if __name__ == "__main__":
    setup()
    fig1_clocks()
    fig2_planetary()
    fig3_headstart()
    fig5_saturation()
    fig6_window()
    fig7_flush()
    fig8_nsweep()
    fig9_fnc()
