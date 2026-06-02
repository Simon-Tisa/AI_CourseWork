from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset


class SegmentationDataset(Dataset):
    def __init__(
        self,
        image_ids: list[str],
        image_dir: str | Path,
        mask_dir: str | Path,
        image_ext: str = ".png",
        mask_ext: str = ".png",
        transform=None,
    ) -> None:
        self.image_ids = image_ids
        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.image_ext = image_ext
        self.mask_ext = mask_ext
        self.transform = transform

    def __len__(self) -> int:
        return len(self.image_ids)

    def __getitem__(self, index: int):
        image_id = self.image_ids[index]
        image_path = self.image_dir / f"{image_id}{self.image_ext}"
        mask_path = self.mask_dir / f"{image_id}{self.mask_ext}"
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Image not found or unreadable: {image_path}")
        if mask is None:
            raise FileNotFoundError(f"Mask not found or unreadable: {mask_path}")

        mask = mask[..., None]
        if self.transform is not None:
            augmented = self.transform(image=image, mask=mask)
            image = augmented["image"]
            mask = augmented["mask"]

        image = image.astype("float32")
        if image.min() >= 0.0 and image.max() > 1.0:
            image = image / 255.0
        mask = (mask.astype("float32") / 255.0 >= 0.5).astype("float32")
        image = torch.from_numpy(image.transpose(2, 0, 1))
        mask = torch.from_numpy(mask.transpose(2, 0, 1))
        return image, mask, {"image_id": image_id}
