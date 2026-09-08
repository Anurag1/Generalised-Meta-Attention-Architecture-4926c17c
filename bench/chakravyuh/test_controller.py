from controller import CandidateAction, ChakravyuhController


def test_action_selection_prefers_information_and_exit_progress():
    controller = ChakravyuhController()
    actions = [
        CandidateAction("low_value", 0.2, 0.1, 0.1, 0.0),
        CandidateAction("high_value", 0.9, 0.2, 0.05, 0.4),
    ]
    assert controller.choose_action(actions).name == "high_value"


def test_cannot_exit_before_verification():
    controller = ChakravyuhController()
    assert controller.can_exit() is False
    controller.mark_verified()
    assert controller.can_exit() is True


def test_contradiction_blocks_exit():
    controller = ChakravyuhController()
    controller.mark_verified()
    controller.register_contradiction("claim conflicts with evidence")
    assert controller.can_exit() is False
