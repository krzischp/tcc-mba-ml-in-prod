"""Uploads fashion dataset from Kaggle into Google Cloud Storage"""
from google.cloud import storage
from os import listdir
from os.path import isfile, join

storage_client = storage.Client()
BUCKET_NAME = "tcc-clothes"

bucket = storage_client.get_bucket(BUCKET_NAME)
only_files = [f for f in listdir("/") if isfile(join("/", f))]
men_files = [
    "images/26538.jpg",
    "images/26554.jpg",
    "images/26553.jpg",
    "images/26548.jpg",
    "images/26550.jpg",
    "images/26535.jpg",
    "images/26542.jpg",
    "images/26552.jpg",
    "images/26541.jpg",
    "images/26549.jpg",
]

for f in men_files:
    destination_blob_name = f"{f}"
    source_file_name = f
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
