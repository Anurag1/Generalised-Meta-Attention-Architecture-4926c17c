# Candidate agent scaffold

This is an integration scaffold for the Gemma 4 Developer Agent competition, not a validated submission archive.

## Contents
- `agent.yaml`: declarative ADK agent configuration using the competition's 31B model variant.
- `prompts/system.md`: evidence-first repair procedure.
- `skills/graph-retrieval`: offline Python file ranking using lexical clues and local import edges.
- `configs/sampling.yaml`: conservative generation settings.

## Local smoke test
Run the skill script against a local fixture by temporarily setting its `ROOT` to the fixture directory, or run it in the official sandbox where `/workspace` is the repository root. It requires only Python's standard library.

## Status and limitations
The scaffold has not yet been compiled by the official competition harness. The competition's installed ADK version and skill subprocess behavior must be validated in Kaggle before packaging. The retrieval script is candidate localization only; it does not edit files, run tests, or prove issue resolution. No real-Gemma benchmark has been run, and no performance gain is claimed.

## Required next validation
1. Run official config validation and compilation.
2. Run the harness on at least one known issue with the official model.
3. Compare against a lexical-only/no-graph ablation under identical settings.
4. Save logs and actual outcomes before updating the paper or creating a final `submission.zip`.
