import math
import unittest

from lunar_thermal.core import (
    SIGMA_W_PER_M2_K4,
    ExternalFluxes,
    ThermalNode,
    advance_constant_forcing,
    equilibrium_temperature_k,
    heat_rates,
)


class ThermalCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.node = ThermalNode(
            heat_capacity_j_per_k=40_000.0,
            radiator_area_m2=1.0,
            emissivity=0.8,
            solar_absorptivity=0.2,
            solar_area_m2=1.0,
            albedo_area_m2=1.0,
            lunar_ir_area_m2=1.0,
            space_view_factor=1.0,
        )

    def test_rejects_nonphysical_inputs(self) -> None:
        with self.assertRaises(ValueError):
            ThermalNode(
                heat_capacity_j_per_k=0.0,
                radiator_area_m2=1.0,
                emissivity=0.8,
                solar_absorptivity=0.2,
                solar_area_m2=1.0,
                albedo_area_m2=1.0,
                lunar_ir_area_m2=1.0,
                space_view_factor=1.0,
            )

    def test_heat_rate_terms_follow_declared_balance(self) -> None:
        fluxes = ExternalFluxes(
            internal_power_w=100.0,
            direct_solar_irradiance_w_per_m2=1_000.0,
            albedo_irradiance_w_per_m2=100.0,
            lunar_ir_irradiance_w_per_m2=50.0,
            radiative_sink_temperature_k=3.0,
        )
        rates = heat_rates(self.node, fluxes, temperature_k=300.0)
        expected_absorbed = 100.0 + 0.2 * 1_000.0 + 0.2 * 100.0 + 0.8 * 50.0
        expected_radiated = 0.8 * SIGMA_W_PER_M2_K4 * (300.0**4 - 3.0**4)
        self.assertAlmostEqual(rates.absorbed_power_w, expected_absorbed)
        self.assertAlmostEqual(rates.radiated_power_w, expected_radiated)
        self.assertAlmostEqual(rates.net_power_w, expected_absorbed - expected_radiated)

    def test_equilibrium_returns_zero_net_power(self) -> None:
        fluxes = ExternalFluxes(
            internal_power_w=120.0,
            direct_solar_irradiance_w_per_m2=0.0,
            albedo_irradiance_w_per_m2=0.0,
            lunar_ir_irradiance_w_per_m2=0.0,
            radiative_sink_temperature_k=3.0,
        )
        temperature_k = equilibrium_temperature_k(self.node, fluxes)
        self.assertAlmostEqual(heat_rates(self.node, fluxes, temperature_k).net_power_w, 0.0, places=9)

    def test_zero_radiation_limit_matches_energy_balance(self) -> None:
        nonradiating_node = ThermalNode(
            heat_capacity_j_per_k=10_000.0,
            radiator_area_m2=0.0,
            emissivity=0.0,
            solar_absorptivity=0.0,
            solar_area_m2=0.0,
            albedo_area_m2=0.0,
            lunar_ir_area_m2=0.0,
            space_view_factor=0.0,
        )
        fluxes = ExternalFluxes(50.0, 0.0, 0.0, 0.0, 3.0)
        result = advance_constant_forcing(nonradiating_node, fluxes, 250.0, duration_s=100.0, time_step_s=10.0)
        self.assertAlmostEqual(result.final_temperature_k, 250.5, places=10)
        self.assertAlmostEqual(result.energy_residual_j, 0.0, places=8)

    def test_larger_radiator_reduces_temperature_for_same_load(self) -> None:
        fluxes = ExternalFluxes(100.0, 0.0, 0.0, 0.0, 3.0)
        small = ThermalNode(40_000.0, 0.5, 0.8, 0.2, 0.0, 0.0, 0.0, 1.0)
        large = ThermalNode(40_000.0, 1.0, 0.8, 0.2, 0.0, 0.0, 0.0, 1.0)
        self.assertLess(equilibrium_temperature_k(large, fluxes), equilibrium_temperature_k(small, fluxes))


if __name__ == "__main__":
    unittest.main()
