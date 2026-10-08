import os
from pathlib import Path
from google.cloud import storage

BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "wahmed-video-outputs-2026")

_client = storage.Client()
_bucket = _client.bucket(BUCKET_NAME)


def upload_video(local_path, blob_name):
 blob = _bucket.blob(blob_name)
 blob.upload_from_filename(str(local_path))
 return blob_name


def download_video_to_temp(blob_name, dest_path):
 blob = _bucket.blob(blob_name)
 blob.download_to_filename(str(dest_path))
 return dest_path
