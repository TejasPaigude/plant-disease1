"""Metric card rendering helpers."""

from pathlib import Path

import streamlit as st


def _history_best(history, key):
    if not history or key not in history or not history[key]:
        return "N/A"
    return f"{max(history[key]) * 100:.1f}%"


def _model_size_mb(model_path):
    path = Path(model_path)
    if not path.exists():
        return "N/A"
    return f"{path.stat().st_size / (1024 * 1024):.1f} MB"


def _card(label, value, note):
    return f"""
    <div class="stat-card">
        <p class="stat-label">{label}</p>
        <p class="stat-value">{value}</p>
        <p class="stat-note">{note}</p>
    </div>
    """


def render_stats(history, class_names, metadata, model_path, threshold_percent):
    """Render product-grade model and system metrics."""
    architecture = metadata.get("architecture", "EfficientNetV2B0")
    input_size = metadata.get("input_size", 224)
    input_scale = metadata.get("input_scale", "0_1")

    st.markdown(
        f"""
        <div class="stats-grid">
            {_card("Disease Classes", len(class_names or []), "PlantVillage class mapping loaded from model metadata.")}
            {_card("Best Validation", _history_best(history, "val_accuracy"), "Highest validation accuracy recorded in training history.")}
            {_card("Top-3 Accuracy", _history_best(history, "val_top_3_accuracy"), "Backup metric when disease symptoms are visually similar.")}
            {_card("Confidence Gate", f"{threshold_percent:.0f}%", "Predictions below this threshold are shown as uncertain.")}
            {_card("Model Runtime", architecture, f"Input: {input_size}x{input_size}, scale: {input_scale}.")}
            {_card("Model Artifact", _model_size_mb(model_path), "Native Keras .keras artifact used for deployment.")}
            {_card("Inference Mode", "Single image", "Optimized for Streamlit upload and FastAPI request workflows.")}
            {_card("Advisory Engine", "Enabled", "Treatment, prevention, irrigation, fertilizer, and organic guidance.")}
        </div>
        """,
        unsafe_allow_html=True,
    )
