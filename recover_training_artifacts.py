"""
Recover non-weight training artifacts after an interrupted final save.

This script does not recreate model weights. It rebuilds metadata, class
indices, and history JSON from the dataset folders and CSV training log so
the next training/evaluation run uses the correct preprocessing contract.
"""

import csv
import json
from pathlib import Path

try:
    from config import MODEL_CONFIG, PATHS
except ImportError:
    MODEL_CONFIG = {}
    PATHS = {}


TRAIN_DIR = Path(PATHS.get("train_split_data", "data/train_split"))
MODEL_PATH = Path(PATHS.get("model", "models/plant_disease.keras"))
HISTORY_PATH = Path(PATHS.get("history", "models/history.json"))
CLASS_INDICES_PATH = Path(PATHS.get("class_indices", "models/class_indices.json"))
METADATA_PATH = Path(PATHS.get("model_metadata", "models/model_metadata.json"))
TRAINING_LOG_PATH = Path(PATHS.get("training_log", "models/training_log.csv"))


def get_class_indices(train_dir):
    if not train_dir.exists():
        raise FileNotFoundError(f"Training directory not found: {train_dir}")

    class_names = sorted(path.name for path in train_dir.iterdir() if path.is_dir())
    if not class_names:
        raise ValueError(f"No class folders found in {train_dir}")

    return {class_name: index for index, class_name in enumerate(class_names)}


def recover_history(log_path):
    if not log_path.exists():
        print(f"Training log not found, skipping history recovery: {log_path}")
        return {}

    with log_path.open("r", encoding="utf-8", newline="") as f:
        rows = [row for row in csv.DictReader(f) if any(row.values())]

    history = {}
    for row in rows:
        for key, value in row.items():
            if key == "epoch" or value in ("", None):
                continue
            try:
                history.setdefault(key, []).append(float(value))
            except ValueError:
                continue

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    print(f"Recovered history from {log_path} to {HISTORY_PATH}")
    return history


def write_class_indices(class_indices):
    CLASS_INDICES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CLASS_INDICES_PATH.open("w", encoding="utf-8") as f:
        json.dump(class_indices, f, indent=4)

    print(f"Wrote class indices to {CLASS_INDICES_PATH}")


def write_metadata(class_indices):
    metadata = {
        "architecture": "EfficientNetV2B0 transfer learning",
        "input_size": MODEL_CONFIG.get("img_size", 224),
        "input_scale": "raw_0_255",
        "num_classes": len(class_indices),
        "class_indices_path": str(CLASS_INDICES_PATH).replace("\\", "/"),
        "top_k_metric": "top_3_accuracy",
        "notes": "Model contains its own EfficientNetV2 preprocessing. Do not divide inputs by 255 before prediction.",
    }

    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"Wrote model metadata to {METADATA_PATH}")


def summarize_model_file():
    if not MODEL_PATH.exists():
        print(f"Model file is missing: {MODEL_PATH}")
        return

    size = MODEL_PATH.stat().st_size
    print(f"Model file: {MODEL_PATH} ({size} bytes)")
    if size < 1024 * 1024:
        print(
            "WARNING: This model file is too small for EfficientNetV2B0 and is probably corrupted. "
            "Retraining is required unless another valid checkpoint exists."
        )


def main():
    class_indices = get_class_indices(TRAIN_DIR)
    write_class_indices(class_indices)
    history = recover_history(TRAINING_LOG_PATH)
    write_metadata(class_indices)
    summarize_model_file()

    if history.get("val_accuracy"):
        print(f"Best logged validation accuracy: {max(history['val_accuracy']):.4f}")
    if history.get("val_top_3_accuracy"):
        print(
            f"Best logged top-3 validation accuracy: "
            f"{max(history['val_top_3_accuracy']):.4f}"
        )


if __name__ == "__main__":
    main()
