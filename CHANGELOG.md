# Changelog

## 2.0.0 - Premium UI and Deployment Readiness

- Rebuilt Streamlit UI into a premium responsive dark dashboard.
- Split UI into reusable modules under `components/`.
- Added product-style hero, sidebar, metric cards, upload panel, prediction cards, Grad-CAM section, advisory tabs, and footer.
- Preserved existing model loading, preprocessing, prediction, Grad-CAM, advisory, and FastAPI behavior.
- Added `.streamlit/config.toml` for consistent hosted styling.
- Added Streamlit Community Cloud deployment configuration.
- Reduced `requirements.txt` to the runtime packages used by the application.
- Added `.gitignore` and `.gitattributes` for safer deployment packaging.
- Added `tests/smoke_test.py` for model, prediction, and Grad-CAM sanity checks.
