set dotenv-load := true
set dotenv-filename := ".env.local"

api_port := env("API_PORT", "8000")
vite_port := env("DEV_PORT", "5173")

# List available recipes
default:
    @just --list

# Install server and client dependencies; creates server/.env if absent
install:
    cd server && uv sync
    cd client && npm install
    @test -f server/.env || cp server/.env.default server/.env

# Run the FastAPI backend (serves the HTML pages, the API, and /edit)
dev-api:
    cd server && uv run uvicorn zapp_atlas.main:app --reload --port {{api_port}}

# Run the backend against the Vite dev server, so the React client hot-reloads
dev-api-hmr:
    # Run `just dev-client` alongside this, then open /edit on the API port —
    # not the Vite port. FastAPI serves the page; Vite only serves its modules.
    cd server && ZAPP_VITE_DEV_SERVER=http://localhost:{{vite_port}} \
        uv run uvicorn zapp_atlas.main:app --reload --port {{api_port}}

# Run the Vite dev server for the React editing client
dev-client:
    cd client && npm run dev

# Build the React editing client into client/dist
build-client:
    cd client && npm run build

# Run Python tests
test:
    cd server && uv run pytest

# Check linting and formatting (no changes written)
lint:
    cd server && uv run ruff check
    cd server && uv run ruff format --check

# Auto-fix lint violations and reformat
fix:
    cd server && uv run ruff check --fix
    cd server && uv run ruff format

# Seed the dev database
seed:
    cd server && uv run python -m zapp_atlas.seed

# Build the Docker image (local/Fly.io)
build:
    docker build -t zapp-atlas .

# --- GCP Cloud Run ---

gcp_project := "monarch-initiative"
gcp_region := "us-central1"
gcp_image := "us-central1-docker.pkg.dev/" + gcp_project + "/cloud-run-source-deploy/zapp-atlas:latest"
gcp_bucket := "zapp-atlas-data"

# Build and push the Docker image for GCP
gcp-build:
    docker buildx build --platform linux/amd64 -t {{gcp_image}} .
    docker push {{gcp_image}}

# Deploy to Cloud Run
gcp-deploy:
    gcloud run deploy zapp-atlas \
      --image {{gcp_image}} \
      --project {{gcp_project}} \
      --region {{gcp_region}} \
      --execution-environment gen2 \
      --max-instances 1 \
      --set-env-vars ZAPP_DB_PATH=/data/zapp.db,ZAPP_UPLOAD_DIR=/data/uploads,PYTHONPATH=/app \
      --add-volume name=data,type=cloud-storage,bucket={{gcp_bucket}} \
      --add-volume-mount volume=data,mount-path=/data

# Build, push, and deploy to GCP in one step
gcp-ship: gcp-build gcp-deploy

# Show Cloud Run service status and URL
gcp-status:
    @gcloud run services describe zapp-atlas \
      --project {{gcp_project}} \
      --region {{gcp_region}} \
      --format="table(status.url, status.conditions[0].status, status.traffic[0].revisionName, status.traffic[0].percent)"
