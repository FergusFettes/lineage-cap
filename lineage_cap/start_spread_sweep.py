"""Save distributed-start bounds, ancestry sensitivity and local-sync ceilings."""

import argparse
import csv
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .expansion import KERNELS, Geometry, galaxy_probability
from .history import History
from .start_spread import (
    cosmic_age_at_redshift, spread_bound, spread_expected_count, spread_q_ceiling,
)


def write_rows(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def bound_rows(h, g, q, speed, kernel, span, groups, target):
    bound = spread_bound(h, g, q, speed, kernel, span, groups, target)
    rows = []
    for i, probability in enumerate(q):
        # Blank ranks at zero width, rather than a spurious first-1-in-K.
        offset = None if span == 0 else float(bound.start_offset_max_gyr[i])
        rows.append({
            "start_span_gyr": span, "start_std_gyr": span/math.sqrt(12),
            "groups_per_galaxy": groups, "zones_now": h.zones_now,
            "q_per_zone": float(probability), "speed_c": speed, "kernel": kernel,
            "mu_threshold": target, "empty_probability_threshold": math.exp(-target),
            "earliest_completion_lead_max_gyr": float(bound.lead.delta_max[i]),
            "lead_constrained_within_history": bool(bound.lead.constrained[i]),
            "our_start_offset_max_gyr": offset,
            "start_percentile_max": None if span == 0 else float(bound.percentile_max[i]),
            "first_one_in": None if span == 0 else float(bound.first_one_in[i]),
            "constrained_within_start_window": bool(bound.constrained_within_window[i]),
            "zero_span_baseline_comparison": span == 0,
        })
    return rows


def select(rows, **criteria):
    return [row for row in rows if all(row[key] == value for key, value in criteria.items())]


def verify(h, geometry, rows, ceilings):
    fine = replace(geometry, quadrature_order=192)
    candidates = [r for r in rows if r["lead_constrained_within_history"]]
    rng = np.random.default_rng(20261008)
    sample = rng.choice(len(candidates), min(600, len(candidates)), replace=False)
    errors = []
    for idx in sample:
        r = candidates[idx]
        scenario = replace(h, zones_now=r["zones_now"])
        mu = spread_expected_count(scenario, fine, r["earliest_completion_lead_max_gyr"],
                                   r["q_per_zone"], r["speed_c"], r["kernel"],
                                   r["start_span_gyr"], r["groups_per_galaxy"])
        errors.append(abs(float(mu)/r["mu_threshold"]-1))
    ceiling_errors = []
    for r in ceilings[::max(1, len(ceilings)//80)]:
        if not r["constrained"]:
            continue
        scenario = replace(h, zones_now=r["zones_now"])
        mu = spread_expected_count(scenario, fine, r["our_start_percentile"]*r["start_span_gyr"],
                                   r["q_per_zone_max"], r["speed_c"], r["kernel"],
                                   r["start_span_gyr"])
        ceiling_errors.append(abs(float(mu)/r["mu_threshold"]-1))
    worst = max(errors+ceiling_errors)
    if worst > 1e-5:
        raise AssertionError(f"Refined forward likelihood misses boundary by {worst}")
    return {"method": "forward boundary check at doubled radial quadrature order",
            "seed": 20261008, "boundaries_sampled": len(errors),
            "q_ceilings_sampled": len(ceiling_errors), "quadrature_order": 192,
            "max_relative_error": worst, "tolerance": 1e-5}


def run(config_path, output):
    raw = config_path.read_bytes()
    config = json.loads(raw)
    h, g = History.from_config(config), Geometry.from_config(config)
    setup = config["start_spread"]
    output.mkdir(parents=True, exist_ok=True)
    (output/"config.json").write_bytes(raw)
    grid = config["sweep"]["expansion_probability"]
    probabilities = np.geomspace(grid["min"], grid["max"], grid["points"])
    bounds, correlations, std_rows = [], [], []
    for n in config["sweep"]["zones_now"]:
        scenario = replace(h, zones_now=n)
        for span in setup["spans_gyr"]:
            for speed in config["sweep"]["speed_c"]:
                for kernel in KERNELS:
                    for target in config["inference"]["mu_contours"]:
                        bounds += bound_rows(scenario, g, probabilities, speed, kernel, span, 1, target)
                        for groups in setup["correlation_groups"]:
                            correlations += bound_rows(scenario, g, setup["correlation_q_values"],
                                                       speed, kernel, span, groups, target)
        print(f"start windows and ancestry groups: {n:.0e} zones", flush=True)
    write_rows(output/"start_bounds.csv", bounds)
    write_rows(output/"ancestry_groups.csv", correlations)

    ref = config["inference"]["reference"]
    # Separate table for readers who mean standard deviation by sigma_s.
    for sigma in setup["standard_deviation_reference_gyr"]:
        for kernel in KERNELS:
            std_rows += bound_rows(h, g, ref["q_values"], ref["speed_c"], kernel,
                                   math.sqrt(12)*sigma, 1, ref["mu_threshold"])
    write_rows(output/"standard_deviation_reference.csv", std_rows)

    ceilings = []
    for n in config["sweep"]["zones_now"]:
        scenario = replace(h, zones_now=n)
        for span in setup["local_sync_spans_gyr"]:
            for percentile in setup["local_sync_percentiles"]:
                for speed in config["sweep"]["speed_c"]:
                    for kernel in KERNELS:
                        for target in config["inference"]["mu_contours"]:
                            qmax, constrained = spread_q_ceiling(
                                scenario, g, percentile, span, speed, kernel, 1, target)
                            ceilings.append({
                                "start_span_gyr": span, "our_start_percentile": percentile,
                                "our_start_offset_gyr": span*percentile,
                                "zones_now": n, "speed_c": speed, "kernel": kernel,
                                "mu_threshold": target, "q_per_zone_max": qmax,
                                "constrained": constrained,
                                "expansion_probability_if_all_zones_completed_today":
                                    float(galaxy_probability(n, qmax)),
                            })
        print(f"local synchronizer q ceilings: {n:.0e} zones", flush=True)
    write_rows(output/"local_sync_q_ceilings.csv", ceilings)

    epochs = []
    for seed in setup["epoch_checks_gyr"]:
        for shift_ramp in (False, True):
            scenario = replace(h, start=seed) if shift_ramp else h
            for span in setup["epoch_check_spans_gyr"]:
                for speed in config["sweep"]["speed_c"]:
                    for kernel in KERNELS:
                        new_rows = bound_rows(scenario, g, ref["q_values"], speed, kernel,
                                              span, 1, ref["mu_threshold"])
                        for r in new_rows:
                            raw_delta = r["earliest_completion_lead_max_gyr"]
                            process_age = h.now-seed
                            r.update({
                                "process_seed_epoch_gyr": seed,
                                "formation_ramp_also_shifted": shift_ramp,
                                "demographic_ramp_start_gyr": scenario.start,
                                "process_age_gyr": process_age,
                                "lead_max_with_process_age_cap_gyr": min(raw_delta, process_age),
                                "lead_constrained_within_process_age":
                                    r["lead_constrained_within_history"] and raw_delta < process_age,
                                "frontier_duration_lower_gyr": max(0, process_age-raw_delta),
                            })
                            epochs.append(r)
    write_rows(output/"epoch_sensitivity.csv", epochs)

    cosmology = setup["cosmology_source_check"]
    ages = cosmic_age_at_redshift(cosmology["redshifts"],
                                 h0_km_s_mpc=cosmology["h0_km_s_mpc"],
                                 omega_m=cosmology["omega_m"], omega_r=cosmology["omega_r"])
    verification = verify(h, g, bounds+correlations+std_rows, ceilings)
    (output/"verification.json").write_text(json.dumps(verification, indent=2)+"\n")
    reference = select(bounds, zones_now=h.zones_now, speed_c=ref["speed_c"],
                       mu_threshold=ref["mu_threshold"])
    reference = [r for r in reference if r["q_per_zone"] in ref["q_values"]]
    local_reference = select(ceilings, zones_now=h.zones_now, speed_c=ref["speed_c"],
                             mu_threshold=ref["mu_threshold"], our_start_percentile=.5)
    summary = {
        "config_sha256": hashlib.sha256(raw).hexdigest(),
        "bound_rows": len(bounds), "correlation_rows": len(correlations),
        "standard_deviation_reference_rows": len(std_rows),
        "local_sync_ceiling_rows": len(ceilings), "epoch_check_rows": len(epochs),
        "reference": reference, "local_sync_median_reference": local_reference,
        "redshift_age_check_gyr": dict(zip(map(str, cosmology["redshifts"]), map(float, ages))),
        "z30_to_z15_elapsed_myr": float((ages[-1]-ages[0])*1000),
        "source_interpretation": "Redshift interval is a plausible sensitivity scale, not a measured uniform first-carbon spread. Sagittarius paper dates solar-neighbourhood bursts, not a proven whole-galaxy complexification reset.",
        "verification": verification,
    }
    (output/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    write_report(output, config, summary, std_rows)
    from .start_spread_figures import render_all
    render_all(output)
    print(f"saved {len(bounds)+len(correlations)} bounds; worst refined error {verification['max_relative_error']:.3g}", flush=True)


def write_report(output, config, summary, std_rows):
    ref = summary["reference"]
    remote = "remote_visibility"
    lines = [
        "# Inherited start spreads", "",
        "Reproduce with `make start-spread`; redraw saved grids with `make start-spread-figures`.", "",
        "Uniform bounded start windows; **W is the full span**, sigma_s=W/sqrt(12).",
        "One shared elapsed clock per galaxy is the primary calculation. Our completion today and a common duration make our start offset from the earliest start equal the earliest completion lead. A percentile ceiling is conditional on that model; it is not a posterior probability for our rank.", "",
        "Reference: 10 billion suitable zones per galaxy, galaxy density 0.01/Mpc^3, expansion speed 0.5c, mu=-log(.05)=2.9957, ideal persistent remote visibility after a 30 kpc host crossing. q is per completed zone.", "",
        "## Leading edge with q=1", "",
        "| Full start span W (Myr) | Standard deviation (Myr) | Our allowed offset after earliest (Myr) | First fraction of starts | First 1 in K |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in select(ref, q_per_zone=1., kernel=remote):
        w = r["start_span_gyr"]
        if w == 0:
            continue
        lines.append(f"| {w*1000:g} | {r['start_std_gyr']*1000:.2f} | {r['our_start_offset_max_gyr']*1000:.2f} | {r['start_percentile_max']:.1%} | {r['first_one_in']:.2f} |")
    zero = select(ref, q_per_zone=1., kernel=remote, start_span_gyr=0)[0]
    lines += ["", f"At W=0 the original completion-lead bound is {zero['earliest_completion_lead_max_gyr']*1000:.3f} Myr. There is no start-rank information in a simultaneous-start population. This row is a baseline comparison, not a claim that our start can be later than identical starts.", "",
              "For W>0, a raw lead root beyond W is capped at W when reporting our start offset. That means all percentiles are allowed, not that our lineage started outside its distribution. q=1e-6 reproduces the q=1 shared-galaxy reference because essentially every completed galaxy has an expander.", "",
              "## If sigma_s means standard deviation", "",
              "| sigma_s (Myr) | Full span W (Myr) | Remote: offset (Myr), first fraction | Arrival: offset (Myr), first fraction |",
              "|---:|---:|---|---|",]
    for sigma in config["start_spread"]["standard_deviation_reference_gyr"][1:]:
        rows = select(std_rows, q_per_zone=1., start_span_gyr=math.sqrt(12)*sigma)
        a = select(rows, kernel=remote)[0]
        b = select(rows, kernel="physical_arrival_diagnostic")[0]
        lines.append(f"| {sigma*1000:g} | {a['start_span_gyr']*1000:.2f} | {a['our_start_offset_max_gyr']*1000:.2f}, {a['start_percentile_max']:.1%} | {b['our_start_offset_max_gyr']*1000:.2f}, {b['start_percentile_max']:.1%} |")
    lines += ["", "## Equations and correlation", "",
              "At distance r the eligible deadline is t=t_now-delay-r/c_kernel; completed start fraction F=clip((t-t_now+delta)/W,0,1). With one shared start: p_gal=F*[1-(1-q)^N(t)]. With H equal-sized independent ancestry groups: p_gal=1-{1-F*[1-(1-q)^(N(t)/H)]}^H. With fully independent zone starts: p_gal=1-(1-q*F)^N(t).",
              "", "Integrate mu=4*pi*n_gal*integral r^2*p_gal dr; P(empty)=exp(-mu). Group counts 100 and 10,000 are sensitivity examples, not measurements. Holding the population formation ramp fixed keeps the start-spread test separate from demographic changes.", "",
              "In the saturated one-start-per-galaxy limit, and for delta-delay <= W, mu=pi*n_gal*c_kernel^3*(delta-delay)^4/(3W). This independently checked analytic limit explains why the allowed lead grows only as W^(1/4), while the allowed start fraction shrinks roughly as W^(-3/4). Remote c_kernel=c; arrival c_kernel=v. The two kernels remain alternative calculations.", "",
              "## Local synchronizers: median-start q ceilings", "",
              "These examples use Gyr-wide galaxy-specific starts, retaining many per-zone expansion decisions. A middle-of-window lineage has earlier predecessors by W/2. The older estimate of a q~1e-8 ceiling is not the computed per-zone ceiling in this model.", "",
              "| W (Gyr) | Remote q per zone maximum | Arrival q per zone maximum | Remote: completed-galaxy expansion probability today |",
              "|---:|---:|---:|---:|",]
    for w in config["start_spread"]["local_sync_spans_gyr"]:
        a = select(summary["local_sync_median_reference"], start_span_gyr=w, kernel=remote)[0]
        b = select(summary["local_sync_median_reference"], start_span_gyr=w, kernel="physical_arrival_diagnostic")[0]
        lines.append(f"| {w:g} | {a['q_per_zone_max']:.4g} | {b['q_per_zone_max']:.4g} | {a['expansion_probability_if_all_zones_completed_today']:.4g} |")
    lines += ["", "Local synchronization can instead meet the empty-sky threshold by placing us near its leading edge; it does not universally require a small q. Ceilings above are conditional on a specified median start. Per-zone q must not be equated with the expansion decision of one whole galaxy or cohort.", "",
              "For example, a 5 Gyr window can be placed at cosmic ages 5.6–10.6 Gyr, with our median start at 8.1 Gyr (5.7 Gyr ago) and common process duration 5.7 Gyr. Holding N(t) fixed gives the same median-start likelihood as translating that whole window to an earlier epoch and increasing T by the same amount.", "",
              "## Does the seed epoch change the bound?", "",
              "For an unchanged N(t), a fixed completion frontier produces exactly the same visibility/arrival likelihood at any seed epoch. Thus near-frontier inherited lead rows can be reused for a 9.7 Gyr lineage if the demographics, expansion assumptions and permitted history remain the same. Subtract the new seed date to obtain durations; do not reuse the old duration or capacity columns. If the original lead exceeds the new process age, that row supplies no constraint within the new history.", "",
              "Moving the demographic ramp from 0.2 to 4.1 Gyr also changes N(t), so invariance is no longer exact. `epoch_sensitivity.csv` separates these two operations and reports finite-process-age caps. A completion-date likelihood by itself does not choose a unique starting epoch.", "",
              "## Source check", "",
              f"Using H0={config['start_spread']['cosmology_source_check']['h0_km_s_mpc']:g} km/s/Mpc, Omega_m={config['start_spread']['cosmology_source_check']['omega_m']:g} and illustrative Omega_r={config['start_spread']['cosmology_source_check']['omega_r']:g}, the age conversion gives z=30: {summary['redshift_age_check_gyr']['30']*1000:.2f} Myr; z=15: {summary['redshift_age_check_gyr']['15']*1000:.2f} Myr; separation: {summary['z30_to_z15_elapsed_myr']:.2f} Myr. Cosmology is used here for this conversion only, not for the visibility kernel.", "",
              "[Bromm (2013)](https://arxiv.org/abs/1305.5178) places typical primordial minihalo collapse around z=20–30; [Stacy & Bromm (2014)](https://arxiv.org/abs/1307.1798) simulate a later example at z=15. Together they motivate testing a ~100–200 Myr epoch span. They do not measure a uniform distribution of first-carbon availability across present-day galaxy progenitors. Carbon production, mixing and usable chemistry can add delays. Cosmological parameter scale: [Planck 2018 VI](https://arxiv.org/abs/1807.06209).", "",
              "[Ruiz-Lara et al. (2020)](https://www.nature.com/articles/s41550-020-1097-0) find bursts 5.7, 1.9 and 1.0 Gyr ago in the ~2 kpc solar-neighbourhood sample, with timings supporting Sagittarius perturbations. This motivates a local-event example; it does not establish a whole-galaxy chemical synchronization or a distribution of such events across galaxies.", "",
              "## Saved files and validation", "",
              f"{summary['bound_rows']:,} shared-galaxy bounds; {summary['correlation_rows']:,} ancestry-group sensitivities; {summary['standard_deviation_reference_rows']} standard-deviation reference rows; {summary['local_sync_ceiling_rows']:,} local-sync q ceilings; {summary['epoch_check_rows']} epoch checks. Copied config and SHA256 are in `config.json` and `summary.json`.", "",
              "`start_bounds.csv`, `ancestry_groups.csv`, `standard_deviation_reference.csv`, `local_sync_q_ceilings.csv`, `epoch_sensitivity.csv`; four PNG/SVG figures. Root bounds use 96-node quadrature per smooth radial interval. `verification.json` checks sampled boundaries and q ceilings at 192 nodes. Tests compare independent convolved-sphere integrals, zero-spread recovery, start correlation, inverse likelihoods and age conversion.", "",
              "Flat-space, independent-galaxy Poisson, ideal detection and uniform starts are scenario assumptions. No survey-calibrated posterior or actual halo start distribution is inferred. Capacity-weighted dispersed starts and actual past-lightcone opportunity budgets remain future work.", ""]
    (output/"README.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/start_spread.json"))
    parser.add_argument("--output", type=Path, default=Path("results/start_spread"))
    args = parser.parse_args()
    run(args.config, args.output)


if __name__ == "__main__":
    main()
