"""Offline issue-to-file retrieval for the competition repository sandbox."""
import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("/workspace")
STOP = {"about", "after", "again", "also", "been", "before", "being", "between", "could", "does", "from", "have", "into", "issue", "just", "more", "most", "other", "should", "that", "their", "there", "these", "they", "this", "those", "the", "through", "under", "using", "when", "where", "which", "while", "with", "would"}

def tokens(text):
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9_]{1,}", text) if len(w) > 2 and w.lower() not in STOP}

def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print(json.dumps({"error": "pass the issue description as an argument", "results": []}))
        return 2
    if not ROOT.is_dir():
        print(json.dumps({"error": "/workspace is not available in this skill runtime", "results": []}))
        return 0
    excluded = {".git", ".venv", "venv", "__pycache__", "site-packages", "node_modules"}
    files = []
    module_paths = {}
    for path in sorted(ROOT.rglob("*.py")):
        if any(part in excluded for part in path.parts):
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = path.relative_to(ROOT).as_posix()
        module = rel[:-3].replace("/", ".")
        if module.endswith(".__init__"):
            module = module[:-9]
        module_paths[module] = rel
        files.append((rel, source, tokens(rel.replace("/", " ") + " " + source)))
    adjacency = defaultdict(set)
    for rel, source, _ in files:
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
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    parent = current.split(".")[:-node.level + 1]
                    base = ".".join(parent + ([base] if base else []))
                if base:
                    names.append(base)
                    names.extend(f"{base}.{alias.name}" for alias in node.names)
            for name in names:
                parts = name.split(".")
                candidates = [name] + [".".join(parts[:i]) for i in range(len(parts) - 1, 0, -1)]
                target = next((module_paths[c] for c in candidates if c in module_paths), None)
                if target and target != rel:
                    adjacency[rel].add(target)
                    adjacency[target].add(rel)
    q = tokens(query)
    if not q:
        print(json.dumps({"query": query, "results": []}))
        return 0
    lexical = {rel: len(terms & q) for rel, _, terms in files}
    seeds = {rel for rel, score in lexical.items() if score}
    neighbors = {n for rel in seeds for n in adjacency.get(rel, set())}
    rows = []
    term_map = {rel: terms for rel, _, terms in files}
    for rel, score in lexical.items():
        bonus = 1 if score == 0 and rel in neighbors else 0
        if score or bonus:
            rows.append({"path": rel, "score": score + bonus, "lexical_score": score,
                         "graph_bonus": bonus, "matched_terms": sorted(term_map[rel] & q)})
    rows.sort(key=lambda row: (-row["score"], -row["lexical_score"], row["path"]))
    print(json.dumps({"query": query, "results": rows[:10]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
