# CHAKRAVYUH AI

## Research proposal

Chakravyuh AI treats complex problem solving as navigation through a partially observed, dynamically constructed state space. The system must discover the structure of the problem, identify contradictions and traps, choose high-information actions, and establish a verified exit rather than merely producing a plausible answer.

> **Hypothesis:** A controller that explicitly models problem layers, contradictions, uncertainty, and verification can improve verified problem solving over direct answer generation, under matched compute and tool budgets.

## Architecture

```text
UNKNOWN PROBLEM
      |
      v
 OBSERVE / PARSE
      |
      v
 STRUCTURED GRAPH
      |
      v
 CHAKRAVYUH CONTROLLER
   |       |        |
   |       |        +--> EXIT DETECTOR
   |       +-----------> TRAP / CONTRADICTION DETECTOR
   +-------------------> LAYER / STATE DETECTOR
      |
      v
 NEXT ACTION SELECTOR
 (question | search | experiment | revise)
      |
      v
 EVIDENCE / RESULT
      |
      v
 INDEPENDENT VERIFIER
      |
   +--+--+
   |     |
 FAIL   PASS
   |     |
   +--> UPDATE GRAPH --> continue / exit
```

## State representation

Each problem state should maintain:

- `layer`: estimated structural depth;
- `beliefs`: active hypotheses with confidence;
- `constraints`: hard and soft constraints;
- `contradictions`: explicit conflicts with provenance;
- `open_questions`: unresolved information gaps;
- `actions`: candidate information-gathering or execution actions;
- `evidence`: observations/results linked to claims;
- `exit_conditions`: criteria that make a solution externally testable;
- `history`: transitions, failures, recoveries, and verification outcomes.

## Action policy

The controller chooses the next action using expected information gain, estimated cost, and risk of entering a known trap.

A simple policy score is:

```text
score(action) = information_gain(action)
                - lambda * cost(action)
                - mu * trap_risk(action)
                + nu * exit_progress(action)
```

The coefficients are experimental parameters, not claims of optimality.

## Contradictions as navigation signals

A contradiction is not treated as noise to be hidden. It becomes a state-transition trigger:

```text
belief -> prediction -> observation
                    |
                 mismatch
                    v
             contradiction node
                    |
                    v
            discriminating question
                    |
                    v
              new evidence
```

## CHAKRAVYUH-Bench

The benchmark should contain procedurally generated and human-authored tasks covering:

1. **Hidden dependency** — a missing relationship must be discovered.
2. **Contradictory evidence** — competing hypotheses require a discriminating observation.
3. **Dynamic environment** — the state changes after actions.
4. **False exit** — an apparently correct answer fails a withheld test.
5. **Unknown depth** — the number of reasoning layers is not revealed.
6. **Discovery** — the system must produce a testable insight not explicitly supplied in the input.

Every task should expose enough information to reproduce the environment while withholding the target trajectory.

## Metrics

Primary metric:

```text
Verified Discovery Rate = independently verified novel discoveries
                           / attempted discoveries
```

Secondary metrics:

- final task success;
- layer identification accuracy;
- contradiction detection precision/recall;
- question utility / information gain;
- actions-to-verification;
- trap-entry rate;
- recovery rate;
- false-exit rate;
- verification success;
- compute/tool cost.

## Baselines

At minimum compare:

- Direct LLM answer generation;
- RAG agent;
- standard tool-using agent;
- standard multi-agent system;
- **Chakravyuh Controller** with the same underlying model/tool budget.

The core ablation is to remove controller capabilities one at a time:

- no explicit layers;
- no contradiction state;
- no information-gain action selection;
- no independent verifier;
- no persistent graph state.

## Scientific standard

This proposal is an architectural hypothesis, not a demonstrated breakthrough. Results must be reported with matched budgets, fixed task seeds where applicable, confidence intervals where possible, and failure cases. A performance improvement on one benchmark is not sufficient evidence for general superiority.

## Relationship to existing work

This module is intentionally positioned as a controller/benchmark layer over the existing reasoning portfolio:

- **MART / Generalised Meta-Attention** — confidence and self-critique;
- **SUPHAI** — orchestration and dynamic allocation;
- **Geometric Engine Intelligence** — graph/relationship discovery;
- **HONET** — contradiction/assumption-driven discovery;
- **symbiote-agent-live** — execution agents;
- **Anurag1 profile** — integrated discovery → hypothesis → testing → validation workflow.

The novelty claim should therefore focus on the composition and its empirical behavior, not on claiming that the individual ingredients are new.
