import unittest

from lunar_thermal.core import (
    ExternalFluxes,
    ThermalNode,
    advance_constant_forcing,
    simulate_constant_forcing_history,
)


class ThermalHistoryTests(unittest.TestCase):
    def test_history_includes_initial_and_final_state(self) -> None:
        node = ThermalNode(10_000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        fluxes = ExternalFluxes(50.0, 0.0, 0.0, 0.0, 3.0)
        history = simulate_constant_forcing_history(node, fluxes, 250.0, duration_s=100.0, time_step_s=10.0)
        direct = advance_constant_forcing(node, fluxes, 250.0, duration_s=100.0, time_step_s=10.0)
        self.assertEqual(history.time_s[0], 0.0)
        self.assertEqual(history.time_s[-1], 100.0)
        self.assertEqual(len(history.time_s), 11)
        self.assertAlmostEqual(history.temperature_k[0], 250.0)
        self.assertAlmostEqual(history.temperature_k[-1], direct.final_temperature_k)
        self.assertAlmostEqual(history.net_power_w[-1], 50.0)

    def test_history_uses_a_partial_final_step_without_overshooting_duration(self) -> None:
        node = ThermalNode(10_000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        fluxes = ExternalFluxes(50.0, 0.0, 0.0, 0.0, 3.0)
        history = simulate_constant_forcing_history(node, fluxes, 250.0, duration_s=105.0, time_step_s=10.0)
        self.assertEqual(history.time_s[-1], 105.0)
        self.assertAlmostEqual(history.temperature_k[-1], 250.525, places=12)


if __name__ == "__main__":
    unittest.main()
