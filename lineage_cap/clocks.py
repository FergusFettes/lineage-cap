"""Deterministic process clocks; completion rates follow zone birth histories."""

import numpy as np

from .history import History

MODES = ("planet_linked", "inherited")
KINDS = ("elapsed_time", "integrated_capacity")


def validate(mode, kind):
    if mode not in MODES or kind not in KINDS:
        raise ValueError(f"Unknown clock: {mode}/{kind}")


def required_threshold(h: History, frontier, kind):
    if kind == "elapsed_time":
        return np.asarray(frontier) - h.start
    if kind == "integrated_capacity":
        return h.capacity_time(frontier)
    raise ValueError(f"Unknown clock kind: {kind}")


def completion_time(h: History, birth, frontier, mode, kind):
    """Completion for a zone cohort given an earliest attainable completion date."""
    validate(mode, kind)
    birth = np.asarray(birth)
    if mode == "inherited":
        return np.maximum(birth, frontier)
    threshold = required_threshold(h, frontier, kind)
    if kind == "elapsed_time":
        return birth + threshold
    return h.time_for_capacity(h.capacity_time(birth) + threshold)


def completed_zones(h: History, time, frontier, mode, kind):
    """Cumulative completions by `time`, including cohorts born after inheritance."""
    validate(mode, kind)
    time, frontier = np.broadcast_arrays(time, frontier)
    if mode == "inherited":
        return np.where(time >= frontier, h.zones(time), 0)
    threshold = required_threshold(h, frontier, kind)
    if kind == "elapsed_time":
        return h.zones(time - threshold)
    remaining = h.capacity_time(time) - threshold
    birth_cutoff = h.time_for_capacity(np.maximum(remaining, 0))
    return np.where(remaining > 0, h.zones(birth_cutoff), 0)
