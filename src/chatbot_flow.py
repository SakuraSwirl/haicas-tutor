"""Lesson content and quizzes for the beginner HAICAS ritual."""

LESSONS = [
    {"key": "Intro", "title": "Orientation", "badge": "Beginner 🌱", "prompt": "Define Human-AI co-assistance in your own words.", "artifact_type": "intro_definition", "questions": [("What is HAICAS about?", ["Human-AI Co-Assistance Skills", "AI speed hacks", "Compliance theater", "Coding only"], 0), ("What is the Intro deliverable?", ["A one-sentence definition", "A certificate ID", "A contradiction log", "A badge"], 0)]},
    {"key": "Vision Anchor", "title": "Vision Anchor", "badge": "Beginner 🌱", "prompt": "Write what AI should do and what it should not do.", "artifact_type": "vision_anchor", "questions": [("What is the Vision Anchor deliverable?", ["A sovereignty statement", "A trust note", "A contradiction log", "An archive record"], 0), ("What should it include?", ["What AI should and should not do", "Only AI answers", "A certificate ID", "A governance checklist"], 0)]},
    {"key": "Challenge", "title": "Challenge", "badge": "Governance 🛡️", "prompt": "Probe your idea and record contradictions or uncertainty.", "artifact_type": "challenge_log", "questions": [("What is the Challenge deliverable?", ["A challenge log", "A certificate", "A checklist", "A sovereignty statement"], 0), ("What should it include?", ["Contradictions and AI responses", "Only successful probes", "Nothing", "A certificate ID"], 0)]},
    {"key": "Scaffolding", "title": "Scaffolding", "badge": "Governance 🛡️", "prompt": "Organize your result and document lineage and trust notes.", "artifact_type": "scaffolding", "questions": [("What is the Scaffolding deliverable?", ["An outline with lineage and trust notes", "A badge", "A certificate", "A sovereignty statement"], 0), ("Why add lineage and trust notes?", ["To show sources and confidence", "To make it longer", "To archive automatically", "To unlock badges"], 0)]},
    {"key": "Artifact", "title": "Artifact", "badge": "Mastery 👑", "prompt": "Turn your learning into a reusable checklist or framework.", "artifact_type": "governance_artifact", "questions": [("What is the Artifact deliverable?", ["A reusable checklist or framework", "A contradiction log", "A certificate ID", "A sovereignty statement"], 0), ("Why create an artifact?", ["So you can reuse it in your work", "To archive automatically", "To unlock badges", "To test contradictions"], 0)]},
    {"key": "Archive", "title": "Archive", "badge": "Mastery 👑", "prompt": "Save your artifact with tags and accountability notes.", "artifact_type": "archive_record", "questions": [("What is the Archive deliverable?", ["A saved record with tags and accountability", "A sovereignty statement", "A contradiction log", "A certificate ID"], 0), ("Why archive your artifact?", ["To prove it later", "To unlock badges", "To test contradictions", "To issue certificates"], 0)]},
]


def get_lesson(key: str) -> dict:
    return next(lesson for lesson in LESSONS if lesson["key"] == key)


def passed(score: int, total: int) -> bool:
    return score >= total - 1
