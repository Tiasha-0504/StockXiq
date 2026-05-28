"""Download model artifacts from a Hugging Face repository into ./models

Usage:
  HF_REPO_ID=your-username/your-model-repo python download_models.py

This script requires `huggingface-hub` to be installed.
"""
import os
import sys
from huggingface_hub import hf_hub_download

FILES = [
    "sniper_beat_p100.bin",
    "sniper_strength_p100.bin",
    "sniper_panic_p100.bin",
]

def main():
    repo = os.environ.get('HF_REPO_ID')
    if not repo:
        print('ERROR: Set HF_REPO_ID environment variable to your HF repo id (e.g. user/repo)')
        sys.exit(1)

    os.makedirs('models', exist_ok=True)

    for fn in FILES:
        try:
            print(f"Downloading {fn} from {repo}...")
            path = hf_hub_download(repo_id=repo, filename=fn)
            # Move/copy into models/ if not already there
            dest = os.path.join('models', fn)
            if os.path.abspath(path) != os.path.abspath(dest):
                import shutil
                shutil.copyfile(path, dest)
            print(f"Saved → {dest}")
        except Exception as e:
            print(f"Failed to download {fn}: {e}")

if __name__ == '__main__':
    main()
