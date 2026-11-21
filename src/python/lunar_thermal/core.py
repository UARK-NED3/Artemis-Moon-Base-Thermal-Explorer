"""Transparent SI-unit single-node thermal model for lunar-surface lessons."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite

SIGMA_W_PER_M2_K4 = 5.670_374_419e-8


def _require_finite(name: str, value: float, minimum: float = 0.0, maximum: float | None = None) -> None:
    if not isfinite(value) or value < minimum or (maximum is not None and value > maximum):
        bounds = f"[{minimum}, {maximum}]" if maximum is not None else f">= {minimum}"
        raise ValueError(f"{name} must be finite and {bounds}; received {value!r}.")


@dataclass(frozen=True)
class ThermalNode:
    """Uniform-temperature asset with declared radiative and absorptive areas."""

    heat_capacity_j_per_k: float
    radiator_area_m2: float
    emissivity: float
    solar_absorptivity: float
    solar_area_m2: float
    albedo_area_m2: float
    lunar_ir_area_m2: float
    space_view_factor: float

    def __post_init__(self) -> None:
        _require_finite("heat_capacity_j_per_k", self.heat_capacity_j_per_k, minimum=1e-12)
        for name, value in (
            ("radiator_area_m2", self.radiator_area_m2),
            ("solar_area_m2", self.solar_area_m2),
            ("albedo_area_m2", self.albedo_area_m2),
            ("lunar_ir_area_m2", self.lunar_ir_area_m2),
        ):
            _require_finite(name, value)
        _require_finite("emissivity", self.emissivity, maximum=1.0)
        _require_finite("solar_absorptivity", self.solar_absorptivity, maximum=1.0)
        _require_finite("space_view_factor", self.space_view_factor, maximum=1.0)


@dataclass(frozen=True)
class ExternalFluxes:
    """Constant external forcing; all heat rates are positive into the control mass."""

    internal_power_w: float
    direct_solar_irradiance_w_per_m2: float
    albedo_irradiance_w_per_m2: float
    lunar_ir_irradiance_w_per_m2: float
    radiative_sink_temperature_k: float

    def __post_init__(self) -> None:
        for name, value in (
            ("internal_power_w", self.internal_power_w),
            ("direct_solar_irradiance_w_per_m2", self.direct_solar_irradiance_w_per_m2),
            ("albedo_irradiance_w_per_m2", self.albedo_irradiance_w_per_m2),
            ("lunar_ir_irradiance_w_per_m2", self.lunar_ir_irradiance_w_per_m2),
            ("radiative_sink_temperature_k", self.radiative_sink_temperature_k),
        ):
            _require_finite(name, value)


@dataclass(frozen=True)
class HeatRates:
    internal_power_w: float
    solar_absorbed_w: float
    albedo_absorbed_w: float
    lunar_ir_absorbed_w: float
    radiated_power_w: float
    absorbed_power_w: float
    net_power_w: float


@dataclass(frozen=True)
class ConstantForcingResult:
    initial_temperature_k: float
    final_temperature_k: float
    duration_s: float
    time_step_s: float
    integrated_net_energy_j: float
    energy_residual_j: float


def heat_rates(node: ThermalNode, fluxes: ExternalFluxes, temperature_k: float) -> HeatRates:
    """Return named W terms in the declared energy balance at one temperature."""
    _require_finite("temperature_k", temperature_k, minimum=0.0)
    solar_absorbed_w = node.solar_absorptivity * node.solar_area_m2 * fluxes.direct_solar_irradiance_w_per_m2
    albedo_absorbed_w = node.solar_absorptivity * node.albedo_area_m2 * fluxes.albedo_irradiance_w_per_m2
    lunar_ir_absorbed_w = node.emissivity * node.lunar_ir_area_m2 * fluxes.lunar_ir_irradiance_w_per_m2
    radiated_power_w = (
        node.emissivity
        * SIGMA_W_PER_M2_K4
        * node.radiator_area_m2
        * node.space_view_factor
        * (temperature_k**4 - fluxes.radiative_sink_temperature_k**4)
    )
    absorbed_power_w = fluxes.internal_power_w + solar_absorbed_w + albedo_absorbed_w + lunar_ir_absorbed_w
    return HeatRates(
        internal_power_w=fluxes.internal_power_w,
        solar_absorbed_w=solar_absorbed_w,
        albedo_absorbed_w=albedo_absorbed_w,
        lunar_ir_absorbed_w=lunar_ir_absorbed_w,
        radiated_power_w=radiated_power_w,
        absorbed_power_w=absorbed_power_w,
        net_power_w=absorbed_power_w - radiated_power_w,
    )


def equilibrium_temperature_k(node: ThermalNode, fluxes: ExternalFluxes) -> float:
    """Analytical steady temperature for constant forcing and a nonzero radiator path."""
    radiative_conductance = node.emissivity * SIGMA_W_PER_M2_K4 * node.radiator_area_m2 * node.space_view_factor
    if radiative_conductance <= 0.0:
        raise ValueError("A positive emissivity, radiator area, and space view factor are required for equilibrium.")
    zero_kelvin_rates = heat_rates(node, fluxes, temperature_k=0.0)
    source_power_w = zero_kelvin_rates.absorbed_power_w + radiative_conductance * fluxes.radiative_sink_temperature_k**4
    return (source_power_w / radiative_conductance) ** 0.25


def advance_constant_forcing(
    node: ThermalNode,
    fluxes: ExternalFluxes,
    initial_temperature_k: float,
    duration_s: float,
    time_step_s: float,
) -> ConstantForcingResult:
    """Advance the energy balance using RK4 and report a stage-consistent energy residual."""
    _require_finite("initial_temperature_k", initial_temperature_k, minimum=0.0)
    _require_finite("duration_s", duration_s, minimum=1e-12)
    _require_finite("time_step_s", time_step_s, minimum=1e-12)

    def derivative(temperature_k: float) -> float:
        return heat_rates(node, fluxes, temperature_k).net_power_w / node.heat_capacity_j_per_k

    temperature_k = initial_temperature_k
    integrated_net_energy_j = 0.0
    steps = ceil(duration_s / time_step_s)
    for step_index in range(steps):
        dt_s = min(time_step_s, duration_s - step_index * time_step_s)
        k1 = derivative(temperature_k)
        k2 = derivative(temperature_k + 0.5 * dt_s * k1)
        k3 = derivative(temperature_k + 0.5 * dt_s * k2)
        k4 = derivative(temperature_k + dt_s * k3)
        average_derivative_k_per_s = (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        temperature_k += dt_s * average_derivative_k_per_s
        integrated_net_energy_j += node.heat_capacity_j_per_k * dt_s * average_derivative_k_per_s

    stored_energy_change_j = node.heat_capacity_j_per_k * (temperature_k - initial_temperature_k)
    return ConstantForcingResult(
        initial_temperature_k=initial_temperature_k,
        final_temperature_k=temperature_k,
        duration_s=duration_s,
        time_step_s=time_step_s,
        integrated_net_energy_j=integrated_net_energy_j,
        energy_residual_j=stored_energy_change_j - integrated_net_energy_j,
    )
