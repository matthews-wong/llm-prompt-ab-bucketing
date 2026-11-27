"""Sample-ratio-mismatch check: chi-square goodness of fit on variant counts."""

import math
from dataclasses import dataclass

DEFAULT_ALPHA = 0.001  # SRM is a data-quality alarm, so keep false alarms rare.
MAX_ITERATIONS = 500
EPSILON = 1e-12


@dataclass(frozen=True)
class SrmResult:
    chi_square: float
    degrees_of_freedom: int
    p_value: float
    mismatch: bool


def _upper_gamma_q(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x)."""
    if x <= 0:
        return 1.0
    log_prefix = a * math.log(x) - x - math.lgamma(a)
    if x < a + 1:
        # Series for the lower function P, then Q = 1 - P.
        term = total = 1.0 / a
        for n in range(1, MAX_ITERATIONS):
            term *= x / (a + n)
            total += term
            if abs(term) < abs(total) * EPSILON:
                break
        return 1.0 - total * math.exp(log_prefix)
    # Lentz continued fraction for Q.
    tiny = 1e-300
    b = x + 1 - a
    c = 1 / tiny
    d = 1 / b
    h = d
    for n in range(1, MAX_ITERATIONS):
        an = -n * (n - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < EPSILON:
            break
    return math.exp(log_prefix) * h


def check_srm(
    counts: dict[str, int], weights: dict[str, float], alpha: float = DEFAULT_ALPHA
) -> SrmResult:
    unknown = sorted(set(counts) - set(weights))
    if unknown:
        raise ValueError(f"counts for unknown variants: {unknown}")
    if len(weights) < 2:
        raise ValueError(f"need at least two variants, got {sorted(weights)}")
    total = sum(counts.get(variant, 0) for variant in weights)
    if total <= 0:
        raise ValueError("total count must be positive")
    weight_sum = sum(weights.values())
    chi_square = 0.0
    for variant, weight in weights.items():
        expected = total * weight / weight_sum
        chi_square += (counts.get(variant, 0) - expected) ** 2 / expected
    dof = len(weights) - 1
    p_value = _upper_gamma_q(dof / 2, chi_square / 2)
    return SrmResult(chi_square, dof, p_value, p_value < alpha)
