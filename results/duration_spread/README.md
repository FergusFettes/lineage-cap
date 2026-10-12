# Duration scatter sensitivity

Regenerate with `make duration-spread`; run checks with `make check`.
Input assumptions: `configs/duration_spread.json` (copied here and SHA256
recorded in `verification.json`).

`bounds.csv` combines independent uniform start and duration offsets. Both
offsets are shared across each galaxy; expansion is saturated. The completion
distribution is trapezoidal, with a hard earliest-completion edge. Durations
are translated to infer the maximum completion lead compatible with
P(empty)>=0.05. Ranks use the convolved CDF, not lead/(sum of widths).

`normal_tail_bounds.csv` replaces uniform durations with a normal distribution
truncated below zero. At a fixed sigma, the normal location is fitted to the
same sky criterion. In these solutions truncation is negligible. There is no
positive hard minimum duration; the fitted typical duration can exceed our
lineage age. The same start windows and galaxy correlation assumption apply.

All fractional widths use the fixed 13.6 Gyr reference. They are NOT a
coefficient of variation relative to the fitted population mean. In the
uniform model full width D and standard deviation sigma_T=D/sqrt(12) are
separate columns. A 10% full width and a 10% standard deviation are different
scenarios. No width or shape is an empirical biological estimate.

These are conditional completion-rank ceilings, not anthropic posteriors or
probabilities of seeing an empty sky averaged over all possible ranks.
The geometry is flat with n_g=0.01 Mpc^-3, v=0.5c, and a 30 kpc host crossing
delay. Observer conditioning, actual survey completeness, clustering,
within-galaxy independent duration draws, and start-rate correlations remain
outside this sensitivity calculation.
