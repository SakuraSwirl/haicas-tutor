from src.badge_system import earned_badges
from src.chatbot_flow import passed
from src.certificate_generator import generate_certificate_id


def test_quiz_pass_threshold_allows_one_miss():
    assert passed(1, 2)
    assert not passed(0, 2)


def test_badges_require_their_lesson_groups():
    assert earned_badges({"Vision Anchor"})[0][0] == "Beginner 🌱"
    assert earned_badges({"Challenge"}) == []
    assert earned_badges({"Challenge", "Scaffolding"})[0][0] == "Governance 🛡️"


def test_certificate_ids_are_prefixed_and_unique():
    first = generate_certificate_id()
    second = generate_certificate_id()
    assert first.startswith("HAICAS-")
    assert first != second
