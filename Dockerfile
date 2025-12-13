# ---- Stage 1: Builder ----
FROM python:3.11-slim AS builder
ENV PIP_NO_CACHE_DIR=1 \
    TZ=UTC

WORKDIR /app

# Install OS build deps needed for cryptography and other wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list and build wheels into /wheels for small final image
COPY requirements.txt .
RUN python -m pip install --upgrade pip wheel setuptools \
 && python -m pip wheel -r requirements.txt -w /wheels

# ---- Stage 2: Runtime ----
FROM python:3.11-slim AS runtime
ENV TZ=UTC
WORKDIR /app

# Install runtime OS deps (cron + tzdata)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

# Copy prebuilt wheels from builder and install using original requirements.txt
COPY --from=builder /wheels /wheels
COPY requirements.txt /app/requirements.txt

# Install packages using wheels in /wheels as find-links
RUN python -m pip install --no-index --find-links /wheels -r /app/requirements.txt

# Copy application files
COPY . /app

# Create required directories and set ownership/permissions
RUN mkdir -p /data /cron /app/scripts \
 && chmod 755 /data /cron /app/scripts \
 && chmod 644 /app/student_public.pem /app/instructor_public.pem || true

# Install cron file (crontab expects LF endings; .gitattributes will help)
RUN crontab cron/2fa-cron || true

# Expose API port
EXPOSE 8080

# Entrypoint script to start cron and the API server
COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Default command
CMD ["/usr/local/bin/start.sh"]
