# =============================================================================
# Stage 1: Builder
# =============================================================================
# This stage builds the Python wheel. It includes build tools that we don't
# need in the final production image.

FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /build

# Install build dependencies
# --no-cache-dir: Don't store pip cache (smaller image)
RUN pip install --no-cache-dir build

# Copy only the files needed for building
# This order is intentional for Docker layer caching:
# 1. pyproject.toml and README.md change less frequently
# 2. Source code changes more frequently
COPY pyproject.toml README.md ./
COPY src/ src/

# Build the wheel
# This creates a .whl file in /build/dist/
RUN python -m build --wheel


# =============================================================================
# Stage 2: Production
# =============================================================================
# This is the final, minimal image that will be deployed.

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create a non-root user for security
# Running as root in containers is a security risk
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

# Copy the wheel from the builder stage
COPY --from=builder /build/dist/*.whl /tmp/

# Install the wheel and clean up
# --no-cache-dir: Don't store pip cache
# rm /tmp/*.whl: Remove the wheel file after installation
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl

# Switch to non-root user
# All subsequent commands run as 'appuser'
USER appuser

# Document which port the app uses
# This is informational; you still need -p to publish it
EXPOSE 8000

# Health check for container orchestration
# Docker and Kubernetes can use this to check if the app is healthy
# --interval: How often to check (every 30 seconds)
# --timeout: How long to wait for response (10 seconds)
# --start-period: Grace period after container starts (5 seconds)
# --retries: How many failures before marking unhealthy (3)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
# Uses the entry point defined in pyproject.toml
CMD ["ai-chat"]