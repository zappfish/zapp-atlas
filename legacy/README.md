# Legacy

These files are preserved for historical reference. Neither is wired into the current build.

- `server/main.py` — the original Flask app that exposed `POST /observation` for image + JSON uploads, with credential-file auth and SPA static serving from `client/dist`.
- `server/credentials.example.txt` — example credentials file consumed by the Flask app.
- `client/` — the first-pass React / Vite prototype (ZappForm, PhenoDemo, wild-type-lines data, static phenotype JSON assets). Built against the old Flask upload endpoint.

The current API lives in `server/api/` (FastAPI, LinkML schema-backed). See the top-level `README.md` for dev quickstart.
