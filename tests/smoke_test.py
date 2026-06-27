"""Local smoke test for model loading, prediction, and Grad-CAM."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image

from config import PATHS, PREDICTION_CONFIG
from utils import (
    generate_gradcam,
    load_class_names,
    load_label_map,
    load_model_metadata,
    predict_top_k,
    preprocess_image,
    resolve_model_path,
)
import tensorflow as tf


def _find_sample_image():
    val_dir = ROOT / PATHS.get("val_split_data", "data/val_split")
    if not val_dir.exists():
        return None

    for pattern in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
        sample = next(val_dir.rglob(pattern), None)
        if sample:
            return sample
    return None


def main():
    model_path, failure_reason = resolve_model_path(
        ROOT / PATHS.get("model", "models/plant_disease.keras")
    )
    if model_path is None:
        raise FileNotFoundError(f"Model unavailable: {failure_reason}")

    labels = load_label_map(ROOT / PATHS.get("labels", "labels.json"))
    metadata = load_model_metadata(ROOT / PATHS.get("model_metadata", "models/model_metadata.json"))
    class_names = load_class_names(
        ROOT / PATHS.get("class_indices", "models/class_indices.json"),
        labels=labels,
    )
    if not labels:
        raise RuntimeError("labels.json is empty or unavailable")
    if not class_names:
        raise RuntimeError("class index mapping is empty or unavailable")

    model = tf.keras.models.load_model(model_path, compile=False)
    print(f"Loaded model: {model_path}")
    print(f"Classes: {len(class_names)}")

    sample = _find_sample_image()
    if sample is None:
        print("No validation image found; skipping prediction and Grad-CAM smoke test.")
        return

    image = Image.open(sample).convert("RGB")
    input_size = int(metadata.get("input_size", 224))
    input_scale = metadata.get("input_scale", PREDICTION_CONFIG.get("input_scale", "0_1"))
    array = preprocess_image(image, img_size=(input_size, input_size), input_scale=input_scale)
    results = predict_top_k(
        model,
        array,
        labels,
        k=int(PREDICTION_CONFIG.get("top_k", 3)),
        class_names=class_names,
    )
    if not results:
        raise RuntimeError("Prediction smoke test failed")

    top = results[0]
    print(f"Sample: {sample}")
    print(f"Prediction: {top['display']} ({top['confidence']:.2f}%)")

    cam = generate_gradcam(model, array, image, class_index=top.get("index"))
    if cam:
        print(f"Grad-CAM generated from layer: {cam['layer_name']}")
    else:
        print("Grad-CAM skipped or unavailable; prediction path is still valid.")


if __name__ == "__main__":
    main()
