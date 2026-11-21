# Specification: Artemis Moon Base Thermal Explorer

## Objective

Build an open Python and MATLAB educational repository that lets learners predict, simulate, and explain the transient thermal behavior of representative lunar-surface assets near the Artemis Moon Base operating context. Version 0.1 is a transparent, screening-level single-node model with synthetic scenarios. It is not flight-analysis, hardware-selection, mission-operations, or safety-certification software.

## Technical invariants

- SI units are required at every code boundary. Temperatures are Kelvin internally; interfaces may display degrees Celsius.
- The modeled control mass is a uniform-temperature thermal node with heat capacity `C_th` in J/K.
- The system boundary includes internal dissipation, absorbed direct solar flux, absorbed albedo, absorbed lunar IR, and radiative rejection to a declared radiative sink.
- The model excludes atmosphere/convection, detailed geometry or view factors, dust deposition, regolith contact, phase change, component conduction networks, and feedback control in v0.1.
- All scenarios are synthetic and must state their assumptions. NASA documents guide scope; they do not calibrate the numerical scenarios.

## Governing model

\[
C_{\mathrm{th}}\frac{dT}{dt}=Q_{\mathrm{internal}}+\alpha_{\mathrm{s}}A_{\mathrm{sun}}G_{\mathrm{sun}}+\alpha_{\mathrm{s}}A_{\mathrm{alb}}G_{\mathrm{alb}}+\epsilon A_{\mathrm{IR}}G_{\mathrm{IR}}-\epsilon\sigma A_{\mathrm{rad}}F_{\mathrm{space}}(T^4-T_{\mathrm{sink}}^4).
\]

`G` terms are incident irradiances in W/m², areas are m², `F_space` is dimensionless, and every heat rate is W.

## Commands

```powershell
$env:PYTHONPATH = 'src\\python'
python -m unittest discover -s tests -v
python scripts/run_scenario.py config/scenarios/lunar_night_survival.json
pip install -r requirements.txt
streamlit run apps/python_thermal_explorer.py
```

MATLAB (after implementation):

```matlab
addpath('src/matlab')
result = runLunarThermalScenario('config/scenarios/lunar_night_survival.json');
LunarThermalExplorer
```

## Project structure

```text
src/python/                 Python thermal core
src/matlab/                 MATLAB-equivalent core
tests/                      Python unit and scenario tests
config/scenarios/           Language-neutral synthetic inputs
scripts/                    Explicit command-line entry points
apps/                       Browser-based Streamlit interface
docs/                       Instructor, source, and model-boundary material
dataset/                    User-downloaded source files; ignored by git
data/raw/, data/processed/  Future datasets; ignored by git
```

## Code style

- Use named dataclasses/structures, explicit SI-unit suffixes, deterministic JSON output, and small pure functions.
- Validate physical ranges at inputs; do not silently clip invalid values.
- Preserve raw files and record data source, units, coordinate frame, and time basis before any future data adapter.

## Testing strategy

- Python standard-library `unittest` tests drive behavior before implementation.
- Tests cover unit/range validation, dimensionally consistent heat-rate composition, radiative-equilibrium limits, energy accounting, and monotonic response to internal load and radiator area.
- MATLAB and Python use the same declared heat-balance terms and shared JSON scenario inputs; formal cross-language regression tolerances remain a future release item.
- GUI verification includes a local Streamlit startup check and MATLAB UI creation/export check. UI graphics are simulations, not measured mission data.

## Boundaries

- Always: run Python tests, retain scenario assumptions, and label output as simulated.
- Ask first: adding a new dependency, bundling NASA/PDS data, or making a validation/operational claim.
- Never: overwrite local datasets, commit downloaded source PDFs or raw data, or claim use for flight/safety decisions.

## Success criteria for v0.1

1. Python and MATLAB expose the same declared single-node heat-balance inputs and SI-unit conventions.
2. The Python core passes its validation and physics-limit tests.
3. A synthetic lunar-night scenario runs from JSON and produces deterministic temperature/heat-rate output.
4. Documentation names NASA source materials and model exclusions without implying empirical validation.
5. Python and MATLAB interfaces graph the transient temperature history and final heat-rate terms for declared synthetic inputs.
