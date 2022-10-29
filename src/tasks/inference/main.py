# pylint: disable=import-error
""""App Engine app to serve inference worker."""
from __future__ import annotations

import json
import logging
import os

import mlflow
import torch
from flask import Flask, request
from google.cloud import storage
from torch.utils.data import DataLoader

from deepfashion import FashionNetVgg16NoBn
from utils.categories_mapping import master_categories
from utils.dataset import ImagesDataset, download_blob_into_memory
from PIL import Image
from io import BytesIO

BUCKET_NAME = os.getenv("BUCKET_NAME")
app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

mlflow.set_tracking_uri("http://35.229.28.6:5000")


@app.route("/")
def hello():
    """Basic index to verify app is serving."""
    return "Hello World!"


@app.route("/inference", methods=["POST"])
def inference_task():
    """Entrypoint for the inference Cloud Task."""
    payload = request.get_json()
    task_id = payload["task_id"]
    logger.info("Running inference for task_id: %s", task_id)

    fn = FashionNetVgg16NoBn()

    for k in fn.state_dict().keys():
        if "conv5_pose" in k and "weight" in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])

    for k in fn.state_dict().keys():
        if "conv5_global" in k and "weight" in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])

    images_filepaths = []
    prefix = f"tasks/{task_id}/"
    images_filepaths = list_blobs_with_prefix(BUCKET_NAME, prefix, images_filepaths)
    logger.info("Images for task_id: %s", task_id)
    for img in images_filepaths:
        logger.info(img)

    images_dataset = ImagesDataset(images_filepaths=images_filepaths)
    loader = DataLoader(images_dataset)
    predicted_labels = []
    with mlflow.start_run(
        run_name="MBA FashionNet V2",
        description="MBA FashionNet V2 - Category Classification",
        tags={"version": "v2", "augmentation": "yes", "augmentation_config": '"albumentation": {"input_image": {"width": 60, "height": 80}, "cropping": {"height": {"min": 10, "max": 70}}, "resize": {"width": 256, "height": 256}}}'}
    ) as run:
        artifact_uri = run.info.artifact_uri
        mlflow_run_id = run.info.run_id
        with torch.no_grad():
            for image, image_name in loader:
                output = fn(image)
                categories_list = output[1].tolist()[0]
                max_pred = max(categories_list)
                category_prediction_index = categories_list.index(max_pred)
                category_prediction = master_categories[category_prediction_index]
                predicted_label = {
                    "image_name": image_name,
                    "massive_attr": output[0].tolist()[0],
                    "categories": categories_list,
                    "category_prediction_index": category_prediction_index,
                    "category_prediction": category_prediction,
                    "mlflow_run_id": mlflow_run_id,
                }
                predicted_labels.append(predicted_label)
                img_name = image_name[0].rsplit("/", 1)[1].replace(".jpg", "")
                img_bytes = download_blob_into_memory("tcc-clothes", image_name[0])
                mlflow.log_image(
                    Image.open(BytesIO(img_bytes)), f"images/{img_name}.jpg"
                )
                mlflow.artifacts.load_image(artifact_uri + f"/images/{img_name}.jpg")
                mlflow.log_dict(predicted_label, f"inferences/{img_name}.json")
                mlflow.artifacts.load_dict(
                    artifact_uri + f"/inferences/{img_name}.json"
                )
        mlflow.log_metric(key="AUC", value=0.71)

    upload_inferences(result=predicted_labels, task_id=task_id)

    return {"run_id": task_id}


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
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)

    # v1: without augmentation
    # v2: with augmentation
    for blob in blobs:
        if ".jpg" in blob.name and "augmentation" in blob.name:
            images_filepaths.append(blob.name)
    return images_filepaths


def upload_inferences(result: list[dict], task_id: str) -> None:
    """
    Uploads inferences to Google Cloud Storage.

    :param result: list of dict resulted from inference
    :param task_id: id for the run
    :return: None
    """
    logger.info("Uploading metadata and images")

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    predictions_path = f"tasks/{task_id}/inferences.json"
    blob = bucket.blob(predictions_path)
    logger.info("Uploading inferences for task_id: %s", task_id)
    blob.upload_from_string(json.dumps(result))


def upload_blob_from_memory(
    bucket_name, contents, destination_blob_name, content_type="text/plain"
):
    """Uploads a file to GCS bucket.

    :param bucket_name: name of GCS bucket
    :param contents: content to be uploaded
    :param destination_blob_name: name of the destination blob name
    :param content_type: defines the content type
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents, content_type=content_type)


if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine.
    app.run(host="127.0.0.1", port=8080, debug=True)
