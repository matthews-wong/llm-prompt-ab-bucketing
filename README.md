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

## Validate

```
make validate
```
