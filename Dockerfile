FROM python:3.10-slim

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create user with UID 1000 as required by Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy app with proper permissions
COPY --chown=user . $HOME/app

# Expose the default HF Space port
ENV PORT=7860
EXPOSE 7860

# Start script
RUN chmod +x $HOME/app/start.sh

CMD ["./start.sh"]
