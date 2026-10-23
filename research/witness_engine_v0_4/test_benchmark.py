import os
import unittest
from unittest.mock import patch

from research.witness_engine_v0_4 import benchmark


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.claims = [
            {"subject": "sample", "predicate": "state", "object": "solid",
             "source_id": "a", "confidence": 0.9, "polarity": True, "context": "same"},
            {"subject": "sample", "predicate": "state", "object": "liquid",
             "source_id": "b", "confidence": 0.8, "polarity": True, "context": "same"},
        ]

    def test_confusion_metrics(self):
        result = benchmark.confusion([True, True, False, False], [True, False, True, False])
        self.assertEqual((result["tp"], result["tn"], result["fp"], result["fn"]), (1, 1, 1, 1))
        self.assertEqual(result["accuracy"], 0.5)

    def test_openai_responses_parser(self):
        mocked = {"id": "resp-test", "usage": {"input_tokens": 10, "output_tokens": 4},
                  "output": [{"type": "message", "content": [
                      {"type": "output_text", "text": '{"contradiction":true,"rationale":"different values"}'}
                  ]}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), patch.object(benchmark, "post", return_value=mocked):
            pred, metadata = benchmark.predict("openai", "test-model", self.claims)
        self.assertTrue(pred)
        self.assertEqual(metadata["request_id"], "resp-test")
        self.assertEqual(metadata["input_tokens"], 10)

    def test_anthropic_messages_parser(self):
        mocked = {"id": "msg-test", "usage": {"input_tokens": 11, "output_tokens": 5},
                  "content": [{"type": "text", "text": '{"contradiction":false,"rationale":"same claim"}'}]}
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}), patch.object(benchmark, "post", return_value=mocked):
            pred, metadata = benchmark.predict("anthropic", "test-model", self.claims)
        self.assertFalse(pred)
        self.assertEqual(metadata["output_tokens"], 5)

    def test_gemini_parser(self):
        mocked = {"responseId": "gem-test",
                  "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 6},
                  "candidates": [{"content": {"parts": [
                      {"text": '{"contradiction":true,"rationale":"conflict"}'}
                  ]}}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), patch.object(benchmark, "post", return_value=mocked):
            pred, metadata = benchmark.predict("gemini", "test-model", self.claims)
        self.assertTrue(pred)
        self.assertEqual(metadata["output_tokens"], 6)

    def test_invalid_json_boolean_is_rejected(self):
        with self.assertRaises(ValueError):
            benchmark.parse_bool('{"contradiction":"true"}')

    def test_invalid_json_is_rejected(self):
        with self.assertRaises(ValueError):
            benchmark.parse_bool("not json")


if __name__ == "__main__":
    unittest.main()
