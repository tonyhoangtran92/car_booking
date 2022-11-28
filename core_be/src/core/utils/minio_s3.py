import logging

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings


def _minio_s3_initialize():
    session = boto3.Session(
        aws_access_key_id=settings.MINIO_ACCESS_KEY_ID,
        aws_secret_access_key=settings.MINIO_SECRET_ACCESS_KEY,
    )
    s3_client = session.client(
        "s3", endpoint_url=settings.MINIO_S3_ENDPOINT_URL, config=Config(
            signature_version='s3v4'),
    )
    return s3_client


def _minio_s3_upload_file(file, folder, bucket_name=settings.MINIO_STORAGE_BUCKET_NAME, s3_client=None, object_name=None, content_type=None, file_name=None):
    if s3_client is None:
        s3_client = _minio_s3_initialize()
    if object_name is None:
        try:
            object_name = "%s/%s/%s" % (settings.MEDIA_FOLDER, folder, file.name)
        except:
            object_name = "%s/%s/%s" % (settings.MEDIA_FOLDER, folder, file_name)
    s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=file, ContentType=content_type)


def minio_s3_get_url_file(object_name, bucket_name=settings.MINIO_STORAGE_BUCKET_NAME, s3_client=None,  expiration=604800):  # a week
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    if s3_client is None:
        s3_client = _minio_s3_initialize()
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None
    # The response contains the presigned URL
    return response


def minio_s3_upload_and_get_file(file, folder, bucket_name=settings.MINIO_STORAGE_BUCKET_NAME, object_name=None):
    s3_client = _minio_s3_initialize()
    if object_name is None:
        object_name = "%s/%s/%s" % (settings.MEDIA_FOLDER, folder, file.name)
    _minio_s3_upload_file(file, folder, bucket_name, s3_client, object_name)
    url = minio_s3_get_url_file(object_name, bucket_name, s3_client)
    return url

