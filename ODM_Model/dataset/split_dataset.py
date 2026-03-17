# dataset/split_dataset.py
"""
Dataset class that uses a pre-defined list of image IDs.
Used for train/val splitting without moving files.
"""

import os
import torch
from torch.utils.data import Dataset
from pycocotools.coco import COCO
from PIL import Image

from dataset.coco_dataset import (
    TARGET_COCO_IDS,
    COCO_ID_TO_LABEL,
    LABEL_TO_NAME,
)


class SplitCOCODataset(Dataset):
    """
    Like COCODataset but accepts a fixed list of image IDs.
    Allows train/val splits from the same annotation file
    and same image folder.

    Args:
        img_dir    : path to images folder
        ann_file   : path to COCO annotation JSON
        image_ids  : list of image IDs to use
        transforms : transform pipeline
    """

    def __init__(
        self,
        img_dir:   str,
        ann_file:  str,
        image_ids: list,
        transforms = None,
    ):
        self.img_dir    = img_dir
        self.transforms = transforms
        self.coco       = COCO(ann_file)

        # Only keep IDs that have target class annotations
        target_ids = set()
        for cid in TARGET_COCO_IDS:
            target_ids.update(
                self.coco.getImgIds(catIds=[cid])
            )

        # Intersect with our split IDs
        self.img_ids = [
            iid for iid in image_ids
            if iid in target_ids
        ]

        print(f"  SplitDataset: {len(self.img_ids)} images "
              f"with target classes")

    def __len__(self):
        return len(self.img_ids)

    def __getitem__(self, idx):
        img_id   = self.img_ids[idx]
        img_info = self.coco.loadImgs(img_id)[0]
        img_path = os.path.join(
            self.img_dir, img_info["file_name"]
        )
        image    = Image.open(img_path).convert("RGB")

        # Load annotations
        ann_ids = self.coco.getAnnIds(
            imgIds   = img_id,
            catIds   = list(TARGET_COCO_IDS),
            iscrowd  = None,
        )
        anns = self.coco.loadAnns(ann_ids)

        boxes, labels, areas, iscrowd = [], [], [], []

        for ann in anns:
            if ann["category_id"] not in TARGET_COCO_IDS:
                continue
            x, y, w, h = ann["bbox"]
            if w <= 1 or h <= 1:
                continue
            boxes.append([x, y, x + w, y + h])
            labels.append(COCO_ID_TO_LABEL[ann["category_id"]])
            areas.append(ann["area"])
            iscrowd.append(int(ann.get("iscrowd", 0)))

        if len(boxes) == 0:
            target = {
                "boxes":    torch.zeros((0, 4),
                            dtype=torch.float32),
                "labels":   torch.zeros((0,),
                            dtype=torch.int64),
                "area":     torch.zeros((0,),
                            dtype=torch.float32),
                "iscrowd":  torch.zeros((0,),
                            dtype=torch.uint8),
                "image_id": torch.tensor([img_id],
                            dtype=torch.int64),
            }
        else:
            target = {
                "boxes":    torch.tensor(boxes,
                            dtype=torch.float32),
                "labels":   torch.tensor(labels,
                            dtype=torch.int64),
                "area":     torch.tensor(areas,
                            dtype=torch.float32),
                "iscrowd":  torch.tensor(iscrowd,
                            dtype=torch.uint8),
                "image_id": torch.tensor([img_id],
                            dtype=torch.int64),
            }

        if self.transforms:
            image, target = self.transforms(image, target)

        return image, target


def build_split_dataloaders(config, split_file: str):
    """
    Build train and val DataLoaders from a saved split file.

    Args:
        config     : configs/config.py module
        split_file : path to data_split.json

    Returns:
        train_loader, val_loader
    """
    from torch.utils.data import DataLoader
    from dataset.coco_dataset import collate_fn
    from dataset.transforms   import (get_train_transforms,
                                       get_val_transforms)
    from utils.split import load_split

    train_ids, val_ids = load_split(split_file)

    train_ds = SplitCOCODataset(
        config.TRAIN_IMG_DIR,
        config.TRAIN_ANN,
        train_ids,
        transforms = get_train_transforms(),
    )

    val_ds = SplitCOCODataset(
        config.TRAIN_IMG_DIR,
        config.TRAIN_ANN,
        val_ids,
        transforms = get_val_transforms(),
    )

    train_loader = DataLoader(
        train_ds,
        batch_size  = config.BATCH_SIZE,
        shuffle     = True,
        num_workers = config.NUM_WORKERS,
        collate_fn  = collate_fn,
        pin_memory  = True,
        drop_last   = True,
    )

    val_loader = DataLoader(
        val_ds,
        batch_size  = 1,
        shuffle     = False,
        num_workers = config.NUM_WORKERS,
        collate_fn  = collate_fn,
        pin_memory  = True,
    )

    print(f"\n  Train: {len(train_ds)} images → "
          f"{len(train_loader)} batches")
    print(f"  Val  : {len(val_ds)} images → "
          f"{len(val_loader)} batches\n")

    return train_loader, val_loader