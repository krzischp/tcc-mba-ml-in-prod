from typing import List

import albumentations as A
import numpy as np
from PIL import Image
from io import BytesIO
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset
from google.cloud import storage


# TODO:
# put this function (also in imagery/worker.py) in a unique utils file
def download_blob_into_memory(bucket_name, blob_name):
    """Downloads a blob into memory."""
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return contents


class ImagesDataset(Dataset):
    def __init__(self, images_filepaths: List[str], device: str = "cpu"):
        self._images_filepaths = images_filepaths
        self._transform = A.Compose([A.Resize(224, 224), ToTensorV2()])
        self._device = device

    def __len__(self) -> int:
        return len(self._images_filepaths)

    def __getitem__(self, idx: int) -> dict:
        image_name = self._images_filepaths[idx]
        # with self.s3_obj.open(image_name, 'rb') as f:
        #     image = np.array(Image.open(f)).astype(np.float32)
        bucket_name = "tcc-clothes"
        img = download_blob_into_memory(bucket_name, image_name)
        image = np.asarray(Image.open(BytesIO(img))).astype(np.float32)

        if self._transform:
            image = self._transform(image=image)["image"]

        return image.to(self._device), image_name
