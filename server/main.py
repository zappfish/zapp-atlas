import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, abort
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


# Paths relative to repo
SERVER_DIR = Path(__file__).resolve().parent
REPO_ROOT = SERVER_DIR.parent
DIST_DIR = (REPO_ROOT / "client" / "dist").resolve()
DEFAULT_UPLOAD_BASE = (SERVER_DIR / "data" / "submissions").resolve()
DEFAULT_CREDENTIALS_FILE = (SERVER_DIR / "credentials.txt").resolve()

# Disable Flask's default static handler; we'll serve only from client/dist explicitly
app = Flask(__name__, static_folder=None)

# 50 MB limit
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


def _env_path(name: str, default: Path) -> Path:
    val = os.getenv(name)
    return Path(val).expanduser().resolve() if val else default


def load_credentials(path: Path) -> dict[str, str]:
    creds: dict[str, str] = {}
    if not path.exists():
        return creds
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        user, pw = line.split(":", 1)
        user = user.strip()
        pw = pw.strip()
        if user:
            creds[user] = pw
    return creds


def authenticate(username: str, password: str) -> tuple[bool, str | None]:
    cred_file = _env_path("ZAPP_AUTH_FILE", DEFAULT_CREDENTIALS_FILE)
    creds = load_credentials(cred_file)
    if not creds:
        return False, "Credentials file not found or empty"
    stored = creds.get(username)
    if stored is None:
        return False, "Unauthorized"
    ok = secrets.compare_digest(stored, password)
    return ok, None if ok else "Unauthorized"


def _make_submission_id() -> str:
    # UTC ISO-like, safe for FS, millisecond precision + 4-hex suffix
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S.%f")[:-3] + "Z"
    return f"{ts}-{secrets.token_hex(2)}"


def _ensure_unique_dir(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    for _ in range(5):
        sub = base / _make_submission_id()
        try:
            sub.mkdir(parents=False, exist_ok=False)
            return sub
        except FileExistsError:
            continue
    sub = base / f"{_make_submission_id()}-{secrets.token_hex(2)}"
    sub.mkdir(parents=True, exist_ok=False)
    return sub


def _parse_observation_json() -> dict:
    data_file = request.files.get("data")
    if data_file:
        try:
            return json.loads(data_file.read())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in 'data' file part: {e}") from e
    if "data" in request.form:
        try:
            return json.loads(request.form["data"])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in 'data' form field: {e}") from e
    raise ValueError("Missing 'data' field containing observation JSON")


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "too_large"}), 413


@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"error": "bad_request", "details": getattr(e, "description", None)}), 400


@app.errorhandler(401)
def handle_unauthorized(e):
    return jsonify({"error": "unauthorized"}), 401


@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"error": "internal_error"}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/observation")
def observation():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if not username or not password:
        return jsonify({"error": "unauthorized"}), 401
    ok, err = authenticate(username, password)
    if not ok:
        msg = "credentials_missing" if err and "file" in err else "unauthorized"
        status = 500 if msg == "credentials_missing" else 401
        return jsonify({"error": msg}), status

    try:
        obs = _parse_observation_json()
    except ValueError as ve:
        return jsonify({"error": "bad_request", "details": str(ve)}), 400

    image_file = request.files.get("image")

    base_dir = _env_path("ZAPP_UPLOAD_BASE_DIR", DEFAULT_UPLOAD_BASE)
    submission_dir = _ensure_unique_dir(base_dir)

    obs_path = submission_dir / "observation.json"
    obs_path.write_text(json.dumps(obs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    image_original: str | None = None
    image_canonical: str | None = None
    if image_file and image_file.filename:
        original_name = secure_filename(image_file.filename)
        img_path = submission_dir / original_name
        image_file.save(str(img_path))
        image_original = original_name

        ext = "".join(Path(original_name).suffixes) or ""
        canonical_name = f"image{ext}"
        canonical_path = submission_dir / canonical_name
        try:
            canonical_path.write_bytes(img_path.read_bytes())
            image_canonical = canonical_name
        except Exception:
            pass

    meta = {
        "id": submission_dir.name,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "client_ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "files": {
            "observation_json": obs_path.name,
            "image_original": image_original,
            "image_canonical": image_canonical,
        },
        "user_agent": request.headers.get("User-Agent"),
    }
    (submission_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    return jsonify({"status": "ok", "id": submission_dir.name}), 201


# Strict dist-only static serving with SPA fallback for "route-like" paths
def _dist_exists() -> bool:
    return DIST_DIR.exists() and (DIST_DIR / "index.html").exists()


@app.get("/")
def serve_index():
    if _dist_exists():
        return send_from_directory(str(DIST_DIR), "index.html")
    return (
        "Client build not found. Run 'npm run build' in the client/ directory to generate client/dist.",
        200,
    )


@app.get("/<path:path>")
def serve_dist(path: str):
    if not DIST_DIR.exists():
        return (
            "Client build not found. Run 'npm run build' in the client/ directory to generate client/dist.",
            200,
        )

    # Serve only files that physically exist inside client/dist
    file_path = (DIST_DIR / path).resolve()
    try:
        # Ensure the resolved path is still within DIST_DIR (prevent traversal)
        file_path.relative_to(DIST_DIR)
    except Exception:
        abort(404)

    if file_path.is_file():
        # Serve the actual file (assets, css, js, etc.)
        return send_from_directory(str(DIST_DIR), path)

    # SPA fallback: for "route-like" paths (no '.' in last segment), return index.html
    last_segment = path.rsplit("/", 1)[-1]
    if "." not in last_segment and (DIST_DIR / "index.html").is_file():
        return send_from_directory(str(DIST_DIR), "index.html")

    # Otherwise, 404
    abort(404)


def main():
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
