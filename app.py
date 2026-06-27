"""Premium Streamlit interface for plant disease detection."""

from PIL import Image
import streamlit as st

from components.footer import render_footer
from components.hero import render_hero, render_sidebar
from components.prediction import (
    render_empty_prediction,
    render_gradcam_section,
    render_prediction_summary,
    render_top_predictions,
)
from components.recommendations import render_advisory
from components.stats import render_about, render_stats
from components.styles import apply_global_styles
from components.upload import render_image_preview, render_upload_panel
from config import PATHS, PREDICTION_CONFIG, STREAMLIT_CONFIG
from utils import (
    generate_gradcam,
    get_confidence_threshold_percent,
    load_class_names,
    load_label_map,
    load_model_cached,
    load_model_metadata,
    load_training_history,
    predict_top_k,
    preprocess_image,
    validate_image_file,
)


st.set_page_config(
    page_title=STREAMLIT_CONFIG.get("page_title", "Plant & Crop Intelligence"),
    page_icon=STREAMLIT_CONFIG.get("page_icon", "🌿"),
    layout=STREAMLIT_CONFIG.get("layout", "wide"),
    initial_sidebar_state=STREAMLIT_CONFIG.get(
        "initial_sidebar_state",
        "expanded",
    ),
)

apply_global_styles()


@st.cache_data(show_spinner=False)
def load_project_metadata():
    """Load lightweight JSON artifacts once per Streamlit session."""
    labels = load_label_map(PATHS.get("labels", "labels.json"))
    metadata = load_model_metadata(
        PATHS.get("model_metadata", "models/model_metadata.json")
    )
    class_names = load_class_names(
        PATHS.get("class_indices", "models/class_indices.json"),
        labels=labels,
    )
    history = load_training_history(PATHS.get("history", "models/history.json"))
    return labels, metadata, class_names, history


def load_project_state():
    """Load model and all inference metadata."""
    labels, metadata, class_names, history = load_project_metadata()
    model = load_model_cached(PATHS.get("model", "models/plant_disease.keras"))
    return model, labels, metadata, class_names, history


def analyze_image(model, labels, metadata, class_names, pil_image):
    """Preprocess one image and return prediction results plus model input."""
    input_size = int(metadata.get("input_size", 224))
    input_scale = metadata.get(
        "input_scale",
        PREDICTION_CONFIG.get("input_scale", "0_1"),
    )
    top_k = int(PREDICTION_CONFIG.get("top_k", 3))

    preprocessed = preprocess_image(
        pil_image,
        img_size=(input_size, input_size),
        input_scale=input_scale,
    )
    results = predict_top_k(
        model,
        preprocessed,
        labels,
        k=top_k,
        class_names=class_names,
    )
    return preprocessed, results


model, labels, metadata, class_names, history = load_project_state()
threshold_percent = get_confidence_threshold_percent()
model_ready = model is not None and bool(labels) and bool(class_names)
show_gradcam = render_sidebar(
    model_ready=model_ready,
    class_count=len(class_names or []),
    threshold_percent=threshold_percent,
)

render_hero()
render_stats(
    history=history,
    class_names=class_names,
    metadata=metadata,
    model_path=PATHS.get("model", "models/plant_disease.keras"),
    threshold_percent=threshold_percent,
)

st.markdown("<div id='analysis'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

upload_col, result_col = st.columns([0.95, 1.05], gap="large")
uploaded_file = None
pil_image = None
results = None
preprocessed = None
gradcam_payload = None

with upload_col:
    st.markdown('<h2 class="section-heading">🔍 Upload Plant Image</h2>', unsafe_allow_html=True)
    uploaded_file = render_upload_panel()

    if uploaded_file:
        if validate_image_file(uploaded_file):
            uploaded_file.seek(0)
            pil_image = Image.open(uploaded_file).convert("RGB")
            render_image_preview(pil_image, uploaded_file)
        else:
            uploaded_file = None

with result_col:
    st.markdown('<h2 class="section-heading">Prediction Results</h2>', unsafe_allow_html=True)
    if not uploaded_file:
        render_empty_prediction()
    elif not model_ready:
        st.error(
            "The model artifacts are not ready. Verify the model, labels, "
            "metadata, and class index files before running predictions."
        )
    else:
        with st.status("Analyzing leaf image...", expanded=False) as status:
            preprocessed, results = analyze_image(
                model,
                labels,
                metadata,
                class_names,
                pil_image,
            )
            if results:
                status.update(label="Analysis complete", state="complete")
            else:
                status.update(label="Analysis failed", state="error")

        if not results:
            st.error("Prediction failed. Try a clearer image or verify model files.")
        else:
            main_result = results[0]
            render_prediction_summary(main_result, threshold_percent)
            render_top_predictions(results)

if uploaded_file and results and model_ready:
    main_result = results[0]

    st.markdown(
        """
        <div class="section-kicker">Explainability</div>
        <h2 class="section-heading">Model focus map</h2>
        """,
        unsafe_allow_html=True,
    )

    if show_gradcam:
        with st.spinner("Generating visual explanation..."):
            gradcam_payload = generate_gradcam(
                model,
                preprocessed,
                pil_image,
                class_index=main_result.get("index"),
            )
        render_gradcam_section(pil_image, gradcam_payload)
    else:
        st.info("Grad-CAM visualization is disabled from the sidebar.")

    st.markdown(
        """
        <div class="section-kicker">Agricultural guidance</div>
        <h2 class="section-heading">Smart crop advisory</h2>
        """,
        unsafe_allow_html=True,
    )
    render_advisory(main_result.get("advisory", {}), main_result.get("remedy"))

render_about(history, class_names)
render_footer()
