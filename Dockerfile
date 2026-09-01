# Two-stage build: compile the React editing client with Node, then bundle
# the emitted assets into the Python runtime that serves both the API and the
# server-rendered HTML shell the client mounts into.

# --- Client build ---------------------------------------------------------
# Produces client/dist (hashed JS/CSS + .vite/manifest.json). The generated
# schema sources are committed under client/src, so this stage needs only the
# client/ tree — nothing from server/.
FROM node:22-slim AS client-build

WORKDIR /client

# Install dependencies (cached layer) — only the lockfile invalidates it.
COPY client/package.json client/package-lock.json ./
RUN npm ci

# Build the client itself
COPY client/ ./
RUN npm run build

# --- Python runtime -------------------------------------------------------
FROM python:3.12-slim AS runtime

# git is required for the git-based schema dependency
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install Python dependencies (cached layer) — deps only, not the local project,
# so this layer stays cached when only server source changes.
COPY server/pyproject.toml server/uv.lock ./server/
RUN cd server && uv sync --frozen --no-dev --no-install-project

# Copy server source code, then install the local project itself
COPY server/ ./server/
RUN cd server && uv sync --frozen --no-dev

# Bundle the built editing client. main.py resolves it at <repo-root>/client/dist
# (parents[2] of the installed package), which is /app/client/dist here.
COPY --from=client-build /client/dist ./client/dist

ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uv", "run", "--no-sync", "--directory", "server", \
     "uvicorn", "zapp_atlas.main:app", "--host", "0.0.0.0", "--port", "8080"]
