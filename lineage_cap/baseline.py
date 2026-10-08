"""Run with: uv run python -m lineage_cap.baseline."""

import argparse
import csv
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path

import numpy as np

from .history import History


def write_csv(path, columns, rows):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)


def run(config_path: Path, output: Path):
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    h = History.from_config(config)
    output.mkdir(parents=True, exist_ok=True)
    (output / "config.json").write_bytes(config_bytes)
    t = np.linspace(0, h.now, 2001)
    scenarios = [("both_linear", h), ("count_only", replace(h, beta=0)),
                 ("capacity_only", replace(h, alpha=0))]
    rows = []
    totals = {}
    for name, scenario in scenarios:
        rows.extend(zip([name] * len(t), t, scenario.zones(t),
                        scenario.capacity(t), scenario.total_capacity(t),
                        scenario.spacetime(t)))
        totals[name] = float(scenario.spacetime(h.now))
    write_csv(output / "history.csv",
              ["scenario", "cosmic_age_gyr", "zones", "capacity_per_zone_ee",
               "total_capacity_ee_zones", "spacetime_ee_zone_gyr"], rows)
    births, numbers = h.cohorts()
    exposure = h.exposure(births, h.now)
    write_csv(output / "cohorts.csv",
              ["birth_cosmic_age_gyr", "age_today_gyr", "zones_in_bin",
               "local_exposure_at_bin_midpoint_ee_gyr"],
              zip(births, h.now - births, numbers, exposure))
    earth_age = config["time"]["earth_age_gyr"]
    summary = {
        "scope": "opportunity baseline; no completion or expansion inference yet",
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "assumed_history": asdict(h),
        "units": {"capacity": "Earth-equivalent productive capacity",
                  "spacetime": "Earth-equivalent zone-Gyr",
                  "per_path_exposure": "Earth-equivalent Gyr"},
        "spacetime_today": totals,
        "mean_local_exposure_per_present_zone": float(h.spacetime(h.now) / h.zones_now),
        "oldest_continuous_path_exposure": float(h.capacity_time(h.now)),
        "earth_birth_reference_exposure": float(h.exposure(h.now - earth_age, h.now)),
        "fraction_zones_older_than_earth": float(h.older_fraction(earth_age)),
        "zones_older_than_earth": float(h.zones(h.now - earth_age)),
        "cohort_budget_relative_error": float(
            (np.dot(numbers, exposure) - h.spacetime(h.now)) / h.spacetime(h.now)),
        "sources": config["sources"],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    from .figures import render_all
    render_all(h, config, output)
    print(f"today: {h.zones_now:.3g} suitable zones (assumed)")
    print(f"both linear: {totals['both_linear']:.6g} EE zone-Gyr")
    print(f"count only: {totals['count_only']:.6g} EE zone-Gyr")
    print(f"zones older than Earth: {summary['fraction_zones_older_than_earth']:.1%}")
    print(f"saved CSV, summary, and three PNG/SVG figures to {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/baseline.json"))
    parser.add_argument("--output", type=Path, default=Path("results/baseline"))
    args = parser.parse_args()
    run(args.config, args.output)


if __name__ == "__main__":
    main()
