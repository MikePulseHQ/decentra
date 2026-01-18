# Pin to working digest for reproducibility and security
FROM python:3.11-slim@sha256:5be45dbade29bebd6886af6b438fd7e0b4eb7b611f39ba62b430263f82de36d2

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies in a single RUN command to reduce layers
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy client code
COPY client.py .

# Set default environment variables
ENV SERVER_HOST=server
ENV SERVER_PORT=8765

# Run the client
CMD ["python", "client.py"]
