"""Uploads fashion dataset from Kaggle into Google Cloud Storage"""
from google.cloud import storage

storage_client = storage.Client()

BUCKET_NAME = "tcc-clothes"

for blob in storage_client.list_blobs(BUCKET_NAME, prefix='images/'):
    print(str(blob))
