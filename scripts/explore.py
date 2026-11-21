"""Run a short prediction-test-explain lunar-night exercise in a terminal."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from lunar_thermal.core import ExternalFluxes, ThermalNode, advance_constant_forcing
from lunar_thermal.explorer import classify_temperature_change

BASELINE_PATH = PROJECT_ROOT / "config" / "scenarios" / "lunar_night_survival.json"
OPTIONS = {
    "1": ("Higher internal load", PROJECT_ROOT / "config" / "scenarios" / "lunar_night_high_load.json"),
    "2": ("Larger radiator", PROJECT_ROOT / "config" / "scenarios" / "lunar_night_large_radiator.json"),
}


def simulate(path: Path):
    with path.open(encoding="utf-8") as stream:
        scenario = json.load(stream)
    return advance_constant_forcing(
        ThermalNode(**scenario["thermal_node"]),
        ExternalFluxes(**scenario["external_fluxes"]),
        scenario["initial_temperature_k"],
        scenario["duration_s"],
        scenario["time_step_s"],
    )


def main() -> None:
    print("Artemis Moon Base Thermal Explorer — synthetic lunar-night lesson")
    print("All inputs are illustrative; this is not an operational or flight model.\n")
    for key, (name, _) in OPTIONS.items():
        print(f"{key}. {name}")
    selected = input("Choose a change [1-2]: ").strip()
    if selected not in OPTIONS:
        raise SystemExit("Choose 1 or 2.")
    prediction = input("Will the final asset temperature Rise, Fall, or Stay the same? ").strip().casefold()
    baseline = simulate(BASELINE_PATH)
    name, candidate_path = OPTIONS[selected]
    candidate = simulate(candidate_path)
    actual = classify_temperature_change(baseline.final_temperature_k, candidate.final_temperature_k, tolerance_k=0.01)
    normalized = {"rise": "Rise", "fall": "Fall", "stay": "Stay the same", "stay the same": "Stay the same"}.get(prediction, "Unrecognized")
    print(f"\nChange: {name}")
    print(f"Baseline final temperature: {baseline.final_temperature_k:.2f} K")
    print(f"Changed-case final temperature: {candidate.final_temperature_k:.2f} K")
    print(f"Computed change: {actual}")
    print("Prediction check: " + ("matches the model." if normalized == actual else "does not match the model."))
    print("Explanation: compare the named scenario input with the radiative heat-rejection term; identify missing geometry, dust, and site-boundary physics before applying the trend beyond this lesson.")


if __name__ == "__main__":
    main()
