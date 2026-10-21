#!/usr/bin/env python3
"""Build a deterministic candidate ZIP with agent.yaml at archive root.

This is an offline structural validator only. It does not replace the official
Kaggle ADK/harness validation or a scored Gemma run.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

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


def validate_tree(root: Path) -> list[str]:
    """Return structural errors for a candidate_agent directory."""
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
        elif model_match.group(1).strip("'\"") not in ALLOWED_MODELS:
            errors.append(f"unsupported model identifier: {model_match.group(1)}")

        # Validate the simple !include and skills paths used by this scaffold.
        for included in re.findall(r"!include\s+([^\s#]+)", agent_text):
            if not (root / included).is_file():
                errors.append(f"unresolved !include path: {included}")
        for skill in re.findall(r"(?m)^\s*-\s*(skills/[^\s#]+)\s*$", agent_text):
            if not (root / skill / "SKILL.md").is_file():
                errors.append(f"skill directory missing SKILL.md: {skill}")

    for py_file in root.rglob("*.py"):
        try:
            compile(py_file.read_text(encoding="utf-8"), str(py_file), "exec")
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"Python syntax/encoding error in {py_file.relative_to(root)}: {exc}")
    return errors


def build_zip(root: Path, output: Path) -> None:
    """Write candidate files at archive root; exclude caches and the output itself."""
    output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix != ".pyc"
        and p.resolve() != output.resolve()
    )
    payloads = [(p.relative_to(root).as_posix(), p.read_bytes()) for p in files]
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
                errors.append("archive paths must be relative to candidate_agent, not nested under candidate_agent/")
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
        print(f"PASS: ZIP structure and checksums verified: {args.validate_zip}")
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
    print(f"PASS: local structural checks; created {args.output}")
    print("LIMITATION: official Kaggle harness/model execution is not tested by this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
