"""Small handcrafted software smoke benchmark; not a general AI evaluation."""
from __future__ import annotations
import json
from skill import Evidence, Hypothesis, audit

def run() -> dict:
    cases = [
        ("separate_observation", [Evidence("Pressure is 4 bar", "observation")], [], "observations"),
        ("separate_interpretation", [Evidence("Pump is failing", "interpretation")], [], "interpretations"),
        ("unknown_evidence", [Evidence("No log available", "unknown", confidence=.1)], [], "unknowns"),
        ("matched_conflict", [Evidence("YES: door locked", "claim", context="A"), Evidence("NOT: door locked", "claim", context="A")], [], "contradictions"),
        ("different_context", [Evidence("YES: door locked", "claim", context="A"), Evidence("NOT: door locked", "claim", context="B")], [], "contradictions"),
        ("falsification_question", [Evidence("One noisy reading", "observation", confidence=.4)], [], "questions"),
        ("competing_hypotheses", [Evidence("Machine stopped", "observation")], [Hypothesis("Power loss", "Voltage is absent"), Hypothesis("Mechanical jam", "Voltage remains present")], "questions"),
        ("high_cost_pause", [Evidence("Unverified alert", "claim", confidence=.2)], [], "recommended_next_step"),
    ]
    results = []
    for name, evidence, hypotheses, field in cases:
        out = audit(evidence, hypotheses, "high" if name == "high_cost_pause" else "medium")
        ok = bool(out[field])
        if name == "different_context":
            ok = not bool(out["contradictions"])
        elif name == "matched_conflict":
            ok = len(out["contradictions"]) == 1
        elif name == "high_cost_pause":
            ok = "human review" in out["recommended_next_step"]
        results.append({"case": name, "passed": ok, "field_checked": field})
    passed = sum(r["passed"] for r in results)
    return {"benchmark": "osho-inspired-cognitive-skill-smoke-v0.1",
            "scope_warning": "Handcrafted software smoke cases only; not evidence of superiority over LLMs.",
            "total_cases": len(results), "passed": passed, "accuracy": passed / len(results),
            "cases": results}

if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] == report["total_cases"] else 1)
