import tempfile
import unittest
import zipfile
from pathlib import Path

import package_submission as packager


class PackageSubmissionTests(unittest.TestCase):
    def make_candidate(self, root: Path) -> None:
        files = {
            "agent.yaml": (
                "name: test_agent\n"
                "model: gemma-4-31b-it-qat-w4a16-ct\n"
                "instruction: !include prompts/system.md\n"
                "generate_content_config: !include configs/sampling.yaml\n"
                "skills:\n  - skills/graph-retrieval\n"
            ),
            "prompts/system.md": "Use evidence.\n",
            "configs/sampling.yaml": "temperature: 0.1\n",
            "skills/graph-retrieval/SKILL.md": "Retrieve relevant files.\n",
            "skills/graph-retrieval/scripts/retrieve.py": "print('ok')\n",
        }
        for rel, content in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def test_valid_candidate_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            self.make_candidate(root)
            self.assertEqual([], packager.validate_tree(root))

    def test_missing_include_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            self.make_candidate(root)
            (root / "prompts/system.md").unlink()
            self.assertTrue(any("missing required file" in e or "unresolved !include" in e
                                for e in packager.validate_tree(root)))

    def test_archive_has_agent_at_root_and_checksums(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            root.mkdir()
            self.make_candidate(root)
            output = Path(tmp) / "submission.zip"
            packager.build_zip(root, output)
            self.assertEqual([], packager.validate_zip(output))
            with zipfile.ZipFile(output) as archive:
                self.assertIn("agent.yaml", archive.namelist())
                self.assertNotIn("candidate/agent.yaml", archive.namelist())

    def test_wrong_model_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            self.make_candidate(root)
            path = root / "agent.yaml"
            path.write_text(path.read_text().replace(
                "gemma-4-31b-it-qat-w4a16-ct", "not-a-gemma-model"), encoding="utf-8")
            self.assertTrue(any("unsupported model" in e for e in packager.validate_tree(root)))


if __name__ == "__main__":
    unittest.main()
