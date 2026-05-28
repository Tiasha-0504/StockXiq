#!/bin/bash
# Start Gunicorn on the configured PORT (default 7860 for Spaces)
PORT=${PORT:-7860}
# Use a single worker to reduce memory usage for small spaces. Increase if needed.
exec gunicorn --bind 0.0.0.0:${PORT} app:app --workers 1 --threads 2 --timeout 120
