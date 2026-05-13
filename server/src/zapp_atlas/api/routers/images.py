"""Image upload / fetch endpoints.

* POST /observations/{observation_id}/images — multipart upload
* GET /images/{image_id} — stream bytes (local) or redirect to signed URL (S3)
"""

from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from zapp_atlas.api.deps import get_app_settings, get_session
from zapp_atlas.api.services.images import (
    ImageTooLargeError,
    UnsupportedImageTypeError,
    create_image_for_observation,
    delete_image,
    get_image_by_id,
    image_url,
    load_image_bytes,
)
from zapp_atlas.db.image_storage import Storage, get_storage
from zapp_atlas.settings import AppSettings

from zapp_atlas.schema.pydantic_crud import ImageRead


router = APIRouter(tags=["images"])


def get_storage_dep(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> Storage:
    return get_storage(settings)


SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[AppSettings, Depends(get_app_settings)]
StorageDep = Annotated[Storage, Depends(get_storage_dep)]


@router.post(
    "/observations/{observation_id}/images",
    response_model=ImageRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image_endpoint(
    observation_id: int,
    session: SessionDep,
    settings: SettingsDep,
    storage: StorageDep,
    file: Annotated[UploadFile, File()],
    magnification: Annotated[str | None, Form()] = None,
    resolution: Annotated[str | None, Form()] = None,
    scale_bar: Annotated[str | None, Form()] = None,
) -> ImageRead:
    data = await file.read()

    try:
        image = create_image_for_observation(
            session,
            observation_id=observation_id,
            data=data,
            content_type=file.content_type or "application/octet-stream",
            storage=storage,
            max_bytes=settings.max_upload_bytes,
            magnification=magnification,
            resolution=resolution,
            scale_bar=scale_bar,
        )
    except UnsupportedImageTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {exc}",
        ) from exc
    except ImageTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found"
        )
    return image  # type: ignore[return-value]


@router.get("/images/{image_id}")
def fetch_image_endpoint(
    image_id: int,
    session: SessionDep,
    storage: StorageDep,
):
    if get_image_by_id(session, image_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    url = image_url(image_id, storage)
    if url:
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

    stored = load_image_bytes(image_id, storage)
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image blob missing"
        )
    return Response(content=stored.data, media_type=stored.content_type)


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image_endpoint(
    image_id: int,
    session: SessionDep,
    storage: StorageDep,
) -> None:
    if not delete_image(session, image_id, storage=storage):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
