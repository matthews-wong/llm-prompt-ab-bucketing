"""Simulate bucketing on synthetic ids and report split accuracy and SRM verdicts."""

from abtest.bucket import Experiment, assign
from abtest.srm import check_srm

SAMPLE_SIZE = 20000
EXPERIMENTS = [
    Experiment("even-two-way", {"a": 1, "b": 1}),
    Experiment("ninety-ten", {"a": 9, "b": 1}),
    Experiment("three-way", {"a": 1, "b": 1, "c": 2}),
]


def main() -> int:
    mismatches = 0
    print(f"synthetic ids: user-0..user-{SAMPLE_SIZE - 1} (n={SAMPLE_SIZE} per experiment)")
    print(f"{'experiment':<14}{'max |share err|':>16}{'chi2':>8}{'p':>8}  verdict")
    for experiment in EXPERIMENTS:
        counts: dict[str, int] = {}
        for i in range(SAMPLE_SIZE):
            variant = assign(experiment, f"user-{i}")
            counts[variant] = counts.get(variant, 0) + 1
        total_weight = sum(experiment.weights.values())
        max_error = max(
            abs(counts.get(v, 0) / SAMPLE_SIZE - w / total_weight)
            for v, w in experiment.weights.items()
        )
        result = check_srm(counts, experiment.weights)
        verdict = "MISMATCH" if result.mismatch else "ok"
        mismatches += result.mismatch
        print(
            f"{experiment.name:<14}{max_error:>16.4f}{result.chi_square:>8.2f}"
            f"{result.p_value:>8.3f}  {verdict}"
        )
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
