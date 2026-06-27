"""Upload panel rendering helpers."""

import streamlit as st


def render_upload_panel():
    """Render the image upload card and return the uploaded file."""
    st.markdown(
        """
        <div class="upload-card">
            <p class="section-kicker">Input</p>
            <h3 class="upload-title">Leaf image upload</h3>
            <p class="muted-copy">
                Use a clear, well-lit photo where the leaf occupies most of the frame.
                Supported formats: JPG, JPEG, PNG, BMP, and GIF. Maximum size: 10 MB.
            </p>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload plant leaf image",
        type=["jpg", "jpeg", "png", "bmp", "gif"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    st.markdown(
        """
            <p class="muted-copy">
                Tip: crop out unrelated background when possible for cleaner predictions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return uploaded_file


def render_image_preview(pil_image, uploaded_file):
    """Render a preview and lightweight image details."""
    st.markdown('<div class="preview-frame">', unsafe_allow_html=True)
    st.image(pil_image, caption="Uploaded image preview", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    width, height = pil_image.size
    size_mb = uploaded_file.size / (1024 * 1024)
    c1, c2, c3 = st.columns(3)
    c1.metric("Width", f"{width}px")
    c2.metric("Height", f"{height}px")
    c3.metric("Size", f"{size_mb:.2f} MB")
