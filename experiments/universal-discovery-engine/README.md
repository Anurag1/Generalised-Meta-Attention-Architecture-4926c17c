# Universal Discovery Engine (UDE) — prototype

A reproducible, dependency-free Python prototype for moving from a claim to a testable candidate discovery. It searches numeric tables for pairwise linear relationships, fits each hypothesis on training rows, tests on held-out rows, and compares prediction error with a constant baseline.

## Run

```bash
cd experiments/universal-discovery-engine
python -m unittest discover -s tests -v
python discovery_engine.py sample_data.csv discovery_report.json
```

## Verification rule

A candidate is marked `verified=true` only when it beats the held-out constant baseline by at least 20% and its held-out mean absolute error is no more than 25% of the held-out target's standard deviation (with a small numerical tolerance). This is a prototype criterion, not a universal scientific standard.

## Evidence boundary

The bundled CSV is synthetic and contains intentionally related numeric columns. It proves the pipeline can recover and test a known relationship; it does **not** establish a novel scientific law or prove the engine outperforms modern AI generally. A next research milestone would use real, licensed datasets, preregistered hypotheses, stronger baselines, and independent evaluation.

## Current limitations

- Searches only pairwise linear relationships.
- Does not establish causality.
- No external LLM or historical corpus is integrated yet.
- Synthetic benchmark validates the implementation, not scientific novelty.
