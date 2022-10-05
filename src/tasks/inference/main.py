"""App Engine app to serve as an endpoint for App Engine queue samples."""
from __future__ import annotations

import json
import logging
import os
import random
from io import BytesIO

import albumentations as A
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from google.cloud import bigquery
from google.cloud import storage

BUCKET_NAME = os.getenv("BUCKET_NAME")
app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = bigquery.Client()


@app.route("/augmentation", methods=["POST"])
def augmentation():
    """Log the request payload."""
    images_to_upload = []
    payload = request.get_json()
    task_id = request.headers.get("X-Appengine-Taskname")
    query = f"""SELECT image_id,
                           gender,
                           master_category,
                           sub_category,
                           article_type,
                           base_colour,
                           season,
                           year,
                           usage,
                           display_name
                    FROM tcc.products
                    WHERE gender = '{payload["gender"]}' AND
                          sub_category = '{payload["sub_category"]}' AND
                          year = {payload["start_year"]}
                    LIMIT {payload["limit"]}"""

    metadata = []
    logger.info("Query: %s", query)
    query_job = client.query(query).result()
    for row in query_job:
        image_id = row.image_id
        image_filename = f"{image_id}.jpg"
        logger.info("Image Filename: %s", image_filename)
        images_to_upload.append(image_filename)
        metadata.append(
            {
                "image_id": row.image_id,
                "gender": row.gender,
                "master_category": row.master_category,
                "sub_category": row.sub_category,
                "article_type": row.article_type,
                "base_colour": row.base_colour,
                "season": row.season,
                "year": row.year,
                "usage": row.usage,
                "display_name": row.display_name,
            }
        )

    upload(images_to_upload, task_id, metadata)
    aug_conf = payload.get("augmentation_config")
    if aug_conf:
        logger.info("Starting augmentation")
        logger.info("AUG_CONF: %s", aug_conf)
        run_augmentations(
            aug_conf=aug_conf,
            task_id=task_id,
            metadata=metadata,
        )

    return jsonify({"task_id": task_id})


def copy_blob(blob_name, destination_blob_name):
    """Copies a blob from one bucket to another with a new name."""
    storage_client = storage.Client()

    source_bucket = storage_client.get_bucket(BUCKET_NAME)
    destination_bucket = storage_client.get_bucket(BUCKET_NAME)
    source_blob = source_bucket.get_blob(blob_name)
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


@app.route("/")
def hello():
    """Basic index to verify app is serving."""
    return "Hello World!"


def run_augmentations(aug_conf: dict, metadata: list[dict], task_id: str):
    """
    Apply augmentation to images from current run.

    :param aug_conf: augmentation config coming from input
    :param metadata: list of dict resulted from querying BigQuery
    :param task_id: s3 path for specific run
    """
    storage_client = storage.Client()
    source_bucket = storage_client.get_bucket(BUCKET_NAME)
    destination_bucket = storage_client.get_bucket(BUCKET_NAME)

    for res in metadata:
        image_id = res["image_id"]
        min_height = aug_conf["albumentation"]["cropping"]["height"]["min"]
        max_height = aug_conf["albumentation"]["cropping"]["height"]["max"]
        width_resized = aug_conf["albumentation"]["resize"]["width"]
        height_resized = aug_conf["albumentation"]["resize"]["height"]
        logger.info(f"Applying augmentation: {image_id}.jpg")
        logger.info(f"min_height: {min_height}")
        logger.info(f"max_height: {max_height}")
        logger.info(f"Width after resize: {width_resized}")
        logger.info(f"Height after resize: {height_resized}")
        source_blob_path = f"fashion-tasks/{task_id}/images/{image_id}.jpg"

        logger.info("SOURCE BLOB PATH: %s", source_blob_path)
        source_blob = source_bucket.get_blob(source_blob_path)
        logger.info("SOURCE BLOB: %s", source_blob)

        original_img = source_blob.download_as_bytes()
        image = np.asarray(Image.open(BytesIO(original_img)))

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

        destination_blob = source_bucket.blob(
            f"fashion-tasks/{task_id}/augmentation/{image_id}.jpg"
        )
        print(
            "AUGMENTATION - Blob {} in bucket {} copied to blob {} in bucket {}.".format(
                source_blob.name,
                source_bucket.name,
                destination_blob.name,
                destination_bucket.name,
            )
        )
        destination_blob.upload_from_string(augmented_image.tobytes())


def upload(result: list, task_id: str, metadata: list[dict]):
    """
    Uploads metadata and images for every run in s3.\

    :param result: list of dict resulted from querying postgres
    :param task_id: gcp path for specific run
    :param metadata: task metadata
    :return: None
    """
    metadata_path = f"fashion-tasks/{task_id}/metadata.json"
    logger.info(f"Writing metadata into {metadata_path}")
    write_metadata(metadata, metadata_path)

    for image_id in result:
        blob_name = f"images/{image_id}"
        new_name = f"fashion-tasks/{task_id}/images/{image_id}"
        logger.info(f"Copying {blob_name} into {new_name}")
        copy_blob(blob_name, new_name)


def write_metadata(metadata, metadata_path):
    """Copies a blob from one bucket to another with a new name."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(metadata_path)
    blob.upload_from_string(json.dumps(metadata))


if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
