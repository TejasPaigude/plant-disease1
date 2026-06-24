"""
FastAPI backend for plant disease detection
Serves predictions to React frontend
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io

from utils import (
    preprocess_image,
    load_model_cached,
    predict_top_k,
    load_label_map,
    load_training_history,
    load_class_names,
    load_model_metadata,
    get_confidence_threshold_percent,
    is_low_confidence,
)

try:
    from config import FILE_CONFIG, PATHS, PREDICTION_CONFIG
except ImportError:
    FILE_CONFIG = {}
    PATHS = {}
    PREDICTION_CONFIG = {}

app = FastAPI(title="Plant Disease Detection API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache model and labels on startup
model = None
labels = None
history = None
class_names = None
model_metadata = None


@app.on_event("startup")
async def startup_event():
    """Load model and labels on startup."""
    global model, labels, history, class_names, model_metadata
    model = load_model_cached(PATHS.get("model", "models/plant_disease.keras"))
    labels = load_label_map(PATHS.get("labels", "labels.json"))
    history = load_training_history(PATHS.get("history", "models/history.json"))
    class_names = load_class_names(
        PATHS.get("class_indices", "models/class_indices.json"),
        labels=labels,
    )
    model_metadata = load_model_metadata(
        PATHS.get("model_metadata", "models/model_metadata.json")
    )


@app.get("/api/model-info")
async def get_model_info():
    """Get model training information."""
    if not history:
        return {"error": "Model history not found"}
    
    return {
        "train_acc": f"{history['accuracy'][-1] * 100:.1f}",
        "val_acc": f"{history['val_accuracy'][-1] * 100:.1f}",
        "epochs": len(history['accuracy']),
    }


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    """Make prediction on uploaded image."""
    if model is None or not labels:
        return JSONResponse(
            status_code=500,
            content={"error": "Model or labels not found"}
        )
    
    try:
        allowed_extensions = set(
            FILE_CONFIG.get("allowed_extensions", ["jpg", "jpeg", "png", "bmp", "gif"])
        )
        max_bytes = int(FILE_CONFIG.get("max_file_size_mb", 10)) * 1024 * 1024
        file_extension = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
        if file_extension not in allowed_extensions:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported image format"},
            )

        # Read uploaded file
        contents = await file.read()
        if len(contents) > max_bytes:
            return JSONResponse(
                status_code=413,
                content={"error": "Image is larger than the configured size limit"},
            )

        image = Image.open(io.BytesIO(contents))
        
        # Preprocess image
        input_scale = (model_metadata or {}).get("input_scale", "0_1")
        input_size = (model_metadata or {}).get("input_size", 224)
        preprocessed = preprocess_image(
            image,
            img_size=(input_size, input_size),
            input_scale=input_scale,
        )
        
        if preprocessed is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Image preprocessing failed"}
            )
        
        # Get predictions
        results = predict_top_k(
            model,
            preprocessed,
            labels,
            k=int(PREDICTION_CONFIG.get("top_k", 3)),
            class_names=class_names,
        )
        
        if not results:
            return JSONResponse(
                status_code=500,
                content={"error": "Prediction failed"}
            )

        threshold = get_confidence_threshold_percent()
        uncertain = is_low_confidence(results[0]["confidence"], threshold)
        
        return {
            "main_result": {
                "display": "Uncertain prediction" if uncertain else results[0]["display"],
                "predicted_display": results[0]["display"],
                "class": results[0]["class"],
                "confidence": results[0]["confidence"],
                "is_uncertain": uncertain,
                "confidence_threshold": threshold,
                "remedy": results[0]["remedy"],
                "advisory": results[0].get("advisory", {}),
            },
            "top_predictions": [
                {
                    "class": r["class"],
                    "display": r["display"],
                    "confidence": r["confidence"],
                    "advisory": r.get("advisory", {}),
                }
                for r in results
            ],
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction error: {str(e)}"}
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "model_loaded": model is not None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
