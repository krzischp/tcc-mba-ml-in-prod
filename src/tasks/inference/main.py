# pylint: disable-all
""""App Engine app to serve as an endpoint for App Engine queue samples."""
from __future__ import annotations

import logging
import os

import torch
from flask import Flask, request, jsonify
from google.cloud import bigquery
from google.cloud import storage

from deepfashion import FashionNetVgg16NoBn

BUCKET_NAME = os.getenv("BUCKET_NAME")
app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = bigquery.Client()


def list_blobs_with_prefix(bucket_name, prefix, images_filepaths, delimiter=None):
    """Lists all the blobs in the bucket that begin with the prefix.

    This can be used to list all blobs in a "folder", e.g. "public/".

    The delimiter argument can be used to restrict the results to only the
    "files" in the given "folder". Without the delimiter, the entire tree under
    the prefix is returned. For example, given these blobs:

        a/1.txt
        a/b/2.txt

    If you specify prefix ='a/', without a delimiter, you'll get back:

        a/1.txt
        a/b/2.txt

    However, if you specify prefix='a/' and delimiter='/', you'll get back
    only the file directly under 'a/':

        a/1.txt

    As part of the response, you'll also get back a blobs.prefixes entity
    that lists the "subfolders" under `a/`:

        a/b/
    """

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)

    # Note: The call returns a response only when the iterator is consumed.
    print("Blobs:")
    for blob in blobs:
        if ".jpg" in blob:
            print(blob.name)
            images_filepaths.append(blob.name)
    return images_filepaths


@app.route("/inference", methods=["POST"])
def inference_task():
    """Log the request payload."""
    payload = request.get_json()
    task_id = payload["task_id"]

    fn = FashionNetVgg16NoBn()

    # pose network needs to be trained from scratch? i guess?
    for k in fn.state_dict().keys():
        if "conv5_pose" in k and "weight" in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])

    for k in fn.state_dict().keys():
        if "conv5_global" in k and "weight" in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])

    images_filepaths = []
    prefix = f"fashion-tasks/{task_id}/"
    images_filepaths = list_blobs_with_prefix(BUCKET_NAME, prefix, images_filepaths)

    return jsonify({"images": images_filepaths})


@app.route("/")
def hello():
    """Basic index to verify app is serving."""
    return "Hello World!"


def upload_blob_from_memory(
    bucket_name, contents, destination_blob_name, content_type="text/plain"
):
    """Uploads a file to the bucket."""

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The contents to upload to the file
    # contents = "these are my contents"

    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents, content_type=content_type)

    print(
        f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
    )


if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
