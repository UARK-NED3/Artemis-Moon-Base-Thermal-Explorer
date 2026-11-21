"""Small, testable teaching helpers for prediction-before-simulation interactions."""


def classify_temperature_change(
    baseline_temperature_k: float,
    candidate_temperature_k: float,
    tolerance_k: float = 1e-9,
) -> str:
    """Classify a change using a stated numerical tolerance in K."""
    if tolerance_k < 0.0:
        raise ValueError("tolerance_k must be nonnegative.")
    difference_k = candidate_temperature_k - baseline_temperature_k
    if difference_k > tolerance_k:
        return "Rise"
    if difference_k < -tolerance_k:
        return "Fall"
    return "Stay the same"
