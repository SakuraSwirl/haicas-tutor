"""Badge rules."""

BADGES = {
    "Beginner 🌱": ("Complete Vision Anchor.", {"Vision Anchor"}),
    "Governance 🛡️": ("Complete Challenge and Scaffolding.", {"Challenge", "Scaffolding"}),
    "Mastery 👑": ("Complete Artifact and Archive.", {"Artifact", "Archive"}),
}


def earned_badges(completed_lessons: set[str]) -> list[tuple[str, str]]:
    return [(name, description) for name, (description, required) in BADGES.items() if required.issubset(completed_lessons)]
