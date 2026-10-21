import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "skills" / "graph-retrieval" / "scripts" / "retrieve.py"

class RetrievalScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "billing.py").write_text(
            "from validators import validate_invoice\ndef create_invoice(amount):\n return validate_invoice(amount)\n",
            encoding="utf-8",
        )
        (self.root / "validators.py").write_text(
            "def validate_invoice(amount):\n if amount < 0: raise ValueError('negative amount')\n return amount\n",
            encoding="utf-8",
        )
        (self.root / "unrelated.py").write_text(
            "def render_banner(theme):\n return theme\n", encoding="utf-8"
        )
    def tearDown(self):
        self.tmp.cleanup()
    def run_script(self, *args):
        env = dict(os.environ, GEMMA4_REPO_ROOT=str(self.root))
        proc = subprocess.run([sys.executable, str(SCRIPT), *args], text=True,
                              capture_output=True, env=env, check=True)
        return json.loads(proc.stdout)
    def test_retrieval_returns_direct_match_and_import_neighbor(self):
        payload = self.run_script("create_invoice")
        paths = [row["path"] for row in payload["results"]]
        self.assertIn("billing.py", paths)
        self.assertIn("validators.py", paths)
        neighbor = next(row for row in payload["results"] if row["path"] == "validators.py")
        self.assertEqual(neighbor["graph_bonus"], 1)
    def test_no_query_is_reported_without_crash(self):
        payload = self.run_script()
        self.assertIn("error", payload)
        self.assertEqual(payload["results"], [])
    def test_results_are_deterministically_sorted(self):
        first = self.run_script("invoice", "amount")
        second = self.run_script("invoice", "amount")
        self.assertEqual(first, second)
        self.assertEqual(first["results"], sorted(
            first["results"], key=lambda row: (-row["score"], -row["lexical_score"], row["path"])
        ))

if __name__ == "__main__":
    unittest.main()
