"""Stable variant assignment from a hash of experiment and user id."""

import hashlib
from dataclasses import dataclass

HASH_BYTES = 8
HASH_SPACE = 1 << (8 * HASH_BYTES)


@dataclass(frozen=True)
class Experiment:
    name: str
    weights: dict[str, float]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("experiment name must not be empty")
        if not self.weights:
            raise ValueError(f"experiment {self.name!r} has no variants")
        for variant, weight in self.weights.items():
            if weight <= 0:
                raise ValueError(
                    f"experiment {self.name!r}: weight for {variant!r} must be positive, got {weight}"
                )


def unit_interval(experiment: str, user_id: str) -> float:
    # The experiment name is part of the key so one user lands in
    # independent buckets across experiments.
    digest = hashlib.sha256(f"{experiment}\x00{user_id}".encode()).digest()
    return int.from_bytes(digest[:HASH_BYTES], "big") / HASH_SPACE


def assign(experiment: Experiment, user_id: str) -> str:
    if not user_id:
        raise ValueError(f"experiment {experiment.name!r}: user id must not be empty")
    total = sum(experiment.weights.values())
    point = unit_interval(experiment.name, user_id) * total
    upper = 0.0
    # Insertion order defines the layout, so reordering variants reshuffles users.
    for variant, weight in experiment.weights.items():
        upper += weight
        if point < upper:
            return variant
    return next(reversed(experiment.weights))
