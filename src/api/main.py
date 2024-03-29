# pylint: disable=too-few-public-methods,import-error,no-name-in-module
"""Defines the image classifier API"""
from typing import Optional

from fastapi import FastAPI
from google.cloud import tasks_v2
from pydantic import BaseModel
from starlette.responses import JSONResponse

PROJECT_ID = "tcc-lucas-pierre"
LOCATION = "southamerica-east1"

client = tasks_v2.CloudTasksClient()

app = FastAPI()


class ImageryModel(BaseModel):
    """Defines attributes for imagery model"""

    queue: str
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


class InferenceModel(BaseModel):
    """Defines attributes for inference model"""

    queue: str
    task_id: str


@app.get("/task/{task_id}", status_code=200)
def get_task_result(task_id: str, queue: str):
    """
    Use this endpoint to check the status of a task

    :param task_id: Cloud Task id
    :param queue: queue to fetch task id status
    """
    try:
        req = tasks_v2.GetTaskRequest(
            name=f"projects/{PROJECT_ID}/locations/{LOCATION}/queues/{queue}/tasks/{task_id}",
        )
        response = client.get_task(request=req)
        first_attempt = response.first_attempt if response.first_attempt else None
        status = "FAILED" if first_attempt else "PENDING"
        return JSONResponse({"status": status})
    except Exception:
        return JSONResponse({"status": "SUCCESS"})


@app.post("/filter", status_code=201)
async def imagery(data: ImageryModel):
    """
    Creates async Cloud Task for imagery worker.

    :param data: request input
    :returns: Cloud Task id
    """
    task = {
        "app_engine_http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "relative_uri": "/imagery",
        }
    }
    task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
    queue = data.dict().get("queue")
    print(queue)
    converted_payload = data.json().encode("utf-8")
    task["app_engine_http_request"]["body"] = converted_payload
    parent_imagery = client.queue_path(PROJECT_ID, LOCATION, queue)

    response = client.create_task(parent=parent_imagery, task=task)

    return JSONResponse(
        {"task_id": response.name.split("tasks/")[1], "queue": queue}
    )


@app.post("/predict", status_code=201)
async def inference(data: InferenceModel):
    """
    Wrapper to make inferences about images. Calls a async Cloud Task.

    :param data: request input
    """
    queue = data.dict().get("queue")
    print(queue)
    parent_inference = client.queue_path(PROJECT_ID, LOCATION, queue)

    task = {
        "app_engine_http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "relative_uri": "/inference",
        }
    }
    task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
    converted_payload = data.json().encode("utf-8")
    task["app_engine_http_request"]["body"] = converted_payload
    response = client.create_task(parent=parent_inference, task=task)

    return JSONResponse({"task_id": response.name.split("tasks/")[1], "queue": queue})
