"""Hero and sidebar rendering helpers."""

import streamlit as st


def render_sidebar(model_ready, class_count, threshold_percent):
    """Render the left navigation and return UI preferences."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-logo">AI</div>
                <p class="sidebar-title">Plant Intelligence</p>
                <p class="sidebar-subtitle">Disease detection, explainability, and smart crop advisory.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="side-nav">
                <span>Dashboard</span>
                <span>Image Analysis</span>
                <span>Grad-CAM</span>
                <span>Crop Advisory</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        show_gradcam = st.toggle("Show Grad-CAM explanation", value=True)

        st.markdown("#### System Status")
        if model_ready:
            st.success("Model ready")
        else:
            st.error("Model unavailable")

        st.markdown("#### Model")
        st.caption("Architecture: EfficientNetV2B0 transfer learning")
        st.caption(f"Classes: {class_count}")
        st.caption(f"Confidence threshold: {threshold_percent:.0f}%")
        st.caption("Model file: models/plant_disease.keras")

        st.markdown("#### Project")
        st.caption("Theme: Premium dark")
        st.caption("Version: 2.0")
        st.caption("Built for final year project review and portfolio deployment.")

    return show_gradcam


def render_hero():
    """Render the product-style landing section."""
    st.markdown(
        """
        <section class="hero-shell">
            <div class="hero-content">
                <div class="badge-row">
                    <span class="soft-badge">AI powered diagnosis</span>
                    <span class="soft-badge">Keras 3 compatible</span>
                    <span class="soft-badge">Grad-CAM explainability</span>
                    <span class="soft-badge">v2.0</span>
                </div>
                <h1 class="hero-title">
                    Plant & Crop <span class="hero-gradient-text">Intelligence</span>
                </h1>
                <p class="hero-subtitle">
                    Upload a leaf image and get disease prediction, confidence analysis,
                    visual model focus maps, and practical crop-care recommendations in one workflow.
                </p>
                <div class="cta-row">
                    <a class="primary-cta" href="#analysis">Start analysis</a>
                    <a class="secondary-cta" href="#deployment">Deployment ready</a>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
