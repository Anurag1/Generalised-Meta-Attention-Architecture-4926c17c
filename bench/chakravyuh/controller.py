"""Minimal reference controller for CHAKRAVYUH-Bench.

This is deliberately model-agnostic: an LLM/tool layer supplies candidate
beliefs and actions while this controller maintains explicit problem state.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CandidateAction:
    name: str
    information_gain: float
    cost: float
    trap_risk: float
    exit_progress: float

    def score(self, lam: float = 1.0, mu: float = 1.0, nu: float = 1.0) -> float:
        return (
            self.information_gain
            - lam * self.cost
            - mu * self.trap_risk
            + nu * self.exit_progress
        )


@dataclass
class ChakravyuhState:
    layer: int = 0
    beliefs: Dict[str, float] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    verified: bool = False


class ChakravyuhController:
    """Stateful controller for adaptive problem-space navigation."""

    def __init__(self, state: ChakravyuhState | None = None) -> None:
        self.state = state or ChakravyuhState()

    def register_observation(self, observation: str) -> None:
        self.state.evidence.append(observation)
        self.state.history.append(f"observation:{observation}")

    def register_contradiction(self, contradiction: str) -> None:
        self.state.contradictions.append(contradiction)
        self.state.history.append(f"contradiction:{contradiction}")

    def choose_action(self, actions: List[CandidateAction]) -> CandidateAction:
        if not actions:
            raise ValueError("At least one candidate action is required")
        selected = max(actions, key=lambda action: action.score())
        self.state.history.append(f"action:{selected.name}")
        return selected

    def advance_layer(self) -> int:
        self.state.layer += 1
        self.state.history.append(f"layer:{self.state.layer}")
        return self.state.layer

    def mark_verified(self) -> None:
        self.state.verified = True
        self.state.history.append("verified")

    def can_exit(self) -> bool:
        return self.state.verified and not self.state.contradictions
