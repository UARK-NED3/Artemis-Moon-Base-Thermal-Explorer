"""Run one declared synthetic scenario without modifying its input file."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from lunar_thermal.core import ExternalFluxes, ThermalNode, advance_constant_forcing, heat_rates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, help="Path to a scenario JSON file.")
    args = parser.parse_args()
    with args.scenario.open(encoding="utf-8") as stream:
        scenario = json.load(stream)

    node = ThermalNode(**scenario["thermal_node"])
    fluxes = ExternalFluxes(**scenario["external_fluxes"])
    result = advance_constant_forcing(
        node,
        fluxes,
        initial_temperature_k=scenario["initial_temperature_k"],
        duration_s=scenario["duration_s"],
        time_step_s=scenario["time_step_s"],
    )
    final_rates = heat_rates(node, fluxes, result.final_temperature_k)
    print(json.dumps({"scenario_id": scenario["scenario_id"], "result": asdict(result), "final_heat_rates": asdict(final_rates)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
