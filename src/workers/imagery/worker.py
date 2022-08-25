"""Imagery Celery worker"""
import json
import os
import random
from typing import Any, Dict, List

import albumentations as A
import cv2
import numpy as np
import s3fs
from PIL import Image
from celery import Celery
from celery.utils.log import get_logger

from app.database import PostgreDB

BUCKET_NAME = os.getenv("BUCKET_NAME", "")
DATA_FOLDER = os.getenv("DATA_FOLDER", "")
S3_HOST = os.getenv("S3_HOST", "")

logger = get_logger(__name__)
imagery = Celery(
    "imagery", broker=os.getenv("BROKER_URL"), backend=os.getenv("REDIS_URL")
)
psql = PostgreDB()


def upload(result: List[dict], s3_obj, s3_target: str):
    """
    Uploads metadata and images for every run in s3.\

    :param result: list of dict resulted from querying postgres
    :param s3_obj: s3fs object
    :param s3_target: s3 path for specific run
    :return: None
    """
    logger.info("Uploading metadata and images")

    # NOTE: example location to store the images
    with s3_obj.open(f"{s3_target}/metadata.json", "w") as meta_f:
        json.dump(result, meta_f)

    for res in result:
        image_id = res["image_id"]
        logger.info(f"Uploading {image_id}.jpg")
        s3_obj.cp(f"s3://fashion-datasets/dataset-v1/{image_id}.jpg",
                  f"{s3_target}/images/{image_id}.jpg")


def run_augmentations(aug_conf: dict, result: List[dict], s3_obj, s3_target: str):
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
        logger.info(f"Applying augmentation: {image_id}.jpg")
        logger.info(f"min_height: {min_height}")
        logger.info(f"max_height: {max_height}")
        logger.info(f"Width after resize: {width_resized}")
        logger.info(f"Height after resize: {height_resized}")
        with s3_obj.open(f"{s3_target}/images/{image_id}.jpg") as original_img:
            image = np.array(Image.open(original_img))

        transform = A.Compose(
            [A.RandomSizedCrop(min_max_height=(min_height, max_height),
                               height=height_resized,
                               width=width_resized)]
        )
        random.seed(42)
        _, augmented_image = cv2.imencode('.jpg', transform(image=image)['image'])

        with s3_obj.open(f"{s3_target}/augmentation/{image_id}.jpg", "wb") as aug_f:
            aug_f.write(augmented_image.tostring())


@imagery.task(bind=True, name="filter")
def filter_task(self, **kwargs) -> Dict[str, Any]:
    """
    Defines the celery task to query SQL database and filter products.

    :returns: s3 path containing file with filtered data according to input
    """
    query = kwargs.get("query")
    aug_conf = kwargs.get("aug_config")
    s3_obj = s3fs.S3FileSystem(client_kwargs={"endpoint_url": f"http://{S3_HOST}:4566"})
    s3_target = f"s3://{BUCKET_NAME}/{self.request.id}"
    result = psql.filter_products(query=query)
    upload(result=result, s3_obj=s3_obj, s3_target=s3_target)
    if aug_conf:
        logger.info("Starting augmentation")
        run_augmentations(aug_conf=aug_conf, s3_target=s3_target, s3_obj=s3_obj, result=result)

    return {"s3_target": s3_target}
