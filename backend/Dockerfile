FROM python:3.11-slim

WORKDIR /app

# Install curl for docker healthcheck and network utilities
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-install CPU-only PyTorch (~150MB instead of ~1.2GB CUDA wheel) with extended timeouts
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 \
    torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

