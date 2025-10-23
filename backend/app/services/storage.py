import os
import uuid
from typing import Dict, Optional


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def upload_to_s3(bucket: str, key: str, data: bytes, expire_seconds: int = 3600) -> Dict:
    """Upload bytes to S3 and return metadata including a presigned URL when possible.

    This function tries to use boto3. If boto3 is not available or credentials are not
    configured, it falls back to writing the file to a local `storage/` directory and
    returns a local file URL.

    Args:
        bucket: S3 bucket name (used in metadata for local fallback)
        key: object key in the bucket
        data: raw bytes to upload
        expire_seconds: presigned URL expiry (seconds)

    Returns:
        dict with keys: bucket, key, url (may be file:// path when local)
    """
    try:
        import boto3  # type: ignore
        from botocore.exceptions import BotoCoreError, ClientError

        s3 = boto3.client('s3')
        # Use put_object since we have bytes
        s3.put_object(Bucket=bucket, Key=key, Body=data)
        url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expire_seconds)
        return {"bucket": bucket, "key": key, "url": url}
    except Exception:
        # Fallback to local storage
        storage_dir = os.path.join(os.getcwd(), 'storage', bucket)
        _ensure_dir(storage_dir)
        local_name = key
        # sanitize key for filesystem
        local_name = local_name.replace('/', '_')
        if not local_name:
            local_name = str(uuid.uuid4())
        local_path = os.path.join(storage_dir, local_name)
        with open(local_path, 'wb') as f:
            f.write(data)
        return {"bucket": bucket, "key": key, "url": f"file://{local_path}"}


def upload_file(path: str, bucket: str, key: Optional[str] = None, expire_seconds: int = 3600) -> Dict:
    """Upload a file on disk to S3 or local storage fallback.

    Args:
        path: local file path
        bucket: target bucket name (or local folder)
        key: optional object key; if not provided filename is used

    Returns:
        dict with bucket, key, url
    """
    if key is None:
        key = os.path.basename(path)
    with open(path, 'rb') as fh:
        return upload_to_s3(bucket=bucket, key=key, data=fh.read(), expire_seconds=expire_seconds)


def save_image_local(data: bytes, filename: Optional[str] = None, subdir: str = "images") -> Dict:
    """Save image bytes to a local storage folder and return metadata.

    Returns a dict: {"bucket": "local", "key": <relative path>, "url": "file://..."}
    """
    base = os.getenv("LOCAL_STORAGE_PATH", os.path.join(os.getcwd(), "storage"))
    storage_dir = os.path.join(base, subdir)
    _ensure_dir(storage_dir)

    if not filename:
        filename = f"{uuid.uuid4().hex}.jpg"
    # sanitize filename
    filename = filename.replace("/", "_")
    local_path = os.path.join(storage_dir, filename)
    with open(local_path, "wb") as f:
        f.write(data)

    return {"bucket": "local", "key": os.path.join(subdir, filename), "url": f"file://{local_path}"}


def upload_file_to_s3(path: str, bucket: Optional[str] = None, key: Optional[str] = None, expire_seconds: int = 3600) -> Dict:
    """Upload a local file to S3 (or fallback to local storage) using configured bucket.

    Bucket defaults to S3_BUCKET env var or 'haski-uploads'.
    """
    target_bucket = bucket or os.getenv("S3_BUCKET", "haski-uploads")
    return upload_file(path=path, bucket=target_bucket, key=key, expire_seconds=expire_seconds)


def save_image(data: bytes, filename: Optional[str] = None) -> Dict:
    """Save image by choosing local or S3 storage depending on env var.

    Environment variables:
      USE_LOCAL_STORAGE (default: 'true') — if truthy, use local save
      S3_BUCKET — target bucket when uploading to S3
    """
    use_local = os.getenv("USE_LOCAL_STORAGE", "true").lower() in ("1", "true", "yes")
    if use_local:
        return save_image_local(data=data, filename=filename)

    # try upload to s3: write to a temp file then call upload_file_to_s3
    tmp_dir = os.path.join(os.getcwd(), "tmp_uploads")
    _ensure_dir(tmp_dir)
    if not filename:
        filename = f"{uuid.uuid4().hex}.jpg"
    tmp_path = os.path.join(tmp_dir, filename)
    with open(tmp_path, "wb") as f:
        f.write(data)

    try:
        result = upload_file_to_s3(tmp_path)
        # cleanup tmp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return result
    except Exception:
        # fallback to local if S3 upload fails
        return save_image_local(data=data, filename=filename)

