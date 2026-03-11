import uuid

import boto3

from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def generate_upload_presigned_url(file_name: str, mime_type: str, startup_id: str) -> dict:
    s3 = get_s3_client()
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else ""
    s3_key = f"startups/{startup_id}/documents/{uuid.uuid4()}.{ext}" if ext else f"startups/{startup_id}/documents/{uuid.uuid4()}"

    url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": s3_key,
            "ContentType": mime_type,
        },
        ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRY,
    )
    return {"upload_url": url, "s3_key": s3_key}


def generate_download_presigned_url(s3_key: str) -> str:
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": s3_key,
        },
        ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRY,
    )


def delete_s3_object(s3_key: str) -> None:
    s3 = get_s3_client()
    s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
