# Plant Disease Detection and Smart Crop Advisory System

AI agricultural assistant for plant disease detection, confidence analysis, Grad-CAM explainability, and crop-care recommendations.

## Overview

This project uses an EfficientNetV2B0 transfer-learning model saved in native Keras format at `models/plant_disease.keras`. The system includes:

- Streamlit UI for leaf-image upload, prediction, confidence display, Grad-CAM visualization, and advisory panels
- FastAPI backend for prediction and model information endpoints
- EfficientNetV2B0 training pipeline with checkpoint validation and rollback-safe saving
- Metadata-driven preprocessing so training and inference stay consistent
- Class-index mapping so prediction outputs match the correct disease labels

## Features

- Disease classification across 38 PlantVillage classes
- Top-3 predictions with confidence scores
- Configurable uncertainty threshold from `config.py`
- Grad-CAM heatmap overlay showing where the model focused
- Smart advisory for disease description, symptoms, causes, prevention, treatment, pesticide guidance, fertilizer guidance, organic options, irrigation advice, environmental triggers, and crop-care guidance
- FastAPI response includes advisory and uncertainty fields
- Native `.keras` model format for Keras 3 compatibility

## Project Structure

```text
app.py                       Streamlit UI
api.py                       FastAPI backend
advisory.py                  Agricultural advisory generator
config.py                    Paths, model settings, thresholds
model_training.py            EfficientNetV2B0 training pipeline
evaluate_model.py            Validation evaluator
utils.py                     Inference, preprocessing, Grad-CAM, model loading
labels.json                  Display names and base remedies
models/plant_disease.keras   Trained model
models/history.json          Training history
models/class_indices.json    Model output index mapping
models/model_metadata.json   Preprocessing metadata
```

## Installation

```powershell
cd "C:\Users\Tejaspaigude987\Desktop\Final Year Project\Project\plant-disease-detection-main (1)\plant-disease-detection-main"
venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Train

Recommended:

```powershell
python model_training.py --epochs 80 --initial-epochs 20 --batch-size 32
```

Or:

```powershell
train_high_accuracy.bat
```

Training outputs:

```text
models/plant_disease.keras
models/history.json
models/class_indices.json
models/model_metadata.json
models/training_log.csv
```

## Evaluate

```powershell
python evaluate_model.py
```

Use this command for the final reported validation accuracy.

## Run Streamlit UI

```powershell
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

The UI shows the uploaded image, primary prediction, top-3 predictions, confidence bars, uncertainty warnings, Grad-CAM overlay, and crop advisory tabs.

## Run FastAPI Backend

```powershell
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Health:

```text
http://localhost:8000/api/health
```

Model info:

```text
http://localhost:8000/api/model-info
```

Prediction endpoint:

```text
POST http://localhost:8000/api/predict
Form field: file=<image>
```

Response includes:

```json
{
  "main_result": {
    "display": "Tomato - Late Blight",
    "predicted_display": "Tomato - Late Blight",
    "class": "Tomato___Late_blight",
    "confidence": 91.2,
    "is_uncertain": false,
    "confidence_threshold": 30.0,
    "remedy": "Treatment recommendation",
    "advisory": {}
  },
  "top_predictions": []
}
```

## Confidence Threshold

`config.py` contains:

```python
PREDICTION_CONFIG = {
    "top_k": 3,
    "confidence_threshold": 0.3,
}
```

`0.3` means 30%. If the top prediction is below this threshold, Streamlit and FastAPI mark the result as uncertain instead of presenting it as a fully trusted diagnosis.

## Grad-CAM

Grad-CAM is generated from the last spatial feature layer inside the nested EfficientNetV2B0 backbone. The app overlays a red/yellow heatmap on the uploaded image so users can see the leaf regions that most influenced the prediction.

If Grad-CAM fails, prediction still works and the UI shows a safe fallback message.

## Advisory System

`advisory.py` generates practical guidance for every class name. Each advisory includes:

- Disease description
- Symptoms
- Causes
- Prevention methods
- Treatment recommendations
- Pesticide suggestions
- Fertilizer suggestions
- Organic treatments
- Irrigation advice
- Environmental triggers
- Crop-care guidance

The guidance is decision support only. Severe cases should be confirmed with a local agricultural expert.

## Troubleshooting

If model loading fails:

```powershell
python evaluate_model.py
```

Then verify:

- `models/plant_disease.keras` exists
- `models/model_metadata.json` uses the correct preprocessing rule
- `models/class_indices.json` has 38 classes
- TensorFlow and Keras versions match the environment

If Grad-CAM is unavailable:

- Confirm the loaded model is the EfficientNetV2B0 transfer-learning model
- Upload a clear leaf-focused image
- Prediction can still be used without the heatmap

## More Details

See:

```text
RUN_AND_THEORY_GUIDE.md
QUICK_REFERENCE.txt
```

Last updated: May 2026
