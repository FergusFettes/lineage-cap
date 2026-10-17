# Moody et al. (2024) LUCA age without the Earth-bound root maximum

Date: 2026-10-17. Relates to `first-flush-likelihood.qmd` Section 4, the sentence
reading Earth's LUCA (~4.2 Ga, Moody et al. 2024) as the date our lineage reached Earth.

## What Moody et al. assume

Their MCMCtree analysis (repo `sabifo4/LUCA-divtimes`, PAML 4.10.7) dates LUCA from
five pre-LUCA paralogue pairs. The tree root is the pre-LUCA duplication and LUCA is
a cross-braced node pair. Two calibrations carry the Earth-bound assumption:

- root: `U(4.520)`, a hard maximum at the Moon-forming impact;
- LUCA (`#1`): `B{3.347, 4.520}`, hard at both ends.

Their rate prior Γ(2, 2.5) is also derived by dividing the ML tree height by 4.52 Ga.
Their published posterior puts the root at 4.49 Ga with upper limit 4.519 Ga, i.e.
pressed against the bound.

## Rerun

Same alignment, Hessian (`in.BV`), tree, control file and priors; shorter chains
(4000 burn-in, 20000 samples every 4 iterations, one chain each, first 20% of
samples discarded). The only change in the "cap X" rows is the root and LUCA
maximum. "exp rate prior" replaces Γ(2, 2.5) with Γ(1, 1.25), same mean, vaguer.
Prior-only rows sample the joint time prior with no sequence data (`usedata = 0`).

| run | root mean [95%] Ga | LUCA mean [95%] Ga | mean lnL |
|---|---:|---:|---:|
| prior only, cap 4.52 | 4.47 [4.35, 4.52] | 4.43 [4.26, 4.51] | |
| paper setup, GBM | 4.49 [4.43, 4.52] | 4.27 [4.18, 4.35] | -269.0 |
| paper setup, ILN | 4.49 [4.42, 4.52] | 4.18 [4.02, 4.31] | -233.4 |
| prior only, cap 6 | 5.93 [5.74, 6.00] | 5.86 [5.61, 5.98] | |
| cap 6, ILN | 5.92 [5.70, 6.00] | 5.31 [4.98, 5.57] | -234.9 |
| prior only, cap 8 | 7.90 [7.65, 8.00] | 7.80 [7.46, 7.98] | |
| cap 8, ILN | 7.75 [7.20, 7.99] | 6.70 [6.06, 7.25] | -235.9 |
| prior only, cap 10 | 9.87 [9.54, 10.00] | 9.75 [9.31, 9.97] | |
| cap 10, ILN | 9.18 [7.85, 9.96] | 7.71 [6.64, 8.75] | -236.2 |
| prior only, cap 13.8 | 13.63 [13.18, 13.80] | 13.46 [12.86, 13.76] | |
| cap 13.8, ILN | 10.20 [8.36, 12.63] | 8.49 [6.96, 10.71] | -236.3 |
| cap 13.8, ILN, exp rate prior | 10.32 [8.34, 12.79] | 8.56 [6.96, 10.66] | -236.1 |
| cap 13.8, GBM | 12.29 [10.22, 13.73] | 11.01 [9.20, 12.55] | -293.9 |
| cap 13.8, GBM, exp rate prior | 12.35 [10.21, 13.74] | 10.97 [9.18, 12.52] | -294.1 |

Published values: GBM LUCA 4.27 [4.18, 4.35], ILN 4.18 [4.03, 4.31]. The control
rows reproduce them.

## Reading

1. The joint time prior pins the root at whatever maximum it is given, and LUCA
   within ~0.1 Gyr of it. With the published 4.52 Ga cap the prior alone gives LUCA
   4.43 Ga; the sequence data move it down by about 150 Myr. The 4.2 Ga result is
   the Moon-forming calibration with a small correction from the data.
2. Lifting the cap, LUCA tracks it: 5.3, 6.7, 7.7, 8.5 Ga for caps of 6, 8, 10,
   13.8 Ga under ILN. The data pull harder as the cap rises (the LUCA/root ratio
   falls from 0.93 to 0.84) but never settle. Mean log-likelihood changes by about
   3 units over this range against a within-chain spread of 15, so under ILN the
   data are close to indifferent to LUCA's absolute age. Under GBM the data prefer
   the young root by about 25 lnL units but the posterior still sits near the cap.
3. The rate prior's dependence on 4.52 Ga does not matter: the exponential rate
   prior gives the same rows. The rate is set by the younger calibrations.
4. So: Moody's data cannot place LUCA above ~4 Ga by themselves. The date is a
   statement that LUCA lived on Earth, plus a molecular clock that is nearly flat
   over several Gyr once that statement is dropped. Under the process clock, which
   drops it, the paper gives no arrival date and no LUCA date. Arrival on Earth is
   then bounded by Earth's formation (4.54 Ga) above and by the first traces of
   life in the rock record (~3.7–3.95 Ga) below.

## Caveats

One chain per row and 84k iterations against the paper's 16 x 2e7; effective sample
sizes for the root are low (tens to hundreds). Means and intervals are good to a
few percent, which is enough for the point. The freed root uses a uniform prior to
13.8 Ga, which is not a neutral prior; the profile over caps is the honest reading.
Only the root and LUCA maxima were lifted; the 4.52 Ga maxima on
total-group Oxyphotobacteria and the mitochondrial stem were kept.

## Reproduce

```
git clone https://github.com/sabifo4/LUCA-divtimes   # 1.2 GB
# PAML 4.10.7 built with -D_FORTIFY_SOURCE=0 on macOS (overlapping strcpy in the tree parser)
# strip CRLF from 00_data_formatting/01_inp_data/LUCAdup_246sp_allcb_calib_MCMCtree.tree
# edit 'U(4.520,1e-300)' and '#1 B{3.347,4.520,...}' maxima; run mcmctree with
# usedata = 2 ./in.BV (01_PAML/00_CODEML/out_CODEML/Hessian/1/in.BV), duplication = 1
```
