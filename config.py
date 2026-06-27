"""
Configuration file for Plant Disease Detection System
"""

# Model Configuration
MODEL_CONFIG = {
    "img_size": 224,
    "batch_size": 32,
    "epochs": 80,
    "initial_epochs": 20,
    "learning_rate": 0.001,
    "fine_tune_learning_rate": 0.00001,
    "dropout_rate": 0.35,
    "weights": "imagenet",
    "fine_tune_at": None,
    "seed": 42,
}

# Data Augmentation Configuration
AUGMENTATION_CONFIG = {
    "rotation_range": 20,
    "zoom_range": 0.15,
    "shear_range": 0.15,
    "width_shift_range": 0.1,
    "height_shift_range": 0.1,
    "horizontal_flip": True,
    "fill_mode": "nearest",
}

# File Paths
PATHS = {
    "model": "models/plant_disease.keras",
    "history": "models/history.json",
    "labels": "labels.json",
    "class_indices": "models/class_indices.json",
    "model_metadata": "models/model_metadata.json",
    "training_log": "models/training_log.csv",
    "demo_image": "assets/demo/sample_leaf.jpg",
    "train_data": "data/train",
    "val_data": "data/val",
    "train_split_data": "data/train_split",
    "val_split_data": "data/val_split",
}

# Model Callbacks Configuration
CALLBACKS_CONFIG = {
    "early_stopping": {
        "monitor": "val_loss",
        "patience": 12,
        "min_delta": 0.0001,
        "restore_best_weights": True,
    },
    "model_checkpoint": {
        "monitor": "val_accuracy",
        "save_best_only": True,
    },
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_title": "Plant & Crop Intelligence",
    "page_icon": "🌿",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Prediction Configuration
PREDICTION_CONFIG = {
    "top_k": 3,
    "confidence_threshold": 0.3,  # 0.3 means 30%; lower predictions are marked uncertain
    "input_scale": "0_1",  # Overridden by models/model_metadata.json after retraining
}

# File Upload Configuration
FILE_CONFIG = {
    "allowed_extensions": ["jpg", "jpeg", "png"],
    "max_file_size_mb": 200,
    "required_image_size": (224, 224),
}
