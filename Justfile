set dotenv-load := true
set dotenv-filename := ".env.local"

api_port := env("API_PORT", "8000")
dev_port := env("DEV_PORT", "5173")

# List available recipes
default:
    @just --list

# Run the FastAPI backend
dev-api:
    cd server && PYTHONPATH=.. uv run uvicorn server.api.main:app --reload --port {{api_port}}

# Run the Vite dev server
dev-client:
    cd client && npm run dev

# Run both API and client (requires two terminals)
dev:
    @echo "Run in two terminals:"
    @echo "  just dev-api     # FastAPI on :{{api_port}}"
    @echo "  just dev-client  # Vite on :{{dev_port}}"

# Run Python tests
test:
    cd server && uv run pytest

# Build the Docker image
build:
    docker build -t zapp-atlas .
