"""Run reproducible head-start and expansion-suppression sweeps."""

import argparse
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path

import numpy as np

from .baseline import write_csv
from .clocks import KINDS, MODES, required_threshold
from .expansion import KERNELS, Geometry, expected_count, galaxy_probability
from .history import History
from .inference import (
    earth_case_frontier, expansion_probability_ceiling, head_start_bound,
)

BOUND_COLUMNS = [
    "clock_kind", "lineage_mode", "kernel", "zones_now", "q", "speed_c",
    "mu_threshold", "empty_probability_threshold", "head_start_max_gyr",
    "frontier_min_cosmic_age_gyr", "earliest_duration_min_gyr",
    "required_threshold_min", "threshold_unit", "constrained_within_history",
]
CEILING_COLUMNS = [
    "clock_kind", "kernel", "zones_now", "speed_c", "mu_threshold",
    "earth_case_frontier_cosmic_age_gyr", "earth_case_head_start_gyr",
    "q_max", "constrained", "galaxy_expansion_probability_today_at_q_max",
]


def run(config_path: Path, output: Path):
    raw = config_path.read_bytes()
    config = json.loads(raw)
    h, geometry = History.from_config(config), Geometry.from_config(config)
    output.mkdir(parents=True, exist_ok=True)
    (output / "config.json").write_bytes(raw)
    grid = config["sweep"]["expansion_probability"]
    q = np.geomspace(grid["min"], grid["max"], grid["points"])
    bounds, ceilings = [], []
    for n in config["sweep"]["zones_now"]:
        scenario = replace(h, zones_now=n)
        for kind in KINDS:
            for mode in MODES:
                for kernel in KERNELS:
                    for speed in config["sweep"]["speed_c"]:
                        for target in config["inference"]["mu_contours"]:
                            bound = head_start_bound(scenario, geometry, q, speed,
                                                     mode, kind, kernel, target)
                            frontier = scenario.now - bound.delta_max
                            threshold = required_threshold(scenario, frontier, kind)
                            for i, probability in enumerate(q):
                                bounds.append({
                                    "clock_kind": kind, "lineage_mode": mode,
                                    "kernel": kernel, "zones_now": n,
                                    "q": float(probability), "speed_c": speed,
                                    "mu_threshold": target,
                                    "empty_probability_threshold": float(np.exp(-target)),
                                    "head_start_max_gyr": float(bound.delta_max[i]),
                                    "frontier_min_cosmic_age_gyr": float(frontier[i]),
                                    "earliest_duration_min_gyr": float(frontier[i] - h.start),
                                    "required_threshold_min": float(threshold[i]),
                                    "threshold_unit": "Gyr" if kind == "elapsed_time" else "EE-Gyr",
                                    "constrained_within_history": bool(bound.constrained[i]),
                                })
                print(f"head-start sweep: {n:.0e} zones, {kind}, {mode}", flush=True)
            frontier = earth_case_frontier(scenario, config["time"]["earth_age_gyr"], kind)
            for kernel in KERNELS:
                for speed in config["sweep"]["speed_c"]:
                    for target in config["inference"]["mu_contours"]:
                        q_max, constrained = expansion_probability_ceiling(
                            scenario, geometry, frontier, speed, "planet_linked",
                            kind, kernel, target)
                        ceilings.append({
                            "clock_kind": kind, "kernel": kernel, "zones_now": n,
                            "speed_c": speed, "mu_threshold": target,
                            "earth_case_frontier_cosmic_age_gyr": frontier,
                            "earth_case_head_start_gyr": h.now - frontier,
                            "q_max": q_max, "constrained": constrained,
                            "galaxy_expansion_probability_today_at_q_max":
                                float(galaxy_probability(scenario.zones_now, q_max)),
                        })
    write_csv(output / "head_start_bounds.csv", BOUND_COLUMNS,
              ([row[col] for col in BOUND_COLUMNS] for row in bounds))
    write_csv(output / "earth_origin_q_ceilings.csv", CEILING_COLUMNS,
              ([row[col] for col in CEILING_COLUMNS] for row in ceilings))
    reference = config["inference"]["reference"]
    highlights = [row for row in bounds
                  if row["clock_kind"] == "elapsed_time"
                  and row["lineage_mode"] == "inherited"
                  and row["zones_now"] == h.zones_now
                  and row["speed_c"] == reference["speed_c"]
                  and row["mu_threshold"] == reference["mu_threshold"]
                  and any(np.isclose(row["q"], v, rtol=1e-8, atol=0)
                          for v in reference["q_values"])]
    highlights.sort(key=lambda row: (row["kernel"], -row["q"]))
    reference_ceilings = [row for row in ceilings
                         if row["zones_now"] == h.zones_now
                         and row["speed_c"] == reference["speed_c"]
                         and row["mu_threshold"] == reference["mu_threshold"]]
    summary = {
        "scope": "conditional flat-space, ideal-loud process benchmark",
        "config_sha256": hashlib.sha256(raw).hexdigest(),
        "history": asdict(h), "geometry": asdict(geometry),
        "bound_rows": len(bounds), "ceiling_rows": len(ceilings),
        "inherited_reference_bounds": highlights,
        "earth_origin_reference_q_ceilings": reference_ceilings,
        "interpretation": {
            "mu": "expected observable external galaxies",
            "thresholds": "conditional P(empty)=exp(-mu) boundaries; not parameter posterior probabilities",
            "capped_head_start": "13.6 Gyr is the end of the modeled history, not a finite inferred bound when constrained=False",
            "visibility": "ideal detection after a host-galaxy crossing; no measured survey selection function",
            "arrival": "separate non-arrival diagnostic, not multiplied with the visibility likelihood",
            "earth_origin_ceiling": "slowest process allowed by Earth's history; faster routes increase expected predecessors",
        },
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    verification = verify_boundaries(h, geometry, bounds)
    (output / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    write_report(output, summary, config)
    from .inference_figures import render_all
    render_all(h, config, bounds, ceilings, output)
    print(f"saved {len(bounds)} bounds, {len(ceilings)} q ceilings and four figures to {output}")


def verify_boundaries(h, geometry, bounds):
    """Independent forward evaluation with twice the radial integration order."""
    constrained = [row for row in bounds if row["constrained_within_history"]]
    if not constrained:
        return {"sampled_constrained_boundaries": 0, "result": "no constrained boundaries"}
    rng = np.random.default_rng(20261008)
    indices = rng.choice(len(constrained), size=min(500, len(constrained)), replace=False)
    errors = []
    fine = replace(geometry, quadrature_order=2 * geometry.quadrature_order)
    for index in indices:
        row = constrained[index]
        scenario = replace(h, zones_now=row["zones_now"])
        mu = expected_count(scenario, fine, row["head_start_max_gyr"], row["q"],
                            row["speed_c"], row["lineage_mode"], row["clock_kind"], row["kernel"])
        errors.append(abs(float(mu) / row["mu_threshold"] - 1))
    result = {
        "random_seed": 20261008, "sampled_constrained_boundaries": len(indices),
        "refinement_quadrature_order": fine.quadrature_order,
        "max_relative_likelihood_boundary_error": max(errors),
        "median_relative_likelihood_boundary_error": float(np.median(errors)),
        "relative_error_tolerance": 1e-5,
        "passed": max(errors) < 1e-5,
    }
    if not result["passed"]:
        raise RuntimeError(f"Quadrature refinement check failed: {result}")
    return result


def write_report(output, summary, config):
    h = summary["history"]
    r = config["inference"]["reference"]
    lines = [
        "# Conditional empty-sky calculation", "",
        "Reproduce with `make inference`. Exact inputs are in `config.json`;",
        "full grids are in the two CSV files and highlights in `summary.json`.", "",
        f"Baseline: {h['zones_now']:.0e} suitable zones per galaxy today, linear birth",
        f"and per-zone capacity ramps from cosmic age {h['start']:g} Gyr to {h['now']:g} Gyr.",
        "Suitable trajectories complete a deterministic process. Expansion has",
        "probability `q` per completed trajectory and a varied speed. The gap",
        "between our completion and the frontier is inferred, not fixed.", "",
        "## Reference results", "",
        f"Speed: {r['speed_c']:g}c. These are the conditional P(empty) = 5% boundaries.", "",
        "| Expansion probability per trajectory | Visibility head start (Myr) | Arrival head start (Myr) | Inherited minimum duration, visibility (Gyr) |",
        "|---|---:|---:|---:|",
    ]
    rows = summary["inherited_reference_bounds"]
    for q in r["q_values"]:
        selected = [row for row in rows if np.isclose(row["q"], q, rtol=1e-8, atol=0)]
        visibility = next(row for row in selected if row["kernel"] == "remote_visibility")
        arrival = next(row for row in selected if row["kernel"] == "physical_arrival_diagnostic")
        lines.append(f"| {q:.0e} | {1000*visibility['head_start_max_gyr']:.2f} | "
                     f"{1000*arrival['head_start_max_gyr']:.2f} | "
                     f"{visibility['earliest_duration_min_gyr']:.5f} |")
    lines += ["", "## Expansion suppression needed for an Earth-origin clock", "",
              "Use the slowest process compatible with Earth's 4.6 Gyr history.",
              "This gives the most permissive expansion probability; any faster",
              "process makes the conflict with the empty sky stronger.", "",
              "| Process clock | Visibility q ceiling | Arrival q ceiling |", "|---|---:|---:|"]
    for kind in KINDS:
        selected = [row for row in summary["earth_origin_reference_q_ceilings"]
                    if row["clock_kind"] == kind]
        visible = next(row for row in selected if row["kernel"] == "remote_visibility")
        arrival = next(row for row in selected if row["kernel"] == "physical_arrival_diagnostic")
        lines.append(f"| {kind} | {visible['q_max']:.3g} | {arrival['q_max']:.3g} |")
    lines += ["", "## What was calculated", "",
              "For elapsed planetary clocks, completions by time `t` are `N(t-T)`.",
              "For inherited clocks they are `N(t)` after the common frontier date",
              "and zero beforehand. The capacity clock instead requires a fixed",
              "integrated per-path exposure; total galactic exposure is not poured",
              "into a single lineage.", "",
              "At each radius, eligible completions give the probability",
              "`p = 1 - (1-q)^m` of at least one expander in a galaxy.",
              "Integrating `p` against `4*pi*n_g*r^2 dr` gives `mu`; the Poisson",
              "benchmark gives `P(empty) = exp(-mu)`. The two saved boundaries",
              "are `mu=1` (P(empty)=36.8%) and `mu=2.996` (P(empty)=5%).", "",
              "Visibility uses the past light cone after the launch and galaxy",
              "crossing delays. Arrival uses a front propagating at `v`, after",
              "launch only. These kernels are alternatives, not independent",
              "observations combined into a stronger likelihood.", "",
              "## Figures", "",
              "- [Head start versus abundance and q](04_head_start_bounds.png)",
              "- [Expansion speed sensitivity](05_expansion_speed.png)",
              "- [Planetary and inherited clock bounds](06_clock_bounds.png)",
              "- [Earth-origin expansion suppression](07_expansion_suppression.png)", "",
              "Each figure also has an SVG export. A capped curve with",
              "`constrained_within_history=False` supplies no exclusion within",
              "the available history. At q=0 there is no empty-sky bound.", "",
              "## Scope", "",
              "These are conditional scenario calculations: flat space, homogeneous",
              "galaxies at the configured density, ideal persistent visibility after",
              "crossing the host galaxy, and deterministic suitable trajectories.",
              "They are not constraints calibrated to a particular survey. Cosmology,",
              "actual survey sensitivity and correlated transport remain extensions.",
              "Physical non-arrival is a diagnostic whose interpretation also needs",
              "observer conditioning; the primary result here is remote visibility.",
              "A full observer-conditioned joint model remains an extension.", "",
              "## Numerical verification", "",
              "The sweep checks 500 sampled constrained boundaries using twice the",
              "radial quadrature order; details are in `verification.json`. The test",
              "suite also checks analytic rare-expander and saturated limits, birth",
              "cohort counts, probability saturation and thin boundary layers.", ""]
    (output / "README.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/baseline.json"))
    parser.add_argument("--output", type=Path, default=Path("results/inference"))
    args = parser.parse_args()
    run(args.config, args.output)


if __name__ == "__main__":
    main()
