"""Uploads fashion dataset from Kaggle into Google Cloud Storage"""
from google.cloud import storage
from os import listdir
from os.path import isfile, join

storage_client = storage.Client()
BUCKET_NAME = "tcc-clothes"

bucket = storage_client.get_bucket(BUCKET_NAME)
only_files = [f for f in listdir("images/images/") if isfile(join("images/images/", f))]
men_files = [
    "10268.jpg",
    "59435.jpg",
    "22198.jpg",
    "29570.jpg",
    "26538.jpg",
    "49495.jpg",
    "33822.jpg",
    "42089.jpg",
    "49461.jpg",
    "34835.jpg",
]

for f in only_files:
    destination_blob_name = f"images/{f}"
    source_file_name = f
    print(f)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
