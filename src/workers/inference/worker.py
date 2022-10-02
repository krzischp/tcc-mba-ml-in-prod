# pylint: disable-all
"""Celery Worker that implements VGG16"""
import json
import os
from typing import Any, Dict

import torch
from celery import Celery
from celery.utils.log import get_logger
from torch.utils.data import DataLoader
from google.cloud import storage

from deepfashion import FashionNetVgg16NoBn
from utils.dataset import ImagesDataset

logger = get_logger(__name__)
inference = Celery(
    "inference", broker=os.getenv("BROKER_URL"), backend=os.getenv("REDIS_URL")
)


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
        # print(blob.name)
        images_filepaths.append(blob.name)
    return images_filepaths


# TODO:
# put this function (also in imagery/worker.py) in a unique utils file
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


@inference.task(name="model")
def inference_task(**kwargs) -> Dict[str, Any]:
    """
    Run inference on image created on Step1 and Step2 using this FashionNetVgg16NoBn implementation
    from https://github.com/i008/pytorch-deepfashion.git
    """
    s3_target = kwargs.get("s3_target")
    logger.info(f"Start executing prediction task - s3 target: {s3_target}")

    fn = FashionNetVgg16NoBn()

    # pose network needs to be trained from scratch? i guess?
    for k in fn.state_dict().keys():
        if "conv5_pose" in k and "weight" in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])
            logger.info(f"filling xavier {k}")

    for k in fn.state_dict().keys():
        if "conv5_global" in k and "weight" in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])
            logger.info(f"filling xavier {k}")

    images_filepaths = []
    bucket_name = "tcc-clothes"
    prefix = f"{s3_target}/images"
    images_filepaths = list_blobs_with_prefix(bucket_name, prefix, images_filepaths)

    prefix = f"{s3_target}/augmented"
    images_filepaths = list_blobs_with_prefix(bucket_name, prefix, images_filepaths)

    images_dataset = ImagesDataset(images_filepaths=images_filepaths)
    loader = DataLoader(images_dataset)
    predicted_labels = []
    with torch.no_grad():
        for image, image_name in loader:
            output = fn(image)
            predicted_labels.append(
                {
                    "image_name": image_name,
                    "massive_attr": output[0].tolist(),
                    "categories": output[1].tolist(),
                }
            )
    bucket_name = "tcc-clothes"
    destination_blob_name = f"{s3_target}/predictions.json"
    logger.info("Uploading metadata and images")
    upload_blob_from_memory(
        bucket_name,
        json.dumps(predicted_labels),
        destination_blob_name,
        content_type="application/json",
    )
    return {"s3_target": s3_target}
