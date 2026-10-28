"""A small, reproducible engine for proposing and testing numeric relationships.

Research prototype, not a general scientific-discovery system. Searches pairwise
linear hypotheses in tabular data and evaluates them on held-out observations
against a constant-prediction baseline.
"""
from __future__ import annotations

import csv
import json
import math
import random
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Discovery:
    input_variable: str
    output_variable: str
    hypothesis: str
    slope: float
    intercept: float
    train_mae: float
    test_mae: float
    baseline_test_mae: float
    improvement_fraction: float
    verified: bool
    n_train: int
    n_test: int
    caveat: str


def mae(actual: list[float], predicted: list[float]) -> float:
    return sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)


def fit_line(xs: list[float], ys: list[float]) -> tuple[float, float]:
    xbar, ybar = statistics.mean(xs), statistics.mean(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    if denom == 0:
        raise ValueError("Input column has no variation; slope is undefined")
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom
    return slope, ybar - slope * xbar


def read_csv(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 8:
        raise ValueError("Need at least 8 rows for a meaningful train/test split")
    if not rows or not rows[0]:
        raise ValueError("CSV must have a header and at least one column")
    data: dict[str, list[float]] = {}
    for key in rows[0]:
        try:
            vals = [float(row[key]) for row in rows]
        except (TypeError, ValueError):
            continue
        if all(math.isfinite(v) for v in vals):
            data[key] = vals
    if len(data) < 2:
        raise ValueError("Need at least two fully numeric columns")
    return data


def discover(data: dict[str, list[float]], seed: int = 7, test_fraction: float = 0.25,
             min_improvement: float = 0.20) -> list[Discovery]:
    columns = list(data)
    n = len(data[columns[0]])
    if any(len(data[c]) != n for c in columns):
        raise ValueError("All columns must have the same row count")
    if n < 8:
        raise ValueError("Need at least 8 rows")
    indices = list(range(n))
    random.Random(seed).shuffle(indices)
    n_test = max(2, min(n - 4, round(n * test_fraction)))
    test_idx, train_idx = indices[:n_test], indices[n_test:]
    results: list[Discovery] = []

    for xname in columns:
        for yname in columns:
            if xname == yname:
                continue
            xs, ys = data[xname], data[yname]
            xtr, ytr = [xs[i] for i in train_idx], [ys[i] for i in train_idx]
            xte, yte = [xs[i] for i in test_idx], [ys[i] for i in test_idx]
            if len(set(xtr)) < 2:
                continue
            slope, intercept = fit_line(xtr, ytr)
            train_pred = [slope * x + intercept for x in xtr]
            test_pred = [slope * x + intercept for x in xte]
            train_error, test_error = mae(ytr, train_pred), mae(yte, test_pred)
            baseline = mae(yte, [statistics.mean(ytr)] * len(yte))
            improvement = 0.0 if baseline == 0 else (baseline - test_error) / baseline
            verified = (
                improvement >= min_improvement
                and test_error <= max(1e-9, 0.25 * statistics.pstdev(yte))
            )
            results.append(Discovery(
                input_variable=xname, output_variable=yname,
                hypothesis=f"{yname} ≈ {slope:.6g} × {xname} + {intercept:.6g}",
                slope=slope, intercept=intercept, train_mae=train_error,
                test_mae=test_error, baseline_test_mae=baseline,
                improvement_fraction=improvement, verified=verified,
                n_train=len(train_idx), n_test=len(test_idx),
                caveat="Predictive association only; this test does not establish causation."
            ))
    return sorted(results, key=lambda d: (d.verified, d.improvement_fraction, -d.test_mae), reverse=True)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python discovery_engine.py DATA.csv [REPORT.json]")
        return 2
    path = Path(sys.argv[1])
    report_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("discovery_report.json")
    results = discover(read_csv(path))
    report = {
        "engine": "Universal Discovery Engine prototype",
        "method": "pairwise linear hypothesis search + held-out test + constant baseline",
        "data_file": path.name,
        "candidate_count": len(results),
        "verified_count": sum(r.verified for r in results),
        "discoveries": [asdict(r) for r in results[:10]],
        "limitations": [
            "Only pairwise linear relationships are searched.",
            "A synthetic benchmark validates the pipeline, not scientific novelty.",
            "Predictive association is not causal proof.",
            "No external LLM is called; results are deterministic and reproducible."
        ]
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "report": str(report_path), "candidate_count": len(results),
        "verified_count": report["verified_count"],
        "top_candidates": [asdict(r) for r in results[:3]]
    }, indent=2))
    return 0 if results and report["verified_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
