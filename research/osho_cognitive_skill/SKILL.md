# Osho-Inspired Witness & Inquiry Skill v0.1

## Purpose
An experimental AI skill translating broad philosophical themes commonly associated with Osho into transparent reasoning procedures. This is an original operationalization, not a claim that Osho formulated scientific laws and not a reproduction of his books or talks.

## Concept-to-computation map
| Inspiration | Computational routine | Falsifiable engineering expectation |
|---|---|---|
| Witnessing / observing | Separate observation, interpretation, claim, and unknown | Fewer observation/inference category errors on labeled cases |
| Non-attachment | Keep hypotheses revisable; request disconfirming evidence | More explicit counterevidence checks without more unsupported claims |
| Inquiry / questioning | Surface missing evidence and discriminating questions | Better coverage of predefined information needs |
| Tolerance of paradox | Preserve context; flag only explicit, context-matched conflicts | Fewer false contradictions when contexts differ |
| Pause before reaction | Scale verification to uncertainty and decision cost | Fewer premature high-impact recommendations on low-evidence cases |

These are hypotheses to test, not established outcomes. This package does not measure awareness, enlightenment, or inner experience.

## Use
Supply structured Evidence records and optional Hypothesis records to audit(). It returns an auditable scaffold, not a final truth judgment.

## Evaluation
Run from repository root:
    python -m unittest discover -s research/osho_cognitive_skill -p 'test_*.py' -v
    python research/osho_cognitive_skill/benchmark.py

The included cases are hand-authored software tests. They validate implementation behavior only, not general AI performance.

## Next scientific gate
1. Build a blinded, independently annotated dataset of real reasoning tasks.
2. Compare the same base model with and without this skill under matched model versions, task order, token budget, and decoding settings.
3. Have evaluators unaware of condition score evidence separation, contradiction precision/recall, assumption coverage, calibration, unsupported-claim rate, and task accuracy.
4. Preregister primary metrics, sample size, exclusion rules, and stopping criteria.
5. Report all outcomes, including null or negative results.
