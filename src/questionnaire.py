"""Questionnaire options and adaptive learning guidance."""

FEARS = {
    "Job loss": "Start with human oversight and clear boundaries.",
    "Bias": "Start with Challenge and Trust Notes so assumptions become visible.",
    "Hallucinations": "Start with Challenge and contradiction testing.",
    "Privacy": "Start with Vision Anchor and define what AI must not handle.",
}
SKILL_LEVELS = ["No experience", "Beginner", "Intermediate", "Advanced"]
TRUST_OPTIONS = ["Yes", "Sometimes", "No"]


def recommended_start(fear_barrier: str) -> str:
    if fear_barrier in {"Bias", "Hallucinations"}:
        return "Challenge"
    return "Vision Anchor"
