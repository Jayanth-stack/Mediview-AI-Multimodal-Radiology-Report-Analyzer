from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import uuid4

from app.services.storage import get_s3_storage
from app.api import deps
from app.db.models import User


router = APIRouter(prefix="/api/uploads")


class PresignRequest(BaseModel):
    filename: str
    content_type: str
    use_post: bool = False


from typing import Optional

class PresignResponse(BaseModel):
    key: str
    method: str
    url: str
    fields: Optional[dict] = None


@router.post("/presign", response_model=PresignResponse)
def presign(
    body: PresignRequest,
    s3=Depends(get_s3_storage),
    current_user: User = Depends(deps.get_current_user),
) -> PresignResponse:
    filename = body.filename.replace("\\", "/").split("/")[-1] or "upload"
    key = f"users/{current_user.id}/uploads/{uuid4().hex}-{filename}"
    if body.use_post:
        post = s3.generate_presigned_post(key=key, content_type=body.content_type)
        return PresignResponse(key=key, method="POST", url=post["url"], fields=post["fields"])
    else:
        url = s3.generate_presigned_put(key=key, content_type=body.content_type)
        return PresignResponse(key=key, method="PUT", url=url, fields=None)

