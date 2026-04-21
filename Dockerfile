# Python runtime — API only. The frontend lived in client/ and is now
# archived under legacy/; this image serves JSON from FastAPI.

FROM python:3.12-slim AS runtime

# git is required for the git-based schema dependency
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install Python dependencies (cached layer)
COPY server/pyproject.toml server/uv.lock ./server/
RUN cd server && uv sync --frozen --no-dev

# Copy server source code
COPY server/ ./server/

ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uv", "run", "--no-sync", "--directory", "server", \
     "uvicorn", "server.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
