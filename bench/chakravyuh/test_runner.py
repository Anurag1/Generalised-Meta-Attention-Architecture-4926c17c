import runner


def test_four_policies_are_present():
    assert set(runner.POLICIES) == {"direct_llm", "rag", "multi_agent", "chakravyuh"}


def test_chakravyuh_policy_covers_all_seed_types():
    types = {task["type"] for task in runner.load_tasks()}
    assert types <= runner.POLICIES["chakravyuh"].keys()
    assert all(runner.POLICIES["chakravyuh"][task_type] for task_type in types)


def test_smoke_result_is_deterministic_and_ranked():
    first = runner.run()
    second = runner.run()
    assert first == second
    scores = {row["policy"]: row["success_rate"] for row in first["results"]}
    assert scores["direct_llm"] < scores["rag"] < scores["multi_agent"] < scores["chakravyuh"]
