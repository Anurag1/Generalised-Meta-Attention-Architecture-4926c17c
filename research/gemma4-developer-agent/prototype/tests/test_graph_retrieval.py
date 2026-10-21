import json
import tempfile
import unittest
from pathlib import Path
from graph_retrieval import PythonRepositoryGraph, tokens

class GraphRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "billing.py").write_text("from validators import validate_invoice\ndef create_invoice(amount):\n return validate_invoice(amount)\n", encoding="utf-8")
        (self.root / "validators.py").write_text("def validate_invoice(amount):\n if amount < 0: raise ValueError('negative amount')\n return amount\n", encoding="utf-8")
        (self.root / "unrelated.py").write_text("def render_banner(theme):\n return theme\n", encoding="utf-8")
        (self.root / "broken.py").write_text("def bad(:\n", encoding="utf-8")
        self.graph = PythonRepositoryGraph(self.root)
    def tearDown(self):
        self.tmp.cleanup()
    def test_tokens_casefold_and_filter(self):
        self.assertEqual(tokens("Invoice AMOUNT with the issue"), {"invoice", "amount"})
    def test_direct_match(self):
        results = self.graph.retrieve("invoice amount validation", top_k=3)
        self.assertEqual(results[0].path, "billing.py")
        self.assertIn("validators.py", [r.path for r in results])
    def test_graph_bonus_retrieves_import_neighbor(self):
        results = self.graph.retrieve("create_invoice", top_k=5, graph_hops=1)
        target = next(r for r in results if r.path == "validators.py")
        self.assertEqual(target.graph_bonus, 1)
    def test_json_and_determinism(self):
        a = self.graph.explain("invoice amount", top_k=5)
        self.assertEqual(a, self.graph.explain("invoice amount", top_k=5))
        json.dumps(a)
    def test_invalid_arguments(self):
        with self.assertRaises(ValueError): self.graph.retrieve("invoice", top_k=0)
        with self.assertRaises(ValueError): self.graph.retrieve("invoice", graph_hops=-1)
    def test_empty_query(self):
        self.assertEqual(self.graph.retrieve("the with"), [])

if __name__ == "__main__":
    unittest.main()
