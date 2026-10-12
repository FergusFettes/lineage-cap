"""Bounded duration variation, separate from the common-duration baseline.

One saturated galaxy clock: completion = s_first + T_min + U + V,
with independent U~Uniform(0,W), V~Uniform(0,D). We infer the maximum
lead delta = t_now - s_first - T_min, then report F_(U+V)(delta).
The two full widths must not be confused with standard deviations.
"""

import csv
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

from .expansion import C_MPC_PER_GYR, Geometry


@lru_cache(maxsize=8)
def normal_nodes(order):
    return np.polynomial.legendre.leggauss(order)


def normal_cdf(x):
    x = np.asarray(x, dtype=float)
    return np.array([.5*math.erfc(-z/math.sqrt(2)) for z in x.flat]).reshape(x.shape)


def normal_completion_cdf(elapsed, start_span, location, sigma):
    """Uniform start plus normal duration conditioned to be nonnegative.

    elapsed is time since earliest start. The normal location is fitted,
    not assumed equal to Earth's lineage age. Sigma is fixed in Gyr.
    """
    if start_span < 0 or sigma <= 0 or location < 0:
        raise ValueError("Require W>=0, sigma>0 and normal location>=0")
    t = np.maximum(np.asarray(elapsed, dtype=float), 0)
    base = float(normal_cdf(-location/sigma))
    if start_span == 0:
        return np.maximum((normal_cdf((t-location)/sigma)-base)/(1-base), 0)
    length = np.minimum(t, start_span)
    z0, z1 = (t-location)/sigma, (t-length-location)/sigma
    def primitive(z):
        return z*normal_cdf(z)+np.exp(-z*z/2)/math.sqrt(2*math.pi)
    return np.clip((sigma*(primitive(z0)-primitive(z1))-length*base)
                   /(start_span*(1-base)), 0, 1)


def normal_count(location, sigma, start_span, geometry, speed_c, history_gyr, order=192):
    """Same saturated host visibility; a smooth early tail, no fitted hard edge."""
    available = max(history_gyr-geometry.delay(speed_c,"remote_visibility"),0)
    nodes, weights = normal_nodes(order)
    travel = available*(nodes+1)/2
    fraction = normal_completion_cdf(available-travel,start_span,location,sigma)
    return (4*math.pi*geometry.galaxy_density*C_MPC_PER_GYR**3
            * available/2*np.dot(weights,travel**2*fraction))


def normal_bound(start_span, sigma, geometry, speed_c, history_gyr,
                 mu_threshold=-math.log(.05), order=192):
    """Infer the smallest normal location compatible with the sky threshold."""
    low, high = 0.0, history_gyr+16*sigma
    if normal_count(low,sigma,start_span,geometry,speed_c,history_gyr,order) < mu_threshold:
        raise ValueError("No positive normal-location boundary for this scenario")
    if normal_count(high,sigma,start_span,geometry,speed_c,history_gyr,order) >= mu_threshold:
        raise ValueError("Normal-location bracket insufficient")
    for _ in range(64):
        mid = (low+high)/2
        if normal_count(mid,sigma,start_span,geometry,speed_c,history_gyr,order) >= mu_threshold:
            low = mid
        else:
            high = mid
    location = (low+high)/2
    rank = float(normal_completion_cdf(history_gyr,start_span,location,sigma))
    return {"normal_location_gyr": location, "completion_fraction_max": rank,
            "first_one_in": 1/rank,
            "forward_mu": normal_count(location,sigma,start_span,geometry,speed_c,history_gyr,2*order)}


def completion_cdf(offset, start_span, duration_span):
    """Stable trapezoidal CDF, including either/both degenerate widths."""
    if any(not math.isfinite(x) or x < 0 for x in (start_span, duration_span)):
        raise ValueError("Full widths must be finite and nonnegative")
    x = np.asarray(offset, dtype=float)
    small, large = sorted((start_span, duration_span))
    if large == 0:
        return (x >= 0).astype(float)
    if small == 0:
        return np.clip(x / large, 0, 1)
    x = np.clip(x, 0, small + large)
    return np.where(x < small, x*x/(2*small*large),
                    np.where(x <= large, (x-small/2)/large,
                             1-(small+large-x)**2/(2*small*large)))


def saturated_count(delta, start_span, duration_span, geometry, speed_c, order=8):
    """Integrate visibility radially, splitting at all CDF polynomial breaks.

    Each piece has degree at most four, so >=3 Gauss nodes is exact up to
    floating point. Using quadrature avoids cancellation of fifth powers.
    This special limit assumes every completed galaxy becomes loud.
    """
    if not math.isfinite(delta) or delta < 0 or not 0 <= speed_c <= 1:
        raise ValueError("Require finite delta>=0 and 0<=speed/c<=1")
    completion_cdf(0, start_span, duration_span)  # Validate widths.
    if order < 3:
        raise ValueError("Need at least three nodes for quartic pieces")
    delay = geometry.delay(speed_c, "remote_visibility")
    available = max(delta-delay, 0)
    if available == 0:
        return 0.0
    cuts = sorted({0.0, available, *[available-k for k in
                  (start_span, duration_span, start_span+duration_span)
                  if 0 < available-k < available]})
    nodes, weights = np.polynomial.legendre.leggauss(order)
    integral = 0.0
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        travel = lo + (hi-lo)*(nodes+1)/2
        integral += (hi-lo)/2 * np.dot(
            weights, travel**2 * completion_cdf(available-travel, start_span, duration_span))
    return 4*math.pi*geometry.galaxy_density*C_MPC_PER_GYR**3 * integral


def duration_bound(start_span, duration_span, geometry, speed_c, history_gyr,
                   mu_threshold=-math.log(.05)):
    """Return lead, completion rank and explicit history/window cap flags."""
    if not math.isfinite(history_gyr) or history_gyr <= 0 or mu_threshold <= 0:
        raise ValueError("Require positive finite history and positive threshold")
    low, high = 0.0, history_gyr
    constrained = saturated_count(high, start_span, duration_span, geometry, speed_c) >= mu_threshold
    if constrained:
        for _ in range(64):
            mid = (low+high)/2
            if saturated_count(mid, start_span, duration_span, geometry, speed_c) >= mu_threshold:
                high = mid
            else:
                low = mid
        delta = (low+high)/2
    else:
        delta = history_gyr
    rank = (float(completion_cdf(delta, start_span, duration_span))
            if start_span+duration_span else None)
    return {"lead_max_gyr": delta, "completion_fraction_max": rank,
            "first_one_in": 1/rank if rank else None,
            "constrained_within_history": constrained,
            "constrained_within_completion_window": constrained and delta < start_span+duration_span}


def run(config_path=Path("configs/duration_spread.json"),
        output=Path("results/duration_spread")):
    raw = config_path.read_bytes()
    cfg = json.loads(raw)
    g = Geometry(cfg["galaxy_density_mpc3"], cfg["host_diameter_mpc"], cfg["launch_delay_gyr"])
    reference = cfg["reference_duration_gyr"]
    rows = []
    for w in cfg["start_spans_gyr"]:
        scenarios = [("full_span", f, reference*f) for f in cfg["duration_full_span_fractions"]]
        scenarios += [("standard_deviation", f, reference*f*math.sqrt(12))
                      for f in cfg["duration_std_fractions"]]
        for definition, fraction, d in scenarios:
            result = duration_bound(w, d, g, cfg["speed_c"],
                                    cfg["now_gyr"]-cfg["earliest_start_gyr"], cfg["mu_threshold"])
            minimum = cfg["now_gyr"]-cfg["earliest_start_gyr"]-result["lead_max_gyr"]
            rows.append({"start_span_gyr": w, "input_definition": definition,
                         "input_fraction_of_reference": fraction,
                         "duration_span_gyr": d, "duration_std_gyr": d/math.sqrt(12),
                         "completion_std_gyr": math.hypot(w, d)/math.sqrt(12),
                         **result, "minimum_duration_gyr": minimum,
                         "mean_duration_gyr": minimum+d/2,
                         "forward_mu": saturated_count(result["lead_max_gyr"], w, d, g, cfg["speed_c"], order=16)})
    output.mkdir(parents=True, exist_ok=True)
    (output/"config.json").write_bytes(raw)
    with (output/"bounds.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    normal_rows = []
    for w in cfg["start_spans_gyr"]:
        for fraction in cfg["duration_std_fractions"]:
            sigma = fraction*reference
            result = normal_bound(w,sigma,g,cfg["speed_c"],
                                  cfg["now_gyr"]-cfg["earliest_start_gyr"],
                                  cfg["mu_threshold"],cfg["normal_quadrature_order"])
            normal_rows.append({"start_span_gyr": w, "duration_std_gyr": sigma,
                                "sigma_fraction_of_reference": fraction, **result})
    with (output/"normal_tail_bounds.csv").open("w",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=normal_rows[0].keys())
        writer.writeheader()
        writer.writerows(normal_rows)
    error = max(abs(r["forward_mu"]/cfg["mu_threshold"]-1) for r in rows)
    if error > 1e-10:
        raise AssertionError(f"Forward boundary error {error}")
    normal_error = max(abs(r["forward_mu"]/cfg["mu_threshold"]-1) for r in normal_rows)
    if normal_error > 1e-7:
        raise AssertionError(f"Normal-tail quadrature error {normal_error}")
    (output/"verification.json").write_text(json.dumps({
        "config_sha256": hashlib.sha256(raw).hexdigest(), "rows": len(rows),
        "method": "8-node piecewise polynomial integration, checked with 16 nodes",
        "max_relative_boundary_error": error, "tolerance": 1e-10,
        "normal_rows": len(normal_rows),
        "normal_method": "radial Gauss-Legendre quadrature at 192 and 384 nodes; analytic start convolution",
        "normal_max_relative_boundary_error": normal_error,
        "normal_tolerance": 1e-7}, indent=2)+"\n")
    print("W(Myr)  duration definition  fraction  span(Gyr)  lead(Myr)  rank(%)  one-in")
    for r in rows:
        print(f"{1000*r['start_span_gyr']:6.0f}  {r['input_definition']:20s} "
              f"{r['input_fraction_of_reference']:5.2f}  {r['duration_span_gyr']:8.3f} "
              f"{1000*r['lead_max_gyr']:9.2f} {100*r['completion_fraction_max']:8.3f} "
              f"{r['first_one_in']:7.2f}")
    print("Normal durations truncated below zero:")
    for r in normal_rows:
        print(f"W={r['start_span_gyr']:.1f} sigma={r['duration_std_gyr']:.3f} "
              f"location={r['normal_location_gyr']:.3f} "
              f"rank={100*r['completion_fraction_max']:.6f}% one-in={r['first_one_in']:.1f}")


if __name__ == "__main__":
    run()
