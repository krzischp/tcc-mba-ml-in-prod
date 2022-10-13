"""Runs CD4ML Pipeline Task to compare classifier models"""
import json
import logging
import os
import sys
import time

import requests
from google.cloud import storage
from mlflow import MlflowClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_ENDPOINT = f'http://{os.getenv("API_HOST")}:5000'
PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")

LIMIT = 10
YEAR = 2012


def download_blob_into_memory(blob_name):
    """Downloads a blob into memory."""
    storage_client = storage.Client()

    bucket = storage_client.bucket(BUCKET_NAME)

    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return contents


def perform_task(params, endpoint):
    api_response = requests.post(f"{API_ENDPOINT}/{endpoint}", json=params).json()
    task_id = api_response["task_id"]
    queue = api_response["queue"]
    print(f"task_id: {task_id}")
    print(f"queue: {queue}")

    status = "PENDING"
    print("Processing...")
    while status == "PENDING":
        time.sleep(3)
        response = requests.get(
            f"{API_ENDPOINT}/task/{task_id}", params={"queue": f"{queue}"}
        ).json()
        status = response["status"]
        print(status)

    if status != "SUCCESS":
        raise Exception(response)
    else:
        print("Task complete!")

    return task_id


def run_imagery(queue: str):
    payload = {
        "queue": queue,
        "gender": "Women",
        "sub_category": "Dress",
        "start_year": YEAR,
        "limit": LIMIT,
        "augmentation_config": {
            "albumentation": {
                "input_image": {"width": 60, "height": 80},
                "cropping": {"height": {"min": 10, "max": 70}},
                "resize": {"width": 256, "height": 256},
            }
        },
    }
    run_id = perform_task(payload, "filter")

    return run_id


def run_inference(run_id: str, queue: str):
    perform_task({"task_id": run_id, "queue": queue}, "predict")
    bucket_file = f"tasks/{run_id}/inferences.json"
    content = download_blob_into_memory(bucket_file)
    predictions = json.loads(content)
    logger.info(f"Number of predictions: {len(predictions)}")
    logger.info(
        f'Prediction output per image: massive_attr-{len(predictions[0]["massive_attr"])}, '
        f'categories-{len(predictions[0]["categories"])}'
    )

    for idx, predict in enumerate(predictions, 1):
        logger.info(
            f'Image number {idx} ----- mlflow_run_id: {predict["mlflow_run_id"]} '
            f'image_id: {predict["image_name"][0].rsplit("/", 1)[1]} '
            f'category_prediction: {predict["category_prediction"]}'
        )
        mlflow_run_id = predict["mlflow_run_id"]

    client = MlflowClient(tracking_uri=f'http://{os.getenv("MLFLOW_HOST")}:5000')
    history = client.get_metric_history(mlflow_run_id, "AUC")

    return history[0].value


if __name__ == "__main__":
    branch_name = sys.argv[1]
    auc_threshold = sys.argv[2]
    logger.info("Branch Name: %s", branch_name)
    logger.info("AUC threshold: %s", auc_threshold)

    logger.info("Running inference for current model")
    run_id_prod = run_imagery(queue="imagery")
    auc_prod = run_inference(run_id=run_id_prod, queue="inference")

    logger.info("Running inference for candidate model")
    run_id_candidate = run_imagery(queue=f"imagery-{branch_name}")
    auc_candidate = run_inference(run_id=run_id_prod, queue=f"inference-{branch_name}")

    logger.info("AUC Prod: %s", auc_prod)
    logger.info("AUC Candidate branch %s: %s", branch_name, auc_candidate)
    logger.info("AUC Threshold: %s", auc_threshold)

    if auc_prod < auc_candidate or auc_candidate < auc_threshold:
        logger.info("Requisites for new model were not match!")
        sys.exit(1)
