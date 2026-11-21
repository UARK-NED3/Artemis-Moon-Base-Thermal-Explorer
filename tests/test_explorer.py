import unittest

from lunar_thermal.explorer import classify_temperature_change


class ExplorerTests(unittest.TestCase):
    def test_classifies_rise_fall_and_no_material_change(self) -> None:
        self.assertEqual(classify_temperature_change(250.0, 251.0), "Rise")
        self.assertEqual(classify_temperature_change(250.0, 249.0), "Fall")
        self.assertEqual(classify_temperature_change(250.0, 250.0), "Stay the same")

    def test_uses_declared_tolerance_for_negligible_change(self) -> None:
        self.assertEqual(classify_temperature_change(250.0, 250.0005, tolerance_k=0.001), "Stay the same")


if __name__ == "__main__":
    unittest.main()
