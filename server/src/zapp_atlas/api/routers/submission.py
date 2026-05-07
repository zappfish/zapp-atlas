"""Form submission endpoint.

POST /observation  — accepts multipart form with observation JSON + optional image.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile


def _secure_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w\-.]", "_", filename)
    filename = filename.lstrip(".-")
    return filename or "file"

_SERVER_DIR = Path(__file__).resolve().parents[4]  # server/
_DEFAULT_UPLOAD_BASE = _SERVER_DIR / "data" / "submissions"
_DEFAULT_CREDENTIALS_FILE = _SERVER_DIR / "credentials.txt"


def _env_path(name: str, default: Path) -> Path:
    val = os.getenv(name)
    return Path(val).expanduser().resolve() if val else default


def _load_credentials(path: Path) -> dict[str, str]:
    creds: dict[str, str] = {}
    if not path.exists():
        return creds
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        user, pw = line.split(":", 1)
        user = user.strip()
        if user:
            creds[user] = pw.strip()
    return creds


def _authenticate(username: str, password: str) -> tuple[bool, str | None]:
    cred_file = _env_path("ZAPP_AUTH_FILE", _DEFAULT_CREDENTIALS_FILE)
    creds = _load_credentials(cred_file)
    if not creds:
        return False, "credentials_missing"
    stored = creds.get(username)
    if stored is None:
        return False, "unauthorized"
    return secrets.compare_digest(stored, password), "unauthorized"


def _make_submission_id() -> str:
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


router = APIRouter(tags=["submission"])


@router.post("/observation", status_code=201)
async def observation(
    username: str = Form(...),
    password: str = Form(...),
    data: UploadFile = File(...),
    image: UploadFile | None = File(None),
) -> dict:
    if not username or not password:
        raise HTTPException(status_code=401, detail="unauthorized")

    ok, err = _authenticate(username, password)
    if not ok:
        status = 500 if err == "credentials_missing" else 401
        raise HTTPException(status_code=status, detail=err)

    raw = await data.read()
    try:
        obs = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'data': {e}") from e

    base_dir = _env_path("ZAPP_UPLOAD_BASE_DIR", _DEFAULT_UPLOAD_BASE)
    submission_dir = _ensure_unique_dir(base_dir)

    obs_path = submission_dir / "observation.json"
    obs_path.write_text(json.dumps(obs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    image_original: str | None = None
    image_canonical: str | None = None
    if image and image.filename:
        original_name = _secure_filename(image.filename)
        img_path = submission_dir / original_name
        img_path.write_bytes(await image.read())
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
        "files": {
            "observation_json": obs_path.name,
            "image_original": image_original,
            "image_canonical": image_canonical,
        },
    }
    (submission_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    return {"status": "ok", "id": submission_dir.name}
