# Dockerfile — MX-UI + Xray Core (Xray v25.1.30 supports xhttp)
# NOTE: CMD runs python directly. No start.sh dependency.

FROM python:3.11-slim AS builder

ARG XRAY_VERSION=v25.1.30
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    ARCH="${TARGETARCH:-amd64}"; \
    case "${ARCH}" in \
        amd64) XRAY_ASSET="Xray-linux-64.zip" ;; \
        arm64) XRAY_ASSET="Xray-linux-arm64-v8a.zip" ;; \
        arm)   XRAY_ASSET="Xray-linux-arm32-v7a.zip" ;; \
        *) echo "unsupported arch: ${ARCH}"; exit 1 ;; \
    esac; \
    echo "==> Fetching Xray ${XRAY_VERSION} ARCH=${ARCH} asset=${XRAY_ASSET}"; \
    curl -fsSL -o /tmp/xray.zip \
        "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/${XRAY_ASSET}"; \
    unzip -o /tmp/xray.zip xray -d /tmp/xray-bin; \
    chmod +x /tmp/xray-bin/xray; \
    /tmp/xray-bin/xray version

# =====================================================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/data \
    INTERNAL_PORT=8001 \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates tzdata curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /tmp/xray-bin/xray /usr/local/bin/xray
RUN chmod +x /usr/local/bin/xray && /usr/local/bin/xray version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data && chmod 755 /data

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD python -c "import urllib.request,os; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8080')+'/health', timeout=3)" || exit 1

CMD ["python", "main.py"]
