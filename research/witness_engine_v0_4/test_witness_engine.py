import unittest

from research.witness_engine_v0_4.witness_engine import (
    Claim, baseline_predict, claims_conflict, make_frozen_cases, witness_predict,
)


class WitnessEngineTests(unittest.TestCase):
    def test_same_context_different_values_conflict(self):
        a = Claim("sample", "state", "solid", "src-a")
        b = Claim("sample", "state", "liquid", "src-b")
        self.assertTrue(claims_conflict(a, b))

    def test_different_context_does_not_conflict(self):
        a = Claim("sample", "state", "solid", "src-a", context="cold")
        b = Claim("sample", "state", "liquid", "src-b", context="hot")
        self.assertFalse(claims_conflict(a, b))

    def test_opposite_polarity_conflicts(self):
        a = Claim("model", "passes", "test", "src-a", polarity=True)
        b = Claim("model", "passes", "test", "src-b", polarity=False)
        self.assertTrue(claims_conflict(a, b))

    def test_claim_validation(self):
        with self.assertRaises(ValueError):
            Claim("sample", "state", "solid", "src-a", confidence=1.5)

    def test_case_insensitive_keys(self):
        a = Claim("Sample", "State", "SOLID", "src-a")
        b = Claim(" sample ", " state ", "liquid", "src-b")
        self.assertTrue(claims_conflict(a, b))

    def test_frozen_cases_are_balanced_and_deterministic(self):
        a = make_frozen_cases()
        b = make_frozen_cases()
        self.assertEqual(a, b)
        self.assertEqual(len(a), 40)
        self.assertEqual(sum(c["gold_contradiction"] for c in a), 20)
        self.assertEqual(len({c["id"] for c in a}), 40)

    def test_rule_engine_matches_generated_labels(self):
        for case in make_frozen_cases():
            claims = [Claim(**row) for row in case["claims"]]
            self.assertEqual(witness_predict(claims), case["gold_contradiction"], case["id"])

    def test_baseline_is_context_blind(self):
        case = make_frozen_cases()[2]
        claims = [Claim(**row) for row in case["claims"]]
        self.assertFalse(case["gold_contradiction"])
        self.assertTrue(baseline_predict(claims))


if __name__ == "__main__":
    unittest.main()
