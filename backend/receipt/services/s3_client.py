import os, boto3
from botocore.config import Config

_s3 = boto3.client("s3",
    region_name=os.getenv("AWS_REGION"),
    config=Config(s3={"addressing_style":"virtual"})
)
BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
UPLOAD_EXPIRE = int(os.getenv("S3_UPLOAD_EXPIRE", "600"))
DOWNLOAD_EXPIRE = int(os.getenv("S3_DOWNLOAD_EXPIRE", "600"))

def presign_upload(key, content_type="application/octet-stream"):
    return _s3.generate_presigned_url("put_object",
        Params={"Bucket": BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=UPLOAD_EXPIRE)

def presign_download(key):
    return _s3.generate_presigned_url("get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=DOWNLOAD_EXPIRE)