"""Helper for inference"""
from __future__ import annotations

from io import BytesIO

import albumentations as A
import numpy as np
from PIL import Image
from albumentations.pytorch import ToTensorV2
from google.cloud import storage
from torch.utils.data import Dataset


def download_blob_into_memory(bucket_name, blob_name):
    """Downloads a blob into memory."""
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return contents


class ImagesDataset(Dataset):
    def __init__(self, images_filepaths: list[str], device: str = "cpu"):
        self._images_filepaths = images_filepaths
        self._transform = A.Compose([A.Resize(224, 224), ToTensorV2()])
        self._device = device

    def __len__(self) -> int:
        return len(self._images_filepaths)

    def __getitem__(self, idx: int):
        image_name = self._images_filepaths[idx]
        bucket_name = "tcc-clothes"
        img = download_blob_into_memory(bucket_name, image_name)
        image = np.asarray(Image.open(BytesIO(img))).astype(np.float32)

        if self._transform:
            image = self._transform(image=image)["image"]

        return image.to(self._device), image_name
