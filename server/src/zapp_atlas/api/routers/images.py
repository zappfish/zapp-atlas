"""Image endpoints.

An image is a file plus a row describing it. The file is uploaded once, beneath
an observation, and never replaced; the description can be.
"""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from fastapi.responses import RedirectResponse

from zapp_atlas.api.authz import SignedIn
from zapp_atlas.api.deps import SessionDep, SettingsDep, StorageDep
from zapp_atlas.api.resources import readable, writable
from zapp_atlas.api.services import levels
from zapp_atlas.schema.pydantic_crud import ImageInput, ImageRead
from zapp_atlas.schema.sqla import Image, PhenotypeObservationSet

router = APIRouter(tags=["images"])

Readable = Annotated[Image, readable("Image")]
Writable = Annotated[Image, writable("Image")]
WritableParent = Annotated[PhenotypeObservationSet, writable("PhenotypeObservationSet")]


class ImageUpload(ImageInput):
    """An image's description, sent as form fields alongside its file."""

    file: UploadFile


@router.post(
    "/observations/{observation_id}/images",
    response_model=ImageRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    parent: WritableParent,
    upload: Annotated[ImageUpload, File()],
    identity: SignedIn,
    session: SessionDep,
    settings: SettingsDep,
    storage: StorageDep,
) -> Image:
    content_type = upload.file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Unsupported content type: {content_type}"
        )
    data = await upload.file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"The file is larger than {settings.max_upload_bytes} bytes",
        )

    body = ImageInput.model_validate(upload.model_dump(exclude={"file"}))
    image = levels.create(session, "Image", body, parent=parent, by=identity)
    storage.put(levels.image_key(image.id), data, content_type)
    return image


@router.get("/images/{image_id}")
def fetch_image(image: Readable, storage: StorageDep) -> Response:
    key = levels.image_key(image.id)
    url = storage.url_for(key)
    if url:
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

    stored = storage.get(key)
    if stored is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image file missing")
    return Response(content=stored.data, media_type=stored.content_type)


@router.put("/images/{image_id}", response_model=ImageRead)
def replace_image(
    image: Writable, body: ImageInput, identity: SignedIn, session: SessionDep
) -> Image:
    return levels.replace(session, "Image", image, body, by=identity)


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image: Writable, identity: SignedIn, session: SessionDep, storage: StorageDep
) -> None:
    levels.delete(session, "Image", image, storage, by=identity)
