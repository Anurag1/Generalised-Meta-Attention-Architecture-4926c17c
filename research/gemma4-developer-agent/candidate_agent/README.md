# Candidate agent scaffold

This is an integration scaffold for the Gemma 4 Developer Agent competition, not an officially validated submission.

## Contents
- `agent.yaml`: declarative ADK candidate configuration using `gemma-4-31b-it-qat-w4a16-ct`.
- `prompts/system.md`: evidence-first repair procedure.
- `skills/graph-retrieval`: offline Python file ranking using lexical clues and local import edges.
- `configs/sampling.yaml`: conservative generation settings.
- `package_submission.py`: deterministic ZIP builder plus offline structural/checksum validator.

## Build a candidate ZIP

From this directory, run:

```bash
python package_submission.py --output /tmp/submission.zip
python package_submission.py --validate-zip /tmp/submission.zip
```

The archive places `agent.yaml` at its root, includes the referenced prompt/config/skill files, and records SHA-256 hashes in `MANIFEST.sha256`. The script checks required files, simple `!include` paths, skill paths, permitted model identifiers, Python syntax, ZIP integrity, and checksums.

Run tests with:

```bash
python -m unittest discover -s tests -v
```

## Status and limitations

The offline package checks are **not** official ADK/harness validation. The retrieval script is candidate localization only; it does not edit files, run repository tests, or prove issue resolution. No real-Gemma benchmark has been run, and no performance gain is claimed. A candidate ZIP built locally is not a Kaggle submission.

## Remaining validation

1. Run official config validation and compilation in the Kaggle competition environment.
2. Run the harness on a fixed issue set with the official model.
3. Compare against a lexical-only/no-graph ablation under identical settings.
4. Save actual logs and measurements before updating the paper.
5. Upload and submit the paper Writeup on Kaggle before its deadline; separately join/accept rules and submit the main-track archive if entering that track.
