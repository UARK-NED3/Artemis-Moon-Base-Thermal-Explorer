# Artemis Moon Base Thermal Explorer

An open Python and MATLAB teaching repository for predicting and explaining the transient thermal behavior of representative lunar-surface assets in an Artemis Moon Base context.

## Status and scope

Version 0.1 implements a **synthetic, screening-level, single-node** thermal model. It supports education and workforce-development activities; it does not represent Artemis hardware, validate against flight data, or support flight, safety, procurement, or operational decisions.

The model accounts for internal dissipation, direct solar flux, albedo, lunar IR, and radiative rejection. It intentionally excludes detailed geometry, dust, regolith contact, phase change, multi-node conduction, controls, and an actual Artemis timeline.

## Quick start: Python

```powershell
cd D:\aerospace-repo
$env:PYTHONPATH = 'src\python'
python -m unittest discover -s tests -v
python scripts/run_scenario.py config/scenarios/lunar_night_survival.json
python scripts/explore.py
streamlit run apps/python_thermal_explorer.py
```

The command runs a declared synthetic lunar-night case and prints simulated SI-unit temperatures, energy accounting, and final heat rates as JSON.
`explore.py` adds a terminal prediction gate: choose a controlled scenario, commit a rise/fall/stay prediction, then inspect the model comparison.
The Streamlit command launches the Python browser GUI with sliders, a temperature-history chart, and a final heat-rate bar chart. Install its pinned dependency with `python -m pip install -r requirements.txt`.

## Quick start: MATLAB

```matlab
cd('D:\aerospace-repo')
addpath('src/matlab')
result = runLunarThermalScenario('config/scenarios/lunar_night_survival.json');
exploreLunarThermal
LunarThermalExplorer
```

## Learning loop

1. Predict whether a change in internal load, radiative area, emissivity, or illumination warms or cools the asset.
2. Run the scenario.
3. Inspect each energy-balance term and the energy residual.
4. State the missing physics or measurement needed before applying the result to hardware.

See [SPEC.md](SPEC.md) for equations, units, validity limits, and implementation boundaries. See [docs/SOURCES.md](docs/SOURCES.md) for data provenance rules.

## MATLAB Central release path

The MATLAB files are maintained in this repository. Before publishing a MATLAB Central File Exchange listing, add a license, create a versioned GitHub Release, generate and verify a MATLAB toolbox (`.mltbx`) if desired, and capture GUI screenshots. MathWorks recommends linking File Exchange to GitHub Releases for stable distribution; see [the official guidance](https://www.mathworks.com/matlabcentral/content/fx/about.html).
