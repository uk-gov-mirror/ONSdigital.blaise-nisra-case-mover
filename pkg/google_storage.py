import binascii

import pybase64
from google.cloud import storage

# workaround to prevent file transfer timeouts
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB


class GoogleStorage:
    def __init__(self, bucket_name, log):
        self.bucket_name = bucket_name
        self.log = log
        self.bucket = None
        self.storage_client = None

    def initialise_bucket_connection(self):
        try:
            self.log.info(f"Connecting to bucket - {self.bucket_name}")
            storage_client = storage.Client()
            self.storage_client = storage_client
            self.bucket = storage_client.get_bucket(self.bucket_name)
            self.log.info(f"Connected to bucket - {self.bucket_name}")
        except Exception as ex:
            self.log.error("Connection to bucket failed - %s", ex)

    def upload_file(self, source, dest):
        blob_destination = self.bucket.blob(dest)
        self.log.info(f"Uploading file - {source}")
        blob_destination.upload_from_filename(source)
        self.log.info(f"Uploaded file - {source}")

    def get_blob(self, blob_location):
        return self.bucket.get_blob(blob_location)

    def list_blobs(self):
        return list(self.bucket.list_blobs())

    def delete_blobs(self, blob_list):
        self.bucket.delete_blobs(blob_list)

    def get_blob_md5(self, blob_location):
        blob = self.bucket.get_blob(blob_location)
        if not blob:
            return None
        return binascii.hexlify(pybase64.urlsafe_b64decode(blob.md5_hash)).decode(
            "utf-8"
        )
