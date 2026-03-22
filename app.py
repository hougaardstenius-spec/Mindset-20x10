import streamlit as st
from dataclasses import dataclass
from typing import List, Dict

st.set_page_config(page_title="Mindset 20x10", page_icon="🎾", layout="centered")


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


def analyze_match(
    focus: int,
    margin: int,
    reset: int,
    intensity: int,
    pressure: int,
    too_aggressive: bool,
    note: str,
) -> AnalysisResult:
    mental_score_index = round((focus + margin + reset + intensity) / 4, 2)
    decision_quality = 2 if too_aggressive else 4
    pressure_score = round((pressure + reset + decision_quality) / 3, 2)

    leak_candidates = {
        "Attention loss": focus,
        "Too risky in neutral rallies": margin,
        "Slow recovery after errors": reset,
        "Low competitive intensity": intensity,
        "Poor pressure handling": pressure,
    }
    biggest_leak = "Overaggression" if too_aggressive else min(leak_candidates, key=leak_candidates.get)

    insights: List[str] = []
    strengths: List[str] = []

    if too_aggressive:
        insights.append("You force too much when the point is not ready.")
    if focus <= 3:
        insights.append("Your attention drifts too easily during parts of the match.")
    if reset <= 3:
        insights.append("Your recovery after mistakes is costing you momentum.")
    if pressure <= 3:
        insights.append("Your level drops in key moments or when closing.")
    if intensity <= 3:
        insights.append("You are not fully switched on throughout the match.")
    if margin <= 3:
        insights.append("Your safety margin is too low in neutral rallies.")

    if focus >= 4:
        strengths.append("Good attentional control")
    if margin >= 4:
        strengths.append("Strong margin discipline")
    if reset >= 4:
        strengths.append("Fast reset after errors")
    if intensity >= 4:
        strengths.append("Competitive intensity is solid")
    if pressure >= 4:
        strengths.append("You handle pressure well")

    if too_aggressive or margin <= 2:
        next_focus = "Play crosscourt with margin"
        feedback = "You are forcing too much. Build the point longer before you accelerate."
    elif reset <= 2:
        next_focus = "Reset faster after errors"
        feedback = "Your recovery speed is costing you points. Use the same reset cue after every miss."
    elif focus <= 2:
        next_focus = "Anchor attention to the next ball"
        feedback = "Your attention is drifting. Use one external anchor: split step, ball contact, or target."
    elif pressure <= 2:
        next_focus = "Slow down when closing"
        feedback = "You lose quality under pressure. Play control first, finish only when the ball is clearly there."
    elif intensity <= 2:
        next_focus = "Bring more energy into easy matches"
        feedback = "Your arousal drops when the match feels too comfortable. Use body language and faster feet to stay switched on."
    else:
        next_focus = "Keep your current structure"
        feedback = "Solid profile. Stay disciplined and avoid changing a winning process."

    if not insights:
        insights.append("No major leak detected. Keep reinforcing your current structure.")

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


if "result" not in st.session_state:
    st.session_state.result = None

st.title("🎾 Mindset 20x10")
st.caption("Mental performance tracking for padel")

with st.container(border=True):
    st.subheader("Log match")
    st.write("Rate the match quickly. The goal is clarity, not perfection.")

    focus = st.slider("Focus", 1, 5, 3)
    margin = st.slider("Margin", 1, 5, 3)
    reset = st.slider("Reset", 1, 5, 3)
    intensity = st.slider("Intensity", 1, 5, 3)
    pressure = st.slider("Pressure handling", 1, 5, 3)
    too_aggressive = st.toggle("Played too aggressive?", value=False)
    note = st.text_input("Optional note", placeholder="Example: Lost focus when ahead")

    if st.button("Analyze", use_container_width=True, type="primary"):
        st.session_state.result = analyze_match(
            focus=focus,
            margin=margin,
            reset=reset,
            intensity=intensity,
            pressure=pressure,
            too_aggressive=too_aggressive,
            note=note,
        )

result = st.session_state.result
if result:
    st.divider()
    st.subheader("Match result")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mental Score Index", result.mental_score_index)
    with col2:
        st.metric("Pressure Score", result.pressure_score)

    with st.container(border=True):
        st.markdown("**Biggest leak**")
        st.write(result.biggest_leak)

    with st.container(border=True):
        st.markdown("**Next match focus**")
        st.write(result.next_focus)

    with st.container(border=True):
        st.markdown("**Coach feedback**")
        st.write(result.feedback)

    profile_cols = st.columns(len(result.profile))
    for idx, (label, value) in enumerate(result.profile.items()):
        with profile_cols[idx]:
            st.metric(label, f"{value}/5")

    with st.container(border=True):
        st.markdown("**Secondary insights**")
        for insight in result.insights:
            st.write(f"- {insight}")

    with st.container(border=True):
        st.markdown("**Current strengths**")
        if result.strengths:
            for strength in result.strengths:
                st.write(f"- {strength}")
        else:
            st.write("- No clear strength signal yet. Keep logging matches to build a more accurate profile.")

    st.info("Rule: only bring one focus point into the next match.")
