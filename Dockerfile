FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY app/ app/
RUN pip install --no-cache-dir .

COPY . .

RUN groupadd --system app && useradd --system --gid app --create-home app \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
