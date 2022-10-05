# pylint: disable=too-few-public-methods,import-error,no-name-in-module
"""Entrypoint for classifier API"""
from typing import Optional

from fastapi import FastAPI
from google.cloud import tasks_v2
from pydantic import BaseModel
from starlette.responses import JSONResponse

PROJECT_ID = "tcc-lucas-pierre"
LOCATION = "southamerica-east1"
QUEUE_IMAGERY = "imagery"
client = tasks_v2.CloudTasksClient()

parent = client.queue_path(PROJECT_ID, LOCATION, QUEUE_IMAGERY)


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


class InferenceModel(BaseModel):
    """Defines attributes for inference model"""

    s3_target: str

@app.post("/filter", status_code=201)
async def upload_images(data: FilterProductsModel):
    """
    Builds query to filter products in database and send as parameter to a Cloud Task.

    :param data: request input
    :returns: Cloud Task id
    """
    task = {
        "app_engine_http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "relative_uri": "/augmentation",
        }
    }
    task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
    converted_payload = data.json().encode("utf-8")
    task["app_engine_http_request"]["body"] = converted_payload
    response = client.create_task(parent=parent, task=task)
    print(f"Created task {response.name}")

    return JSONResponse({"task_id": response.name.split("tasks/")[1]})


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
    try:
        request = tasks_v2.GetTaskRequest(
            name=f"projects/{PROJECT_ID}/locations/{LOCATION}/queues/{QUEUE_IMAGERY}/tasks/{task_id}",
        )
        response = client.get_task(request=request)
        first_attempt = response.first_attempt if response.first_attempt else None
        status = "FAILED" if first_attempt else "PENDING"
        return JSONResponse({"status": status})
    except Exception as ex:
        print(ex)
        return JSONResponse({"status": "SUCCESS"})
