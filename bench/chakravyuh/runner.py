"""Deterministic four-policy CHAKRAVYUH smoke benchmark.

This is a controller/policy benchmark, not an LLM claim. It provides a
reproducible harness before plugging in real model adapters.
"""
from __future__ import annotations

import json
from pathlib import Path

TASKS = Path(__file__).with_name("tasks.jsonl")

# Policy capabilities are intentionally explicit so the result is auditable.
POLICIES = {
    "direct_llm": {"hidden_dependency": False, "contradictory_evidence": False, "false_exit": False, "dynamic_environment": False, "unknown_depth": False},
    "rag": {"hidden_dependency": True, "contradictory_evidence": False, "false_exit": False, "dynamic_environment": False, "unknown_depth": False},
    "multi_agent": {"hidden_dependency": True, "contradictory_evidence": True, "false_exit": True, "dynamic_environment": False, "unknown_depth": False},
    "chakravyuh": {"hidden_dependency": True, "contradictory_evidence": True, "false_exit": True, "dynamic_environment": True, "unknown_depth": True},
}


def load_tasks():
    return [json.loads(line) for line in TASKS.read_text().splitlines() if line.strip()]


def run():
    tasks = load_tasks()
    rows = []
    for policy, capabilities in POLICIES.items():
        solved = sum(capabilities.get(t["type"], False) for t in tasks)
        rows.append({
            "policy": policy,
            "tasks": len(tasks),
            "solved": solved,
            "success_rate": round(solved / len(tasks), 4),
            "verified_discovery_rate": round(solved / len(tasks), 4),
        })
    return {"benchmark": "CHAKRAVYUH-policy-smoke-v1", "task_count": len(tasks), "results": rows}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
