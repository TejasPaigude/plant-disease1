"""Agricultural advisory UI rendering."""

from html import escape

import streamlit as st


def _list_html(items):
    if not items:
        return "<p class='muted-copy'>Not available for this class.</p>"
    lines = "".join(f"<li>{escape(str(item))}</li>" for item in items)
    return f"<ul>{lines}</ul>"


def _info_card(title, body_html):
    return f"""
    <div class="info-card">
        <h3 class="card-title">{escape(title)}</h3>
        {body_html}
    </div>
    """


def render_advisory(advisory, immediate_remedy=None):
    """Render disease explanation, treatment, prevention, and care guidance."""
    if not advisory:
        st.info("Advisory details are unavailable for this prediction.")
        return

    crop = escape(advisory.get("crop", "Unknown crop"))
    disease = escape(advisory.get("disease_name", "Unknown condition"))
    urgency = escape(advisory.get("urgency", "medium").title())
    description = escape(advisory.get("description", "No description available."))
    treatments = advisory.get("treatment", [])
    first_treatment = treatments[0] if treatments else "Monitor the plant and confirm field conditions before treatment."
    immediate = escape(immediate_remedy or first_treatment)
    disclaimer = escape(
        advisory.get(
            "disclaimer",
            "Use this guidance as decision support and confirm severe cases with a local expert.",
        )
    )

    st.markdown(
        f"""
        <div class="premium-card" style="padding:22px;margin-bottom:16px;">
            <span class="status-pill status-info">Urgency: {urgency}</span>
            <h3 class="prediction-name" style="font-size:1.65rem;">{crop} - {disease}</h3>
            <p class="muted-copy">{description}</p>
            <p class="muted-copy"><strong>First action:</strong> {immediate}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview, treatment, prevention, field_care = st.tabs(
        ["Overview", "Treatment", "Prevention", "Field Care"]
    )

    with overview:
        st.markdown(
            f"""
            <div class="advisory-grid">
                {_info_card("Symptoms", _list_html(advisory.get("symptoms", [])))}
                {_info_card("Likely Causes", _list_html(advisory.get("causes", [])))}
                {_info_card("Environmental Triggers", _list_html(advisory.get("environmental_triggers", [])))}
                {_info_card("Scientific Note", f"<p class='muted-copy'>{description}</p>")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with treatment:
        st.markdown(
            f"""
            <div class="advisory-grid">
                {_info_card("Treatment Recommendations", _list_html(advisory.get("treatment", [])))}
                {_info_card("Pesticide Suggestions", _list_html(advisory.get("pesticide_suggestions", [])))}
                {_info_card("Organic Treatment Options", _list_html(advisory.get("organic_treatments", [])))}
                {_info_card("Fertilizer Suggestions", _list_html(advisory.get("fertilizer_suggestions", [])))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with prevention:
        st.markdown(
            f"""
            <div class="advisory-grid">
                {_info_card("Prevention Methods", _list_html(advisory.get("prevention", [])))}
                {_info_card("Early Monitoring", _list_html(advisory.get("crop_care_guidance", [])))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with field_care:
        st.markdown(
            f"""
            <div class="advisory-grid">
                {_info_card("Irrigation Advice", _list_html(advisory.get("irrigation_advice", [])))}
                {_info_card("Crop-Care Guidance", _list_html(advisory.get("crop_care_guidance", [])))}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(disclaimer)
