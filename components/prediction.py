"""Prediction and explainability panels."""

from html import escape

import streamlit as st

from utils import is_low_confidence


def _progress(value_percent):
    value = min(max(float(value_percent) / 100.0, 0.0), 1.0)
    st.progress(value)


def render_empty_prediction():
    """Render a polished empty state."""
    html = (
        '<div class="prediction-card empty-result">'
        "<p>Upload an image to analyze</p>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_prediction_summary(result, threshold_percent):
    """Render the primary disease result and confidence gate."""
    confidence = float(result["confidence"])
    uncertain = is_low_confidence(confidence, threshold_percent)
    status_class = "status-warning" if uncertain else "status-ok"
    status_text = "Uncertain prediction" if uncertain else "High-confidence prediction"
    display_name = escape(result.get("display", "Unknown condition"))
    class_name = escape(result.get("class", "Unknown class"))
    remedy = escape(result.get("remedy", "No recommendation available."))
    severity = _severity_label(confidence, uncertain)

    html = (
        '<div class="prediction-card">'
        '<p class="section-kicker">Prediction Results</p>'
        f'<span class="status-pill {status_class}">{status_text}</span>'
        f'<h3 class="prediction-name">{display_name}</h3>'
        f'<p class="muted-copy">Model class: {class_name}</p>'
        '<div class="confidence-row">'
        '<span class="muted-copy">Confidence score</span>'
        f'<span class="confidence-number">{confidence:.1f}%</span>'
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
    _progress(confidence)

    if uncertain:
        st.warning(
            f"Top confidence is below the configured {threshold_percent:.0f}% "
            "threshold. Treat this as a candidate diagnosis and upload a clearer image if possible."
        )
    else:
        st.success(f"Severity signal: {severity}")

    html = (
        '<div class="premium-card" style="padding:18px;margin-top:14px;">'
        '<p class="stat-label">Immediate recommendation</p>'
        f'<p class="muted-copy" style="margin-bottom:0;">{remedy}</p>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_top_predictions(results):
    """Render top-k alternatives as compact cards."""
    if not results:
        return

    cards = []
    for rank, result in enumerate(results[:3], start=1):
        display_name = escape(result.get("display", "Unknown"))
        confidence = float(result.get("confidence", 0.0))
        cards.append(
            f'<div class="rank-card">'
            f'<span class="status-pill status-info">Rank {rank}</span>'
            f'<p class="rank-title">{display_name}</p>'
            f'<p class="muted-copy" style="margin:0 0 8px;">Confidence: {confidence:.1f}%</p>'
            "</div>"
        )

    html = (
        '<div style="margin-top:18px;">'
        '<p class="section-kicker">Alternatives</p>'
        '<h3 class="card-title">Top prediction candidates</h3>'
        f'<div class="rank-grid">{"".join(cards)}</div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_gradcam_section(original_image, gradcam_payload):
    """Render side-by-side original and Grad-CAM images."""
    if not gradcam_payload:
        st.info(
            "Grad-CAM could not be generated for this image/model output. "
            "The prediction still completed normally."
        )
        return

    layer_name = gradcam_payload.get("layer_name", "feature layer")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("#### Original")
        st.image(original_image, use_container_width=True)
    with right:
        st.markdown(f"#### Grad-CAM overlay")
        st.image(
            gradcam_payload["overlay"],
            caption=f"Focus layer: {layer_name}",
            use_container_width=True,
        )

    st.caption(
        "Warmer red/yellow regions had the strongest influence on the predicted class."
    )


def _severity_label(confidence, uncertain):
    if uncertain:
        return "Needs confirmation"
    if confidence >= 90:
        return "Strong visual match"
    if confidence >= 70:
        return "Moderate visual match"
    return "Low visual certainty"
