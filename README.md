# Plant & Crop Intelligence

Premium AI plant disease detection and smart crop advisory system built with Streamlit, TensorFlow/Keras, EfficientNetV2B0, and FastAPI.

The application detects plant diseases from leaf images, reports confidence and top alternatives, shows Grad-CAM visual explanations, and provides crop-care guidance including treatment, prevention, irrigation, fertilizer, pesticide, and organic management suggestions.

## Key Features

- Modern Streamlit interface with responsive dark SaaS-style layout
- Native Keras model artifact: `models/plant_disease.keras`
- EfficientNetV2B0 transfer-learning inference path
- 38 PlantVillage disease classes
- Top-3 prediction candidates with confidence scores
- Configurable uncertainty threshold from `config.py`
- Grad-CAM heatmap overlay for explainability
- Smart agricultural advisory for every predicted class
- FastAPI backend with `/api/health`, `/api/model-info`, and `/api/predict`
- Streamlit Community Cloud deployment files

## Project Structure

```text
app.py                         Streamlit app entry point
api.py                         FastAPI backend
advisory.py                    Disease advisory generation
config.py                      Paths, model settings, thresholds, upload limits
utils.py                       Model loading, preprocessing, prediction, Grad-CAM
components/                    Reusable Streamlit UI components
  hero.py                      Hero and sidebar
  stats.py                     Model/system metric cards
  upload.py                    Upload and image preview panels
  prediction.py                Prediction, uncertainty, top-k, Grad-CAM panels
  recommendations.py           Advisory tabs and cards
  footer.py                    Footer
  styles.py                    Central CSS theme
models/
  plant_disease.keras          Production model artifact
  class_indices.json           Output-index to class-name mapping
  model_metadata.json          Input size and preprocessing scale
  history.json                 Training metrics
labels.json                    Display names and base remedies
tests/smoke_test.py            Local sanity check
DEPLOYMENT.md                  Streamlit deployment guide
CHANGELOG.md                   Project changes
```

## Setup

```powershell
cd "C:\Users\Tejaspaigude987\Desktop\Final Year Project\Project\plant-disease-detection-main (1)\plant-disease-detection-main"
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run Streamlit UI

```powershell
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Run FastAPI Backend

```powershell
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:

```text
GET  /api/health
GET  /api/model-info
POST /api/predict
```

`POST /api/predict` expects a form field named `file` containing an image.

## Train Model

```powershell
python model_training.py --epochs 80 --initial-epochs 20 --batch-size 32
```

Training outputs:

```text
models/plant_disease.keras
models/class_indices.json
models/model_metadata.json
models/history.json
models/training_log.csv
```

## Evaluate Model

```powershell
python evaluate_model.py
```

The final reported accuracy should come from this evaluator or from a held-out test set, not from the UI display alone.

## How Prediction Works

1. The uploaded image is validated for extension and file size.
2. The image is converted to RGB and resized to the model input size from `models/model_metadata.json`.
3. Preprocessing uses the same input scale saved during training, usually `0_1`.
4. `models/plant_disease.keras` returns class probabilities.
5. `models/class_indices.json` maps each output index to the correct disease class.
6. The app returns the top prediction plus top-3 alternatives.
7. If confidence is below the configured threshold, the result is marked uncertain.
8. Grad-CAM generates a heatmap from the model backbone to show regions that influenced the result.
9. The advisory system generates practical crop guidance for the predicted class.

## Confidence Threshold

`config.py` controls uncertainty handling:

```python
PREDICTION_CONFIG = {
    "top_k": 3,
    "confidence_threshold": 0.3,
}
```

`0.3` means 30%. Predictions below this threshold are displayed as uncertain so the system does not overstate low-confidence results.

## Grad-CAM Explainability

Grad-CAM uses the final spatial layer inside the EfficientNet-style backbone. The app overlays the heatmap on the original image:

- Red/yellow regions had stronger influence on the predicted class.
- If Grad-CAM fails, prediction still works and the app shows a safe fallback message.
- Grad-CAM is a visual explanation aid, not proof of disease presence.

## Advisory System

`advisory.py` creates advisory content for every class:

- Description
- Symptoms
- Causes
- Environmental triggers
- Prevention
- Treatment
- Pesticide suggestions
- Fertilizer suggestions
- Organic treatment options
- Irrigation advice
- Crop-care guidance

The recommendations are decision support. Severe field cases should be confirmed with a local agricultural expert.

## Local Smoke Test

```powershell
python tests\smoke_test.py
```

The smoke test validates model loading, metadata, class mapping, prediction, and Grad-CAM when a validation image is available.

## Deployment

See `DEPLOYMENT.md`.

Current target: Streamlit Community Cloud.

Important: training data should remain local and is ignored by `.gitignore`. The deployed app needs the model files in `models/`, not the full dataset.

## Troubleshooting

If the model does not load:

- Confirm `models/plant_disease.keras` exists.
- Confirm the file is not zero bytes or partially copied.
- Confirm TensorFlow and Python versions match `requirements.txt` and `runtime.txt`.
- Run `python tests\smoke_test.py`.

If predictions look wrong:

- Confirm `models/class_indices.json` matches the trained model.
- Confirm `models/model_metadata.json` uses the same preprocessing scale as training.
- Re-run `python evaluate_model.py` on `data/val_split`.

If deployment fails:

- Confirm `requirements.txt` is in the repository root.
- Confirm large local folders such as `data/`, `venv/`, and `frontend/node_modules/` are not committed.
- If TensorFlow cannot install on Streamlit Community Cloud, document the exact log error before preparing a fallback platform.
