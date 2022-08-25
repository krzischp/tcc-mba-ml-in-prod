# pylint: disable-all
"""Celery Worker that implements VGG16"""
import json
import os
from typing import Any, Dict, List

import s3fs
import torch
from celery import Celery
from celery.utils.log import get_logger
from torch.utils.data import DataLoader

from deepfashion import FashionNetVgg16NoBn
from utils.dataset import ImagesDataset

logger = get_logger(__name__)
inference = Celery(
    "inference", broker=os.getenv("BROKER_URL"), backend=os.getenv("REDIS_URL")
)


def upload(result: List[dict], s3_obj, s3_target: str):
    """
    Uploads predictions to S3.

    :param result: list of dict resulted from inference
    :param s3_obj: s3fs object
    :param s3_target: s3 path for specific run
    :return: None
    """
    logger.info("Uploading metadata and images")

    # NOTE: example location to store the images
    with s3_obj.open(f"{s3_target}/predictions.json", "w") as meta_f:
        json.dump(result, meta_f)


@inference.task(name="model")
def inference_task(**kwargs) -> Dict[str, Any]:
    """
    Run inference on image created on Step1 and Step2 using this FashionNetVgg16NoBn implementation
    from https://github.com/i008/pytorch-deepfashion.git
    """
    s3_target = kwargs.get("s3_target")
    logger.info(f"Start executing prediction task - s3 target: {s3_target}")

    s3_obj = s3fs.S3FileSystem(client_kwargs={"endpoint_url": f'http://{os.getenv("S3_HOST")}:4566'})
    fn = FashionNetVgg16NoBn()

    # pose network needs to be trained from scratch? i guess?
    for k in fn.state_dict().keys():
        if 'conv5_pose' in k and 'weight' in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])
            logger.info(f"filling xavier {k}")

    for k in fn.state_dict().keys():
        if 'conv5_global' in k and 'weight' in k:
            torch.nn.init.xavier_normal_(fn.state_dict()[k])
            logger.info(f"filling xavier {k}")

    images_filepaths = []
    for file in s3_obj.ls(f"{s3_target}/images"):
        images_filepaths.append(file)

    for file in s3_obj.ls(f"{s3_target}/augmented"):
        images_filepaths.append(file)

    images_dataset = ImagesDataset(images_filepaths=images_filepaths, s3_obj=s3_obj)
    loader = DataLoader(images_dataset)
    predicted_labels = []
    with torch.no_grad():
        for image, image_name in loader:
            output = fn(image)
            predicted_labels.append({"image_name": image_name,
                                     "massive_attr": output[0].tolist(),
                                     "categories": output[1].tolist()})
    upload(result=predicted_labels, s3_target=s3_target, s3_obj=s3_obj)

    return {"s3_target": s3_target}
