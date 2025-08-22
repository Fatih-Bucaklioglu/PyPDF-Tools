# PyPDF-Tools Dockerfile
# Multi-stage build for hibrit PyQt6 + React uygulaması

# Stage 1: Node.js build environment for React
FROM node:18-alpine AS react-builder

WORKDIR /app

# Package files kopyala
COPY web/package*.json ./

# Dependencies kur
RUN npm ci --only=production

# Source kopyala ve build
COPY web/ ./
RUN npm run build

# Stage 2: Python application
FROM python:3.11-slim AS python-base

# System dependencies
RUN apt-get update && apt-get install -y \
    # Qt dependencies
    libgl1-mesa-glx \
    libegl1-mesa \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6 \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    # Build tools
    gcc \
    g++ \
    make \
    # Additional utilities
    wget \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Python environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final application image
FROM python-base AS final

# Non-root user oluştur
RUN groupadd -r pypdftools && \
    useradd -r -g pypdftools -d /app -s /bin/bash pypdftools && \
    chown -R pypdftools:pypdftools /app

# Application source kopyala
COPY --chown=pypdftools:pypdftools src/ ./src/
COPY --chown=pypdftools:pypdftools setup.py pyproject.toml MANIFEST.in ./
COPY --chown=pypdftools:pypdftools LICENSE README.md CHANGELOG.md ./

# React build'ini kopyala
COPY --from=react-builder --chown=pypdftools:pypdftools /app/build/ ./src/pypdf_tools/web/build/

# Package'ı install et
RUN pip install -e .

# User'a geç
USER pypdftools

# Environment variables
ENV QT_QPA_PLATFORM=offscreen \
    DISPLAY=:99 \
    PYPDF_CONTAINER=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pypdf_tools; print('OK')" || exit 1

# Volumes
VOLUME ["/app/data", "/app/config"]

# Ports (eğer web server modu eklenirse)
EXPOSE 8080

# Default command
CMD ["python", "-m", "pypdf_tools.cli.cli_handler", "--help"]

# Labels for metadata
LABEL maintainer="Fatih Bucaklıoğlu <fatih.bucaklioglu@example.com>" \
      org.opencontainers.image.title="PyPDF-Tools" \
      org.opencontainers.image.description="Hibrit PDF yönetim ve düzenleme uygulaması" \
      org.opencontainers.image.url="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools" \
      org.opencontainers.image.source="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.created="2024-01-15" \
      org.opencontainers.image.licenses="MIT"
