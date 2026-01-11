# Stage 1: Builder
FROM python:3.14-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project --locked
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Production
FROM python:3.14-slim as production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy python dependencies from builder stage
COPY --from=builder /usr/local/ /usr/local/

# Copy collected static files from builder stage
COPY --from=builder /app/staticfiles/ /app/staticfiles/

# Copy application code
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8000

# Run Gunicorn, explicitly passing the application module
CMD ["gunicorn", "--config", "gunicorn.conf.py", "timeline.wsgi:application"]