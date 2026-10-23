# HONET Witness Engine — experimental staging package v0.4

This code stages a narrow structured-claim contradiction experiment alongside MART's meta-attention research. It is **not yet integrated into the canonical HONET repository**.

## What this tests
Given two normalized claims, detect incompatible object values or opposite polarity only when subject, predicate, and context match. Includes a context-blind baseline and an optional single-model API arm for OpenAI Responses, Anthropic Messages, or Gemini generateContent.

## Local checks
From repository root:

```bash
python -m unittest research.witness_engine_v0_4.test_witness_engine -v
python research/witness_engine_v0_4/benchmark.py --help
```

## Live model run
The optional model run calls paid APIs. Use repository Actions secrets; do not place keys in source files, command-line arguments, logs, issues, or this chat. See `../../.github/workflows/witness-engine-benchmark.yml`.

Provider secret names:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

The frozen case generator makes 40 cases (20 positive, 20 negative), deterministically. Each provider run reports a dataset fingerprint, per-case outputs, usage/latency metadata, metrics, and failed requests. Use the exact same case generator and prompt version for each run.

## Interpretation policy
This benchmark is deliberately synthetic and has simple rules. It validates that the comparison process works; it cannot establish general reasoning superiority. A real claim requires a separate expert-labeled benchmark with realistic, non-template data. The planned next target is paper–code discrepancy detection (e.g. SciCoQA), which needs full paper/code retrieval and cannot be replaced by this claim comparator.

## Provenance
The original HONET organization's branch-write permission was unavailable to the current GitHub integration. This staging module is in the user-owned Generalised Meta-Attention repository on a feature branch as a reviewable alternative; it does not modify HONET's default branch.
