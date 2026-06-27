"""Footer component."""

import streamlit as st


def render_footer():
    """Render a compact professional footer."""
    st.markdown(
        """
        <div id="deployment" class="footer">
            <strong>AI-Based Plant Disease Detection and Smart Crop Advisory System</strong><br>
            Built with Streamlit, TensorFlow/Keras, FastAPI, and EfficientNetV2B0.
            This tool provides decision support only; field treatment decisions should be verified locally.
        </div>
        """,
        unsafe_allow_html=True,
    )
