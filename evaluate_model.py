"""
Evaluate the saved plant disease model on the validation split.
"""

import argparse

import tensorflow as tf

from utils import load_model_metadata, resolve_model_path

try:
    from config import MODEL_CONFIG, PATHS
except ImportError:
    MODEL_CONFIG = {}
    PATHS = {}


def preprocess_batch(images, labels, input_scale):
    images = tf.cast(images, tf.float32)
    if input_scale == "0_1":
        images = images / 255.0
    elif input_scale == "minus_1_1":
        images = (images / 127.5) - 1.0
    return images, labels


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate plant disease model.")
    parser.add_argument("--model-path", default=PATHS.get("model", "models/plant_disease.keras"))
    parser.add_argument(
        "--metadata-path",
        default=PATHS.get("model_metadata", "models/model_metadata.json"),
    )
    parser.add_argument("--val-dir", default=PATHS.get("val_split_data", "data/val_split"))
    parser.add_argument("--batch-size", type=int, default=MODEL_CONFIG.get("batch_size", 32))
    return parser.parse_args()


def main():
    args = parse_args()
    metadata = load_model_metadata(args.metadata_path)
    input_size = int(metadata.get("input_size", 224))
    input_scale = metadata.get("input_scale", "0_1")

    model_path, failure_reason = resolve_model_path(args.model_path)
    if model_path is None:
        raise FileNotFoundError(f"Valid model not found. Checked: {failure_reason}")

    model = tf.keras.models.load_model(model_path, compile=False)
    val_ds = tf.keras.utils.image_dataset_from_directory(
        args.val_dir,
        labels="inferred",
        label_mode="categorical",
        image_size=(input_size, input_size),
        batch_size=args.batch_size,
        shuffle=False,
    )

    output_classes = int(model.output_shape[-1])
    if output_classes != len(val_ds.class_names):
        raise ValueError(
            "Class count mismatch: model outputs "
            f"{output_classes} classes but validation data has {len(val_ds.class_names)}."
        )

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy"),
        ],
    )

    val_ds = val_ds.map(
        lambda images, labels: preprocess_batch(images, labels, input_scale),
        num_parallel_calls=tf.data.AUTOTUNE,
    ).prefetch(tf.data.AUTOTUNE)

    results = model.evaluate(val_ds, verbose=1, return_dict=True)
    print("\nValidation metrics")
    for name, value in results.items():
        print(f"{name}: {value:.4f}")


if __name__ == "__main__":
    main()
