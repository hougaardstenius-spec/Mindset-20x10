import streamlit as st
from dataclasses import dataclass
from typing import List, Dict
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


# ── Data model ──────────────────────────────────────────────────────────────
@dataclass
class AnalysisResult:
    mental_score_index: float
    pressure_score: float
    biggest_leak: str
    next_focus: str
    feedback: str
    insights: List[str]
    strengths: List[str]
    profile: Dict[str, int]


# ── Analysis engine ─────────────────────────────────────────────────────────
def analyze_match(
    focus: int,
    margin: int,
    reset: int,
    intensity: int,
    pressure: int,
    too_aggressive: bool,
    note: str,
) -> AnalysisResult:
    mental_score_index = round((focus + margin + reset + intensity) / 4, 1)
    decision_quality = 4 if too_aggressive else 8
    pressure_score = round((pressure + reset + decision_quality) / 3, 1)

    leak_candidates = {
        "Attention loss": focus,
        "Too risky in neutral rallies": margin,
        "Slow recovery after errors": reset,
        "Low competitive intensity": intensity,
        "Poor pressure handling": pressure,
    }
    biggest_leak = (
        "Overaggression"
        if too_aggressive
        else min(leak_candidates, key=leak_candidates.get)
    )

    insights: List[str] = []
    strengths: List[str] = []

    if too_aggressive:
        insights.append("You force too much when the point is not ready.")
    if focus <= 6:
        insights.append("Your attention drifts too easily during parts of the match.")
    if reset <= 6:
        insights.append("Your recovery after mistakes is costing you momentum.")
    if pressure <= 6:
        insights.append("Your level drops in key moments or when closing.")
    if intensity <= 6:
        insights.append("You are not fully switched on throughout the match.")
    if margin <= 6:
        insights.append("Your safety margin is too low in neutral rallies.")

    if focus >= 7:
        strengths.append("Good attentional control")
    if margin >= 7:
        strengths.append("Strong margin discipline")
    if reset >= 7:
        strengths.append("Fast reset after errors")
    if intensity >= 7:
        strengths.append("Competitive intensity is solid")
    if pressure >= 7:
        strengths.append("You handle pressure well")

    if too_aggressive or margin <= 4:
        next_focus = "Play crosscourt with margin"
        feedback = "You are forcing too much. Build the point longer before you accelerate."
    elif reset <= 4:
        next_focus = "Reset faster after errors"
        feedback = "Your recovery speed is costing you points. Use the same reset cue after every miss."
    elif focus <= 4:
        next_focus = "Anchor attention to the next ball"
        feedback = "Your attention is drifting. Use one external anchor: split step, ball contact, or target."
    elif pressure <= 4:
        next_focus = "Slow down when closing"
        feedback = "You lose quality under pressure. Play control first, finish only when the ball is clearly there."
    elif intensity <= 4:
        next_focus = "Bring more energy into easy matches"
        feedback = "Your arousal drops when the match feels too comfortable. Use body language and faster feet to stay switched on."
    else:
        next_focus = "Keep your current structure"
        feedback = "Solid profile. Stay disciplined and avoid changing a winning process."

    if not insights:
        insights.append(
            "No major leak detected. Keep reinforcing your current structure."
        )

    profile = {
        "Focus": focus,
        "Margin": margin,
        "Reset": reset,
        "Intensity": intensity,
        "Pressure": pressure,
    }

    if note.strip():
        feedback += f"\n\nMatch note: {note.strip()}"

    return AnalysisResult(
        mental_score_index=mental_score_index,
        pressure_score=pressure_score,
        biggest_leak=biggest_leak,
        next_focus=next_focus,
        feedback=feedback,
        insights=insights[:3],
        strengths=strengths[:3],
        profile=profile,
    )


# ── Session state ───────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None

# ── Hero ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>🎾 Mindset <span class="accent">20x10</span></h1>
        <p>Mental performance tracking for padel</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Navigation tabs ─────────────────────────────────────────────────────────
tab_match, tab_drills = st.tabs(["📋 Log match", "🎯 Pressure Training"])

# ── Tab 1: Log match ───────────────────────────────────────────────────────
with tab_match:
    with st.container(border=True):
        st.markdown("##### 📋 Log match")
        st.caption("Rate the match quickly. The goal is clarity, not perfection.")

        st.markdown("")
        col_l, col_r = st.columns(2)
        with col_l:
            focus = st.slider("🎯 Focus", 1, 10, 5)
            reset = st.slider("🔄 Reset", 1, 10, 5)
            pressure = st.slider("💎 Pressure handling", 1, 10, 5)
        with col_r:
            margin = st.slider("📏 Margin", 1, 10, 5)
            intensity = st.slider("🔥 Intensity", 1, 10, 5)
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
                too_aggressive=too_aggressive,
                note=note,
            )

    # ── Results ─────────────────────────────────────────────────────────────
    result = st.session_state.result
    if result:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("##### 📊 Match result")

        # Score cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="label">Mental Score Index</div>
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
                <div class="card-body">{result.feedback.replace(chr(10), '<br>')}</div>
            </div>
            """,
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
    st.caption("Train specific match situations. Check off drills as you complete them.")

    st.markdown("")

    # Closing situations
    with st.container(border=True):
        st.markdown("**🔴 Closing situations**")
        c1 = st.checkbox("Close match (5-3)")
        c2 = st.checkbox("Match point (no errors first 3 shots)")
        c3 = st.checkbox("Serve for match (safe play only)")
        c4 = st.checkbox("Close game at 40-30")

    # High pressure points
    with st.container(border=True):
        st.markdown("**🟡 High pressure points**")
        p1 = st.checkbox("Deuce (40-40)")
        p2 = st.checkbox("Break point against you")
        p3 = st.checkbox("Break point for you")
        p4 = st.checkbox("Tie-break simulation")

    # Error control
    with st.container(border=True):
        st.markdown("**🟢 Error control**")
        e1 = st.checkbox("Reset immediately after error")
        e2 = st.checkbox("Stop error streak (3 in a row)")
        e3 = st.checkbox("No frustration game")
        e4 = st.checkbox("Same routine every point")

    # Discipline / focus
    with st.container(border=True):
        st.markdown("**🔵 Discipline / focus**")
        d1 = st.checkbox("10 shots without error")
        d2 = st.checkbox("Crosscourt only")
        d3 = st.checkbox("No winners for one game")
        d4 = st.checkbox("Long rally discipline")

    completed = sum([c1, c2, c3, c4, p1, p2, p3, p4, e1, e2, e3, e4, d1, d2, d3, d4])

    st.markdown("")
    st.markdown(
        f"""
        <div class="score-card">
            <div class="label">Drills completed</div>
            <div class="value">{completed}/16</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")

    if completed >= 10:
        st.success("🔥 High level mental session!")
    elif completed >= 5:
        st.info("💪 Solid training session")
