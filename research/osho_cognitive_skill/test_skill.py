import unittest
from research.osho_cognitive_skill.skill import Evidence, Hypothesis, audit

class OshoCognitiveSkillTests(unittest.TestCase):
    def test_observations_and_interpretations_are_separated(self):
        result = audit([Evidence("Reading was 8.1", "observation", confidence=.9),
                        Evidence("Sensor must be broken", "interpretation", confidence=.3)])
        self.assertEqual(result["observations"], ["Reading was 8.1"])
        self.assertEqual(result["interpretations"], ["Sensor must be broken"])
        self.assertIn("Which part is directly observed", " ".join(result["questions"]))

    def test_unknowns_trigger_question(self):
        result = audit([Evidence("Calibration history unavailable", "unknown", confidence=.2)])
        self.assertTrue(any("missing information" in q for q in result["questions"]))
        self.assertEqual(result["confidence_label"], "low")

    def test_same_context_conflict_is_detected(self):
        result = audit([Evidence("YES: valve is open", "claim", context="test A"),
                        Evidence("NOT: valve is open", "claim", context="test A")])
        self.assertEqual(len(result["contradictions"]), 1)
        self.assertIn("independent measurement", result["recommended_next_step"])

    def test_different_context_is_not_flagged(self):
        result = audit([Evidence("YES: valve is open", "claim", context="test A"),
                        Evidence("NOT: valve is open", "claim", context="test B")])
        self.assertEqual(result["contradictions"], [])

    def test_hypotheses_trigger_discriminating_question(self):
        result = audit([Evidence("Temperature rose after restart", "observation", confidence=.6)],
                       [Hypothesis("Sensor drift", "Reference sensor disagrees"),
                        Hypothesis("Real heating", "Independent sensor also rises")])
        self.assertTrue(any("prediction differs" in q for q in result["questions"]))

    def test_high_cost_decision_requires_review(self):
        result = audit([Evidence("One report suggests failure", "claim", confidence=.3)],
                       decision_cost="high")
        self.assertIn("human review", result["recommended_next_step"])

    def test_confidence_validation(self):
        with self.assertRaises(ValueError):
            Evidence("x", "observation", confidence=1.2)

    def test_empty_input_is_not_confident(self):
        result = audit([])
        self.assertEqual(result["confidence_label"], "insufficient_evidence")
        self.assertEqual(result["mean_input_confidence"], 0.0)

    def test_question_deduplication(self):
        result = audit([Evidence("Interpretation A", "interpretation"),
                        Evidence("Interpretation B", "interpretation")])
        self.assertEqual(len(result["questions"]), len(set(result["questions"])))

    def test_uncertainty_is_bounded(self):
        result = audit([Evidence("Observed", "observation", confidence=.8),
                        Evidence("Interpretation", "interpretation", confidence=.4)])
        self.assertGreaterEqual(result["uncertainty_score"], 0)
        self.assertLessEqual(result["uncertainty_score"], 1)

if __name__ == "__main__":
    unittest.main()
