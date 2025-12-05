from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import uuid4

from app.services.storage import get_s3_storage
from app.api import deps


router = APIRouter(prefix="/api/uploads")


class PresignRequest(BaseModel):
    filename: str
    content_type: str
    use_post: bool = False


class PresignResponse(BaseModel):
    key: str
    method: str
    url: str
    fields: dict | None = None


@router.post("/presign", response_model=PresignResponse)
def presign(
    body: PresignRequest,
    s3=Depends(get_s3_storage),
    current_user=Depends(deps.get_current_user),
) -> PresignResponse:
    key = f"uploads/{uuid4().hex}-{body.filename}"
    if body.use_post:
        post = s3.generate_presigned_post(key=key, content_type=body.content_type)
        return PresignResponse(key=key, method="POST", url=post["url"], fields=post["fields"])
    else:
        url = s3.generate_presigned_put(key=key, content_type=body.content_type)
        return PresignResponse(key=key, method="PUT", url=url, fields=None)

