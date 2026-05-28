# WEBSITE

This repository contains a Flask-based website with a front-end and local data/models.

## Contents

- `app.py` — Flask application entrypoint
- `index.html` — website markup
- `style.css` — styling
- `script.js` — client-side behavior
- `requirements.txt` — Python dependencies
- `models/` — local model files and data

## Setup

1. Install dependencies:
```bash
python -m pip install -r requirements.txt
```
2. Run the app:
```bash
python app.py
```

## Notes

- The project ignores Python virtual environments and cache files.
- If you want to add more model files, keep them under `models/`.

## Deploying models to Hugging Face (recommended for demo)

For a live demo we recommend hosting the large model files on Hugging Face and keeping the repo lightweight.

1. Create a model/repo on Hugging Face (https://huggingface.co/new). Upload the model binaries (`sniper_beat_p100.bin`, `sniper_strength_p100.bin`, `sniper_panic_p100.bin`) to the repo. You can use the web upload or `git lfs`.

2. In your deployment environment (or locally) set the environment variable `HF_REPO_ID` to the repo id, e.g. `DReekis/StockXiq`.

3. Use the helper to download models into the `models/` folder:

```bash
HF_REPO_ID=your-username/your-model-repo python download_models.py
```

4. The Flask app will also attempt to download missing model files at startup if `HF_REPO_ID` is set and `huggingface-hub` is installed.

## Deploying the website

- For a quick live demo, host the front-end/API on Vercel (or Render). Note: Vercel provides serverless functions with cold-starts and limited execution time — for model inference you'll likely want to host the Flask API separately (e.g., on a small VM, Railway, Render or Hugging Face Space) and point the frontend to that API.

Recommended demo setup:

- Host your model files and optionally a simple model-serving endpoint on a Hugging Face Space (Docker or Gradio/Flask). This keeps the heavy model where it runs reliably.
- Host the website (static `index.html`, `script.js`) on Vercel and configure it to call your deployed inference API (Space or Render).

If you want, I can:
- Prepare the repository for a Hugging Face Space (Dockerfile + minimal wrapper)
- Add instructions to deploy the frontend on Vercel and connect it to the HF-hosted model

## Deploying as a Hugging Face Space (Option B)

This repo now includes a `Dockerfile` and `start.sh` to run the Flask app inside a Space. Steps:

1. Create a new Space on Hugging Face: https://huggingface.co/new-space. Choose `Other` and `Docker`.
2. Clone the new Space locally:

```bash
git clone https://huggingface.co/spaces/<USERNAME>/<SPACE_NAME>
cd <SPACE_NAME>
```

3. Copy your project files into the space repository (or push from this repo). Ensure the model binaries (`sniper_beat_p100.bin`, `sniper_strength_p100.bin`, `sniper_panic_p100.bin`) are present in the root or `models/`.

4. Commit & push. For large model files, use `git lfs`:

```bash
pip install git-lfs
git lfs install
git add -A
git commit -m "Add app + models"
git push
```

5. In the Space settings you can set environment variables like `HF_REPO_ID` or `HUGGINGFACE_HUB_TOKEN` if you want the Space to download files from another HF repo.

Notes:
- The container runs `start.sh` which launches `gunicorn` and serves the Flask API. The default port is `7860`.
- The app will attempt to load models from `models/`. If missing and `HF_REPO_ID` is set, it will call `hf_hub_download` to pull the binaries.

If you'd like, I can prepare a ready-to-push Space repo layout and test that the app loads remotely (you'll need to provide the HF token or make the model repo public). 
