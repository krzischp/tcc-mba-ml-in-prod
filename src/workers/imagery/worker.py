"""Imagery Celery worker"""
import json
import os
import random
from typing import Any, Dict, List

import albumentations as A
import cv2
import numpy as np
from google.cloud import storage

BUCKET_NAME = os.getenv("BUCKET_NAME", "")
DATA_FOLDER = os.getenv("DATA_FOLDER", "")
S3_HOST = os.getenv("S3_HOST", "")


def copy_blob(bucket_name, blob_name, destination_bucket_name, destination_blob_name):
    """Copies a blob from one bucket to another with a new name."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # destination_bucket_name = "destination-bucket-name"
    # destination_blob_name = "destination-object-name"

    storage_client = storage.Client()

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.bucket(destination_bucket_name)

    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name
    )

    print(
        "Blob {} in bucket {} copied to blob {} in bucket {}.".format(
            source_blob.name,
            source_bucket.name,
            blob_copy.name,
            destination_bucket.name,
        )
    )


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


def upload(result: List[dict], s3_target: str):
    """
    Uploads metadata and images for every run in s3.\

    :param result: list of dict resulted from querying postgres
    :param s3_obj: s3fs object
    :param s3_target: s3 path for specific run
    :return: None
    """
    # NOTE: example location to store the images
    bucket_name = "tcc-clothes"
    destination_blob_name = f"{s3_target}/metadata.json"
    upload_blob_from_memory(
        bucket_name,
        json.dumps(result),
        destination_blob_name,
        content_type="application/json",
    )

    for res in result:
        image_id = res["image_id"]
        blob_name = f"fashion-datasets/dataset-v1/{image_id}.jpg"
        new_name = f"{s3_target}/images/{image_id}.jpg"
        copy_blob(bucket_name, blob_name, bucket_name, new_name)


from io import BytesIO
from PIL import Image


def download_blob_into_memory(bucket_name, blob_name):
    """Downloads a blob into memory."""
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return contents


def run_augmentations(aug_conf: dict, result: List[dict], s3_target: str):
    """
    Apply augmentation to images from current run.

    :param aug_conf: augmentation config coming from input
    :param result: list of dict resulted from querying postgre
    :param s3_obj: s3fs object
    :param s3_target: s3 path for specific run
    """
    for res in result:
        image_id = res["image_id"]
        min_height = aug_conf["cropping"]["height"]["min"]
        max_height = aug_conf["cropping"]["height"]["max"]
        width_resized = aug_conf["resize"]["width"]
        height_resized = aug_conf["resize"]["height"]
        bucket_name = "tcc-clothes"

        img = download_blob_into_memory(
            bucket_name, f"{s3_target}/images/{image_id}.jpg"
        )
        image = np.asarray(Image.open(BytesIO(img)))

        transform = A.Compose(
            [
                A.RandomSizedCrop(
                    min_max_height=(min_height, max_height),
                    height=height_resized,
                    width=width_resized,
                )
            ]
        )
        random.seed(42)
        _, augmented_image = cv2.imencode(".jpg", transform(image=image)["image"])

        destination_blob_name = f"{s3_target}/augmentation/{image_id}.jpg"
        upload_blob_from_memory(
            bucket_name,
            augmented_image.tobytes(),
            destination_blob_name,
            content_type="text/plain",
        )


def filter_task(self, **kwargs) -> Dict[str, Any]:
    """
    Defines the celery task to query SQL database and filter products.

    :returns: s3 path containing file with filtered data according to input
    """
    query = kwargs.get("query")
    aug_conf = kwargs.get("aug_config")
    s3_target = f"{BUCKET_NAME}/{self.request.id}"
    return {"s3_target": s3_target}
