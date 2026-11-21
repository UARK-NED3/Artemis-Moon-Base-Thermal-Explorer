"""Browser GUI for the synthetic, screening-level lunar thermal lesson."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from lunar_thermal.core import ExternalFluxes, ThermalNode, simulate_constant_forcing_history


st.set_page_config(page_title="Artemis Moon Base Thermal Explorer", layout="wide")
st.title("Artemis Moon Base Thermal Explorer")
st.caption("Synthetic, screening-level lunar-surface thermal lesson. Results are simulated and are not Artemis hardware predictions or operational guidance.")

with st.sidebar:
    st.header("Model inputs")
    internal_power_w = st.slider("Internal dissipation (W)", min_value=0.0, max_value=200.0, value=35.0, step=1.0)
    radiator_area_m2 = st.slider("Radiator area (m²)", min_value=0.1, max_value=2.0, value=0.6, step=0.05)
    emissivity = st.slider("Radiator emissivity (-)", min_value=0.10, max_value=1.00, value=0.82, step=0.01)
    initial_temperature_k = st.slider("Initial temperature (K)", min_value=180.0, max_value=350.0, value=270.0, step=1.0)
    duration_h = st.slider("Simulated duration (h)", min_value=1.0, max_value=336.0, value=12.0, step=1.0)

node = ThermalNode(
    heat_capacity_j_per_k=40_000.0,
    radiator_area_m2=radiator_area_m2,
    emissivity=emissivity,
    solar_absorptivity=0.25,
    solar_area_m2=0.5,
    albedo_area_m2=0.5,
    lunar_ir_area_m2=0.5,
    space_view_factor=0.8,
)
fluxes = ExternalFluxes(
    internal_power_w=internal_power_w,
    direct_solar_irradiance_w_per_m2=0.0,
    albedo_irradiance_w_per_m2=0.0,
    lunar_ir_irradiance_w_per_m2=0.0,
    radiative_sink_temperature_k=3.0,
)
history = simulate_constant_forcing_history(node, fluxes, initial_temperature_k, duration_h * 3600.0, 60.0)
result = history.result

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Final temperature", f"{result.final_temperature_k:.2f} K", f"{result.final_temperature_k - initial_temperature_k:+.2f} K")
metric_b.metric("Final temperature", f"{result.final_temperature_k - 273.15:.2f} °C")
metric_c.metric("Energy residual", f"{result.energy_residual_j:.3e} J")

temperature_frame = pd.DataFrame({
    "Time (h)": [value / 3600.0 for value in history.time_s],
    "Temperature (K)": history.temperature_k,
})
power_frame = pd.DataFrame({
    "Term": ["Internal dissipation", "Radiative rejection", "Net at final state"],
    "Power (W)": [internal_power_w, -history.radiated_power_w[-1], history.net_power_w[-1]],
})
left, right = st.columns(2)
with left:
    st.subheader("Temperature response")
    st.line_chart(
        temperature_frame,
        x="Time (h)",
        y="Temperature (K)",
        x_label="Time (h)",
        y_label="Temperature (K)",
        alt="Simulated asset temperature over the selected lunar-surface scenario duration.",
    )
with right:
    st.subheader("Final-state heat-rate balance")
    st.bar_chart(
        power_frame,
        x="Term",
        y="Power (W)",
        x_label="Heat-rate term",
        y_label="Power (W), positive into the node",
        alt="Internal heating, radiative rejection, and net heat rate at the final simulated state.",
    )

with st.expander("Assumptions and learning prompt", expanded=True):
    st.write("This case uses no direct solar, albedo, or lunar-IR input to represent a simplified darkness lesson. The uniform-temperature node radiates to a 3 K sink through a fixed space-view factor. Predict how changing one slider changes the final temperature, then check the chart and named heat-rate terms.")
    st.write("Missing physics includes detailed geometry, dust, regolith contact, multi-node conduction, thermal controls, and a site-specific lunar boundary condition.")
