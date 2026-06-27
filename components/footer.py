"""Footer component."""

import streamlit as st


def render_footer():
    """Render a compact professional footer."""
    st.markdown(
        """
        <div id="deployment" class="footer">
            <strong>AI-Based Plant Disease Detection and Smart Crop Advisory System</strong><br>
            Built using:
            <div class="tech-row">
                <span class="tech-chip">TensorFlow</span>
                <span class="tech-chip">Keras</span>
                <span class="tech-chip">Python</span>
                <span class="tech-chip">Streamlit</span>
                <span class="tech-chip">OpenCV</span>
                <span class="tech-chip">Pandas</span>
                <span class="tech-chip">Scikit-learn</span>
            </div>
            This tool provides decision support only; field treatment decisions should be verified locally.
        </div>
        """,
        unsafe_allow_html=True,
    )
