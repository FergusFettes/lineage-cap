"""Analytic opportunity histories, with time in Gyr and capacity in EE units."""

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class History:
    now: float = 13.8
    start: float = 0.2
    zones_now: float = 1e10
    capacity_now: float = 1.0
    alpha: float = 1.0
    beta: float = 1.0

    def __post_init__(self):
        values = (self.now, self.start, self.zones_now, self.capacity_now,
                  self.alpha, self.beta)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("History parameters must be finite")
        if not 0 <= self.start < self.now:
            raise ValueError("Require 0 <= start < now")
        if min(self.zones_now, self.capacity_now, self.alpha, self.beta) < 0:
            raise ValueError("Counts, capacity and exponents must be nonnegative")

    @classmethod
    def from_config(cls, config):
        a, h, t = config["abundance"], config["history"], config["time"]
        return cls(t["now_gyr"], t["ramp_start_gyr"],
                   a["stars_now"] * a["appropriate_fraction"]
                   * a["trajectories_per_appropriate_zone"],
                   a["per_zone_capacity_now"], h["count_exponent"],
                   h["capacity_exponent"])

    @property
    def duration(self):
        return self.now - self.start

    def fraction(self, time):
        return np.clip((np.asarray(time) - self.start) / self.duration, 0, 1)

    def _ramp(self, time, exponent):
        return np.where(np.asarray(time) < self.start, 0,
                        self.fraction(time) ** exponent)

    def zones(self, time):
        return self.zones_now * self._ramp(time, self.alpha)

    def capacity(self, time):
        return self.capacity_now * self._ramp(time, self.beta)

    def total_capacity(self, time):
        return self.zones(time) * self.capacity(time)

    def _integral(self, time, normalization, exponent):
        # After today the rates are held fixed, rather than extrapolating the ramp.
        ramp = normalization * self.duration / (exponent + 1)
        return (ramp * self.fraction(time) ** (exponent + 1)
                + normalization * np.maximum(np.asarray(time) - self.now, 0))

    def spacetime(self, time):
        """Physical opportunity integrated over all existing zones (EE zone-Gyr)."""
        return self._integral(time, self.zones_now * self.capacity_now,
                              self.alpha + self.beta)

    def capacity_time(self, time):
        """Exposure of a path existing continuously from the ramp start (EE-Gyr)."""
        return self._integral(time, self.capacity_now, self.beta)

    def exposure(self, birth, time):
        """Local exposure, zero until the zone exists; no inherited ancestry."""
        return np.maximum(self.capacity_time(time) - self.capacity_time(birth), 0)

    def time_for_capacity(self, exposure):
        """Invert the per-path capacity clock, extending today's rate if needed."""
        exposure = np.asarray(exposure)
        if np.any(exposure < 0) or self.capacity_now <= 0:
            raise ValueError("Require nonnegative exposure and positive capacity")
        at_now = self.capacity_time(self.now)
        within = self.start + self.duration * (
            np.minimum(exposure, at_now) / at_now) ** (1 / (self.beta + 1))
        return within + np.maximum(exposure - at_now, 0) / self.capacity_now

    def cohorts(self, bins=2000):
        """Present-day zones by birth cohort; no destruction or sub-zone trials."""
        if self.alpha <= 0:
            raise ValueError("Cohort table requires a growing zone population")
        edges = np.linspace(self.start, self.now, bins + 1)
        births = (edges[:-1] + edges[1:]) / 2
        return births, np.diff(self.zones(edges))

    def older_fraction(self, age):
        return self._ramp(self.now - np.asarray(age), self.alpha)
