"""Static publication exports of the baseline; no frontier inference yet."""

from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .history import History

BLUE = "#2166ac"
ORANGE = "#d97827"
GREEN = "#2d8067"
PURPLE = "#7758a6"


def save(fig, output, name):
    for suffix in ("png", "svg"):
        fig.savefig(Path(output) / f"{name}.{suffix}", dpi=180, facecolor="white")
    plt.close(fig)


def setup():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": "#333333", "text.color": "#222222",
        "axes.edgecolor": "#aaaaaa", "grid.alpha": .2,
        "svg.fonttype": "none",
    })


def timeline(ax, history):
    ax.set_xlim(history.start, history.now)
    ax.set_xlabel("cosmic age (Gyr after the big bang)")
    ax.grid(axis="y")


def history_figure(h: History, output):
    t = np.linspace(h.start, h.now, 1500)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.8))
    fig.subplots_adjust(left=.09, right=.97, top=.85, bottom=.13,
                        hspace=.52, wspace=.32)
    fig.suptitle("Goldilocks opportunity in a Milky Way progenitor history",
                 fontsize=16, x=.09, ha="left", y=.97)
    fig.text(.09, .91,
             f"Fermi benchmark: {h.zones_now:.0e} zones today; "
             f"both ramps linear from cosmic age {h.start:g} Gyr",
             fontsize=11, color="#555555")
    curves = [
        (h.zones(t) / 1e9, "separate suitable zones (billions)",
         "1  Number of trajectories", BLUE),
        (h.capacity(t), "productive capacity per zone (EE)",
         "2  Capacity of each zone", ORANGE),
        (h.total_capacity(t) / 1e9, "total capacity (billion EE zones)",
         "3  Available opportunity at each epoch", GREEN),
        (h.spacetime(t) / 1e9, "accumulated exposure (billion EE zone-Gyr)",
         "4  Integrated Goldilocks spacetime", PURPLE),
    ]
    for ax, (y, label, title, color) in zip(axes.flat, curves):
        ax.plot(t, y, color=color, linewidth=2.6)
        ax.fill_between(t, y, color=color, alpha=.08)
        ax.set_title(title, loc="left", pad=12, fontsize=11)
        ax.set_ylabel(label, fontsize=9)
        timeline(ax, h)
        ax.set_ylim(0, max(y[-1] * 1.14, .1))
        ax.annotate(f"{y[-1]:,.2f}", (t[-1], y[-1]), xytext=(-7, 9),
                    textcoords="offset points", ha="right", color=color,
                    fontweight="bold")
    fig.text(.09, .045,
             "EE = Earth-equivalent productive capacity, normalized to 1 today. "
             "This is an assumed opportunity budget, not a measured assembly rate.",
             fontsize=9, color="#555555")
    save(fig, output, "01_goldilocks_history")


def sensitivity_figure(h: History, zone_counts, output):
    t = np.linspace(h.start, h.now, 1500)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.7))
    fig.subplots_adjust(left=.09, right=.97, top=.78, bottom=.23, wspace=.36)
    fig.suptitle("What the Fermi choices change", x=.09, ha="left", y=.96,
                 fontsize=16)
    fig.text(.09, .88, "Same present-day normalization; different assumed pasts",
             fontsize=11, color="#555555")
    scenarios = [
        ("both ramp: N ∝ x, w ∝ x", h, PURPLE),
        ("count only: N ∝ x, w = 1", replace(h, beta=0), BLUE),
        ("capacity only: N constant, w ∝ x", replace(h, alpha=0), ORANGE),
    ]
    for name, scenario, color in scenarios:
        axes[0].plot(t, scenario.spacetime(t) / 1e9,
                     color=color, linewidth=2.5, label=name)
    axes[0].set_title("Integrated opportunity versus cosmic age", loc="left")
    axes[0].set_ylabel("billion EE zone-Gyr")
    timeline(axes[0], h)
    axes[0].legend(loc="upper left", fontsize=8.4, frameon=False)
    n = np.asarray(zone_counts, dtype=float)
    total = n * h.capacity_now * h.duration / (h.alpha + h.beta + 1)
    axes[1].plot(n, total, color=PURPLE, linewidth=2.5)
    axes[1].scatter(n, total, color=PURPLE, zorder=3)
    axes[1].scatter([h.zones_now], [h.spacetime(h.now)], s=100,
                    facecolors="white", edgecolors=PURPLE, linewidths=2, zorder=4)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("number of separate suitable zones today")
    axes[1].set_ylabel("total exposure today (EE zone-Gyr)")
    axes[1].set_title("Abundance sensitivity, both ramps linear", loc="left")
    axes[1].grid(alpha=.2)
    fig.text(.09, .08,
             "The two single-ramp integrated curves coincide. The capacity-only case "
             "puts today's zone count at the start; it is a comparison, not the baseline.",
             fontsize=8.8, color="#555555")
    fig.text(.09, .035,
             "The open circle is the baseline. Total opportunity scales directly "
             "with zone count and capacity normalization.", fontsize=9, color="#555555")
    save(fig, output, "02_abundance_sensitivity")


def trajectories_figure(h: History, earth_age, output):
    t = np.linspace(h.start, h.now, 1500)
    earth_birth = h.now - earth_age
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.9))
    fig.subplots_adjust(left=.09, right=.97, top=.79, bottom=.23, wspace=.36)
    fig.suptitle("Individual trajectories and the available head starts",
                 x=.09, ha="left", y=.96, fontsize=16)
    fig.text(.09, .88, "An opportunity inventory; completion thresholds have not been inferred",
             fontsize=11, color="#555555")
    axes[0].plot(t, h.capacity_time(t), color=PURPLE, linewidth=2.6,
                 linestyle="--", label="hypothetical inherited path from ramp start")
    for b, color, name in [(5.0, BLUE, "zone born at cosmic age 5 Gyr"),
                           (earth_birth, ORANGE, "zone born when Earth forms")]:
        y = np.where(t >= b, h.exposure(b, t), np.nan)
        axes[0].plot(t, y, color=color, linewidth=2.5, label=name)
        axes[0].annotate(f"{y[-1]:.2f}", (h.now, y[-1]),
                         xytext=(-5, 6), textcoords="offset points",
                         ha="right", color=color)
    axes[0].set_title("Per-path productive exposure", loc="left")
    axes[0].set_ylabel("EE-Gyr along one path")
    timeline(axes[0], h)
    axes[0].legend(loc="upper left", fontsize=8.0, frameon=False)
    age = np.linspace(0, h.duration, 500)
    older = h.older_fraction(age) * 100
    frac_earth = float(h.older_fraction(earth_age)) * 100
    axes[1].plot(age, older, color=GREEN, linewidth=2.5)
    axes[1].axvline(earth_age, color=ORANGE, linestyle=":", linewidth=1.8)
    axes[1].scatter([earth_age], [frac_earth], color=ORANGE, zorder=4)
    axes[1].annotate(f"{frac_earth:.1f}% older than Earth", (earth_age, frac_earth),
                     xytext=(12, 10), textcoords="offset points", fontsize=9)
    axes[1].set_title("Zone ages implied by the count ramp", loc="left")
    axes[1].set_xlabel("zone age today (Gyr)")
    axes[1].set_ylabel("zones at least this old (% of today's total)")
    axes[1].set_xlim(0, h.duration)
    axes[1].set_ylim(0, 105)
    axes[1].grid(axis="y")
    fig.text(.09, .085,
             "Earth's 4.6 Gyr age is a reference. The model proxies zone births by "
             "planet formation; its age distribution is assumed, not fitted to data.",
             fontsize=8.8, color="#555555")
    fig.text(.09, .035,
             "Inherited exposure includes shared ancestral history. Summing it over "
             "descendants would count shared history repeatedly.",
             fontsize=9, color="#555555")
    save(fig, output, "03_trajectory_exposure")


def render_all(history, config, output):
    setup()
    history_figure(history, output)
    sensitivity_figure(history, config["sweep"]["zones_now"], output)
    trajectories_figure(history, config["time"]["earth_age_gyr"], output)
