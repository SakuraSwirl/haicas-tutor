"""Streamlit interface for HAICAS Tutor."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from .archive_manager import get_user_archive
from .ai_integration import generate_adaptive_quiz, generate_lesson_response
from .badge_system import earned_badges
from .certificate_generator import issue_certificate
from .database import (
    create_user,
    get_badges,
    get_certificate,
    get_artifacts,
    get_passed_lessons,
    init_db,
    save_artifact,
    save_badge,
    save_questionnaire,
    save_quiz_result,
)
from .glossary import TERMS
from .questionnaire import FEARS, SKILL_LEVELS, TRUST_OPTIONS, recommended_start


st.set_page_config(page_title="HAICAS Tutor", page_icon="🌱", layout="wide")


def apply_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --navy: #0A1A2F;
            --navy-deep: #071326;
            --silver: #C0C0C0;
            --white: #FFFFFF;
            --gold: #FFD700;
            --gold-dark: #FFB800;
            --gray: #D9D9D9;
            --red: #B22222;
            --green: #228B22;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background: var(--navy) !important;
            color: var(--white) !important;
        }
        [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
            background: var(--navy-deep) !important;
            border-right: 1px solid var(--silver) !important;
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
            color: var(--gold) !important;
        }
        .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] {
            color: var(--white) !important;
        }
        .hero { padding: 2.5rem 0 1.5rem; border-bottom: 1px solid var(--silver); }
        .muted, small, .stCaption { color: var(--gray) !important; }
        .badge { border: 1px solid var(--silver); padding: .45rem .75rem; display: inline-block; margin: .2rem; }
        hr { border-color: var(--silver) !important; }
        div[data-testid="stForm"] {
            border: 1px solid var(--silver) !important;
            background: rgba(7, 19, 38, .72) !important;
        }
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div,
        textarea, input {
            background: var(--navy-deep) !important;
            color: var(--white) !important;
            border-color: var(--silver) !important;
        }
        div[data-baseweb="select"] span, div[data-baseweb="select"] input,
        textarea, input { color: var(--white) !important; }
        div[data-baseweb="select"] svg { fill: var(--gold) !important; }
        div[data-testid="stRadio"] label p { color: var(--white) !important; }
        div[data-testid="stRadio"] [data-checked="true"] { background: var(--gold) !important; }
        .stButton > button, .stFormSubmitButton > button,
        button[kind="primary"], button[kind="secondary"] {
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            color: var(--navy-deep) !important;
            border: 1px solid var(--silver) !important;
            font-weight: 700 !important;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover,
        button[kind="primary"]:hover, button[kind="secondary"]:hover {
            background: var(--gold) !important;
            color: var(--navy-deep) !important;
            border-color: var(--white) !important;
        }
        div[data-testid="stAlert"] {
            border: 1px solid var(--silver) !important;
            color: var(--white) !important;
        }
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] { color: var(--white) !important; }
        div[data-testid="stAlert"]:has(svg[ data-testid="stIconSuccess"]) { background: rgba(34, 139, 34, .28); }
        div[data-testid="stAlert"]:has(svg[ data-testid="stIconError"]) { background: rgba(178, 34, 34, .30); }
        div[data-testid="stAlert"]:has(svg[ data-testid="stIconInfo"]) { background: rgba(192, 192, 192, .14); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_user() -> int | None:
    return int(st.session_state.user_id) if "user_id" in st.session_state else None


def request_navigation(page: str) -> None:
    """Apply navigation on the next rerun, before the radio widget is created."""
    st.session_state.pending_navigation = page
    st.rerun()


def render_footer() -> None:
    st.markdown(
        """
        <div style="text-align: center; color: #C0C0C0; padding: 2rem 0 1rem; margin-top: 3rem; border-top: 1px solid #C0C0C0;">
            © 2026 HAICAS Tutor · Beginner Demo · MIT License
        </div>
        """,
        unsafe_allow_html=True,
    )


def home() -> None:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    logo_path = Path(__file__).resolve().parent.parent / "static" / "haicastutorlogo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=250)
    st.title("HAICAS Tutor")
    st.subheader("Learn to co-assistant with AI responsibly")
    st.markdown("</div>", unsafe_allow_html=True)

    st.header("What we offer")
    st.write("HAICAS Tutor is an AI learning app that teaches anyone wanting to learn how to co-assistant with AI responsibly. It’s not about memorizing prompts or chasing speed hacks — it’s about building skills that make AI adoption trustworthy and repeatable.")

    st.header("Why we offer it")
    st.write("AI adoption often fails because outputs drift, contradictions creep in, and accountability is missing. HAICAS Tutor solves this by turning governance into a set of practical learning steps anyone can follow.")

    st.header("Benefits")
    for benefit in [
        "Clarity: Define exactly what AI should and shouldn’t do.",
        "Confidence: Test contradictions and learn how to handle them.",
        "Structure: Organize results with lineage + trust notes.",
        "Practicality: Create reusable checklists and frameworks for real work.",
        "Proof: Archive outputs with accountability, earning certificates that demonstrate literacy, governance, or mastery.",
    ]:
        st.write(f"- {benefit}")

    st.markdown("---")
    if st.button("Sign Up to Start Lessons"):
        request_navigation("Questionnaire")

    st.header("Learning Path")
    st.write("Beginner Lessons — The HAICAS Ritual")
    st.write("🌱 Vision Anchor → 🌱 Challenge → 🌱 Scaffolding → 🌱 Artifact → 🌱 Archive")

    st.markdown("---")
    st.subheader("Earn Your Certificate")
    st.write("Complete lessons and quizzes to earn your HAICAS Literacy Certificate.")
    st.write("Badges: 🌱 Beginner, 🛡️ Governance (coming soon), 👑 Mastery (coming soon)")
    if st.button("Preview Certificate"):
        request_navigation("Certificate")


def questionnaire_page() -> None:
    st.header("Pre-course questionnaire")
    st.write("Your answers personalize the path. They are used for your learning experience and can be aggregated without identifying you.")
    with st.form("questionnaire"):
        fear = st.selectbox("What concerns you most about using AI?", list(FEARS))
        skill = st.selectbox("How much experience do you have?", SKILL_LEVELS)
        trust = st.selectbox("How much do you currently trust AI outputs?", TRUST_OPTIONS)
        submitted = st.form_submit_button("Save and continue")
    if submitted:
        user_id = ensure_user()
        if user_id is None:
            st.warning("Create your learner profile in the sidebar first.")
        else:
            save_questionnaire(user_id, fear, skill, trust)
            st.session_state.recommended_lesson = recommended_start(fear)
            request_navigation("Lessons")


def introduction_section() -> None:
    st.header("🌱 Introduction to AI and HAICAS")

    st.subheader("What is AI?")
    st.write(
        """
        AI is software that learns patterns from data and then generates outputs - text, images, or decisions.
        It doesn't "think" like humans. It predicts what comes next based on training.
        Example: If trained on millions of sentences, it can guess the next word in your sentence.
        """
    )
    st.write("Analogy: AI is like a super-fast librarian who has read every book and can summarize instantly.")
    st.write("How it works: Input -> Pattern recognition -> Output")
    st.write("Types of AI: Narrow AI (what exists today) vs General AI (hypothetical)")
    st.write("Examples you already know: autocorrect, spam filters, Netflix recommendations, face unlock")
    st.write("Limits: AI can't think, feel, or know truth - it only predicts.")
    st.write("Safety tips: Don't share sensitive info, double-check facts, treat AI like a smart intern.")
    st.write("Beginner myths: 'AI is too complicated' (false), 'AI replaces people' (false - it replaces tasks).")

    st.subheader("Things You Can Do With AI 🌱")
    st.write("- Education: personalized study help, automatic lesson summaries, practice questions")
    st.write("- Business: automated customer support, faster paperwork, decision support with data, Create reports and outlines")
    st.write("- Creativity: new art styles, story generation, music/video ideas")
    st.write("- Retail: personalized recommendations, smarter product search, logistics optimization")
    
    st.subheader("Why Governance Matters")
    st.write(
        """
        Without rules, AI can produce contradictions or misleading results.
        Governance means setting boundaries, checking lineage (sources), and adding trust notes.
        HAICAS rituals teach you how to do this step by step.
        """
    )

    st.subheader("Core Principle: Intent before Instructions 🌱")
    st.write("Start with *why* and *what* before *how*.")
    st.write("- Intent: What outcome do you want? (deliverable, decision, draft, checklist)")
    st.write("- Audience: Who is this for? (client, internal, technical, non-technical)")
    st.write("- Scope: What's in vs out? (must-include, must-exclude)")
    st.write("- Constraints: Time, format, tone, length, tools, data sources")
    st.write("- Non-negotiables: Rules the AI must not violate (no fluff, no repetition, no restating conclusions)")

    st.subheader("The Human Layer AI Misses 🌱")
    st.write("- Context of use: 'This will be used in...' (proposal, onboarding call, SOP)")
    st.write("- Decision posture: 'I need a quick verdict vs exploration'")
    st.write("- Cognitive load: 'I'm mid-flow vs refining'")
    st.write("- Emotional temperature: 'Keep tone calm, confident, warm'")

    st.subheader("Takeaway for Beginners")
    st.write(
        """
        AI optimizes for completeness. You need to optimize for usefulness in your moment.
        That's why HAICAS starts with rituals: Vision -> Challenge -> Scaffolding -> Artifact -> Archive.
        By the end, you'll walk away with literacy, confidence, and a certificate 🌱.
        """
    )


def lesson_page(user_id: int) -> None:
    st.header("Beginner lessons")
    lessons = [
        (
            "Vision Anchor",
            "This step is about setting intent before instructions. You define the governance challenge you want AI to help with.",
            "Think of it as drawing the boundary: what AI should do, and what humans must decide.",
            "**Scaffold:** Outcome → Audience → Scope → Constraints → Non-negotiables",
            "**Example:** AI supports customer service, but humans define escalation rules.",
            "**Quick Exercise:** Ask AI: 'Explain fairness in customer service like I'm 12.' Notice how AI adjusts complexity.",
            "**Reflection:** Boundaries - where AI helps, where humans stay in control.",
            "Your Vision Anchor",
            "vision_anchor",
        ),
        (
            "Challenge",
            "Here you pressure-test your vision. AI often blends concepts that feel similar. By probing contradictions, you see where governance is needed.",
            "**Example:** Check if rage, anger, fear, and anxiety are different.",
            "**Quick Exercise:** Ask AI: 'Compare anger vs fear.' Then ask: 'Are rage and anxiety the same?'",
            "**Reflection:** Notice contradictions and how AI responds. This shows why governance matters.",
            "",
            "",
            "Your Challenge Prompt",
            "challenge_log",
        ),
        (
            "Scaffolding",
            "Scaffolding means structuring outputs with lineage and trust notes. Instead of raw text, you ask AI to organize information with sources and validation.",
            "**Example:** Source: WHO report. Trust: verified by two experts.",
            "**Quick Exercise:** Paste messy notes and ask AI: 'Turn these notes into a clean bullet list with sources.'",
            "**Reflection:** Would someone else trust this output if they saw your notes?",
            "",
            "",
            "Your Scaffolding Notes",
            "scaffolding",
        ),
        (
            "Artifact",
            "Artifacts are reusable outputs - frameworks, checklists, or rituals. They turn scaffolding into something portable.",
            "**Example:** Customer escalation checklist with clear steps.",
            "**Quick Exercise:** Ask AI: 'Create a checklist for customer escalation with clear steps.'",
            "**Reflection:** How does this artifact help others repeat the process?",
            "",
            "",
            "Your Artifact",
            "governance_artifact",
        ),
        (
            "Archive",
            "Archiving means saving your artifact with tags, lineage, and accountability notes. This makes it auditable later.",
            "**Example:** Tag: Customer Service, Accountability: Reviewed by manager.",
            "**Quick Exercise:** Ask AI: 'Tag this checklist as Customer Service and add accountability: reviewed by manager.'",
            "**Reflection:** Imagine someone auditing your work - what proof would they need?",
            "",
            "",
            "Your Archive Notes",
            "archive_record",
        ),
    ]
    completed = get_passed_lessons(user_id)
    lesson_step = st.session_state.setdefault("lesson_step", 0)
    if lesson_step == 0:
        introduction_section()
        st.divider()
        if st.button("Continue to Lesson 1", key="continue-introduction"):
            st.session_state.lesson_step = 1
            st.rerun()
        return

    if lesson_step <= len(lessons):
        index = lesson_step - 1
        title, description, example, exercise, reflection, scaffold, extra, label, artifact_type = lessons[index]
        st.subheader(f"🌱 Lesson {lesson_step}: {title}")
        st.write(description)
        for detail in (scaffold, example, exercise, reflection, extra):
            if detail:
                st.markdown(detail)
        with st.form(f"lesson-{artifact_type}"):
            content = st.text_area(f"✍️ {label}", key=f"input-{artifact_type}")
            generate_response = st.form_submit_button("Ask HAICAS AI")
            save_response = st.form_submit_button("Save lesson response")
            continue_label = "Continue to Beginner Quiz" if lesson_step == len(lessons) else f"Continue to Lesson {lesson_step + 1}"
            continue_lesson = st.form_submit_button(continue_label)
        if generate_response:
            if not content.strip():
                st.error("Write an input before asking HAICAS AI.")
            else:
                st.session_state[f"ai-output-{artifact_type}"] = generate_lesson_response(title, content)
        if save_response or continue_lesson:
            if not content.strip():
                st.error("Write a response before continuing.")
            else:
                ai_output = st.session_state.get(f"ai-output-{artifact_type}", "")
                save_artifact(user_id, artifact_type, content, {"lesson": title, "ai_output": ai_output})
                if save_response:
                    st.success(f"{title} response saved.")
                if continue_lesson:
                    st.session_state.lesson_step += 1
                    st.rerun()
        ai_output = st.session_state.get(f"ai-output-{artifact_type}")
        if ai_output:
            st.subheader("HAICAS AI response")
            st.write(ai_output)
        st.caption(f"Lesson {lesson_step} of {len(lessons)}")
        return

    st.header("🌱 Beginner Quiz")
    st.write("Generate a quiz from your own workshop inputs, then answer all five questions.")
    if st.button("Generate adaptive quiz", key="generate-adaptive-quiz"):
        artifacts = get_artifacts(user_id)
        context = "\n\n".join(f"{row['artifact_type']}: {row['content']}" for row in artifacts)
        st.session_state.adaptive_quiz = generate_adaptive_quiz(context)
        st.rerun()

    questions = st.session_state.get("adaptive_quiz", [])
    if not questions:
        st.info("Save your lesson responses, then generate your adaptive quiz.")
        return

    answers = []
    for index, question in enumerate(questions, start=1):
        st.subheader(f"{index}. Workshop reflection")
        answers.append(st.radio(question["question"], question["options"], key=f"adaptive-quiz-{index}"))

    if st.button("Submit Quiz", key="submit-adaptive-quiz"):
        score = sum(answer == question["answer"] for answer, question in zip(answers, questions))
        quiz_passed = score == 5
        save_quiz_result(user_id, "Beginner Quiz", score, len(questions), quiz_passed)
        if quiz_passed:
            for title, *_ in lessons:
                save_quiz_result(user_id, title, 1, 1, True)
                completed.add(title)
            for badge_name, description in earned_badges(completed):
                save_badge(user_id, badge_name, description)
            st.success("Congratulations! You've completed the Beginner Workshop and earned your 🌱 Literacy Certificate.")
        else:
            st.warning("Keep practicing the rituals - review your answers and try again.")
        st.write(f"✅ You scored {score}/5")

    st.caption(f"Progress: {len(completed)}/{len(lessons)} lessons completed")


def glossary_page() -> None:
    st.header("Glossary and explainers")
    for item in TERMS:
        with st.expander(item["term"]):
            st.write(item["definition"])
            st.caption(f"Example: {item['example']}")
            st.write(f"Reflection: {item['reflection']}")


def archive_page(user_id: int) -> None:
    st.header("Your archive")
    records = get_user_archive(user_id)
    if not records:
        st.info("Your saved artifacts will appear here.")
        return
    for record in records:
        metadata = json.loads(record["metadata"])
        with st.expander(f"{record['artifact_type']} · {record['created_at']}"):
            st.write(record["content"])
            st.caption(f"Lineage: {metadata.get('lineage', 'Not recorded')}")
            st.caption(f"Trust note: {metadata.get('trust_notes', 'Not recorded')}")


def certificate_page(user_id: int) -> None:
    st.header("Certificate")
    completed = get_passed_lessons(user_id)
    certificate_id = issue_certificate(user_id, completed)
    if certificate_id is None:
        st.warning("Complete all five lessons and pass the Beginner Quiz to earn your HAICAS Literacy Certificate.")
        return
    certificate = get_certificate(user_id)
    st.success("Certificate ready")
    st.title("Certificate of HAICAS Literacy")
    st.write(f"This certifies that **{st.session_state.user_name}** completed the beginner program.")
    st.write(f"Certificate ID: `{certificate_id}`")
    st.write(f"Issued: {certificate['issued_at']}")
    st.write("Badges earned:")
    for badge in get_badges(user_id):
        st.write(f"{badge['name']} · {badge['description']}")


def main() -> None:
    init_db()
    apply_style()
    pending_navigation = st.session_state.pop("pending_navigation", None)
    if pending_navigation:
        st.session_state.navigation = pending_navigation
    with st.sidebar:
        st.title("HAICAS Tutor")
        if ensure_user() is None:
            with st.form("profile"):
                name = st.text_input("Your name")
                email = st.text_input("Email (optional)")
                create = st.form_submit_button("Create learner profile")
            if create and name.strip():
                st.session_state.user_id = create_user(name, email)
                st.session_state.user_name = name.strip()
                st.rerun()
            elif create:
                st.error("Enter a name to continue.")
        else:
            st.caption(f"Learner: {st.session_state.user_name}")
        page = st.radio(
            "Navigate",
            ["Home", "Questionnaire", "Lessons", "Glossary", "Archive", "Certificate"],
            key="navigation",
        )
    user_id = ensure_user()
    if page == "Home":
        home()
    elif page == "Questionnaire":
        questionnaire_page()
    elif page == "Lessons":
        lesson_page(user_id) if user_id else st.info("Create a learner profile to begin.")
    elif page == "Glossary":
        glossary_page()
    elif page == "Archive":
        archive_page(user_id) if user_id else st.info("Create a learner profile to view your archive.")
    elif page == "Certificate":
        certificate_page(user_id) if user_id else st.info("Create a learner profile to view your certificate.")
    render_footer()