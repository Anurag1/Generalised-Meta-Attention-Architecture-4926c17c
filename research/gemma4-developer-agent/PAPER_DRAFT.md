# Graph-Guided, Test-Verified Repository Repair with Gemma 4

**Subtitle:** A reproducible experimental protocol for the Google Gemma 4 Developer Agent Competition  
**Status:** Research-protocol draft. No benchmark results are claimed. This must not be presented as a completed empirical paper until experiments have been run and the results independently checked.

## Abstract

Autonomous software-engineering agents must locate relevant code, infer intended behavior from incomplete issue descriptions, construct a patch, and verify that the change resolves the issue without introducing regressions. This paper proposes a compact method for repository-level repair that combines graph-guided context retrieval with explicit hypothesis tracking and test-driven verification. A repository graph prioritizes files and symbols connected to issue-relevant code; a repair loop records candidate explanations, maps each explanation to a proposed change, and uses available tests and failure messages to accept, revise, or reject a patch.

The central research question is whether this structured workflow improves the fraction of benchmark issues whose patches pass validation, compared with a simpler repository-search-and-edit baseline, under the same model, compute budget, and evaluation split. This document specifies the method and the experiments required to answer that question. No performance improvement is claimed here.

## 1. Introduction

Repository-level bug fixing is difficult because issue reports are often underspecified, relevant behavior may span multiple files, and a plausible edit is not necessarily a correct edit. Agents need both efficient codebase navigation and a reliable mechanism for checking proposed changes.

This project tests the hypothesis that lightweight code-graph retrieval, combined with explicit repair hypotheses and bounded test-driven revision, can help a fixed Gemma 4 agent allocate its context and tool calls more effectively. The approach is modular: each component must earn its place through controlled ablation.

Research questions:

- **RQ1:** Does graph-guided retrieval improve issue-level patch pass rate over ordinary repository search?
- **RQ2:** Does explicit hypothesis tracking plus test-guided revision add value beyond graph retrieval alone?
- **RQ3:** Are gains robust across repository types and issue categories, and do they justify additional latency or tool calls?
- **RQ4:** Which failure modes remain dominant after adding the proposed components?

## 2. Method

### 2.1 Workflow

The agent follows five stages: (1) parse the issue into a concise problem representation; (2) locate candidate files and symbols; (3) construct and rank a bounded evidence set; (4) draft a minimal patch tied to an explicit hypothesis; and (5) run available validation and revise only when observed evidence supports a change. The agent stops when relevant checks pass, the per-task budget is exhausted, or further actions are unlikely to provide useful evidence.

### 2.2 Issue representation

Represent the issue using observed behavior, expected behavior, reproduction clues, constraints, likely subsystem, and unresolved questions. These are search hints, not ground truth. Distinguish observed evidence from assumptions. Unknown fields remain unknown rather than being filled with invented details.

### 2.3 Graph-guided retrieval

Use only repository structure and graph data available in the permitted competition environment. Candidate nodes may include files, symbols, imports, calls, tests, and dependency relationships when those are available. Seed retrieval with issue terms and initial search results, then expand through a bounded neighborhood. Rank candidates using a transparent combination of lexical relevance, graph proximity, test adjacency, and evidence discovered during the current task. Tune weights only on a development split, not hidden evaluation tasks.

The graph is a navigation aid, not a correctness oracle. When graph data is missing or stale, fall back to repository search and direct file inspection. Source files remain authoritative.

### 2.4 Hypothesis ledger

Maintain a compact ledger with hypothesis, supporting evidence, contradicting evidence, predicted behavior, candidate edit, and verification status. Limit the number of active hypotheses to prevent unbounded deliberation. Prefer the smallest justified change that explains the evidence. A contradiction is evidence that conflicts with a prediction—for example, a test indicating that the suspected function is not on the failing path. Use it to revise or discard the hypothesis rather than rationalize it away.

### 2.5 Patch construction and verification

Prefer minimal patches. Before editing, identify the expected behavior change and relevant tests. After editing, inspect the diff and run the narrowest relevant tests first, followed by broader tests when budget permits. Treat test output as evidence: passing tests support a patch but do not prove universal correctness. Classify failures as likely regressions, pre-existing failures, environment problems, or inconclusive results. Never claim validation succeeded unless the command ran and returned success.

### 2.6 Budget control

Use a bounded action policy with stages for localization, focused inspection, first patch, verification, and a limited number of evidence-driven revisions. Record tool calls, elapsed time, test outcomes, and stop reason. Calibrate limits with the official harness, then freeze them before final evaluation.

## 3. Experimental Design

### 3.1 Baselines and ablations

Run configurations with the same permitted Gemma 4 base model, sampling settings, tools, task subset, and per-task budget. Confirm the current official rules before execution.

- **A — Search-and-edit baseline:** ordinary text search, file reading, one patch attempt, and available tests.
- **B — Graph retrieval:** baseline plus bounded graph-guided candidate ranking.
- **C — Hypothesis ledger:** baseline plus explicit predictions and contradiction checks, without graph ranking.
- **D — Combined method:** graph retrieval plus hypothesis ledger and bounded test-driven revision.
- **E — Optional adapter:** if a LoRA adapter is trained, compare it with the strongest non-adapter configuration on the same development split. Omit it unless gains are repeatable and the artifact is compatible with the official evaluator.

### 3.2 Split discipline

Use a development subset for implementation and tuning, a separate validation subset for final configuration selection, and the official hidden evaluation for final scoring. If the official data does not support this arrangement, document the available split and avoid repeated selection against hidden leaderboard feedback. Freeze the configuration and analysis rules before final evaluation. Prevent repository, issue, or near-duplicate leakage across local splits where feasible.

### 3.3 Metrics

**Primary metric:** issue-level validation pass rate, calculated as tasks whose final patch passes validation divided by tasks evaluated. Always report numerator and denominator.

**Secondary metrics:** time to first patch; total wall-clock time per issue; tool calls; test executions; pass rate by issue category; invalid or empty patch rate; and failure categories. Compare configurations using paired per-issue outcomes on the same subset. Report uncertainty where sample size permits and avoid treating small differences on small samples as decisive.

### 3.4 Failure analysis

Use a fixed taxonomy: wrong localization; incomplete issue understanding; incorrect causal hypothesis; patch too broad; syntactically invalid patch; relevant tests not found; tests fail after patch; environment/dependency failure; budget exhaustion; and ambiguous or insufficient evidence. Publish examples only when permitted by competition rules and never disclose hidden evaluation content.

### 3.5 Reproducibility record

For each run, save code revision, configuration hash, model identifier, split identifier, random seed where applicable, environment notes, task-level outcomes, elapsed time, and logs allowed by competition rules. Preserve failed runs; do not silently exclude them.

## 4. Results

**No experiments have been executed for this draft.** Therefore, it reports no empirical results and makes no claim that the proposed method outperforms a baseline.

Populate the table only after running the experiment:

| Configuration | Tasks (n) | Passed (k) | Pass rate | Median time/task | Mean tool calls |
|---|---:|---:|---:|---:|---:|
| Search-and-edit baseline | Not run | Not run | Not run | Not run | Not run |
| Graph retrieval | Not run | Not run | Not run | Not run | Not run |
| Hypothesis ledger | Not run | Not run | Not run | Not run | Not run |
| Combined method | Not run | Not run | Not run | Not run | Not run |
| Combined + LoRA (optional) | Not run | Not run | Not run | Not run | Not run |

Report absolute pass-rate differences versus baseline and uncertainty. If the combined method does not improve results, report that finding and identify any component that increases cost without measurable benefit.

## 5. Limitations and Threats to Validity

Graph quality may vary by language, repository size, dynamic behavior, and available metadata. Graph proximity can surface irrelevant code and miss reflection, generated code, runtime configuration, or implicit dependencies. The hypothesis ledger may add latency or merely formalize reasoning the base model already performs. Test suites are incomplete: passing tests do not guarantee intended behavior, and failures can arise from environment issues. Results on small development subsets may not generalize to hidden tasks. Tuning can overfit, especially when leaderboard feedback is repeatedly used. Performance also depends on the exact competition harness, model variant, tool restrictions, and runtime environment. Controlled ablations, frozen evaluation, and transparent reporting are essential.

## 6. Conclusion

This draft defines a falsifiable, resource-conscious approach to repository-level repair: use code graphs to guide navigation, record repair hypotheses and contradictory evidence, and revise patches based on observed tests. Its current contribution is a reproducible experimental protocol, not a demonstrated performance gain. The method should be considered successful only if controlled experiments show a robust improvement in validation pass rate that justifies added complexity and runtime. A final submission must include verified results, the exact configuration, and the evaluation setup.

## References

1. Google DeepMind. [Google — The Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview).
2. Google DeepMind. [Google — The Gemma 4 Developer Agent Paper Track](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper/overview).
3. Jimenez, C. E., et al. “SWE-bench: Can Language Models Resolve Real-World GitHub Issues?” ICLR, 2024. [SWE-bench](https://www.swebench.com/).

## Pre-submission checklist

- Implement the method in the official harness.
- Verify the currently permitted model variant and current competition rules.
- Run the baseline and feasible ablations on a frozen development/validation subset.
- Replace all “Not run” values with actual measurements and denominators.
- Add run IDs, configuration hashes, environment details, and failure analysis.
- Verify citations and confirm the work is original and unpublished.
- Check the paper track's word limit and submit through the official Kaggle Writeup workflow.
- Do not claim a rank, win probability, or performance improvement without evidence.
