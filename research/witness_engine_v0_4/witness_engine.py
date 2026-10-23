"""Experimental structured-claim contradiction detector.

This module is intentionally small and auditable. It does not claim awareness,
scientific discovery, or general reasoning superiority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Claim:
    subject: str
    predicate: str
    object: str
    source_id: str
    confidence: float = 1.0
    polarity: bool = True
    context: str = "default"

    def __post_init__(self) -> None:
        for field in ("subject", "predicate", "object", "source_id", "context"):
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")


def claims_conflict(a: Claim, b: Claim) -> bool:
    """True for explicit conflicts under a narrow categorical-claim schema."""
    key_a = (a.subject.casefold().strip(), a.predicate.casefold().strip(),
             a.context.casefold().strip())
    key_b = (b.subject.casefold().strip(), b.predicate.casefold().strip(),
             b.context.casefold().strip())
    if key_a != key_b:
        return False
    opposite_polarity = a.polarity != b.polarity
    incompatible_values = a.object.casefold().strip() != b.object.casefold().strip()
    return opposite_polarity or incompatible_values


def witness_predict(claims: list[Claim]) -> bool:
    return any(
        claims_conflict(a, b)
        for index, a in enumerate(claims)
        for b in claims[index + 1:]
    )


def baseline_predict(claims: list[Claim]) -> bool:
    """Naive comparison baseline: detects object/polarity conflict, ignores context."""
    return any(
        (
            a.subject.casefold().strip(), a.predicate.casefold().strip()
        ) == (
            b.subject.casefold().strip(), b.predicate.casefold().strip()
        )
        and (a.polarity != b.polarity or a.object.casefold().strip() != b.object.casefold().strip())
        for index, a in enumerate(claims)
        for b in claims[index + 1:]
    )


def make_frozen_cases() -> list[dict[str, Any]]:
    """Generate the versioned 40-case synthetic smoke set deterministically."""
    subjects = [
        ("material", "conductivity", "high", "low"),
        ("reactor", "temperature-regime", "stable", "unstable"),
        ("model", "passes-validation", "yes", "no"),
        ("sensor", "status", "active", "inactive"),
        ("network", "connected", "true", "false"),
        ("algorithm", "converges", "yes", "no"),
        ("compound", "toxicity-level", "low", "high"),
        ("controller", "safe-state", "enabled", "disabled"),
        ("dataset", "balanced", "yes", "no"),
        ("device", "calibrated", "yes", "no"),
    ]
    cases: list[dict[str, Any]] = []
    for group, (subject, predicate, value_a, value_b) in enumerate(subjects, start=1):
        variants = [
            ("positive_same_context_different_values", value_a, value_b, "ctx-common", True, True),
            ("negative_same_claim", value_a, value_a, "ctx-common", True, False),
            ("negative_different_context", value_a, value_b, "ctx-A", True, False),
            ("positive_opposite_polarity", value_a, value_a, "ctx-common", False, True),
        ]
        for local_index, (pattern, obj_a, obj_b, context_a, polarity_b, gold) in enumerate(variants, start=1):
            context_b = context_a if pattern != "negative_different_context" else "ctx-B"
            claims = [
                asdict(Claim(subject, predicate, obj_a, f"G{group}A", 0.9, True, context_a)),
                asdict(Claim(subject, predicate, obj_b, f"G{group}B", 0.8, polarity_b, context_b)),
            ]
            case_num = len(cases) + 1
            cases.append({
                "id": f"syn-{case_num:03d}",
                "group": group,
                "pattern": pattern,
                "claims": claims,
                "gold_contradiction": gold,
            })
    if len(cases) != 40 or sum(case["gold_contradiction"] for case in cases) != 20:
        raise AssertionError("Frozen synthetic set generation changed unexpectedly.")
    return cases
