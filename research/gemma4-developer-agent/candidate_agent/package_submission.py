#!/usr/bin/env python3
"""Build a candidate ZIP and perform offline structural checks.

This validator is intentionally conservative. It is not the official Kaggle ADK
compiler, model runtime, or scoring harness.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

# Model variants announced by Kaggle staff; all agents/subagents in one submission must agree.
ALLOWED_MODELS = {
    "gemma-4-31b-it-qat-w4a16-ct",
    "gemma-4-12b-it-qat-w4a16-ct",
    "gemma-4-e4b-it-qat-w4a16-ct",
    "gemma-4-e2b-it-qat-w4a16-ct",
}
REQUIRED_FILES = (
    Path("agent.yaml"),
    Path("prompts/system.md"),
    Path("configs/sampling.yaml"),
    Path("skills/graph-retrieval/SKILL.md"),
    Path("skills/graph-retrieval/scripts/retrieve.py"),
)
SUBMISSION_ROOTS = {"prompts", "configs", "sub_agents", "skills", "adapters"}


def _safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def validate_tree(root: Path) -> list[str]:
    """Return structural errors for the candidate agent directory."""
    errors: list[str] = []
    if not root.is_dir():
        return [f"candidate directory does not exist: {root}"]

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel.as_posix()}")

    agent_path = root / "agent.yaml"
    if agent_path.is_file():
        agent_text = agent_path.read_text(encoding="utf-8")
        model_match = re.search(r"(?m)^model:\s*([^\s#]+)", agent_text)
        if not model_match:
            errors.append("agent.yaml must declare a top-level model")
        elif model_match.group(1).strip("'\\\"") not in ALLOWED_MODELS:
            errors.append(
                "unsupported competition model; allowed models: " + ", ".join(sorted(ALLOWED_MODELS)) + "; "
                f"found {model_match.group(1)}"
            )

        root_model = model_match.group(1).strip("'\\\"") if model_match else None
        for config_path in sorted(root.rglob("*.yaml")) + sorted(root.rglob("*.yml")):
            if config_path == agent_path:
                continue
            config_text = config_path.read_text(encoding="utf-8")
            for configured_model in re.findall(r"(?m)^model:\s*([^\s#]+)", config_text):
                configured_model = configured_model.strip("'\\\"")
                if configured_model not in ALLOWED_MODELS:
                    errors.append(f"unsupported competition model in {config_path.relative_to(root)}: {configured_model}")
                elif root_model and configured_model != root_model:
                    errors.append(
                        f"mixed base models are not allowed: agent.yaml uses {root_model}, "
                        f"{config_path.relative_to(root)} uses {configured_model}"
                    )

        for included in re.findall(r"!include\s+([^\s#]+)", agent_text):
            if not _safe_relative(included):
                errors.append(f"unsafe !include path: {included}")
            elif not (root / included).is_file():
                errors.append(f"unresolved !include path: {included}")

        for skill in re.findall(r"(?m)^\s*-\s*(skills/[^\s#]+)\s*$", agent_text):
            if not _safe_relative(skill):
                errors.append(f"unsafe skill path: {skill}")
                continue
            manifest = root / skill / "SKILL.md"
            if not manifest.is_file():
                errors.append(f"skill directory missing SKILL.md: {skill}")
                continue
            manifest_text = manifest.read_text(encoding="utf-8")
            if not re.search(r"(?s)^---\s*\n.*?^name:\s*[A-Za-z0-9_-]+\s*$.*?^---\s*$", manifest_text, re.M):
                errors.append(f"skill manifest requires YAML frontmatter with name: {skill}")

    for py_file in root.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            compile(py_file.read_text(encoding="utf-8"), str(py_file), "exec")
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"Python syntax/encoding error in {py_file.relative_to(root)}: {exc}")
    return errors


def _submission_files(root: Path) -> list[Path]:
    """Include only runtime submission assets, never dev tests or packaging code."""
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(root)
        if relative == Path("agent.yaml") or relative.parts[0] in SUBMISSION_ROOTS:
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def build_zip(root: Path, output: Path) -> None:
    """Write submission runtime assets at archive root with a checksum manifest."""
    output.parent.mkdir(parents=True, exist_ok=True)
    payloads = [
        (p.relative_to(root).as_posix(), p.read_bytes())
        for p in _submission_files(root)
    ]
    manifest = "".join(
        f"{hashlib.sha256(data).hexdigest()}  {name}\n"
        for name, data in payloads
    ).encode("utf-8")
    payloads.append(("MANIFEST.sha256", manifest))

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in payloads:
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.date_time = (2026, 1, 1, 0, 0, 0)
            archive.writestr(info, data)


def validate_zip(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"archive does not exist: {path}"]
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if "agent.yaml" not in names:
                errors.append("archive root must contain agent.yaml")
            if any(name.startswith("candidate_agent/") for name in names):
                errors.append("archive paths must not be nested under candidate_agent/")
            if any(name.startswith(("tests/", "candidate_agent/tests/")) for name in names):
                errors.append("development tests must not be included in the submission ZIP")
            if "package_submission.py" in names or any(name.endswith("/package_submission.py") for name in names):
                errors.append("development packaging script must not be included in the submission ZIP")
            bad_member = archive.testzip()
            if bad_member:
                errors.append(f"ZIP CRC check failed for: {bad_member}")
            if "MANIFEST.sha256" not in names:
                errors.append("archive is missing MANIFEST.sha256")
            else:
                manifest = archive.read("MANIFEST.sha256").decode("utf-8")
                for line in manifest.splitlines():
                    expected, sep, name = line.partition("  ")
                    if not sep or name not in names:
                        errors.append(f"invalid manifest entry: {line}")
                        continue
                    actual = hashlib.sha256(archive.read(name)).hexdigest()
                    if actual != expected:
                        errors.append(f"checksum mismatch: {name}")
                listed = {
                    line.partition("  ")[2]
                    for line in manifest.splitlines()
                    if "  " in line
                }
                if listed != names - {"MANIFEST.sha256"}:
                    errors.append("manifest does not cover exactly the archive payload files")
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError) as exc:
        errors.append(f"cannot read ZIP: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="candidate_agent directory (default: this script's directory)")
    parser.add_argument("--output", type=Path, default=Path("submission.zip"),
                        help="output ZIP path (default: ./submission.zip)")
    parser.add_argument("--validate-zip", type=Path,
                        help="validate an existing candidate archive instead of building one")
    args = parser.parse_args()

    if args.validate_zip:
        errors = validate_zip(args.validate_zip)
        if errors:
            print("FAIL: " + "\nFAIL: ".join(errors), file=sys.stderr)
            return 1
        print(f"PASS: offline ZIP structure and checksums verified: {args.validate_zip}")
        print("LIMITATION: official Kaggle compiler and model execution are not tested.")
        return 0

    errors = validate_tree(args.root)
    if errors:
        print("FAIL: " + "\nFAIL: ".join(errors), file=sys.stderr)
        return 1
    build_zip(args.root, args.output)
    zip_errors = validate_zip(args.output)
    if zip_errors:
        print("FAIL: " + "\nFAIL: ".join(zip_errors), file=sys.stderr)
        return 1
    print(f"PASS: offline structural checks; created {args.output}")
    print("LIMITATION: official Kaggle compiler and model execution are not tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
