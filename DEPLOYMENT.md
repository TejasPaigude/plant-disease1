# Streamlit Deployment Guide

Current target: Streamlit Community Cloud.

## Required Files

```text
app.py
advisory.py
config.py
utils.py
components/
labels.json
models/plant_disease.keras
models/class_indices.json
models/model_metadata.json
models/history.json
requirements.txt
runtime.txt
.streamlit/config.toml
```

The `data/` folder is not required for inference deployment and should not be committed.

## Deploy On Streamlit Community Cloud

1. Push the project to GitHub.
2. Confirm `requirements.txt` and `runtime.txt` are in the repository root.
3. Confirm `runtime.txt` contains:

```text
python-3.11
```

4. In Streamlit Community Cloud, select the repository.
5. Set the main file path to:

```text
app.py
```

6. Deploy and inspect the app logs.

## Streamlit Failure Checklist

Check these before changing application code:

- Python version mismatch
- TensorFlow wheel compatibility
- Dependency conflict in `requirements.txt`
- Missing `models/plant_disease.keras`
- Repository size too large because `data/`, `venv/`, or `frontend/node_modules/` is committed
- Startup timeout while TensorFlow loads
- Memory limit exceeded during model import

## Local Verification

```powershell
python tests\smoke_test.py
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Known Limitation

Remote Streamlit deployment cannot be verified from Codex without access to the target Streamlit/GitHub account. The repository is prepared for Streamlit deployment; final cloud validation must be done from the hosting dashboard.
