# llm-prompt-ab-bucketing

Deterministic A/B bucketing for prompt variants, plus a sample-ratio-mismatch
(SRM) check. Pure Python standard library, no network, no model calls.

When two prompt versions run side by side, the same user should always see the
same one, and the observed traffic split should match the configured weights.
This repo covers both halves:

- `assign` hashes `experiment + user id` to a stable bucket, so a user keeps
  their variant across sessions and processes with no stored state.
- `srm` runs a chi-square goodness-of-fit test on observed counts and flags a
  split that is too far from the weights to be chance.

## Usage

```
python3 -m abtest assign --config fixtures/experiment.json user-1 user-2
python3 -m abtest srm --config fixtures/experiment.json --counts control=5210 concise=4790
```

The `srm` command exits 1 on a mismatch, so it can gate a report in CI. The
example above (5210 vs 4790 on a 50/50 split) is flagged: chi2 = 17.64,
p = 2.7e-5.

## Design notes

- **No stored state.** The bucket is `sha256(experiment NUL user id)`, first
  8 bytes, scaled to [0, 1). Any process computes the same answer.
- **Variant order is part of the layout.** Variants are laid out in config
  order along the unit interval. Reordering or changing weights moves users, so
  treat a config change as a new experiment name.
- **SRM alpha defaults to 0.001.** A mismatch usually means a logging or
  routing bug, not a real effect, so the check is tuned to stay quiet unless
  the skew is large.
- **Chi-square tail is computed locally** (regularized incomplete gamma), and
  tested against the closed forms for df=1 and df=2.

## Validate

```
make validate
```

Last run of `python3 -m abtest.evaluate` on synthetic ids `user-0..user-19999`
(20000 per experiment, not real traffic):

| experiment   | max share error | chi2 | p     | verdict |
|--------------|-----------------|------|-------|---------|
| even-two-way | 0.0022          | 0.39 | 0.534 | ok      |
| ninety-ten   | 0.0008          | 0.14 | 0.706 | ok      |
| three-way    | 0.0024          | 0.61 | 0.735 | ok      |
