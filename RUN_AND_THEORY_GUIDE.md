# Plant Disease Detection: Run Guide and Updated Theory

This guide reflects the updated high-accuracy training pipeline based on
EfficientNetV2 transfer learning.

## 1. Open The Project

Use PowerShell or Command Prompt:

```bat
cd /d "C:\Users\Tejaspaigude987\Desktop\Final Year Project\Project\plant-disease-detection-main (1)\plant-disease-detection-main"
```

Activate the Python virtual environment:

```bat
venv\Scripts\activate
```

Install or refresh Python dependencies:

```bat
python -m pip install -r requirements.txt
```

## 2. Dataset Folders

The training script expects this structure:

```text
data/
  train_split/
    Apple___Apple_scab/
    Apple___Black_rot/
    ...
  val_split/
    Apple___Apple_scab/
    Apple___Black_rot/
    ...
```

Your current dataset contains:

- Training images: 8691
- Validation images: 2158
- Classes: 38

If you ever need to rebuild the split from `data/train`, run:

```bat
python split_dataset.py
```

## 3. Train The High-Accuracy Model

Recommended Windows command:

```bat
train_high_accuracy.bat
```

Equivalent manual command:

```bat
python model_training.py --epochs 80 --initial-epochs 20 --batch-size 32
```

The first run may download ImageNet EfficientNetV2 weights. Keep internet on
for the first training run if the weights are not already cached.

Training outputs:

```text
models/plant_disease.keras
models/history.json
models/class_indices.json
models/model_metadata.json
models/training_log.csv
labels.json
```

## 4. Evaluate Real Accuracy

After training completes, run:

```bat
python evaluate_model.py
```

This prints the real validation metrics, for example:

```text
accuracy: 0.9650
loss: 0.1200
top_3_accuracy: 0.9950
```

Do not rely on hard-coded UI text for accuracy. The evaluator and
`models/history.json` are the correct sources.

Important accuracy note:

- The current saved model file must be retrained before final submission.
- The previous history file claimed much higher validation accuracy than the
  currently saved model produced during direct evaluation.
- Final report accuracy should be written only after running
  `python evaluate_model.py` on the newly trained model.

## 5. Run The Streamlit UI

Streamlit is the simplest UI for demonstration:

```bat
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

Upload a leaf image and view:

- Top prediction
- Confidence score
- Treatment recommendation
- Top-3 prediction list
- Uncertainty warning when confidence is below the configured threshold
- Grad-CAM focus visualization
- Smart crop advisory tabs

## 6. Run The FastAPI Backend

Install dependencies first:

```bat
python -m pip install -r requirements.txt
```

Start the backend:

```bat
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```text
http://localhost:8000/api/health
```

Model info:

```text
http://localhost:8000/api/model-info
```

The React frontend calls this backend at `http://localhost:8000`.

## 7. Run The React Frontend

Open a second terminal:

```bat
cd /d "C:\Users\Tejaspaigude987\Desktop\Final Year Project\Project\plant-disease-detection-main (1)\plant-disease-detection-main\frontend"
npm install
npm start
```

Then open:

```text
http://localhost:3000
```

For a production build:

```bat
npm run build
```

## 8. Updated Theory

### Problem Statement

Plant disease identification from leaf images is a multi-class image
classification problem. Each input image must be assigned to one of 38 crop or
disease categories, such as healthy leaves, black rot, powdery mildew, leaf
scorch, early blight, late blight, bacterial spot, and viral diseases.

Manual visual inspection can be slow and dependent on expert availability.
The system automates first-level detection by using deep learning to recognize
visual disease patterns such as spots, rust, mold, discoloration, blight, and
leaf deformation.

### Previous Approach

The earlier implementation used a custom CNN with Conv2D, pooling,
batch-normalization, dropout, and dense layers. A custom CNN can learn useful
features, but it often needs much more data and training time to reach high
accuracy. The saved training history showed unstable validation performance,
with validation accuracy peaking around 73.96%.

### Updated Approach

The updated training pipeline uses EfficientNetV2B0 transfer learning.
EfficientNetV2 has already learned strong image features from ImageNet, such
as edges, textures, shapes, colors, and object parts. Instead of learning all
visual features from scratch, the project reuses this pretrained backbone and
learns a new 38-class classification head for plant diseases.

### Model Architecture In Simple Words

The model has three main parts:

1. Input layer: accepts one RGB image resized to 224 x 224 pixels.
2. EfficientNetV2B0 backbone: extracts visual features from the image, such as
   edges, leaf texture, spots, color changes, rust patterns, mildew-like
   regions, and diseased areas.
3. Classification head: converts the extracted features into probabilities for
   the 38 disease classes.

The final layer is a softmax layer. Softmax converts raw model scores into
probabilities that add up to 1. For example, the model may output:

```text
Tomato___Late_blight: 0.91
Tomato___Early_blight: 0.06
Tomato___healthy: 0.02
Other classes combined: 0.01
```

The app displays the class with the highest probability as the main prediction
and also shows the top 3 classes.

### Why Transfer Learning Improves Accuracy

Transfer learning improves performance because the model begins with useful
general-purpose image features. The classifier only needs to adapt those
features to plant leaf disease classes. This usually improves convergence,
reduces overfitting, and gives higher validation accuracy than a small CNN
trained from scratch.

### Training Strategy

The training is performed in two phases:

1. Classifier-head training: EfficientNetV2 is frozen and only the final
   classification layers are trained.
2. Fine-tuning: the upper layers of EfficientNetV2 are unfrozen and trained
   with a smaller learning rate so the visual features adapt to leaf disease
   images without destroying pretrained knowledge.

Exact training defaults:

| Setting | Value | Meaning |
|---|---:|---|
| Image size | 224 x 224 | Every image is resized before training and prediction. |
| Batch size | 32 | Training processes 32 images at a time. |
| Total epochs | 80 | Maximum training passes over the dataset. |
| Initial epochs | 20 | First phase trains only the classifier head. |
| Initial learning rate | 0.001 | Learning rate for classifier-head training. |
| Fine-tune learning rate | 0.00001 | Smaller learning rate for fine-tuning pretrained layers. |
| Dropout | 0.35 | Reduces overfitting in the classifier head. |
| Weights | ImageNet | Uses pretrained visual features. |
| Random seed | 42 | Helps make training more repeatable. |

### Data Augmentation

The model uses augmentation to improve generalization:

- Horizontal flipping
- Small rotations
- Zoom changes
- Width and height translation
- Contrast variation

These transformations simulate natural image variation caused by different
camera positions, lighting conditions, and leaf placement.

### Class Imbalance Handling

The dataset is imbalanced. Some classes have many images, while others have
very few images. For example, some classes have hundreds of samples while
`Potato___healthy` has very few. The updated training script computes class
weights so minority classes receive more importance during training.

The class weight formula is:

```text
class_weight = total_training_images / (number_of_classes * images_in_that_class)
```

This means a class with fewer images receives a larger training weight, and a
class with many images receives a smaller weight. This helps the model avoid
learning only the most common classes.

### Training Callbacks and Stopping Rules

The training script uses callbacks to save the best model and avoid wasting
epochs when improvement stops:

| Callback | Setting | Purpose |
|---|---|---|
| SafeModelCheckpoint | monitor `val_accuracy` | Saves the best model to `models/plant_disease.keras` using a temporary file, load validation, and rollback protection. |
| EarlyStopping | monitor `val_loss`, patience `12`, min_delta `0.0001` | Stops training if validation loss stops improving. |
| Restore best weights | `True` | Keeps the best validation model, not just the final epoch model. |
| ReduceLROnPlateau | monitor `val_loss`, factor `0.2`, patience `4`, min_lr `1e-7` | Reduces learning rate when validation loss gets stuck. |
| CSVLogger | `models/training_log.csv` | Saves epoch-by-epoch metrics. |

### Prediction Pipeline

During inference:

1. The uploaded image is converted to RGB.
2. The image is resized to 224 x 224.
3. Preprocessing follows `models/model_metadata.json`.
4. The model outputs probabilities for 38 classes.
5. The highest probability class is returned as the main prediction.
6. The top 3 classes are displayed with confidence scores.
7. Confidence is compared with the configured threshold in `config.py`.
8. Disease remedies are loaded from `labels.json`.
9. `advisory.py` generates crop-care guidance for the predicted class.
10. Grad-CAM creates a heatmap overlay from the EfficientNetV2B0 feature layer.

### Grad-CAM Explainability

Grad-CAM highlights the image regions that most influenced the predicted
class. In this project it uses the nested EfficientNetV2B0 backbone inside
`models/plant_disease.keras`, finds the last spatial feature layer, computes
class-specific gradients, and overlays a red/yellow heatmap on the uploaded
image.

If Grad-CAM fails, prediction still works and the UI shows a safe fallback
message. A useful Grad-CAM result should focus mainly on leaf tissue or visible
lesions rather than the background.

### Smart Crop Advisory System

The advisory engine is implemented in `advisory.py`. For every predicted class
it returns disease description, symptoms, causes, prevention methods,
treatment recommendations, pesticide suggestions, fertilizer suggestions,
organic treatments, irrigation advice, environmental triggers, and crop-care
guidance.

Streamlit renders this advisory in tabs. FastAPI includes it in
`main_result.advisory` and each `top_predictions[].advisory` item.

### Prediction Thresholds and Confidence Rules

These are the important thresholds and interpretation rules in the current
code:

| Area | Current value | What it means |
|---|---:|---|
| Number of returned predictions | Top 3 | The app displays the three most likely classes. |
| Main prediction | Highest softmax probability | The class with the largest probability is shown first. |
| Config confidence threshold | 0.3, meaning 30% | Streamlit and FastAPI mark predictions below this as uncertain. |
| File upload helper limit | 10 MB | Enforced by Streamlit validation and FastAPI upload validation. |
| Input image size | 224 x 224 | Required by training and prediction. |

Important: the model always returns the top prediction even if confidence is
low, but the UI/API label it as uncertain to prevent misleading diagnosis.
Low-confidence cases should be verified by an agricultural expert or by
testing with a clearer leaf image.

Recommended interpretation:

| Confidence | How to interpret |
|---:|---|
| 90% to 100% | Strong prediction if the uploaded image is clear and leaf-focused. |
| 80% to 89% | Good prediction, but still check the top-3 list. |
| 60% to 79% | Moderate confidence; compare symptoms manually. |
| Below 60% | Uncertain prediction; use a better image or expert confirmation. |

### Preprocessing Rules

The preprocessing step depends on `models/model_metadata.json`:

| Metadata value | Behavior |
|---|---|
| `input_scale: "0_1"` | Divide pixel values by 255. Used for the legacy custom CNN. |
| `input_scale: "raw_0_255"` | Keep pixel values from 0 to 255. Used after EfficientNetV2 retraining because the model contains its own preprocessing. |
| `input_scale: "minus_1_1"` | Scale pixels to -1 to 1. Supported for MobileNet-style models if needed later. |

This metadata is important because a model trained with one preprocessing rule
can perform badly if prediction uses a different rule.

### Class Mapping Fix

The updated system saves `models/class_indices.json`. This is important
because model output index order must match class folder order. Without this
mapping, the model can predict the correct output index but the app may display
the wrong disease name. The fix improves prediction correctness and avoids
misleading treatment recommendations.

Example:

```text
Model output index 0 -> Apple___Apple_scab
Model output index 1 -> Apple___Black_rot
...
Model output index 37 -> Tomato___healthy
```

The app uses this mapping before it reads display names and remedies from
`labels.json`.

### Evaluation Metrics

The training and evaluation scripts report these metrics:

| Metric | Meaning |
|---|---|
| Accuracy | Percentage of validation images where the top prediction is correct. |
| Loss | Error value used for training; lower is usually better. |
| Top-3 accuracy | Percentage of validation images where the correct class appears anywhere in the top 3 predictions. |
| Validation accuracy | Accuracy on unseen validation images; this is more important than training accuracy. |

For project reporting, use validation accuracy and top-3 validation accuracy
after retraining. Training accuracy alone is not enough because it can be high
even when the model overfits.

### Expected Accuracy

The previous saved model is not reliable and must be retrained. With the new
pipeline, a realistic target on a clean PlantVillage-style validation split is
usually around 95% to 98%, sometimes near 99%. A guaranteed 100% is not a
healthy target because it may indicate overfitting or data leakage.

If validation accuracy is much lower than expected after retraining, check:

- Whether all 38 class folders exist in both `train_split` and `val_split`.
- Whether `models/model_metadata.json` matches the trained model.
- Whether `models/class_indices.json` was regenerated during training.
- Whether the validation images are from the same class naming structure.
- Whether the uploaded test image is a clean, leaf-focused image.

For final reporting, always use the accuracy printed by:

```bat
python evaluate_model.py
```

## 9. Recommended Demo Order

1. Start with `python evaluate_model.py` to show baseline metrics.
2. Run `train_high_accuracy.bat` to train the improved model.
3. Run `python evaluate_model.py` again to show improved accuracy.
4. Start Streamlit with `streamlit run app.py`.
5. Upload sample leaf images and explain top-3 predictions.
6. Optionally start FastAPI and React for a separate frontend/backend demo.
