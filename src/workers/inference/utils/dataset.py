from typing import List

import albumentations as A
import numpy as np
import torch
from PIL import Image
from albumentations.pytorch import ToTensorV2
from torch.utils.data import Dataset


class ImagesDataset(Dataset):
    def __init__(
            self,
            images_filepaths: List[str],
            device: str = "cpu",
            s3_obj=None,
    ):
        self._images_filepaths = images_filepaths
        self._transform = A.Compose([A.Resize(224, 224), ToTensorV2()])
        self._device = device
        self.s3_obj = s3_obj

    def __len__(self) -> int:
        return len(self._images_filepaths)

    def __getitem__(self, idx: int) -> dict:
        image_name = self._images_filepaths[idx]
        with self.s3_obj.open(image_name, 'rb') as f:
            image = np.array(Image.open(f)).astype(np.float32)

        if self._transform:
            image = self._transform(image=image)["image"]

        return image.to(self._device), image_name
