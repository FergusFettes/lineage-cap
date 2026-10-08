"""Paper figures, drawn from the saved inference grids in results/inference.

Every bound in the grid depends on q and N only through qN, the number of
expanding civilisations a galaxy would produce if every zone completed, so
each figure plots against qN and shows one curve.
"""

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
GRID = ROOT / "results/inference/head_start_bounds.csv"
OUT = ROOT / "figures"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#222222"
MUTED = "#666666"
EARTH_AGE = 4.6
P_EMPTY = 0.05


def curve(mode):
    """(qN, minimum duration Gyr, head start Myr), 10^10 zones, 0.5c, visibility."""
    mu = -math.log(P_EMPTY)
    rows = [r for r in csv.DictReader(open(GRID))
            if r["clock_kind"] == "elapsed_time"
            and r["kernel"] == "remote_visibility"
            and r["lineage_mode"] == mode
            and float(r["zones_now"]) == 1e10
            and float(r["speed_c"]) == 0.5
            and math.isclose(float(r["mu_threshold"]), mu, rel_tol=1e-9)]
    rows.sort(key=lambda r: float(r["q"]))
    return ([float(r["q"]) * 1e10 for r in rows],
            [max(float(r["earliest_duration_min_gyr"]), 0) for r in rows],
            [float(r["head_start_max_gyr"]) * 1e3 for r in rows])


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
    ax.set_xlabel("Expanding civilisations per galaxy, $qN$")
    ax.grid(alpha=.25, linewidth=.6)


def save(fig, name):
    for suffix in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{suffix}", dpi=200, facecolor="white",
                    bbox_inches="tight")
    plt.close(fig)


def earth_origin():
    qn, duration, _ = curve("planet_linked")
    crossing = next(x for x, d in zip(qn, duration) if d > EARTH_AGE)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    qn_axis(ax)
    ax.fill_between([1e-12, crossing], 0, EARTH_AGE, color=ORANGE, alpha=.08,
                    linewidth=0)
    ax.axhline(EARTH_AGE, color=ORANGE, linewidth=1.5, linestyle=(0, (4, 3)))
    ax.text(1e10, EARTH_AGE + .3, "Earth: first life to us in 4.6 Gyr", ha="right",
            color=INK, fontsize=9)
    ax.plot(qn, duration, color=BLUE, linewidth=2)
    ax.text(3e5, 12.3, "Shortest process\nthe empty sky allows", color=INK,
            fontsize=9, ha="center")
    ax.axvline(crossing, color=MUTED, linewidth=.8, linestyle=":")
    ax.text(crossing * 1.6, 1.0, "Earth origin\npossible only\nto the left",
            color=MUTED, fontsize=8.5)
    ax.set_ylim(0, 14.5)
    ax.set_ylabel("Minimum process duration (Gyr)")
    save(fig, "fig1_earth_origin")
    return crossing


def shared_start():
    qn, _, head = curve("inherited")
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    qn_axis(ax)
    ax.set_yscale("log")
    ax.set_ylim(8, 2e4)
    ax.axhline(13600, color=MUTED, linewidth=.8, linestyle=":")
    ax.text(1e10, 9500, "All of cosmic history (13.6 Gyr)", color=MUTED, ha="right",
            fontsize=8.5)
    ax.plot(qn, head, color=BLUE, linewidth=2)
    plateau = head[-1]
    ax.text(3e3, plateau * 1.35, f"Plateau: {plateau:.1f} Myr", color=INK,
            fontsize=9)
    ax.set_ylabel("Maximum head start of the first\nlineages over us (Myr)")
    save(fig, "fig2_shared_start")


if __name__ == "__main__":
    setup()
    print("earth-origin crossing qN", earth_origin())
    shared_start()
