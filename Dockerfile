# Multi-stage Docker build for C2 Phantom
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="C2 Phantom Team"
LABEL description="Advanced C2 Framework for Red Team Training"
LABEL version="1.0.0"

# Create non-root user
RUN useradd -m -u 1000 phantom && \
    mkdir -p /home/phantom/.phantom && \
    chown -R phantom:phantom /home/phantom

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY --from=builder /build /app
WORKDIR /app

# Switch to non-root user
USER phantom

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PHANTOM_HOME=/home/phantom/.phantom

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import c2_phantom; print('healthy')" || exit 1

# Expose ports (if running server mode)
EXPOSE 443

# Default command
CMD ["phantom", "--help"]
