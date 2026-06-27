"""
Utility functions for plant disease detection system.

These helpers keep inference preprocessing, model metadata, and class-index
mapping aligned with the training pipeline.
"""

import json
import re
from pathlib import Path

import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image

from advisory import get_advisory

try:
    from config import FILE_CONFIG, PATHS, PREDICTION_CONFIG
except ImportError:
    FILE_CONFIG = {}
    PATHS = {}
    PREDICTION_CONFIG = {}


DEFAULT_MODEL_PATH = PATHS.get("model", "models/plant_disease.keras")
MIN_MODEL_FILE_BYTES = 1024 * 1024


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _model_candidates(model_path):
    """Prefer native Keras checkpoints, with legacy H5 only as fallback."""
    path = Path(model_path)
    candidates = [path]

    if path.suffix == ".h5":
        candidates.insert(0, path.with_suffix(".keras"))
    elif path.suffix == ".keras":
        candidates.append(path.with_suffix(".h5"))

    unique_candidates = []
    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)
    return unique_candidates


def validate_model_file(model_path, min_bytes=MIN_MODEL_FILE_BYTES):
    """Validate that a model file exists, has a sane size, and can be loaded."""
    path = Path(model_path)
    if not path.exists():
        return False, f"model file does not exist: {path}"
    if not path.is_file():
        return False, f"model path is not a file: {path}"
    if path.stat().st_size < min_bytes:
        return False, f"model file is too small ({path.stat().st_size} bytes)"

    try:
        tf.keras.models.load_model(path, compile=False)
    except Exception as exc:
        return False, f"model load validation failed: {exc}"

    return True, "ok"


def resolve_model_path(model_path=DEFAULT_MODEL_PATH):
    """Return the first valid model path, preferring .keras over legacy .h5."""
    failures = []
    for candidate in _model_candidates(model_path):
        if not candidate.exists():
            failures.append(f"{candidate}: missing")
            continue

        is_valid, reason = validate_model_file(candidate)
        if is_valid:
            return candidate, None

        failures.append(f"{candidate}: {reason}")

    return None, "; ".join(failures)


def load_model_metadata(metadata_path="models/model_metadata.json"):
    """
    Load preprocessing metadata saved during training.

    If metadata is missing, default to the legacy model behavior where images
    are scaled to [0, 1] before prediction.
    """
    default_metadata = {
        "architecture": "legacy_custom_cnn",
        "input_size": 224,
        "input_scale": "0_1",
    }

    try:
        if not Path(metadata_path).exists():
            return default_metadata

        metadata = _load_json(metadata_path)
        return {**default_metadata, **metadata}
    except Exception as e:
        st.warning(f"Could not load model metadata: {str(e)}")
        return default_metadata


def preprocess_image(image_input, img_size=(224, 224), input_scale="0_1"):
    """
    Preprocess image for model prediction.

    Args:
        image_input: PIL Image or file path
        img_size: Target image size
        input_scale: "0_1" for legacy models, "raw_0_255" for models with
            built-in preprocessing, or "minus_1_1" for MobileNet-style inputs

    Returns:
        Preprocessed image array ready for prediction
    """
    try:
        if isinstance(image_input, str):
            img = Image.open(image_input)
        else:
            img = image_input

        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img = img.resize(img_size, Image.Resampling.LANCZOS)
        img_array = np.array(img, dtype=np.float32)

        if input_scale == "0_1":
            img_array = img_array / 255.0
        elif input_scale == "minus_1_1":
            img_array = (img_array / 127.5) - 1.0
        elif input_scale == "raw_0_255":
            pass
        else:
            st.warning(f"Unknown input scale '{input_scale}'. Using legacy [0, 1] scaling.")
            img_array = img_array / 255.0

        return np.expand_dims(img_array, axis=0)

    except Exception as e:
        st.error(f"Error preprocessing image: {str(e)}")
        return None


@st.cache_resource
def load_model_cached(model_path=DEFAULT_MODEL_PATH):
    """
    Load pre-trained model with caching for performance.
    """
    try:
        path, failure_reason = resolve_model_path(model_path)
        if path is None:
            st.error(f"Valid model not found. Checked: {failure_reason}")
            st.info("Please train the model first using: python model_training.py")
            return None

        return tf.keras.models.load_model(path, compile=False)

    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None


def get_confidence_threshold_percent():
    """Return configured confidence threshold as a percentage."""
    threshold = float(PREDICTION_CONFIG.get("confidence_threshold", 0.3))
    return threshold * 100.0 if threshold <= 1.0 else threshold


def is_low_confidence(confidence_percent, threshold_percent=None):
    """Return True when a prediction should be treated as uncertain."""
    threshold = (
        get_confidence_threshold_percent()
        if threshold_percent is None
        else float(threshold_percent)
    )
    return float(confidence_percent) < threshold


def canonicalize_class_name(class_name):
    """Normalize class names so folder-name variants can match label metadata."""
    cleaned = class_name.lower()
    for token in (
        "including_sour",
        "citrus_greening",
        "black_measles",
        "isariopsis_leaf_spot",
        "gray_leaf_spot",
        "two_spotted_spider_mite",
        "two-spotted_spider_mite",
        "maize",
        "bell",
    ):
        cleaned = cleaned.replace(token, "")
    return re.sub(r"[^a-z0-9]+", "", cleaned)


def format_class_name(class_name):
    """Create a readable label from a dataset folder name."""
    if "___" in class_name:
        crop, disease = class_name.split("___", 1)
    else:
        crop, disease = "Plant", class_name

    crop = re.sub(r"_+", " ", crop).replace(",", ", ")
    disease = re.sub(r"_+", " ", disease)
    crop = re.sub(r"\s+", " ", crop).strip()
    disease = re.sub(r"\s+", " ", disease).strip(" _-")
    return f"{crop.title()} - {disease.title()}"


def resolve_label_info(class_name, labels):
    """Return display/remedy info with exact, canonical, and partial matching."""
    if class_name in labels:
        return labels[class_name]

    target = canonicalize_class_name(class_name)
    canonical_lookup = {
        canonicalize_class_name(key): value for key, value in labels.items()
    }

    if target in canonical_lookup:
        return canonical_lookup[target]

    for key, value in canonical_lookup.items():
        if target.startswith(key) or key.startswith(target):
            return value

    if class_name.lower().endswith("healthy"):
        return {
            "display": format_class_name(class_name),
            "remedy": "No treatment needed. Continue regular monitoring.",
        }

    return {
        "display": format_class_name(class_name),
        "remedy": "Remove affected leaves where practical, isolate severely infected plants, and consult a local agricultural expert for crop-specific treatment.",
    }


def _call_inference_layer(layer, inputs):
    """Call a Keras layer in inference mode when the layer supports it."""
    try:
        return layer(inputs, training=False)
    except TypeError:
        return layer(inputs)


def _find_nested_backbone(model):
    """Find the nested CNN backbone inside the full transfer-learning model."""
    nested_models = [layer for layer in model.layers if isinstance(layer, tf.keras.Model)]
    for layer in nested_models:
        if "efficientnet" in layer.name.lower():
            return layer
    return nested_models[0] if nested_models else None


def _find_last_4d_layer(backbone, preferred_layer_name=None):
    """Find a spatial feature layer suitable for Grad-CAM."""
    if preferred_layer_name:
        return backbone.get_layer(preferred_layer_name)

    for layer in reversed(backbone.layers):
        try:
            output_shape = layer.output.shape
        except Exception:
            continue

        if len(output_shape) == 4:
            return layer

    return None


def make_gradcam_heatmap(model, image_array, class_index=None, layer_name=None):
    """
    Generate a normalized Grad-CAM heatmap for the predicted class.

    The model architecture contains augmentation layers, a nested
    EfficientNetV2B0 backbone, and a classifier head. This function keeps that
    full inference path intact while exposing the last spatial backbone layer.
    """
    if model is None or image_array is None:
        return None

    try:
        backbone = _find_nested_backbone(model)
        if backbone is None:
            return None

        target_layer = _find_last_4d_layer(backbone, layer_name)
        if target_layer is None:
            return None

        feature_model = tf.keras.Model(
            backbone.inputs,
            [target_layer.output, backbone.output],
        )

        image_tensor = tf.convert_to_tensor(image_array, dtype=tf.float32)
        with tf.GradientTape() as tape:
            x = image_tensor
            passed_backbone = False

            for layer in model.layers[1:]:
                if layer is backbone:
                    conv_outputs, x = feature_model(x, training=False)
                    passed_backbone = True
                    continue

                x = _call_inference_layer(layer, x)

            predictions = x
            if class_index is None:
                class_index = int(tf.argmax(predictions[0]).numpy())

            class_score = predictions[:, int(class_index)]

        grads = tape.gradient(class_score, conv_outputs)
        if grads is None:
            return None

        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_sum(conv_outputs * pooled_grads, axis=-1)
        heatmap = tf.maximum(heatmap, 0)
        max_value = tf.reduce_max(heatmap)

        if float(max_value.numpy()) <= 1e-8:
            return None

        heatmap = heatmap / max_value
        return {
            "heatmap": heatmap.numpy(),
            "layer_name": target_layer.name,
            "class_index": int(class_index),
        }

    except Exception:
        return None


def overlay_heatmap_on_image(original_image, heatmap, alpha=0.48):
    """Create a heatmap image and a red/yellow overlay on the original image."""
    try:
        base = original_image.convert("RGB")
        heatmap_uint8 = np.uint8(255 * np.clip(heatmap, 0.0, 1.0))
        heatmap_img = Image.fromarray(heatmap_uint8).resize(
            base.size,
            Image.Resampling.BILINEAR,
        )
        heatmap_arr = np.array(heatmap_img, dtype=np.float32) / 255.0
        base_arr = np.array(base, dtype=np.float32)

        color_arr = np.zeros_like(base_arr)
        color_arr[..., 0] = 255.0
        color_arr[..., 1] = np.clip(heatmap_arr * 220.0, 0.0, 220.0)

        alpha_map = (heatmap_arr ** 0.7) * float(alpha)
        alpha_map = np.expand_dims(alpha_map, axis=-1)
        overlay_arr = (base_arr * (1.0 - alpha_map)) + (color_arr * alpha_map)
        overlay_arr = np.clip(overlay_arr, 0, 255).astype(np.uint8)

        heat_color = np.zeros_like(base_arr, dtype=np.uint8)
        heat_color[..., 0] = 255
        heat_color[..., 1] = np.clip(heatmap_arr * 220, 0, 220).astype(np.uint8)

        return Image.fromarray(heat_color), Image.fromarray(overlay_arr)

    except Exception:
        return None, None


def generate_gradcam(model, image_array, original_image, class_index=None):
    """Return Grad-CAM heatmap and overlay images, or None on safe failure."""
    cam = make_gradcam_heatmap(model, image_array, class_index=class_index)
    if not cam:
        return None

    heatmap_img, overlay_img = overlay_heatmap_on_image(original_image, cam["heatmap"])
    if heatmap_img is None or overlay_img is None:
        return None

    return {
        "heatmap": heatmap_img,
        "overlay": overlay_img,
        "layer_name": cam["layer_name"],
        "class_index": cam["class_index"],
    }


def load_class_names(
    class_indices_path="models/class_indices.json",
    train_dir="data/train_split",
    labels=None,
):
    """
    Load class names in the same index order used by the trained model.

    Priority:
    1. models/class_indices.json saved during training
    2. alphabetically sorted train_split folders, matching Keras directory order
    3. alphabetically sorted labels keys as a last fallback
    """
    try:
        path = Path(class_indices_path)
        if path.exists():
            data = _load_json(path)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return [
                    class_name
                    for class_name, _ in sorted(data.items(), key=lambda item: int(item[1]))
                ]

        train_path = Path(train_dir)
        if train_path.exists():
            class_names = sorted(
                path.name for path in train_path.iterdir() if path.is_dir()
            )
            if class_names:
                return class_names

        if labels:
            return sorted(labels.keys())

        return []
    except Exception as e:
        st.warning(f"Could not load class index mapping: {str(e)}")
        return sorted(labels.keys()) if labels else []


def predict_top_k(model, image_array, labels, k=3, class_names=None):
    """
    Get top-k predictions from the model.

    Args:
        model: Trained Keras model
        image_array: Preprocessed image array
        labels: Dictionary with class metadata
        k: Number of top predictions to return
        class_names: Class names ordered by model output index

    Returns:
        List of dicts with class, display, confidence, and remedy
    """
    try:
        if model is None or image_array is None:
            return None

        predictions = model.predict(image_array, verbose=0)
        probabilities = predictions[0]
        class_names = class_names or load_class_names(labels=labels)
        output_classes = int(probabilities.shape[-1])

        if class_names and len(class_names) != output_classes:
            st.error(
                "Class mapping mismatch: model outputs "
                f"{output_classes} classes but metadata contains {len(class_names)}."
            )
            return None

        k = min(int(k), output_classes)
        top_k_indices = np.argsort(probabilities)[-k:][::-1]

        results = []
        for idx in top_k_indices:
            idx = int(idx)
            confidence = float(probabilities[idx])
            if idx < len(class_names):
                class_name = class_names[idx]
            else:
                class_name = f"Class_{idx}"

            disease_info = resolve_label_info(class_name, labels or {})
            display_name = disease_info.get("display", format_class_name(class_name))
            remedy = disease_info.get("remedy", "No information available.")
            advisory = get_advisory(class_name, disease_info)

            results.append(
                {
                    "index": idx,
                    "class": class_name,
                    "display": display_name,
                    "confidence": confidence * 100,
                    "remedy": remedy,
                    "advisory": advisory,
                }
            )

        return results

    except Exception as e:
        st.error(f"Error during prediction: {str(e)}")
        return None


def load_label_map(label_path="labels.json"):
    """
    Load label mapping from JSON file.
    """
    try:
        if not Path(label_path).exists():
            st.warning(f"Labels file not found at {label_path}")
            return {}

        return _load_json(label_path)

    except json.JSONDecodeError:
        st.error("Error reading labels.json - invalid JSON format")
        return {}
    except Exception as e:
        st.error(f"Error loading labels: {str(e)}")
        return {}


def load_training_history(history_path="models/history.json"):
    """
    Load training history for displaying model metrics.
    """
    try:
        if not Path(history_path).exists():
            return None

        return _load_json(history_path)

    except Exception as e:
        st.warning(f"Could not load training history: {str(e)}")
        return None


def validate_image_file(uploaded_file):
    """
    Validate uploaded image file.
    """
    if uploaded_file is None:
        return False

    valid_extensions = set(
        FILE_CONFIG.get("allowed_extensions", ["jpg", "jpeg", "png", "bmp", "gif"])
    )
    max_file_size_mb = int(FILE_CONFIG.get("max_file_size_mb", 10))
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension not in valid_extensions:
        st.error(f"Invalid file type. Accepted formats: {', '.join(valid_extensions)}")
        return False

    if uploaded_file.size > max_file_size_mb * 1024 * 1024:
        st.error(f"File size exceeds {max_file_size_mb} MB limit")
        return False

    return True


def get_dataset_info(train_dir="data/train", val_dir="data/val"):
    """
    Get information about the dataset.
    """
    try:
        train_path = Path(train_dir)
        val_path = Path(val_dir)

        train_classes = len([d for d in train_path.iterdir() if d.is_dir()])
        val_classes = len([d for d in val_path.iterdir() if d.is_dir()])

        train_samples = sum(1 for _ in train_path.rglob("*") if _.is_file())
        val_samples = sum(1 for _ in val_path.rglob("*") if _.is_file())

        return {
            "train_classes": train_classes,
            "val_classes": val_classes,
            "train_samples": train_samples,
            "val_samples": val_samples,
        }

    except Exception as e:
        st.warning(f"Could not load dataset info: {str(e)}")
        return None
