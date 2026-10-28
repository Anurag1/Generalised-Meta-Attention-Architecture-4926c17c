import unittest

from discovery_engine import discover


class DiscoveryEngineTests(unittest.TestCase):
    def test_recovers_known_relation_and_verifies_heldout_data(self):
        x = [float(i) for i in range(1, 41)]
        data = {"x": x, "y": [3 * v + 2 for v in x], "constant": [4.0] * len(x)}
        results = discover(data, seed=11)
        best = next(r for r in results if r.input_variable == "x" and r.output_variable == "y")
        self.assertAlmostEqual(best.slope, 3.0, places=9)
        self.assertAlmostEqual(best.intercept, 2.0, places=9)
        self.assertTrue(best.verified)
        self.assertEqual(best.test_mae, 0.0)

    def test_does_not_claim_constant_output_is_discovered_from_constant_input(self):
        data = {"x": [float(i) for i in range(1, 21)], "flat": [7.0] * 20}
        results = discover(data, seed=7)
        candidate = next(r for r in results if r.input_variable == "x" and r.output_variable == "flat")
        self.assertFalse(candidate.verified)

    def test_rejects_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            discover({"x": [1.0] * 8, "y": [1.0] * 7})


if __name__ == "__main__":
    unittest.main()
