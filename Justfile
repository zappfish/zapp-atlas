set dotenv-load := true
set dotenv-filename := ".env.local"

api_port := env("API_PORT", "8000")

# List available recipes
default:
    @just --list

# Run the FastAPI backend
dev-api:
    cd server && PYTHONPATH=.. uv run uvicorn server.api.main:app --reload --port {{api_port}}

# Run Python tests
test:
    cd server && uv run pytest

# Seed the dev database
seed:
    cd server && PYTHONPATH=.. uv run python -m server.seed

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
