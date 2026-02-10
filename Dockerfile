# Use an official lightweight Python image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY app/ app/
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
