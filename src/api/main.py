# pylint: disable=too-few-public-methods,import-error,no-name-in-module
"""Entrypoint for classifier API"""
from typing import Optional, Any

from fastapi import FastAPI
from google.cloud import pubsub_v1
from pydantic import BaseModel
from starlette.responses import JSONResponse

PROJECT_ID = "tcc-lucas-pierre"
TOPIC_ID = "tcc_mba"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

app = FastAPI()


class FilterProductsModel(BaseModel):
    """Defines attributes for filter products model"""

    gender: str
    master_category: Optional[str]
    sub_category: Optional[str]
    article_type: Optional[str]
    base_colour: Optional[str]
    season: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    limit: Optional[int]
    usage: Optional[str]
    augmentation_config: Optional[dict] = None


class TaskResult(BaseModel):
    """Defines attributes for task result model"""

    id: str
    status: str
    error: Optional[str] = None
    result: Optional[Any] = None


class InferenceModel(BaseModel):
    """Defines attributes for inference model"""

    s3_target: str


@app.post("/filter", status_code=201)
async def upload_images(data: FilterProductsModel):
    """
    Builds query to filter products in database and send as parameter to a PubSub topic.

    :param data: request input
    :returns: PubSub message id
    """
    future = publisher.publish(topic_path, data.json().encode("utf-8"))
    task_id = future.result()

    return JSONResponse({"task_id": task_id})


@app.post("/predict", status_code=201)
async def predict_images(data: InferenceModel):
    """
    Wrapper to make inferences about images. Calls a async task.

    :param data: request input
    """
    return "Hello"


@app.get("/task/{task_id}", status_code=200)
def get_task_result(task_id: str):
    """
    Use this endpoint to check the status of a task
    """

    return "Hello"
