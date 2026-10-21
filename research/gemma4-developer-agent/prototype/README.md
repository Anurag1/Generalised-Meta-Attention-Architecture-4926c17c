# Graph-guided repository retrieval prototype

This folder contains an experimental retrieval component for the Gemma 4 Developer Agent Paper Track. It is not a complete Kaggle submission and is not integrated with the official harness.

The prototype indexes Python files, extracts import edges, and ranks candidate files using lexical overlap plus a small graph-neighbor bonus. It does not invoke Gemma, edit files, or run repository tests.

Run tests from this directory with: `python -m unittest discover -s tests -v`

The next research step is to compare graph_hops=0 and graph_hops=1 on a fixed held-out issue set, recording localization Recall@k, verified resolution rate, tool calls, and elapsed time. Do not claim benchmark gains until measured.