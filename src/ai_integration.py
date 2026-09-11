"""Optional Hugging Face integration for HAICAS Tutor."""

from __future__ import annotations

import json
import os
import re
from urllib.error import URLError
from urllib.request import Request, urlopen
from functools import lru_cache
from typing import Any

AI_PROVIDER = os.getenv("HAICAS_AI_PROVIDER", "ollama").lower()
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
HF_MODEL_NAME = os.getenv("HAICAS_MODEL", "distilgpt2")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


@lru_cache(maxsize=1)
def _get_generator() -> Any:
    """Load the configured model only when the first AI request is made."""
    from transformers import pipeline

    return pipeline(
        "text-generation",
        model=HF_MODEL_NAME,
        device_map="auto",
    )


def haicas_ai(prompt: str) -> str:
    """Generate a response with the configured Ollama or Hugging Face provider."""
    if AI_PROVIDER == "ollama":
        return _ollama_generate(prompt)
    return _hugging_face_generate(prompt)


def _ollama_generate(prompt: str) -> str:
    request = Request(
        OLLAMA_URL,
        data=json.dumps({"model": MODEL_NAME, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode())
        return _clean_response(str(payload.get("response", "")))
    except (OSError, URLError, json.JSONDecodeError) as error:
        return f"AI model is not available yet. Start Ollama and run {MODEL_NAME}. Details: {error}"


def _hugging_face_generate(prompt: str) -> str:
    """Optional compatibility path for environments that explicitly choose it."""
    try:
        generator = _get_generator()
        response = generator(
            prompt,
            max_new_tokens=220,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            repetition_penalty=1.15,
            no_repeat_ngram_size=4,
            return_full_text=False,
        )
        return _clean_response(str(response[0]["generated_text"]))
    except Exception as error:
        return (
            "AI model is not available yet. Install the optional Hugging Face dependencies "
            f"and retry. Details: {error}"
        )


def _clean_response(text: str) -> str:
    """Remove continuation artifacts produced by small text-generation models."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"^(?:[,.;:!?]|and\b|or\b)\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def _is_usable_response(text: str) -> bool:
    words = text.split()
    if (
        len(words) < 8
        or text[:1] in ",.;:!?"
        or text.startswith("AI model is not available yet.")
    ):
        return False
    normalized = " ".join(words).lower()
    return not any(normalized.count(" ".join(words[index:index + 5]).lower()) >= 4 for index in range(max(1, len(words) - 4)))


def generate_lesson_response(title: str, content: str) -> str:
    """Generate a lesson response and reject low-quality continuation output."""
    prompts = {
        "Vision Anchor": """You are a helpful AI governance tutor. Return a concise, complete response.
Use exactly these headings: Outcome, Audience, Scope, Constraints, Non-negotiables.
Do not repeat phrases. Do not begin mid-sentence.
Governance challenge: """,
        "Challenge": """You are a helpful AI governance tutor. Compare the concepts in the user's prompt.
Return a concise response with headings: Comparison, Contradiction or uncertainty, Governance need.
Do not repeat phrases. Do not begin mid-sentence.
User prompt: """,
        "Scaffolding": """You are a helpful AI governance tutor. Organize the user's notes into concise bullet points.
Include headings: Organized notes, Lineage, Trust note. Never invent a source.
Do not repeat phrases. Do not begin mid-sentence.
Messy notes: """,
        "Artifact": """You are a helpful AI governance tutor. Create a concise reusable checklist or workflow.
Use numbered steps and include a short human review step.
Do not repeat phrases. Do not begin mid-sentence.
Request: """,
        "Archive": """You are a helpful AI governance tutor. Return concise archive metadata.
Use headings: Tags, Accountability, Audit evidence.
Do not repeat phrases. Do not begin mid-sentence.
Artifact: """,
    }
    response = haicas_ai(prompts[title] + content[:3000])
    if _is_usable_response(response):
        return response
    return fallback_lesson_response(title, content)


def fallback_lesson_response(title: str, content: str) -> str:
    """Provide a structured response when a small model produces poor text."""
    subject = content.strip().rstrip(".") or "the learner's governance challenge"
    responses = {
        "Vision Anchor": f"Outcome: Clarify a useful result for {subject}.\nAudience: The people who will use or review the result.\nScope: Define what AI may support and what remains out of scope.\nConstraints: Set format, timing, sources, and tone.\nNon-negotiables: Keep humans responsible for final decisions and verify important claims.",
        "Challenge": f"Comparison: Break {subject} into distinct concepts and compare their definitions, causes, and effects.\nContradiction or uncertainty: Ask where the concepts overlap and where the evidence is incomplete.\nGovernance need: Record the boundary and require human review before acting on the result.",
        "Scaffolding": f"Organized notes:\n- Topic: {subject}\n- Key claim: Extract the main point and separate facts from assumptions.\nLineage: Record the source for each important claim; do not invent sources.\nTrust note: Verify consequential claims with an independent source or reviewer.",
        "Artifact": f"1. Define the goal for {subject}.\n2. List the inputs and decision points.\n3. Assign AI-supported steps and human approval steps.\n4. Test the checklist with an example.\n5. Review and revise it before reuse.",
        "Archive": f"Tags: Add the topic, workflow, and risk level for {subject}.\nAccountability: Record the owner and reviewer.\nAudit evidence: Keep the source notes, generated artifact, review date, and approval decision.",
    }
    return responses[title]


def _extract_json(text: str) -> list[dict[str, Any]]:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        value = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


def generate_adaptive_quiz(context: str, count: int = 5) -> list[dict[str, Any]]:
    """Generate quiz items about the learner's own workshop inputs."""
    prompt = f"""
Create {count} multiple-choice questions about this learner's HAICAS workshop work:
{context[:4000]}

Return only valid JSON in this shape:
[{{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}}]
Each answer must exactly match one option. Test intent, contradiction testing, lineage,
reusable artifacts, and auditability where relevant.
"""
    generated = _extract_json(haicas_ai(prompt))
    valid = [
        item
        for item in generated
        if isinstance(item, dict)
        and isinstance(item.get("question"), str)
        and isinstance(item.get("options"), list)
        and len(item["options"]) >= 2
        and item.get("answer") in item["options"]
    ]
    if len(valid) < count:
        valid.extend(fallback_quiz(context, count - len(valid)))
    return valid[:count]


def fallback_quiz(context: str, count: int = 5) -> list[dict[str, Any]]:
    """Keep the demo usable when a model is not installed or downloaded."""
    topic = next((word for word in context.split() if word.isalpha()), "your project")
    questions = [
        (f"What should come first when planning {topic} with AI?", "Intent", ["Intent", "Formatting", "Speed", "Tone"]),
        ("Why should the learner probe contradictions?", "Governance boundaries", ["Governance boundaries", "To confuse AI", "For decoration", "To avoid sources"]),
        ("What supports trust in an AI output?", "Lineage and trust notes", ["Lineage and trust notes", "Length", "Confidence alone", "A polished tone"]),
        ("What makes a workshop artifact useful?", "Reusable steps", ["Reusable steps", "Random ideas", "Hidden assumptions", "Unverified claims"]),
        ("Why add tags and accountability notes?", "Auditability", ["Auditability", "Shorter text", "More decoration", "Less context"]),
    ]
    return [
        {"question": question, "answer": answer, "options": options}
        for question, answer, options in questions[:count]
    ]
