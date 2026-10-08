"""Plot saved-grid frontier bounds and the expansion suppression needed to escape."""

import math

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from .figures import BLUE, GREEN, ORANGE, PURPLE, save, setup

COLORS = [BLUE, GREEN, PURPLE, ORANGE, "#555555"]
KERNEL_LABELS = {
    "remote_visibility": "remote visibility · primary scenario",
    "physical_arrival_diagnostic": "physical arrival · separate diagnostic",
}


def select(rows, **criteria):
    def matches(row):
        for key, value in criteria.items():
            if isinstance(value, (int, float)):
                if not math.isclose(row[key], value, rel_tol=1e-9, abs_tol=0):
                    return False
            elif row[key] != value:
                return False
        return True
    return [row for row in rows if matches(row)]


def pair(title, subtitle):
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 6.6))
    fig.subplots_adjust(left=.085, right=.975, top=.77, bottom=.32, wspace=.34)
    fig.suptitle(title, x=.085, ha="left", y=.97, fontsize=16)
    fig.text(.085, .89, subtitle, fontsize=10.5, color="#555555")
    return fig, axes


def q_axis(ax, config):
    ax.set_xscale("log")
    ax.set_xlim(config["sweep"]["expansion_probability"]["min"], 1)
    ax.set_xticks([10.0 ** k for k in range(-24, 1, 4)])
    ax.set_xlabel("expansion probability per completed trajectory, q")
    ax.grid(alpha=.2)


def head_axis(ax, h, config):
    q_axis(ax, config)
    ax.set_yscale("log")
    ax.set_ylim(8, h.duration * 1300)
    ax.set_ylabel("maximum permitted head start (Myr)")
    ax.axhline(h.duration * 1000, color="#888888", linewidth=1, linestyle=":")


def head_start_figure(h, config, bounds, output):
    speed = config["inference"]["reference"]["speed_c"]
    fig, axes = pair("How much earlier could the frontier have appeared?",
                     f"Inherited clocks · expansion speed {speed:g}c · varied suitable-zone abundance")
    thresholds = config["inference"]["mu_contours"]
    for ax, kernel in zip(axes, KERNEL_LABELS):
        for n, color in zip(config["sweep"]["zones_now"], COLORS):
            for target, style in zip(thresholds, ["--", "-"]):
                rows = sorted(select(bounds, clock_kind="elapsed_time", lineage_mode="inherited",
                                     kernel=kernel, zones_now=n, speed_c=speed, mu_threshold=target),
                              key=lambda row: row["q"])
                ax.plot([row["q"] for row in rows],
                        [1000 * row["head_start_max_gyr"] for row in rows],
                        color=color, linestyle=style, linewidth=2 if style == "-" else 1.1,
                        alpha=1 if style == "-" else .6)
        head_axis(ax, h, config)
        ax.set_title(KERNEL_LABELS[kernel], loc="left", fontsize=11)
    handles = [Line2D([0], [0], color=color, linewidth=2,
                      label=f"{n:.0e} zones today")
               for n, color in zip(config["sweep"]["zones_now"], COLORS)]
    handles += [Line2D([0], [0], color="#444444", linestyle="-", label="P(empty) = 5%"),
                Line2D([0], [0], color="#444444", linestyle="--", label="P(empty) = 36.8%")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.53, .11),
               ncol=3, frameon=False, fontsize=9)
    fig.text(.085, .055,
             "Plateaus at 13.6 Gyr mark no exclusion within the modeled history. At q = 0 there is no bound.",
             fontsize=9, color="#555555")
    fig.text(.085, .02,
             "Conditional flat-space benchmark: ideal persistent loudness; galaxy density 0.01/Mpc³. Visibility and arrival are not combined.",
             fontsize=8.7, color="#555555")
    save(fig, output, "04_head_start_bounds")


def speed_figure(h, config, bounds, output):
    target = config["inference"]["reference"]["mu_threshold"]
    fig, axes = pair("Expansion speed changes visibility and arrival differently",
                     f"Inherited clocks · {h.zones_now:.0e} zones today · P(empty) = 5% boundary")
    for ax, kernel in zip(axes, KERNEL_LABELS):
        for speed, color in zip(config["sweep"]["speed_c"], COLORS):
            rows = sorted(select(bounds, clock_kind="elapsed_time", lineage_mode="inherited",
                                 kernel=kernel, zones_now=h.zones_now, speed_c=speed,
                                 mu_threshold=target), key=lambda row: row["q"])
            ax.plot([row["q"] for row in rows],
                    [1000 * row["head_start_max_gyr"] for row in rows],
                    color=color, linewidth=2, label=f"{speed:g}c")
        head_axis(ax, h, config)
        ax.set_title(KERNEL_LABELS[kernel], loc="left", fontsize=11)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center",
               bbox_to_anchor=(.53, .11), ncol=5, frameon=False, fontsize=9)
    fig.text(.085, .055,
             "Visibility propagates at c after the galaxy is transformed. Arrival propagates at v; very slow fronts permit large leads.",
             fontsize=9, color="#555555")
    fig.text(.085, .02,
             "Flat space, ideal detection, 30 kpc host crossing for visibility. Capped curves mark no exclusion within the modeled history.",
             fontsize=8.7, color="#555555")
    save(fig, output, "05_expansion_speed")


def clock_figure(h, config, bounds, output):
    reference = config["inference"]["reference"]
    fig, axes = pair("Which process clocks fit Earth's history and the empty sky?",
                     f"Remote visibility · {h.zones_now:.0e} zones · {reference['speed_c']:g}c · P(empty) = 5% boundary")
    age = config["time"]["earth_age_gyr"]
    for ax, kind in zip(axes, ["elapsed_time", "integrated_capacity"]):
        for mode, color, label in [("planet_linked", BLUE, "planet-linked starts"),
                                    ("inherited", PURPLE, "inherited cosmic start")]:
            rows = sorted(select(bounds, clock_kind=kind, lineage_mode=mode,
                                 kernel="remote_visibility", zones_now=h.zones_now,
                                 speed_c=reference["speed_c"], mu_threshold=reference["mu_threshold"]),
                          key=lambda row: row["q"])
            ax.plot([row["q"] for row in rows],
                    [row["required_threshold_min"] for row in rows],
                    color=color, linewidth=2.5, label=label)
        terrestrial = age if kind == "elapsed_time" else float(h.exposure(h.now-age, h.now))
        cosmic = h.duration if kind == "elapsed_time" else float(h.capacity_time(h.now))
        ax.axhspan(0, terrestrial, color=ORANGE, alpha=.08)
        ax.axhline(terrestrial, color=ORANGE, linestyle=":", linewidth=1.8,
                   label="Earth-origin upper limit")
        ax.axhline(cosmic, color="#888888", linestyle=":", linewidth=1)
        ax.set_ylim(0, cosmic * 1.1)
        q_axis(ax, config)
        ax.set_title("elapsed-time clock" if kind == "elapsed_time" else "capacity-weighted clock",
                     loc="left", fontsize=11)
        ax.set_ylabel("minimum required duration (Gyr)" if kind == "elapsed_time"
                      else "minimum required exposure (EE-Gyr)")
        ax.legend(loc="lower right", frameon=False, fontsize=8.5)
    fig.text(.085, .12,
             "For Earth origin, a sky-derived lower bound above the orange line conflicts with the observed terrestrial history.",
             fontsize=9, color="#555555")
    fig.text(.085, .07,
             "The common early-start case can use the full cosmic history. Its distance from the frontier is inferred from these bounds.",
             fontsize=9, color="#555555")
    fig.text(.085, .025,
             "Capacity-weighted exposure is not elapsed time. No environmental variation or hard-step completion lottery is added.",
             fontsize=8.8, color="#555555")
    save(fig, output, "06_clock_bounds")


def suppression_figure(h, config, ceilings, output):
    target = config["inference"]["reference"]["mu_threshold"]
    fig, axes = pair("How strongly must expansion be suppressed for Earth origin?",
                     "Maximum q for the slowest process compatible with Earth's history · P(empty) = 5% boundary")
    for ax, kind in zip(axes, ["elapsed_time", "integrated_capacity"]):
        for n, color in zip(config["sweep"]["zones_now"], COLORS):
            for kernel, style in [("remote_visibility", "-"), ("physical_arrival_diagnostic", "--")]:
                rows = sorted(select(ceilings, clock_kind=kind, kernel=kernel,
                                     zones_now=n, mu_threshold=target), key=lambda row: row["speed_c"])
                restricted = [row for row in rows if row["constrained"]]
                ax.plot([row["speed_c"] for row in restricted], [row["q_max"] for row in restricted],
                        color=color, linestyle=style, linewidth=2 if style == "-" else 1.4,
                        marker="o", markersize=3)
                unrestricted = [row for row in rows if not row["constrained"]]
                ax.scatter([row["speed_c"] for row in unrestricted],
                           [row["q_max"] for row in unrestricted], marker="^", s=40,
                           facecolors="white", edgecolors=color, zorder=4)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("expansion front speed (fraction of c)")
        ax.set_ylabel("maximum permitted expansion probability, q")
        ax.set_ylim(1e-20, 3)
        ax.grid(alpha=.2)
        ax.set_title("elapsed-time clock" if kind == "elapsed_time" else "capacity-weighted clock",
                     loc="left", fontsize=11)
    handles = [Line2D([0], [0], color=color, label=f"{n:.0e} zones today", linewidth=2)
               for n, color in zip(config["sweep"]["zones_now"], COLORS)]
    handles += [Line2D([0], [0], color="#444444", linestyle="-", label="visibility"),
                Line2D([0], [0], color="#444444", linestyle="--", label="arrival diagnostic")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.53, .11),
               ncol=3, frameon=False, fontsize=9)
    fig.text(.085, .055,
             "Triangles at q = 1 mark no exclusion from non-arrival for that slow front. Visibility is the primary scenario.",
             fontsize=9, color="#555555")
    fig.text(.085, .02,
             "q is per completed trajectory, not per year. Faster development requires even stronger suppression than the limits shown.",
             fontsize=8.7, color="#555555")
    save(fig, output, "07_expansion_suppression")


def render_all(h, config, bounds, ceilings, output):
    setup()
    head_start_figure(h, config, bounds, output)
    speed_figure(h, config, bounds, output)
    clock_figure(h, config, bounds, output)
    suppression_figure(h, config, ceilings, output)


def main():
    """Re-render figures from saved numbers without repeating the inference."""
    import argparse
    import csv
    import json
    from pathlib import Path
    from .history import History

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/inference"))
    args = parser.parse_args()
    config = json.loads((args.input / "config.json").read_text())
    text_fields = {"clock_kind", "lineage_mode", "kernel", "threshold_unit"}
    bool_fields = {"constrained", "constrained_within_history"}

    def load(name):
        with (args.input / name).open() as stream:
            return [{key: value if key in text_fields else
                     value == "True" if key in bool_fields else float(value)
                     for key, value in row.items()}
                    for row in csv.DictReader(stream)]

    render_all(History.from_config(config), config, load("head_start_bounds.csv"),
               load("earth_origin_q_ceilings.csv"), args.input)


if __name__ == "__main__":
    main()
