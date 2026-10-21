---
name: graph-retrieval
description: Find likely relevant Python files using issue-term overlap and import-graph neighbors. Use early when the fix location is unclear, then verify candidates against source and tests.
---

# Graph-guided repository retrieval

Call the skill script with the issue description as a single argument string:

`run_skill_script(skill_name="graph-retrieval", file_path="scripts/retrieve.py", args=["<issue description>"])`

The script scans Python files in `/workspace`, extracts local import edges, ranks files by issue-term overlap, and adds a small bonus for directly connected files that have no direct term matches.

Interpretation:
- Treat the ranking as candidate generation, not a correctness proof.
- Read the highest-ranked files and associated tests before editing.
- If the result is empty, use repository search tools and inspect the project layout.
- Do not assume the import graph is complete: dynamic imports, namespace packages, and non-Python dependencies may be missed.
