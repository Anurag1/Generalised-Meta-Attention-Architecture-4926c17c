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
            "skills/graph-retrieval/SKILL.md": (
                "---\nname: graph-retrieval\ndescription: retrieve files\n---\n"
                "Retrieve relevant files.\n"
            ),
            "skills/graph-retrieval/scripts/retrieve.py": "print('ok')\n",
            "tests/test_example.py": "def test_example(): pass\n",
            "package_submission.py": "# development-only\n",
            "README.md": "# development notes\n",
        }
        for rel, text in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

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

    def test_archive_root_manifest_and_dev_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            root.mkdir()
            self.make_candidate(root)
            output = Path(tmp) / "submission.zip"
            packager.build_zip(root, output)
            self.assertEqual([], packager.validate_zip(output))
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertIn("agent.yaml", names)
                self.assertNotIn("candidate/agent.yaml", names)
                self.assertNotIn("tests/test_example.py", names)
                self.assertNotIn("package_submission.py", names)
                self.assertNotIn("README.md", names)
                self.assertIn("skills/graph-retrieval/SKILL.md", names)

    def test_wrong_model_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            self.make_candidate(root)
            path = root / "agent.yaml"
            path.write_text(path.read_text().replace(
                "gemma-4-31b-it-qat-w4a16-ct", "gemma-4-12b-it-qat-w4a16-ct"), encoding="utf-8")
            self.assertTrue(any("requires model gemma-4-31b-it-qat-w4a16-ct" in e
                                for e in packager.validate_tree(root)))

    def test_skill_manifest_requires_frontmatter_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            self.make_candidate(root)
            (root / "skills/graph-retrieval/SKILL.md").write_text(
                "No YAML frontmatter here\n", encoding="utf-8")
            self.assertTrue(any("frontmatter" in e for e in packager.validate_tree(root)))


if __name__ == "__main__":
    unittest.main()
