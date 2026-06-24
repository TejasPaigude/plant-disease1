import streamlit as st
from PIL import Image

from config import PATHS, PREDICTION_CONFIG
from utils import (
    generate_gradcam,
    get_confidence_threshold_percent,
    is_low_confidence,
    load_class_names,
    load_label_map,
    load_model_cached,
    load_model_metadata,
    load_training_history,
    predict_top_k,
    preprocess_image,
    validate_image_file,
)


st.set_page_config(page_title="Plant Disease Detection", page_icon="🌾", layout="wide")


st.markdown(
    """
    <style>
    * {box-sizing: border-box;}
    body {background: linear-gradient(135deg, #07130d 0%, #101b2d 100%);}
    .header-title {color: #22c55e; text-align: center; font-size: 42px; font-weight: 800; letter-spacing: 1px; margin: 28px 0 8px 0;}
    .header-subtitle {color: #b7c7bd; text-align: center; font-size: 15px; margin-bottom: 24px;}
    .metric-band {border: 1px solid rgba(34,197,94,.35); border-radius: 12px; padding: 16px; background: rgba(5,20,12,.72);}
    .status-card {border-radius: 12px; padding: 18px; background: rgba(10,25,18,.86); border: 1px solid rgba(0,206,209,.38);}
    .prediction-box {border-radius: 12px; padding: 22px; background: rgba(6,24,18,.86); border: 1px solid rgba(34,197,94,.55);}
    .warning-box {border-radius: 10px; padding: 14px; background: rgba(255,149,0,.13); border: 1px solid rgba(255,149,0,.52); color: #ffd28a;}
    .ok-box {border-radius: 10px; padding: 14px; background: rgba(34,197,94,.12); border: 1px solid rgba(34,197,94,.44); color: #bff5ce;}
    .muted {color: #9aa8a0; font-size: 13px;}
    .section-title {color: #22c55e; font-weight: 750; margin: 22px 0 10px 0;}
    .small-label {color: #7dd3fc; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px;}
    .rank-card {border-radius: 12px; padding: 16px; background: rgba(8,16,32,.88); border: 1px solid rgba(125,211,252,.34); min-height: 154px;}
    .rank-card h4 {color: #e9f7ef; font-size: 15px; line-height: 1.25; margin: 0 0 10px 0;}
    .advice-card {border-radius: 10px; padding: 14px 16px; background: rgba(10,25,18,.7); border: 1px solid rgba(148,163,184,.24); margin-bottom: 10px;}
    @media (max-width: 800px) {
        .header-title {font-size: 30px;}
        .header-subtitle {font-size: 13px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_project_state():
    labels = load_label_map(PATHS.get("labels", "labels.json"))
    metadata = load_model_metadata(PATHS.get("model_metadata", "models/model_metadata.json"))
    class_names = load_class_names(
        PATHS.get("class_indices", "models/class_indices.json"),
        labels=labels,
    )
    history = load_training_history(PATHS.get("history", "models/history.json"))
    model = load_model_cached(PATHS.get("model", "models/plant_disease.keras"))
    return model, labels, metadata, class_names, history


def history_metric(history, key):
    if not history or key not in history or not history[key]:
        return "N/A"
    return f"{max(history[key]) * 100:.2f}%"


def render_list(items):
    for item in items or []:
        st.markdown(f"- {item}")


def render_advisory(advisory):
    if not advisory:
        st.info("Advisory details are not available for this prediction.")
        return

    overview, symptoms, treatment, prevention, care = st.tabs(
        ["Overview", "Symptoms & Causes", "Treatment", "Prevention", "Crop Care"]
    )

    with overview:
        st.markdown(f"**Crop:** {advisory.get('crop', 'Unknown')}")
        st.markdown(f"**Condition:** {advisory.get('disease_name', 'Unknown')}")
        st.markdown(advisory.get("description", "No description available."))
        st.markdown(f"**Urgency:** {advisory.get('urgency', 'medium').title()}")

    with symptoms:
        st.markdown("**Symptoms**")
        render_list(advisory.get("symptoms", []))
        st.markdown("**Likely Causes**")
        render_list(advisory.get("causes", []))
        st.markdown("**Environmental Triggers**")
        render_list(advisory.get("environmental_triggers", []))

    with treatment:
        st.markdown("**Treatment Recommendations**")
        render_list(advisory.get("treatment", []))
        st.markdown("**Pesticide Suggestions**")
        render_list(advisory.get("pesticide_suggestions", []))
        st.markdown("**Organic Options**")
        render_list(advisory.get("organic_treatments", []))

    with prevention:
        st.markdown("**Prevention Methods**")
        render_list(advisory.get("prevention", []))
        st.markdown("**Fertilizer Suggestions**")
        render_list(advisory.get("fertilizer_suggestions", []))

    with care:
        st.markdown("**Irrigation Advice**")
        render_list(advisory.get("irrigation_advice", []))
        st.markdown("**Crop-Care Guidance**")
        render_list(advisory.get("crop_care_guidance", []))
        st.caption(advisory.get("disclaimer", "Confirm field decisions with a local expert."))


def render_prediction_summary(main_result, threshold):
    confidence = float(main_result["confidence"])
    uncertain = is_low_confidence(confidence, threshold)

    if uncertain:
        st.markdown(
            f"<div class='warning-box'><strong>Uncertain prediction.</strong> "
            f"Top confidence is {confidence:.1f}%, below the configured {threshold:.1f}% threshold. "
            "Use the top predictions as candidates and upload a clearer leaf image if possible.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='ok-box'><strong>Prediction confidence is above the configured threshold.</strong></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class='prediction-box'>
            <div class='small-label'>Primary Result</div>
            <h3 style='color:#e9f7ef;margin:0 0 8px 0;'>{main_result['display']}</h3>
            <p class='muted' style='margin:0;'>Class: {main_result['class']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(min(max(confidence / 100.0, 0.0), 1.0))
    st.metric("Confidence", f"{confidence:.1f}%")


def render_top_predictions(results):
    st.markdown("<h3 class='section-title'>Top Predictions</h3>", unsafe_allow_html=True)
    columns = st.columns(min(3, len(results)), gap="medium")
    for idx, result in enumerate(results[:3]):
        with columns[idx]:
            confidence = float(result["confidence"])
            st.markdown(
                f"""
                <div class='rank-card'>
                    <div class='small-label'>Rank {idx + 1}</div>
                    <h4>{result['display']}</h4>
                    <p class='muted' style='margin:0 0 10px 0;'>{result['class']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(max(confidence / 100.0, 0.0), 1.0))
            st.markdown(f"**{confidence:.1f}%**")


def render_gradcam(model, image_array, original_image, class_index):
    with st.spinner("Generating Grad-CAM explanation..."):
        cam = generate_gradcam(
            model,
            image_array,
            original_image,
            class_index=class_index,
        )

    st.markdown("<h3 class='section-title'>Model Focus Visualization</h3>", unsafe_allow_html=True)
    if not cam:
        st.info("Grad-CAM could not be generated for this model output. Prediction still completed normally.")
        return

    left, right = st.columns(2, gap="large")
    with left:
        st.image(original_image, caption="Original Image", use_column_width=True)
    with right:
        st.image(cam["overlay"], caption=f"Grad-CAM Overlay ({cam['layer_name']})", use_column_width=True)


model, labels, metadata, class_names, history_data = load_project_state()
threshold_percent = get_confidence_threshold_percent()
top_k = int(PREDICTION_CONFIG.get("top_k", 3))

st.markdown("<div class='header-title'>Plant & Crop Intelligence</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='header-subtitle'>Disease detection, confidence analysis, explainability, and crop-care advisory</div>",
    unsafe_allow_html=True,
)

metric_cols = st.columns(4, gap="medium")
with metric_cols[0]:
    st.markdown("<div class='metric-band'><div class='small-label'>Model</div><strong>EfficientNetV2B0</strong></div>", unsafe_allow_html=True)
with metric_cols[1]:
    st.markdown(f"<div class='metric-band'><div class='small-label'>Best Validation</div><strong>{history_metric(history_data, 'val_accuracy')}</strong></div>", unsafe_allow_html=True)
with metric_cols[2]:
    st.markdown(f"<div class='metric-band'><div class='small-label'>Top-3 Validation</div><strong>{history_metric(history_data, 'val_top_3_accuracy')}</strong></div>", unsafe_allow_html=True)
with metric_cols[3]:
    st.markdown(f"<div class='metric-band'><div class='small-label'>Classes</div><strong>{len(class_names) if class_names else 0}</strong></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h2 class='section-title'>Upload Plant Image</h2>", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1.15], gap="large")
with left_col:
    uploaded_file = st.file_uploader(
        "Choose a leaf image",
        type=["jpg", "jpeg", "png", "bmp"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        if not validate_image_file(uploaded_file):
            st.stop()
        uploaded_file.seek(0)
        pil_image = Image.open(uploaded_file).convert("RGB")
        st.image(pil_image, caption="Uploaded Image", use_column_width=True)
    else:
        pil_image = None
        st.markdown(
            "<div class='status-card'><strong>Upload a leaf image to begin analysis.</strong></div>",
            unsafe_allow_html=True,
        )

with right_col:
    st.markdown("<h3 class='section-title'>Prediction Results</h3>", unsafe_allow_html=True)
    if not uploaded_file:
        st.info("Waiting for image upload.")
    elif model is None or not labels:
        st.error("Model or labels are unavailable. Train the model and verify project artifacts first.")
    else:
        input_size = int(metadata.get("input_size", 224))
        input_scale = metadata.get("input_scale", "0_1")

        with st.spinner("Analyzing leaf image..."):
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

        if not results:
            st.error("Prediction failed. Try another image or verify the model artifacts.")
        else:
            main = results[0]
            render_prediction_summary(main, threshold_percent)

if uploaded_file and model is not None and labels and "results" in locals() and results:
    st.markdown("---")
    render_top_predictions(results)

    st.markdown("---")
    render_gradcam(model, preprocessed, pil_image, class_index=main.get("index"))

    st.markdown("---")
    st.markdown("<h3 class='section-title'>Smart Crop Advisory</h3>", unsafe_allow_html=True)
    render_advisory(main.get("advisory", {}))

st.markdown("---")
st.markdown(
    """
    <div class='status-card'>
        <strong>Production note:</strong>
        predictions are decision-support only. Confirm severe field cases with a local agricultural expert.
    </div>
    """,
    unsafe_allow_html=True,
)
