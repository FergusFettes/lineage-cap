"""Paper figures from saved grids, with targeted roots from saved configurations.

qN is the expected expansion yield if all present-day zones complete. Curves
approximately collapse against it; finite-q corrections are audited in notes.
"""

import csv
import json
import math
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lineage_cap.expansion import Geometry
from lineage_cap.history import History
from lineage_cap.inference import earth_case_frontier, expansion_probability_ceiling
from lineage_cap.start_spread import spread_bound

GRID = ROOT / "results/inference/head_start_bounds.csv"
OUT = ROOT / "figures"
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#b8773d", "#222222", "#666666"
CONFIG = json.loads((ROOT / "configs/baseline.json").read_text())
SPREAD_CONFIG = json.loads((ROOT / "configs/start_spread.json").read_text())
EARTH_AGE = CONFIG["time"]["earth_age_gyr"]
MU = CONFIG["inference"]["reference"]["mu_threshold"]


def curve(mode):
    """qN, minimum duration Gyr, lead Myr, history-constrained flags."""
    with GRID.open() as stream:
        rows = [r for r in csv.DictReader(stream)
                if r["clock_kind"] == "elapsed_time"
                and r["kernel"] == "remote_visibility"
                and r["lineage_mode"] == mode
                and float(r["zones_now"]) == 1e10
                and float(r["speed_c"]) == .5
                and math.isclose(float(r["mu_threshold"]), MU, rel_tol=1e-9)]
    rows.sort(key=lambda r: float(r["q"]))
    return (np.array([float(r["q"]) * 1e10 for r in rows]),
            np.array([max(float(r["earliest_duration_min_gyr"]), 0) for r in rows]),
            np.array([float(r["head_start_max_gyr"]) * 1e3 for r in rows]),
            np.array([r["constrained_within_history"] == "True" for r in rows]))


def setup():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": "#aaaaaa", "svg.fonttype": "none",
    })


def qn_axis(ax):
    ax.set_xscale("log")
    ax.set_xlim(1e-12, 1e10)
    ax.set_xticks([10.0 ** k for k in range(-12, 11, 2)])
    ax.set_xlabel("Expected expansion if all zones complete, $qN$")
    ax.grid(alpha=.2, linewidth=.6)
    ax.set_axisbelow(True)


def save(fig, name):
    for suffix in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{suffix}", dpi=200, facecolor="white",
                    bbox_inches="tight")
        if suffix == "svg":
            path = OUT / f"{name}.svg"
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)


def earth_origin():
    qn, duration, _, _ = curve("planet_linked")
    h, g = History.from_config(CONFIG), Geometry.from_config(CONFIG)
    q, constrained = expansion_probability_ceiling(
        h, g, earth_case_frontier(h, EARTH_AGE, "elapsed_time"), .5,
        "planet_linked", "elapsed_time", "remote_visibility", MU)
    assert constrained
    crossing = q * h.zones_now
    # Insert the actual root, so shading stops at the exact Earth-age crossing.
    i = np.searchsorted(qn, crossing)
    qn = np.insert(qn, i, crossing)
    duration = np.insert(duration, i, EARTH_AGE)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    qn_axis(ax)
    allowed = qn <= crossing
    ax.fill_between(qn[allowed], duration[allowed], EARTH_AGE,
                    color=ORANGE, alpha=.12, linewidth=0)
    ax.axhline(EARTH_AGE, color=ORANGE, linewidth=1.3, linestyle=(0, (4, 3)))
    ax.text(1e10, EARTH_AGE + .3, "Earth's age: terrestrial upper limit (4.6 Gyr)",
            ha="right", fontsize=8.7)
    ax.plot(qn, duration, color=BLUE, linewidth=2)
    ax.text(3e5, 11.8, "Shortest process\nthe empty sky allows", fontsize=9,
            ha="center")
    ax.axvline(crossing, color=MUTED, linewidth=.8, linestyle=":")
    ax.annotate("Earth-age crossing\n$qN = 2.06\\times10^{-8}$", xy=(crossing, EARTH_AGE),
                xytext=(2e-5, 7.5), color=MUTED, fontsize=8.5,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .7})
    ax.text(2e-12, 2.5, "Allowed\nterrestrial\ndurations", color=MUTED, fontsize=8)
    ax.set_ylim(0, 14.5)
    ax.set_ylabel("Minimum process duration (Gyr)")
    save(fig, "fig1_earth_origin")
    return crossing


def shared_start():
    qn, _, head, constrained = curve("inherited")
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    qn_axis(ax)
    ax.set_yscale("log")
    ax.set_ylim(8, 2e4)
    # Capped values are search limits, not likelihood-derived upper bounds.
    ax.plot(qn, np.where(constrained, head, np.nan), color=BLUE, linewidth=2)
    ax.plot(qn, np.where(~constrained, head, np.nan), color=MUTED,
            linewidth=1.3, linestyle=(0, (4, 3)))
    ax.text(2e-12, 1400, "No constraint\nwithin modeled\nhistory\n(13.6 Gyr)",
            color=MUTED, fontsize=7.8)
    ax.text(3e3, head[-1] * 1.4, f"Plateau: {head[-1]:.1f} Myr", fontsize=9)
    ax.set_ylabel("Maximum candidate frontier lead (Myr)")
    ax.text(.98, .94, "Zero-spread benchmark", transform=ax.transAxes,
            ha="right", fontsize=9, color=MUTED)
    save(fig, "fig2_shared_start")


def start_spread():
    h = History.from_config(SPREAD_CONFIG)
    g = Geometry.from_config(SPREAD_CONFIG)
    # Targeted W roots supplement the saved coarse window grid; no new assumptions.
    spans = np.unique(np.concatenate((np.geomspace(.01, 5, 100),
                                      [.1, .2, .5, 1, 5])))
    bounds = [spread_bound(h, g, 1, .5, "remote_visibility", float(w), 1, MU)
              for w in spans]
    fractions = np.array([float(b.percentile_max) for b in bounds])
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10, 5000)
    ax.set_ylim(.01, 1.3)
    ax.axvspan(100, 200, color=ORANGE, alpha=.12, linewidth=0)
    ax.plot(spans*1000, fractions, color=BLUE, linewidth=2)
    points = {}
    for w in [.1, .2, .5, 1, 5]:
        f = fractions[np.flatnonzero(spans == w)[0]]
        points[w] = f
        ax.plot(w*1000, f, "o", color=BLUE, markersize=4)
        ax.annotate(f"{f*100:.1f}%", xy=(w*1000, f),
                    xytext=(-8 if w == 5 else 7, -19 if w == 5 else 9), textcoords="offset points",
                    ha="right" if w == 5 else "left", fontsize=8.5)
    ax.set_xticks([10, 30, 100, 200, 500, 1000, 5000],
                  labels=["10", "30", "100", "200", "500", "1,000", "5,000"])
    ax.set_yticks([.01, .02, .05, .1, .2, .5, 1],
                  labels=["1%", "2%", "5%", "10%", "20%", "50%", "100%"])
    ax.minorticks_off()
    ax.set_xlabel("Full start-window width, $W$ (Myr)")
    ax.set_ylabel("Latest permitted fraction of the start window")
    ax.text(18, .015, "Shading: illustrative first-carbon window\nConditional rank ceiling; not a posterior probability",
            color=MUTED, fontsize=8)
    ax.grid(alpha=.2, linewidth=.6)
    ax.set_axisbelow(True)
    save(fig, "fig3_start_spread")
    return points


if __name__ == "__main__":
    setup()
    print("Earth-age crossing qN:", earth_origin())
    shared_start()
    print("Start-window fraction ceilings:", start_spread())
