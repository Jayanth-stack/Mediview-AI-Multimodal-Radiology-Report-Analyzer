from __future__ import annotations

import boto3
from botocore.client import Config
from typing import Optional

from app.core.config import settings


class S3Storage:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            use_ssl=bool(settings.S3_SECURE),
        )
        self._bucket = settings.S3_BUCKET

    def put_bytes(self, key: str, data: bytes, content_type: str) -> str:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)
        return f"{self._bucket}/{key}"

    def generate_presigned_put(self, key: str, content_type: str, expires_seconds: int = 3600) -> str:
        return self._client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": self._bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expires_seconds,
        )

    def generate_presigned_post(
        self, key: str, content_type: str, expires_seconds: int = 3600, max_size_mb: int = 50
    ) -> dict:
        conditions = [["content-length-range", 1, max_size_mb * 1024 * 1024], {"Content-Type": content_type}]
        fields = {"Content-Type": content_type}
        return self._client.generate_presigned_post(
            Bucket=self._bucket,
            Key=key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expires_seconds,
        )

    def get_object_bytes(self, key: str) -> bytes:
        obj = self._client.get_object(Bucket=self._bucket, Key=key)
        try:
            return obj["Body"].read()
        finally:
            try:
                obj["Body"].close()
            except Exception:
                pass


_s3_singleton: Optional[S3Storage] = None


def get_s3_storage() -> S3Storage:
    global _s3_singleton
    if _s3_singleton is None:
        _s3_singleton = S3Storage()
    return _s3_singleton

