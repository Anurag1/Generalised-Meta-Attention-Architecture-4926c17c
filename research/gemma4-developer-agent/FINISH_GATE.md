# Finish Gate: Gemma 4 Developer Agent

**Purpose:** Explicit, evidence-based completion gate for PR #10. This file is a checklist, not evidence that any unchecked step has passed.

## Current state (2026-10-21)

- Branch: `gemma4-submission-prep`
- PR: [#10](https://github.com/Anurag1/Generalised-Meta-Attention-Architecture-4926c17c/pull/10) — draft, must not merge until validation passes.
- CI: latest observed jobs failed before any steps ran; no runner was assigned. This is an infrastructure/setup blocker, not a test result.
- Kaggle: official compiler/runtime and actual Gemma evaluations have not been run by this connected workflow.
- Performance: no measured improvement is claimed. Synthetic prototype tests are not competition results.

## Gate 0 — Access and prerequisites

- [ ] Confirm the repository's GitHub Actions service and hosted-runner entitlement are operational; inspect repository/org Actions settings and billing/usage limits with an authorized maintainer.
- [ ] Confirm the connected GitHub identity can read workflow logs, write the feature branch, and access PR checks.
- [ ] In the user's own Kaggle session, confirm entry eligibility, accept the current competition rules, and confirm access to the official competition notebook/runtime and required datasets.
- [ ] Read the live rules and harness README immediately before testing. The official overview may lag newer staff announcements; the latest staff notice allows four Gemma 4 variants but forbids mixing variants within one submission.
- [ ] Do not paste access tokens, cookies, API keys, or passwords into chat or repository files. Use platform-provided secrets/credentials only where actually supported.

## Gate 1 — Local/CI structural validation

Run from the repository root on Python 3.12 (or the exact supported version stated by the current workflow):

```bash
cd research/gemma4-developer-agent/prototype
PYTHONPATH=. python -m unittest discover -s tests -v

cd ../candidate_agent
python -m unittest discover -s tests -v
python package_submission.py --output /tmp/submission.zip
python package_submission.py --validate-zip /tmp/submission.zip
```

Required evidence:
- [ ] Every command actually executes and exits zero.
- [ ] Save the complete logs, commit SHA, Python version, and generated ZIP SHA-256.
- [ ] Confirm `agent.yaml` is at the ZIP root; all `!include` and skill paths resolve; no tests or packager code are included; archive integrity and manifest checks pass.
- [ ] Review the archive contents and the full diff manually.
- [ ] Verify all root/subagent configs use the same permitted base-model variant.
- [ ] Never treat a job with no runner/steps/log as a test pass.

## Gate 2 — Repair GitHub Actions

- [ ] Inspect Actions settings, hosted-runner quota/billing, organization policies, concurrency limits, and current GitHub service status with authorized account access.
- [ ] If hosted runners are unavailable, restore authorized runner access or use an approved runner. Do not add a self-hosted runner without the maintainer's explicit security review.
- [ ] Rerun the Gemma workflow after runner access is restored.
- [ ] Require actual checkout/setup/test/package steps in the run log and a successful final conclusion.
- [ ] Investigate unrelated legacy workflows separately; do not hide, skip, or weaken failing checks merely to make the PR green.

## Gate 3 — Official Kaggle compatibility

- [ ] Use the official competition notebook/runtime and its current harness instructions.
- [ ] Build the submission ZIP with `agent.yaml` at archive root.
- [ ] Compile/load the agent using the official compiler; resolve schema, tool-name, sandbox, include, skill, and model errors.
- [ ] Run the smallest permitted official smoke evaluation first and preserve its actual logs.
- [ ] Verify the submission respects the current task/time budget and uses only tools exposed by the harness.
- [ ] Do not infer compatibility from the offline packager alone.

## Gate 4 — Controlled model and method comparison

Compare model variants in separate packages/runs, never mixed within one package. Use only variants confirmed by the live rules.

### Minimum ablation matrix

| ID | Retrieval | Reasoning/verification | Purpose |
|---|---|---|---|
| A | Ordinary search | Minimal patch + tests | Baseline |
| B | Graph-guided retrieval | Same patch/test loop as A | Isolate graph retrieval |
| C | Ordinary search | Hypothesis ledger + contradiction checks + bounded test-driven revision | Isolate verification method |
| D | Graph-guided retrieval | Hypothesis ledger + contradiction checks + bounded test-driven revision | Combined method |

- [ ] Freeze a reproducible development task subset and a separate validation subset; avoid tuning against hidden evaluation results.
- [ ] Keep model variant, task set, sampling, tool access, action/time budget, and evaluation procedure fixed within each paired comparison.
- [ ] Run every configuration on the same task IDs. Record per-task results, not only averages.
- [ ] Report issue-level pass rate as passed / evaluated, invalid or empty patch rate, localization Recall@k if reference locations are available, time per issue, tool calls, test executions, and failure category.
- [ ] Keep environment/dependency failures separate from agent failures; retain failed and incomplete runs.
- [ ] Report paired differences and uncertainty where sample size permits. Do not claim an improvement if the evidence is weak or mixed.
- [ ] Compare smaller Gemma variants only as separate controlled runs, subject to actual compute and the competition's model rules.
- [ ] Save run ID, commit SHA, configuration hash, model ID, task split, seed (if applicable), environment details, and allowed logs for every run.

## Gate 5 — Research write-up

- [ ] Update `PAPER_DRAFT.md` only with measured results and correct denominators.
- [ ] Explain methodology, baseline, ablations, task split, metrics, environment, limitations, failure taxonomy, and reproducibility artifacts.
- [ ] Include negative results and failures; remove unsupported claims.
- [ ] Check novelty and citations; confirm the write-up is original and unpublished as required by the paper track.
- [ ] Respect the live paper-track word limit (currently listed as 3,000 words) and submit a saved **and submitted** Kaggle Writeup, not merely a draft.
- [ ] Deadline listed on the official pages: Paper Track — November 12, 2026 at 11:59 PM UTC. Recheck the live competition page before relying on this date.

## Gate 6 — Main competition submission (if desired)

- [ ] Join the main competition and accept its rules before the entry deadline.
- [ ] Upload/run the official-harness-validated `submission.zip`.
- [ ] Confirm the platform accepts the submission and record its submission/version ID and status.
- [ ] Main-track timeline currently lists entry deadline November 25, 2026 and final submission deadline December 2, 2026, both 11:59 PM UTC; verify live dates before acting.
- [ ] A public leaderboard score is not a substitute for controlled local evidence, and no rank or win is guaranteed.

## Gate 7 — PR and merge policy

- [ ] All relevant required checks completed successfully on the exact latest PR head SHA.
- [ ] Official-harness compilation and smoke evaluation passed.
- [ ] Controlled results, artifacts, and write-up are reviewed and reproducible.
- [ ] Diff and dependency/security review completed; no credentials or prohibited files in the archive.
- [ ] Only after all gates pass, request/perform merge authorization consistent with repository protections. Current user instruction does **not** authorize merging while any gate remains unverified.

## Evidence bundle to publish

- CI run URL(s) with actual step logs
- Commit SHA and reviewed diff
- ZIP checksum, ZIP listing, and official compiler/smoke logs
- Machine-readable per-task results and aggregate metrics
- Experiment config and environment manifest
- Failure analysis and reproducibility instructions
- Final paper/write-up URL and Kaggle submission/version ID, if submitted

## Blockers requiring account/runtime access

This GitHub connection cannot repair account-level hosted-runner entitlement/settings, authenticate to the user's Kaggle account, accept competition rules, launch a Kaggle notebook on the user's behalf, or submit a Kaggle Writeup/competition entry. Those actions must occur through an authorized account session or a tool that explicitly exposes those capabilities. No credentials should be shared in chat.
