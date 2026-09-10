"""Responsible AI glossary used by the learner-facing app."""

TERMS = [
    {"term": "Responsible AI", "definition": "Using AI with clear boundaries, human judgment, and accountability.", "example": "A person reviews a customer escalation before action is taken.", "reflection": "Where should a human stay in the loop?"},
    {"term": "Bias", "definition": "A systematic pattern that can produce unfair or distorted outcomes.", "example": "A hiring workflow consistently ranks one group lower because its examples are unbalanced.", "reflection": "Which groups or perspectives could be missing?"},
    {"term": "Hallucination", "definition": "An AI output that sounds confident but is unsupported or incorrect.", "example": "A model invents a citation that does not exist.", "reflection": "What evidence would you check?"},
    {"term": "Privacy", "definition": "Protecting personal or sensitive information from unnecessary exposure.", "example": "Remove customer identifiers before sending notes to an AI tool.", "reflection": "What data does this task truly require?"},
    {"term": "Lineage", "definition": "A record of where information came from and how it changed.", "example": "Link a recommendation to the policy and dataset used.", "reflection": "Could someone else retrace this decision?"},
]
