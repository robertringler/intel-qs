# syntax=docker/dockerfile:1.7
# ---- build stage: hash-pinned dependencies only (no unpinned build backends) ----
FROM python:3.11-slim-bookworm AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
COPY requirements.lock /tmp/requirements.lock
# Optional build secret "extra_ca" for networks with TLS-inspecting proxies; never persisted in the image.
RUN --mount=type=secret,id=extra_ca,required=false \
    if [ -f /run/secrets/extra_ca ]; then export PIP_CERT=/run/secrets/extra_ca; fi; \
    pip install --require-hashes --only-binary=:all: -r /tmp/requirements.lock

# ---- runtime stage: minimal, non-root, read-only friendly ----
FROM python:3.11-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH=/opt/venv/bin:$PATH PYTHONPATH=/app/src PP_ENV=production
# python:*-slim already ships ca-certificates; no apt packages are added (smaller attack surface).
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app --no-create-home app
COPY --from=build /opt/venv /opt/venv
COPY --chown=root:root src /app/src
RUN python -m compileall -q /app/src && printf '#!/bin/sh\nexec python -m payeeproof.cli "$@"\n' > /usr/local/bin/payeeproof \
    && chmod 0755 /usr/local/bin/payeeproof
USER 10001:10001
WORKDIR /app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2).status==200 else 1)"
# Default: web server. Override with ["payeeproof", "worker"] or ["payeeproof", "migrate"].
CMD ["payeeproof", "serve", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
