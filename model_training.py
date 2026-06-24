"""
Accuracy-focused training script for plant disease detection.

The previous training path used a small custom CNN. This version uses
transfer learning with EfficientNetV2B0, class weighting for imbalanced
classes, two-phase training, and saved class-index metadata so inference
uses the same label order as training.
"""

import argparse
import json
import os
import random
import re
import shutil
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.callbacks import (
    Callback,
    CSVLogger,
    EarlyStopping,
    ReduceLROnPlateau,
)
from tensorflow.keras.optimizers import Adam

try:
    from config import CALLBACKS_CONFIG, MODEL_CONFIG, PATHS
except ImportError:
    CALLBACKS_CONFIG = {}
    MODEL_CONFIG = {}
    PATHS = {}


DEFAULT_MODEL_PATH = PATHS.get("model", "models/plant_disease.keras")
DEFAULT_HISTORY_PATH = PATHS.get("history", "models/history.json")
DEFAULT_LABELS_PATH = PATHS.get("labels", "labels.json")
DEFAULT_CLASS_INDICES_PATH = PATHS.get(
    "class_indices", "models/class_indices.json"
)
DEFAULT_METADATA_PATH = PATHS.get("model_metadata", "models/model_metadata.json")
DEFAULT_TRAIN_LOG_PATH = PATHS.get("training_log", "models/training_log.csv")
DEFAULT_TRAIN_DIR = PATHS.get("train_split_data", "data/train_split")
DEFAULT_VAL_DIR = PATHS.get("val_split_data", "data/val_split")
MIN_MODEL_FILE_BYTES = 1024 * 1024


def set_seed(seed):
    """Make training runs as repeatable as TensorFlow allows."""
    random.seed(seed)
    np.random.seed(seed)
    tf.keras.utils.set_random_seed(seed)


def canonicalize_class_name(class_name):
    """Normalize class names so metadata can match folder-name variants."""
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
    cleaned = re.sub(r"[^a-z0-9]+", "", cleaned)
    return cleaned


def format_class_name(class_name):
    """Create a readable display name from a dataset folder name."""
    if "___" in class_name:
        crop, disease = class_name.split("___", 1)
    else:
        crop, disease = "Plant", class_name

    crop = re.sub(r"_+", " ", crop).replace(",", ", ")
    disease = re.sub(r"_+", " ", disease)
    crop = re.sub(r"\s+", " ", crop).strip()
    disease = re.sub(r"\s+", " ", disease).strip(" _-")
    return f"{crop.title()} - {disease.title()}"


def load_existing_labels(label_path):
    """Load existing display/remedy metadata if it is available."""
    path = Path(label_path)
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_label_info(class_name, existing_labels):
    """Return display/remedy metadata for a class, with tolerant matching."""
    if class_name in existing_labels:
        return existing_labels[class_name]

    target = canonicalize_class_name(class_name)
    canonical_lookup = {
        canonicalize_class_name(key): value for key, value in existing_labels.items()
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


def count_images_by_class(data_dir, class_names):
    """Count image files per class directory."""
    valid_suffixes = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    counts = []
    for class_name in class_names:
        class_dir = Path(data_dir) / class_name
        count = sum(
            1
            for path in class_dir.iterdir()
            if path.is_file() and path.suffix.lower() in valid_suffixes
        )
        counts.append(count)
    return counts


def validate_model_file(model_path, min_bytes=MIN_MODEL_FILE_BYTES):
    """Return (is_valid, reason) after size and Keras load validation."""
    path = Path(model_path)
    if not path.exists():
        return False, f"model file does not exist: {path}"

    if not path.is_file():
        return False, f"model path is not a file: {path}"

    file_size = path.stat().st_size
    if file_size < min_bytes:
        return False, f"model file is too small ({file_size} bytes)"

    try:
        tf.keras.models.load_model(path, compile=False)
    except Exception as exc:
        return False, f"model load validation failed: {exc}"

    return True, "ok"


def safe_save_model(model, model_path, min_bytes=MIN_MODEL_FILE_BYTES):
    """
    Save a model through a validated temporary file and atomically replace target.

    This prevents a failed write from destroying the last valid checkpoint.
    """
    path = Path(model_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_name(f"{path.stem}.tmp-{os.getpid()}{path.suffix}")
    backup_path = path.with_name(f"{path.stem}.backup{path.suffix}")

    if temp_path.exists():
        temp_path.unlink()

    backup_created = False
    try:
        model.save(str(temp_path))
        is_valid, reason = validate_model_file(temp_path, min_bytes=min_bytes)
        if not is_valid:
            raise RuntimeError(f"Temporary checkpoint validation failed: {reason}")

        if path.exists():
            existing_valid, _ = validate_model_file(path, min_bytes=min_bytes)
            if existing_valid:
                shutil.copy2(path, backup_path)
                backup_created = True

        os.replace(temp_path, path)
        is_valid, reason = validate_model_file(path, min_bytes=min_bytes)
        if not is_valid:
            if backup_created:
                os.replace(backup_path, path)
            raise RuntimeError(f"Final checkpoint validation failed: {reason}")

    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


class SafeModelCheckpoint(Callback):
    """Keras callback that saves only full models using rollback-safe writes."""

    def __init__(
        self,
        filepath,
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
        min_delta=0.0,
        verbose=1,
        save_weights_only=False,
    ):
        super().__init__()
        if save_weights_only:
            raise ValueError("SafeModelCheckpoint requires save_weights_only=False.")

        self.filepath = Path(filepath)
        self.monitor = monitor
        self.mode = mode
        self.save_best_only = save_best_only
        self.min_delta = float(min_delta)
        self.verbose = verbose

        if mode not in {"max", "min"}:
            raise ValueError("SafeModelCheckpoint mode must be 'max' or 'min'.")

        self.best = -np.inf if mode == "max" else np.inf

    def _is_improvement(self, current):
        if self.mode == "max":
            return current > self.best + self.min_delta
        return current < self.best - self.min_delta

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        current = logs.get(self.monitor)
        if current is None:
            if self.verbose:
                print(
                    f"\nEpoch {epoch + 1}: monitor '{self.monitor}' is unavailable; "
                    "checkpoint not saved."
                )
            return

        current = float(current)
        should_save = not self.save_best_only or self._is_improvement(current)

        if not should_save:
            if self.verbose:
                print(
                    f"\nEpoch {epoch + 1}: {self.monitor} did not improve "
                    f"from {self.best:.5f}"
                )
            return

        previous_best = self.best
        self.best = current
        if self.verbose:
            print(
                f"\nEpoch {epoch + 1}: {self.monitor} improved "
                f"from {previous_best:.5f} to {current:.5f}, "
                f"saving model to {self.filepath}"
            )

        try:
            safe_save_model(self.model, self.filepath)
        except Exception:
            self.best = previous_best
            raise

        if self.verbose:
            print(f"\nEpoch {epoch + 1}: validated checkpoint saved to {self.filepath}")


class PlantDiseaseModel:
    """Builds and trains a transfer-learning model for plant disease detection."""

    def __init__(
        self,
        img_size=224,
        num_classes=None,
        learning_rate=1e-3,
        fine_tune_learning_rate=1e-5,
        dropout_rate=0.35,
        weights="imagenet",
    ):
        self.img_size = img_size
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.fine_tune_learning_rate = fine_tune_learning_rate
        self.dropout_rate = dropout_rate
        self.weights = weights
        self.model = None
        self.base_model = None
        self.history = None
        self.class_indices = {}
        self.class_names = []

    def build_model(self, num_classes):
        """
        Build an EfficientNetV2B0 transfer-learning classifier.

        EfficientNetV2B0 with ImageNet weights usually gives a much higher
        ceiling on PlantVillage-style image classification than a small CNN.
        """
        self.num_classes = num_classes

        inputs = layers.Input(shape=(self.img_size, self.img_size, 3), name="image")
        x = layers.RandomFlip("horizontal", name="augment_flip")(inputs)
        x = layers.RandomRotation(0.08, name="augment_rotate")(x)
        x = layers.RandomZoom(0.12, name="augment_zoom")(x)
        x = layers.RandomTranslation(0.08, 0.08, name="augment_translate")(x)
        x = layers.RandomContrast(0.12, name="augment_contrast")(x)

        self.base_model = self._create_backbone()
        self.base_model.trainable = False

        x = self.base_model(x, training=False)
        x = layers.GlobalAveragePooling2D(name="global_average_pooling")(x)
        x = layers.BatchNormalization(name="head_batch_norm")(x)
        x = layers.Dropout(self.dropout_rate, name="head_dropout")(x)
        outputs = layers.Dense(
            num_classes,
            activation="softmax",
            dtype="float32",
            name="predictions",
        )(x)

        self.model = tf.keras.Model(inputs, outputs, name="plant_disease_efficientnetv2b0")
        self._compile(self.learning_rate)
        return self.model

    def _create_backbone(self):
        """Create an EfficientNetV2B0 backbone, falling back if weights are unavailable."""
        kwargs = {
            "include_top": False,
            "weights": self.weights,
            "input_shape": (self.img_size, self.img_size, 3),
        }

        def instantiate(weights):
            kwargs["weights"] = weights
            try:
                return tf.keras.applications.EfficientNetV2B0(
                    **kwargs,
                    include_preprocessing=True,
                )
            except TypeError:
                return tf.keras.applications.EfficientNetV2B0(**kwargs)

        try:
            return instantiate(self.weights)
        except Exception as exc:
            if self.weights is None:
                raise
            print(
                "Warning: ImageNet weights could not be loaded. "
                "Training will continue from random initialization, which usually lowers accuracy."
            )
            print(f"Original weight-loading error: {exc}")
            return instantiate(None)

    def _compile(self, learning_rate):
        self.model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss="categorical_crossentropy",
            metrics=[
                "accuracy",
                tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy"),
            ],
        )

    def _make_datasets(self, train_dir, val_dir, batch_size, seed):
        train_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir,
            labels="inferred",
            label_mode="categorical",
            image_size=(self.img_size, self.img_size),
            batch_size=batch_size,
            shuffle=True,
            seed=seed,
        )

        val_ds = tf.keras.utils.image_dataset_from_directory(
            val_dir,
            labels="inferred",
            label_mode="categorical",
            image_size=(self.img_size, self.img_size),
            batch_size=batch_size,
            shuffle=False,
        )

        if train_ds.class_names != val_ds.class_names:
            raise ValueError(
                "Training and validation class folders do not match exactly. "
                "Re-run split_dataset.py or make both splits contain the same classes."
            )

        self.class_names = list(train_ds.class_names)
        self.class_indices = {name: idx for idx, name in enumerate(self.class_names)}

        autotune = tf.data.AUTOTUNE
        return train_ds.prefetch(autotune), val_ds.prefetch(autotune)

    def _compute_class_weights(self, train_dir):
        counts = count_images_by_class(train_dir, self.class_names)
        total = float(sum(counts))
        class_count = float(len(counts))

        class_weights = {}
        for idx, count in enumerate(counts):
            if count == 0:
                class_weights[idx] = 1.0
            else:
                class_weights[idx] = total / (class_count * float(count))

        print("Class weights enabled for imbalanced data.")
        return class_weights

    def _build_callbacks(self, checkpoint_path, log_path):
        Path(checkpoint_path).parent.mkdir(parents=True, exist_ok=True)
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)

        early_cfg = CALLBACKS_CONFIG.get("early_stopping", {})
        checkpoint_cfg = CALLBACKS_CONFIG.get("model_checkpoint", {})

        return [
            SafeModelCheckpoint(
                checkpoint_path,
                monitor=checkpoint_cfg.get("monitor", "val_accuracy"),
                save_best_only=checkpoint_cfg.get("save_best_only", True),
                mode="max",
                save_weights_only=checkpoint_cfg.get("save_weights_only", False),
                verbose=1,
            ),
            EarlyStopping(
                monitor=early_cfg.get("monitor", "val_loss"),
                patience=early_cfg.get("patience", 12),
                min_delta=early_cfg.get("min_delta", 1e-4),
                restore_best_weights=early_cfg.get("restore_best_weights", True),
                verbose=1,
            ),
            ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.2,
                patience=4,
                min_lr=1e-7,
                verbose=1,
            ),
            CSVLogger(log_path, append=False),
        ]

    def _unfreeze_for_fine_tuning(self, fine_tune_at=None):
        if self.base_model is None:
            raise ValueError("Backbone not built.")

        self.base_model.trainable = True

        if fine_tune_at is None:
            fine_tune_at = max(len(self.base_model.layers) - 40, 0)

        for layer in self.base_model.layers[:fine_tune_at]:
            layer.trainable = False

        for layer in self.base_model.layers:
            if isinstance(layer, layers.BatchNormalization):
                layer.trainable = False

        trainable_count = sum(1 for layer in self.base_model.layers if layer.trainable)
        print(f"Fine-tuning enabled. Trainable backbone layers: {trainable_count}")

    def train(
        self,
        train_dir,
        val_dir,
        epochs=80,
        initial_epochs=20,
        batch_size=32,
        seed=42,
        checkpoint_path=DEFAULT_MODEL_PATH,
        log_path=DEFAULT_TRAIN_LOG_PATH,
        use_class_weights=True,
        fine_tune=True,
        fine_tune_at=None,
    ):
        """Train frozen-head first, then fine-tune the best backbone layers."""
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")

        train_ds, val_ds = self._make_datasets(train_dir, val_dir, batch_size, seed)
        class_weights = (
            self._compute_class_weights(train_dir) if use_class_weights else None
        )
        callbacks = self._build_callbacks(checkpoint_path, log_path)

        print(f"Training samples: {sum(count_images_by_class(train_dir, self.class_names))}")
        print(f"Validation samples: {sum(count_images_by_class(val_dir, self.class_names))}")
        print(f"Number of classes: {len(self.class_names)}")
        print("Phase 1: training the classifier head.")

        initial_epochs = min(initial_epochs, epochs)
        histories = []
        history = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=initial_epochs,
            callbacks=callbacks,
            class_weight=class_weights,
            verbose=1,
        )
        histories.append(history.history)

        if fine_tune and epochs > initial_epochs:
            print("Phase 2: fine-tuning the pretrained backbone.")
            self._unfreeze_for_fine_tuning(fine_tune_at=fine_tune_at)
            self._compile(self.fine_tune_learning_rate)

            history = self.model.fit(
                train_ds,
                validation_data=val_ds,
                initial_epoch=initial_epochs,
                epochs=epochs,
                callbacks=callbacks,
                class_weight=class_weights,
                verbose=1,
            )
            histories.append(history.history)

        self.history = self._merge_histories(histories)
        if Path(checkpoint_path).exists():
            is_valid, reason = validate_model_file(checkpoint_path)
            if not is_valid:
                raise RuntimeError(f"Best checkpoint is invalid: {reason}")

            self.model = tf.keras.models.load_model(checkpoint_path, compile=False)
            print(f"Loaded best checkpoint from {checkpoint_path}")
        return self.history

    def _merge_histories(self, histories):
        merged = {}
        for history in histories:
            for key, values in history.items():
                merged.setdefault(key, []).extend(float(value) for value in values)
        return merged

    def save_model(self, model_path=DEFAULT_MODEL_PATH, overwrite=False):
        if self.model is None:
            raise ValueError("No model to save.")

        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)

        if model_path.exists() and not overwrite:
            is_valid, reason = validate_model_file(model_path)
            if is_valid:
                print(
                    f"Best checkpoint already exists at {model_path}; "
                    "skipping final re-save because it already passed validation."
                )
                return

            print(
                f"Warning: existing model file at {model_path} is invalid ({reason}). "
                "Attempting a safe replacement through a temporary file."
            )

        safe_save_model(self.model, model_path)
        print(f"Model saved to {model_path}")

    def save_history(self, history_path=DEFAULT_HISTORY_PATH):
        if self.history is None:
            raise ValueError("No training history to save.")

        Path(history_path).parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

        print(f"Training history saved to {history_path}")

    def save_class_indices(self, output_path=DEFAULT_CLASS_INDICES_PATH):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.class_indices, f, indent=4)

        print(f"Class indices saved to {output_path}")

    def save_label_metadata(
        self,
        output_path=DEFAULT_LABELS_PATH,
        existing_label_path=DEFAULT_LABELS_PATH,
    ):
        existing_labels = load_existing_labels(existing_label_path)
        labels = {
            class_name: resolve_label_info(class_name, existing_labels)
            for class_name in self.class_names
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(labels, f, indent=4)

        print(f"Label metadata saved to {output_path}")

    def save_metadata(self, output_path=DEFAULT_METADATA_PATH):
        metadata = {
            "architecture": "EfficientNetV2B0 transfer learning",
            "input_size": self.img_size,
            "input_scale": "raw_0_255",
            "num_classes": self.num_classes,
            "class_indices_path": DEFAULT_CLASS_INDICES_PATH,
            "top_k_metric": "top_3_accuracy",
            "notes": "Model contains its own EfficientNetV2 preprocessing. Do not divide inputs by 255 before prediction.",
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        print(f"Model metadata saved to {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Train plant disease classifier.")
    parser.add_argument("--train-dir", default=DEFAULT_TRAIN_DIR)
    parser.add_argument("--val-dir", default=DEFAULT_VAL_DIR)
    parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--history-path", default=DEFAULT_HISTORY_PATH)
    parser.add_argument("--class-indices-path", default=DEFAULT_CLASS_INDICES_PATH)
    parser.add_argument("--metadata-path", default=DEFAULT_METADATA_PATH)
    parser.add_argument("--labels-path", default=DEFAULT_LABELS_PATH)
    parser.add_argument("--training-log-path", default=DEFAULT_TRAIN_LOG_PATH)
    parser.add_argument("--img-size", type=int, default=MODEL_CONFIG.get("img_size", 224))
    parser.add_argument("--batch-size", type=int, default=MODEL_CONFIG.get("batch_size", 32))
    parser.add_argument("--epochs", type=int, default=MODEL_CONFIG.get("epochs", 80))
    parser.add_argument(
        "--initial-epochs",
        type=int,
        default=MODEL_CONFIG.get("initial_epochs", 20),
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=MODEL_CONFIG.get("learning_rate", 1e-3),
    )
    parser.add_argument(
        "--fine-tune-learning-rate",
        type=float,
        default=MODEL_CONFIG.get("fine_tune_learning_rate", 1e-5),
    )
    parser.add_argument(
        "--dropout-rate",
        type=float,
        default=MODEL_CONFIG.get("dropout_rate", 0.35),
    )
    parser.add_argument("--seed", type=int, default=MODEL_CONFIG.get("seed", 42))
    parser.add_argument(
        "--weights",
        default=MODEL_CONFIG.get("weights", "imagenet"),
        help="Use 'imagenet' for best accuracy or 'none' to train from scratch.",
    )
    parser.add_argument(
        "--fine-tune-at",
        type=int,
        default=MODEL_CONFIG.get("fine_tune_at"),
        help="Backbone layer index where fine-tuning starts.",
    )
    parser.add_argument("--no-class-weights", action="store_true")
    parser.add_argument("--no-fine-tune", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    weights = None if str(args.weights).lower() == "none" else args.weights

    set_seed(args.seed)

    if not os.path.exists(args.train_dir) or not os.path.exists(args.val_dir):
        print("Error: Training or validation data directory not found.")
        print(f"Expected train directory: {args.train_dir}")
        print(f"Expected validation directory: {args.val_dir}")
        return

    num_classes = len(
        [
            d
            for d in os.listdir(args.train_dir)
            if os.path.isdir(os.path.join(args.train_dir, d))
        ]
    )
    if num_classes == 0:
        print(f"Error: No class folders found in {args.train_dir}")
        return

    print(f"Found {num_classes} disease classes")
    print("Building EfficientNetV2B0 transfer-learning model...")

    model_trainer = PlantDiseaseModel(
        img_size=args.img_size,
        num_classes=num_classes,
        learning_rate=args.learning_rate,
        fine_tune_learning_rate=args.fine_tune_learning_rate,
        dropout_rate=args.dropout_rate,
        weights=weights,
    )

    model_trainer.build_model(num_classes)
    model_trainer.model.summary()

    history = model_trainer.train(
        train_dir=args.train_dir,
        val_dir=args.val_dir,
        epochs=args.epochs,
        initial_epochs=args.initial_epochs,
        batch_size=args.batch_size,
        seed=args.seed,
        checkpoint_path=args.model_path,
        log_path=args.training_log_path,
        use_class_weights=not args.no_class_weights,
        fine_tune=not args.no_fine_tune,
        fine_tune_at=args.fine_tune_at,
    )

    print("Saving model artifacts...")
    model_trainer.save_history(args.history_path)
    model_trainer.save_class_indices(args.class_indices_path)
    model_trainer.save_label_metadata(args.labels_path, args.labels_path)
    model_trainer.save_metadata(args.metadata_path)
    model_trainer.save_model(args.model_path)

    if history:
        print("Training complete!")
        print(f"Best validation accuracy: {max(history.get('val_accuracy', [0])):.4f}")
        print(f"Best top-3 validation accuracy: {max(history.get('val_top_3_accuracy', [0])):.4f}")
        print(f"Final validation loss: {history.get('val_loss', [0])[-1]:.4f}")


if __name__ == "__main__":
    main()
