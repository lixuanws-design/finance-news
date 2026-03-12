# Use official Python slim image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install build deps (if any) and runtime deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose Flask default port (will be overridden by $PORT env when on cloud)
EXPOSE 8899

# Default command – Flask will bind to $PORT if provided
CMD ["python", "app.py"]