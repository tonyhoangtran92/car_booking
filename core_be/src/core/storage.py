from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class CustomS3Boto3Storage_2(S3Boto3Storage):
    endpoint_url = settings.MINIO_S3_ENDPOINT_URL
    bucket_name = settings.MINIO_STORAGE_BUCKET_NAME
    region_name = None

    access_key = settings.MINIO_ACCESS_KEY_ID
    secret_key = settings.MINIO_SECRET_ACCESS_KEY
