"""Osho-inspired cognitive routines, operationalized as auditable AI scaffolding.

Concepts are design inspirations, not scientific laws: witnessing separates
observation from interpretation; non-attachment keeps beliefs revisable; inquiry
surfaces assumptions; paradox tolerance preserves context; pausing scales
commitment to evidence and decision cost.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Iterable, Literal

EvidenceKind = Literal["observation", "interpretation", "claim", "unknown"]

@dataclass(frozen=True)
class Evidence:
    text: str
    kind: EvidenceKind
    source: str = "unspecified"
    context: str = "default"
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Evidence text cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.kind not in ("observation", "interpretation", "claim", "unknown"):
            raise ValueError(f"Unsupported evidence kind: {self.kind}")

@dataclass(frozen=True)
class Hypothesis:
    text: str
    prediction: str
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.text.strip() or not self.prediction.strip():
            raise ValueError("Hypothesis and prediction must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

def _unique_text(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        normalized = " ".join(item.casefold().split())
        if normalized and normalized not in seen:
            seen.add(normalized)
            output.append(item)
    return output

def audit(evidence: list[Evidence], hypotheses: list[Hypothesis] | None = None,
          decision_cost: Literal["low", "medium", "high"] = "medium") -> dict:
    """Return an auditable reasoning scaffold from structured evidence.

    Does not parse arbitrary prose or prove truth. Conflict detection is limited
    to explicit YES:/NOT: markers and matching contexts.
    """
    hypotheses = hypotheses or []
    observations = [e.text for e in evidence if e.kind == "observation"]
    interpretations = [e.text for e in evidence if e.kind == "interpretation"]
    claims = [e for e in evidence if e.kind == "claim"]
    unknowns = [e.text for e in evidence if e.kind == "unknown"]
    conflicts = []
    for i, left in enumerate(claims):
        for right in claims[i + 1:]:
            if left.context.casefold().strip() != right.context.casefold().strip():
                continue
            a, b = left.text.strip(), right.text.strip()
            for neg, pos in (("NOT:", "YES:"), ("YES:", "NOT:")):
                if a.upper().startswith(neg) and b.upper().startswith(pos):
                    if a[len(neg):].strip().casefold() == b[len(pos):].strip().casefold():
                        conflicts.append({"left": a, "right": b, "context": left.context})
                elif a.upper().startswith(pos) and b.upper().startswith(neg):
                    if a[len(pos):].strip().casefold() == b[len(neg):].strip().casefold():
                        conflicts.append({"left": a, "right": b, "context": left.context})

    mean_confidence = sum(e.confidence for e in evidence) / len(evidence) if evidence else 0.0
    uncertainty = round(1.0 - mean_confidence, 3)
    if not evidence:
        label = "insufficient_evidence"
    elif mean_confidence >= 0.8 and not unknowns and not conflicts:
        label = "provisionally_high"
    elif mean_confidence >= 0.5:
        label = "moderate_or_mixed"
    else:
        label = "low"

    questions = []
    if not observations:
        questions.append("What directly observable evidence supports the current interpretation?")
    if interpretations:
        questions.append("Which part is directly observed, and which part is an interpretation?")
    if not hypotheses:
        questions.append("What are at least two plausible explanations for the observations?")
    if unknowns or not evidence:
        questions.append("What missing information would most change the conclusion?")
    if conflicts:
        questions.append("What independent measurement could distinguish the conflicting claims?")
    if mean_confidence < 0.8:
        questions.append("What evidence would falsify the leading hypothesis?")
    if hypotheses:
        questions.append("Which prediction differs most between the competing hypotheses?")

    if conflicts:
        next_step = "Predefine an independent measurement and decision threshold to resolve the conflict."
    elif decision_cost == "high":
        next_step = "For this high-cost decision, seek independent evidence and human review before acting."
    else:
        next_step = "Use a reversible, low-cost test before committing."

    return {
        "skill": "osho_inspired_witness_inquiry", "version": "0.1.0",
        "inspiration_map": {
            "witnessing": "separate observations from interpretations",
            "non_attachment": "keep beliefs revisable; seek falsifying evidence",
            "inquiry": "surface assumptions and ask discriminating questions",
            "paradox_tolerance": "compare context before declaring contradiction",
            "pause": "scale commitment to evidence and decision cost",
        },
        "observations": _unique_text(observations),
        "interpretations": _unique_text(interpretations),
        "claims": [asdict(e) for e in claims],
        "unknowns": _unique_text(unknowns), "contradictions": conflicts,
        "hypotheses": [asdict(h) for h in hypotheses],
        "questions": _unique_text(questions),
        "mean_input_confidence": round(mean_confidence, 3),
        "uncertainty_score": uncertainty, "confidence_label": label,
        "recommended_next_step": next_step,
        "limitations": [
            "Philosophical inspiration is not evidence of a scientific law.",
            "The engine only processes structured inputs; it does not parse free text.",
            "Confidence values are supplied by the caller and are not calibrated probabilities.",
            "Contradiction detection uses a narrow explicit-marker rule and will miss many natural-language conflicts.",
            "Not a clinical, diagnostic, or spiritual-state assessment.",
        ],
    }
