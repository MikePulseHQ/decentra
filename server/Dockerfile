# Pin to working digest for reproducibility and security
FROM python:3.11-slim@sha256:5be45dbade29bebd6886af6b438fd7e0b4eb7b611f39ba62b430263f82de36d2

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies in a single RUN command to reduce layers
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application files in one layer
COPY server.py database.py api.py encryption_utils.py email_utils.py ssl_utils.py ./
COPY static/ ./static/

# Expose WebSocket port
EXPOSE 8765

# Run the server
CMD ["python", "-u", "server.py"]
