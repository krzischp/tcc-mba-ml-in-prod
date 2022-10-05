"""Imagery Celery worker"""
import json
import random
from concurrent.futures import TimeoutError
from io import BytesIO
from typing import List

import albumentations as A
import cv2
import numpy as np
from PIL import Image
from google.cloud import pubsub_v1
from google.cloud import storage

PROJECT_ID = "tcc-lucas-pierre"
SUBSCRIPTION_ID = "imagery-sub"
BUCKET_NAME = "tcc-clothes"
TIMEOUT = 5.0


def copy_blob(bucket_name, blob_name, destination_bucket_name, destination_blob_name):
    """Copies a blob from one bucket to another with a new name."""
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


def consume_messages():
    """Initializes PubSub subscriber"""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=process_messages
    )
    print(f"Listening for messages on {subscription_path}.\n")

    with subscriber:
        try:
            streaming_pull_future.result(timeout=TIMEOUT)
        except TimeoutError:
            streaming_pull_future.cancel()
            streaming_pull_future.result()


def download_blob_into_memory(bucket_name, blob_name):
    """Downloads a blob into memory."""
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return contents


def process_messages(message: pubsub_v1.subscriber.message.Message) -> None:
    """Callback method to PubSub subscriber"""
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
                FROM products
                WHERE gender = '{message.gender}' AND
                      sub_category = '{message.sub_category}' AND
                      year = '{message.start_year}'
                LIMIT {message.limit}"""

    message.ack()


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


def upload_blob_from_memory(
    bucket_name, contents, destination_blob_name, content_type="text/plain"
):
    """Uploads a file to the bucket."""
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

    destination_blob_name = f"{s3_target}/metadata.json"
    upload_blob_from_memory(
        BUCKET_NAME,
        json.dumps(result),
        destination_blob_name,
        content_type="application/json",
    )

    for res in result:
        image_id = res["image_id"]
        blob_name = f"fashion-datasets/dataset-v1/{image_id}.jpg"
        new_name = f"{s3_target}/images/{image_id}.jpg"
        copy_blob(BUCKET_NAME, blob_name, BUCKET_NAME, new_name)


if __name__ == "__main__":
    print(f"Consuming messages from Subscription {SUBSCRIPTION_ID}")
    while True:
        consume_messages()
