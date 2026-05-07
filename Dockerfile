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

# Production: Gunicorn + Uvicorn workers (see gunicorn.conf.py). Override WEB_CONCURRENCY as needed.
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
