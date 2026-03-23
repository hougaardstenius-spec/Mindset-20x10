import streamlit as st
from dataclasses import dataclass
from typing import List, Dict
from statistics import mean
from datetime import date
import pandas as pd
import altair as alt

st.set_page_config(page_title="Mindset 20x10", page_icon="🎾", layout="centered")

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global ─────────────────────────────────────────── */
    .block-container { max-width: 720px; padding-top: 2rem; }

    /* ── Hero header ───────────────────────────────────── */
    .hero {
        text-align: center;
        padding: 2rem 0 0.5rem 0;
    }
    .hero h1 {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.15rem;
    }
    .hero .accent { color: #00E676; }
    .hero p {
        color: #888;
        font-size: 0.95rem;
        margin-top: 0;
    }

    /* ── Score cards ────────────────────────────────────── */
    .score-card {
        background: linear-gradient(135deg, #1A1F2B 0%, #232A3A 100%);
        border: 1px solid #2A3040;
        border-radius: 14px;
        padding: 1.4rem 1.2rem;
        text-align: center;
    }
    .score-card .label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #888;
        margin-bottom: 0.3rem;
    }
    .score-card .value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #00E676;
    }

    /* ── Info cards ─────────────────────────────────────── */
    .info-card {
        background: #1A1F2B;
        border-left: 4px solid #00E676;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .info-card.leak { border-left-color: #FF5252; }
    .info-card.strength { border-left-color: #00E676; }
    .info-card .card-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #888;
        margin-bottom: 0.25rem;
    }
    .info-card .card-body {
        font-size: 1rem;
        color: #FAFAFA;
    }

    /* ── Insight / strength pills ───────────────────────── */
    .pill-red {
        display: inline-block;
        background: rgba(255,82,82,0.12);
        color: #FF8A80;
        border: 1px solid rgba(255,82,82,0.25);
        border-radius: 20px;
        padding: 0.35rem 0.9rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        font-size: 0.85rem;
    }
    .pill-green {
        display: inline-block;
        background: rgba(0,230,118,0.10);
        color: #69F0AE;
        border: 1px solid rgba(0,230,118,0.2);
        border-radius: 20px;
        padding: 0.35rem 0.9rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        font-size: 0.85rem;
    }

    /* ── Drill pill ────────────────────────────────────── */
    .pill-blue {
        display: inline-block;
        background: rgba(66,165,245,0.10);
        color: #90CAF9;
        border: 1px solid rgba(66,165,245,0.2);
        border-radius: 20px;
        padding: 0.35rem 0.9rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        font-size: 0.85rem;
    }

    /* ── Slider labels ─────────────────────────────────── */
    .stSlider label { font-weight: 600; letter-spacing: 0.3px; }

    /* ── Divider ───────────────────────────────────────── */
    .section-divider {
        border: none;
        border-top: 1px solid #2A3040;
        margin: 2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Pressure drill data ────────────────────────────────────────────────────
PRESSURE_DRILLS = {
    "Closing": [
        "Close match from 5-3",
        "Close game from 40-30",
        "Match point, no free errors",
        "Serve for match",
    ],
    "High Pressure Points": [
        "Deuce battle",
        "Break point for you",
        "Break point against you",
        "Tie-break simulation",
    ],
    "Error Control": [
        "Reset after error within 1 point",
        "Break 3-error spiral",
        "Same cue after every mistake",
        "No frustration game",
    ],
    "Discipline / Boredom": [
        "10 shots without error",
        "Crosscourt only for one game",
        "No winners for one game",
        "Long rally discipline",
    ],
    "Attention Control": [
        "Split-step anchor drill",
        "Contact-point focus drill",
        "One external cue for full game",
        "Refocus after distraction",
    ],
    "Arousal Regulation": [
        "Raise energy before easy match",
        "Calm down before closing",
        "Breath reset before serve",
        "Body-language reset drill",
    ],
    "Identity": [
        "No free points challenge",
        "Play one full game to identity",
        "Identity cue before key points",
        "Return to standard after momentum shift",
    ],
    "Recovery Speed": [
        "Next-ball response drill",
        "Miss and reset within 1 point",
        "Fast reset after partner error",
        "Recover after lost deuce",
    ],
}

DRILL_MAP = {
    "Recovery speed": PRESSURE_DRILLS["Recovery Speed"][:3],
    "Attention control": PRESSURE_DRILLS["Attention Control"][:3],
    "Pressure handling": PRESSURE_DRILLS["High Pressure Points"][:3],
    "Identity alignment": PRESSURE_DRILLS["Identity"][:3],
    "Arousal regulation": PRESSURE_DRILLS["Arousal Regulation"][:3],
    "Margin discipline": PRESSURE_DRILLS["Discipline / Boredom"][:3],
    "Overaggression": [
        "Crosscourt only for one game",
        "No winners for one game",
        "Match point, no free errors",
    ],
    "Intensity": PRESSURE_DRILLS["Arousal Regulation"][:3],
}


# ── Data model ──────────────────────────────────────────────────────────────
@dataclass
class AnalysisResult:
    mental_score_index: float
    pressure_score: float
    identity_score: float
    biggest_leak: str
    next_focus: str
    coach_feedback: str
    insights: List[str]
    strengths: List[str]
    recommended_drills: List[str]
    profile: Dict[str, int]


# ── Analysis helpers ────────────────────────────────────────────────────────
def avg(values: List[float]) -> float:
    return round(mean(values), 2)


def get_decision_quality(too_aggressive: bool) -> int:
    return 4 if too_aggressive else 8


def detect_biggest_leak(scores: Dict[str, int], too_aggressive: bool) -> str:
    if too_aggressive and scores["margin"] <= 6:
        return "Overaggression"
    priority_order = [
        "recovery_speed",
        "attention_control",
        "pressure",
        "identity_alignment",
        "arousal_regulation",
        "margin",
        "intensity",
        "reset",
        "focus",
    ]
    label_map = {
        "recovery_speed": "Recovery speed",
        "attention_control": "Attention control",
        "pressure": "Pressure handling",
        "identity_alignment": "Identity alignment",
        "arousal_regulation": "Arousal regulation",
        "margin": "Margin discipline",
        "intensity": "Intensity",
        "reset": "Reset quality",
        "focus": "General focus",
    }
    lowest_value = min(scores[key] for key in priority_order)
    for key in priority_order:
        if scores[key] == lowest_value:
            return label_map[key]
    return "General focus"


def get_recommended_drills(biggest_leak: str) -> List[str]:
    return DRILL_MAP.get(biggest_leak, PRESSURE_DRILLS["Error Control"][:3])


def generate_feedback(
    scores: Dict[str, int], biggest_leak: str, too_aggressive: bool, note: str
) -> tuple:
    insights: List[str] = []
    strengths: List[str] = []

    if scores["attention_control"] <= 6:
        insights.append("Your attention drifts too easily during parts of the match.")
    if scores["recovery_speed"] <= 6:
        insights.append("You stay inside errors too long before resetting.")
    if scores["pressure"] <= 6:
        insights.append("Your level drops in key moments or when closing.")
    if scores["arousal_regulation"] <= 6:
        insights.append("Your energy level is not regulated well enough for the situation.")
    if scores["identity_alignment"] <= 6:
        insights.append("You moved away from your performance identity under pressure.")
    if too_aggressive:
        insights.append("You accelerate before the point is ready.")
    if scores["margin"] <= 6:
        insights.append("Your safety margin is too low in neutral rallies.")

    if scores["attention_control"] >= 7:
        strengths.append("Good attentional control")
    if scores["recovery_speed"] >= 7:
        strengths.append("Fast recovery after mistakes")
    if scores["pressure"] >= 7:
        strengths.append("You handle pressure well")
    if scores["identity_alignment"] >= 7:
        strengths.append("You stay close to your performance identity")
    if scores["margin"] >= 7:
        strengths.append("Strong margin discipline")

    if biggest_leak == "Overaggression":
        next_focus = "Play crosscourt with margin before you accelerate"
        coach_feedback = "Your main issue is not courage but timing. Build the point longer and earn the right to attack."
    elif biggest_leak == "Recovery speed":
        next_focus = "Reset within one point after every error"
        coach_feedback = "Your performance drops because recovery is too slow. Use the same reset cue every time and get back to the next ball faster."
    elif biggest_leak == "Attention control":
        next_focus = "Use one external attention anchor next match"
        coach_feedback = "Your mind is drifting. Anchor attention to split step, contact point, or target instead of trying to control thoughts."
    elif biggest_leak == "Pressure handling":
        next_focus = "Slow down and play control first in key moments"
        coach_feedback = "You lose quality when it matters. Reduce speed, increase clarity, and finish only when the ball is clearly there."
    elif biggest_leak == "Identity alignment":
        next_focus = "Return to your standard under pressure"
        coach_feedback = "You are strongest when you play like your identity. Reconnect to your standard before key points."
    elif biggest_leak == "Arousal regulation":
        next_focus = "Regulate your energy before key moments"
        coach_feedback = "You are either too flat or too rushed. Use breath, feet, and body language to get to the right activation level."
    elif biggest_leak == "Margin discipline":
        next_focus = "Add more safety margin in neutral play"
        coach_feedback = "You are giving away too much for free. Use height, direction, and patience to make the match simpler."
    elif biggest_leak == "Intensity":
        next_focus = "Bring more competitive energy into the match"
        coach_feedback = "Your body and mind are not switched on enough. Use sharper feet and stronger intent from the first point."
    else:
        next_focus = "Keep your current structure and reinforce it"
        coach_feedback = "The profile is solid. Stay disciplined and keep repeating the same high-quality process."

    if not insights:
        insights.append("No major leak detected. Keep reinforcing your current structure.")

    if note.strip():
        coach_feedback += f"\n\nMatch note: {note.strip()}"

    return next_focus, coach_feedback, insights[:3], strengths[:3]


# ── Analysis engine ─────────────────────────────────────────────────────────
def analyze_match(
    focus: int,
    margin: int,
    reset: int,
    intensity: int,
    pressure: int,
    attention_control: int,
    arousal_regulation: int,
    recovery_speed: int,
    identity_alignment: int,
    too_aggressive: bool,
    note: str,
) -> AnalysisResult:
    decision_quality = get_decision_quality(too_aggressive)
    mental_score_index = avg([
        focus, margin, reset, intensity, attention_control, recovery_speed,
    ])
    pressure_score = avg([
        pressure, recovery_speed, arousal_regulation, identity_alignment, decision_quality,
    ])
    identity_score = avg([
        identity_alignment, margin, attention_control, reset,
    ])

    scores = {
        "focus": focus,
        "margin": margin,
        "reset": reset,
        "intensity": intensity,
        "pressure": pressure,
        "attention_control": attention_control,
        "arousal_regulation": arousal_regulation,
        "recovery_speed": recovery_speed,
        "identity_alignment": identity_alignment,
    }
    biggest_leak = detect_biggest_leak(scores, too_aggressive)
    recommended_drills = get_recommended_drills(biggest_leak)
    next_focus, coach_feedback, insights, strengths = generate_feedback(
        scores=scores, biggest_leak=biggest_leak,
        too_aggressive=too_aggressive, note=note,
    )
    profile = {
        "Focus": focus,
        "Margin": margin,
        "Reset": reset,
        "Pressure": pressure,
        "Attention": attention_control,
        "Arousal": arousal_regulation,
        "Recovery": recovery_speed,
        "Identity": identity_alignment,
    }
    return AnalysisResult(
        mental_score_index=mental_score_index,
        pressure_score=pressure_score,
        identity_score=identity_score,
        biggest_leak=biggest_leak,
        next_focus=next_focus,
        coach_feedback=coach_feedback,
        insights=insights,
        strengths=strengths,
        recommended_drills=recommended_drills,
        profile=profile,
    )


# ── Session state ───────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None

# ── Hero ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero">
        <h1>🎾 Mindset <span class="accent">20x10</span></h1>
        <p>Mental performance system for padel &bull; {date.today().isoformat()}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Navigation tabs ─────────────────────────────────────────────────────────
tab_match, tab_drills, tab_history = st.tabs(
    ["📋 Log match", "🎯 Pressure Training", "📜 History"]
)

# ── Tab 1: Log match ───────────────────────────────────────────────────────
with tab_match:
    with st.container(border=True):
        st.markdown("##### 📋 Log match")
        st.caption("Fast input. Clear diagnosis. One next focus.")

        st.info("Rate based on what you did, not how you felt. Scale: 1–3 = weak · 4–6 = okay · 7–8 = strong · 9–10 = elite")

        st.markdown("")
        col_l, col_r = st.columns(2)
        with col_l:
            focus = st.slider("🎯 Focus", 1, 10, 6,
                help="How consistently you stayed present on the ball and situation. 1 = distracted · 5 = inconsistent · 10 = fully locked in every point")
            reset = st.slider("🔄 Reset", 1, 10, 6,
                help="How well you handled momentum shifts. 1 = stuck after mistakes · 5 = sometimes recover · 10 = immediate reset every time")
            pressure = st.slider("💎 Pressure handling", 1, 10, 6,
                help="How well you performed in key points. 1 = collapse under pressure · 5 = inconsistent · 10 = execute well in big moments")
            attention_control = st.slider("🧠 Attention control", 1, 10, 6,
                help="Ability to direct your attention deliberately. 1 = reactive mind · 5 = partly controlled · 10 = fully intentional focus")
            recovery_speed = st.slider("⏱️ Recovery speed", 1, 10, 6,
                help="How fast you returned to neutral after mistakes. 1 = multiple points to recover · 5 = slow recovery · 10 = reset within 1 point")
        with col_r:
            margin = st.slider("📏 Margin", 1, 10, 6,
                help="How safe and controlled your shot selection was. 1 = constant errors · 5 = mixed control · 10 = very few free errors")
            intensity = st.slider("🔥 Intensity", 1, 10, 6,
                help="Your overall competitive energy and presence. 1 = flat · 5 = okay energy · 10 = fully engaged and sharp")
            arousal_regulation = st.slider("💨 Arousal regulation", 1, 10, 6,
                help="How well you managed your energy level. 1 = too flat or too rushed · 5 = mixed · 10 = right energy for the situation")
            identity_alignment = st.slider("🪞 Identity alignment", 1, 10, 6,
                help="How well you played according to your standard. 1 = far from your standard · 5 = mixed · 10 = fully your game regardless of opponent")
            too_aggressive = st.toggle("⚡ Played too aggressive?", value=False)

        note = st.text_input(
            "📝 Optional note", placeholder="Example: Lost focus when ahead"
        )

        st.markdown("")
        if st.button("Analyze  →", use_container_width=True, type="primary"):
            st.session_state.result = analyze_match(
                focus=focus,
                margin=margin,
                reset=reset,
                intensity=intensity,
                pressure=pressure,
                attention_control=attention_control,
                arousal_regulation=arousal_regulation,
                recovery_speed=recovery_speed,
                identity_alignment=identity_alignment,
                too_aggressive=too_aggressive,
                note=note,
            )

    # ── Results ─────────────────────────────────────────────────────────────
    result = st.session_state.result
    if result:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("##### 📊 Match result")

        # Score cards — 3 columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="label">Mental Score</div>
                    <div class="value">{result.mental_score_index}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="label">Pressure Score</div>
                    <div class="value">{result.pressure_score}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="label">Identity Score</div>
                    <div class="value">{result.identity_score}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("")

        # Biggest leak & next focus
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"""
                <div class="info-card leak">
                    <div class="card-title">🚨 Biggest leak</div>
                    <div class="card-body">{result.biggest_leak}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="card-title">🎯 Next match focus</div>
                    <div class="card-body">{result.next_focus}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Coach feedback
        st.markdown(
            f"""
            <div class="info-card">
                <div class="card-title">🗣️ Coach feedback</div>
                <div class="card-body">{result.coach_feedback.replace(chr(10), '<br>')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Recommended drills
        st.markdown(
            '<div class="info-card">'
            '<div class="card-title">🏋️ Recommended drills</div>'
            '<div class="card-body">'
            + "".join(f'<span class="pill-blue">{d}</span>' for d in result.recommended_drills)
            + "</div></div>",
            unsafe_allow_html=True,
        )

        # Profile bar chart
        st.markdown("")
        st.markdown("##### 📈 Performance profile")
        chart_df = pd.DataFrame(
            {"Category": list(result.profile.keys()), "Score": list(result.profile.values())}
        )
        chart = (
            alt.Chart(chart_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color="#00E676")
            .encode(
                x=alt.X("Category:N", sort=list(result.profile.keys()), title=None),
                y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 10]), title="Score"),
            )
            .properties(height=260)
            .configure_axis(
                labelColor="#888",
                titleColor="#888",
                gridColor="#2A3040",
            )
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(chart, use_container_width=True)

        # Insights & strengths side by side
        col_ins, col_str = st.columns(2)
        with col_ins:
            st.markdown("##### ⚠️ Insights")
            if result.insights:
                pills = "".join(
                    f'<span class="pill-red">{i}</span>' for i in result.insights
                )
                st.markdown(pills, unsafe_allow_html=True)
        with col_str:
            st.markdown("##### ✅ Strengths")
            if result.strengths:
                pills = "".join(
                    f'<span class="pill-green">{s}</span>' for s in result.strengths
                )
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.caption(
                    "No clear strength signal yet. Keep logging matches."
                )

        st.markdown("")
        st.info("💡 Rule: only bring **one** focus point into the next match.")

# ── Tab 2: Pressure Training ───────────────────────────────────────────────
with tab_drills:
    st.markdown("##### 🎯 Pressure Training")
    st.caption("Check off the drills you completed today.")

    # Show recommended category if a match has been analyzed
    recommended_category = "Error Control"
    result_for_drills = st.session_state.get("result")
    if result_for_drills:
        recommended_category = {
            "Recovery speed": "Recovery Speed",
            "Attention control": "Attention Control",
            "Pressure handling": "High Pressure Points",
            "Identity alignment": "Identity",
            "Arousal regulation": "Arousal Regulation",
            "Margin discipline": "Discipline / Boredom",
            "Overaggression": "Discipline / Boredom",
            "Intensity": "Arousal Regulation",
        }.get(result_for_drills.biggest_leak, "Error Control")

    st.markdown(
        f"""
        <div class="info-card">
            <div class="card-title">📌 Recommended category today</div>
            <div class="card-body">{recommended_category}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")
    completed_drills: List[str] = []
    for category, drills in PRESSURE_DRILLS.items():
        with st.expander(category, expanded=(category == recommended_category)):
            for drill in drills:
                key = f"drill_{category}_{drill}"
                if st.checkbox(drill, key=key):
                    completed_drills.append(f"{category}: {drill}")

    completed_count = len(completed_drills)

    st.markdown("")
    st.markdown(
        f"""
        <div class="score-card">
            <div class="label">Drills completed</div>
            <div class="value">{completed_count}/{sum(len(d) for d in PRESSURE_DRILLS.values())}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")

    if completed_count >= 10:
        st.success("🔥 High level mental session!")
    elif completed_count >= 5:
        st.info("💪 Solid training session")
    elif completed_count > 0:
        st.caption("Good start. Consistency matters more than volume.")

    if completed_drills:
        with st.container(border=True):
            st.markdown("**Completed drills**")
            for drill in completed_drills:
                st.write(f"- {drill}")

# ── Tab 3: History ──────────────────────────────────────────────────────────
with tab_history:
    st.markdown("##### 📜 History")
    st.caption("History and storage come in the next build.")

    with st.container(border=True):
        st.markdown("**Coming soon:**")
        st.write("- Last 5 matches")
        st.write("- Average scores")
        st.write("- Most frequent leaks")
        st.write("- Drills completed this week")
