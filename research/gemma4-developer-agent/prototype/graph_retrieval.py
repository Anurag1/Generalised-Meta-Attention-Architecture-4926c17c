"""Deterministic graph-guided retrieval prototype; not a complete Kaggle agent."""
from __future__ import annotations
import ast
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

STOP_WORDS = {"about", "after", "again", "also", "been", "before", "being", "between", "could", "does", "from", "have", "into", "issue", "just", "more", "most", "other", "should", "that", "their", "there", "these", "they", "this", "those", "the", "through", "under", "using", "when", "where", "which", "while", "with", "would"}

def tokens(text: str) -> set[str]:
    words = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9_]{1,}", text)}
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}

@dataclass(frozen=True)
class RetrievalResult:
    path: str
    lexical_score: int
    graph_bonus: int
    matched_terms: tuple[str, ...]
    @property
    def score(self) -> int:
        return self.lexical_score + self.graph_bonus

class PythonRepositoryGraph:
    """Index Python files/import edges and rank files against an issue description."""
    def __init__(self, root: str | Path, *, max_file_bytes: int = 1_000_000):
        self.root = Path(root).resolve()
        self.max_file_bytes = max_file_bytes
        self.contents: dict[str, str] = {}
        self.file_terms: dict[str, set[str]] = {}
        self.adjacency: dict[str, set[str]] = defaultdict(set)
        self._index()

    def _index(self) -> None:
        excluded = {".git", ".venv", "venv", "__pycache__", "site-packages"}
        paths = sorted(p for p in self.root.rglob("*.py") if not any(x in excluded for x in p.parts))
        module_to_path: dict[str, str] = {}
        for path in paths:
            try:
                if path.stat().st_size > self.max_file_bytes:
                    continue
                rel = path.relative_to(self.root).as_posix()
                source = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            self.contents[rel] = source
            self.file_terms[rel] = tokens(rel.replace("/", " ") + " " + source)
            module = rel[:-3].replace("/", ".")
            if module.endswith(".__init__"):
                module = module[:-9]
            module_to_path[module] = rel
        for rel, source in self.contents.items():
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            current = rel[:-3].replace("/", ".")
            if current.endswith(".__init__"):
                current = current[:-9]
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names.extend(a.name for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    base = node.module or ""
                    if node.level:
                        parent = current.split(".")[:-node.level + 1]
                        base = ".".join(parent + ([base] if base else []))
                    if base:
                        names.append(base)
                        names.extend(f"{base}.{a.name}" for a in node.names)
                for name in names:
                    candidates = [name]
                    parts = name.split(".")
                    candidates.extend(".".join(parts[:i]) for i in range(len(parts) - 1, 0, -1))
                    target = next((module_to_path[c] for c in candidates if c in module_to_path), None)
                    if target and target != rel:
                        self.adjacency[rel].add(target)
                        self.adjacency[target].add(rel)

    def retrieve(self, issue: str, *, top_k: int = 8, graph_hops: int = 1) -> list[RetrievalResult]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        if graph_hops < 0:
            raise ValueError("graph_hops must be >= 0")
        terms = tokens(issue)
        if not terms:
            return []
        lexical = {p: len(v & terms) for p, v in self.file_terms.items()}
        distance = {p: 0 for p, score in lexical.items() if score > 0}
        frontier = set(distance)
        for depth in range(1, graph_hops + 1):
            following = {n for p in frontier for n in self.adjacency.get(p, set()) if n not in distance}
            distance.update({n: depth for n in following})
            frontier = following
            if not frontier:
                break
        results = []
        for path, score in lexical.items():
            dist = distance.get(path)
            bonus = 1 if dist is not None and 0 < dist <= graph_hops and score == 0 else 0
            matched = tuple(sorted(self.file_terms[path] & terms))
            if score or bonus:
                results.append(RetrievalResult(path, score, bonus, matched))
        return sorted(results, key=lambda r: (-r.score, -r.lexical_score, r.path))[:top_k]

    def explain(self, issue: str, *, top_k: int = 8, graph_hops: int = 1) -> list[dict[str, object]]:
        return [{"path": r.path, "score": r.score, "lexical_score": r.lexical_score, "graph_bonus": r.graph_bonus, "matched_terms": list(r.matched_terms)} for r in self.retrieve(issue, top_k=top_k, graph_hops=graph_hops)]
