import io
import mimetypes
import os
from minio import Minio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

minio_client = Minio(
    os.environ.get("MINIO_ENDPOINT_URL"),
    access_key=os.environ.get("MINIO_ACCESS_KEY"),
    secret_key=os.environ.get("MINIO_SECRET_KEY"),
    secure=False
)

BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "media")

if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)