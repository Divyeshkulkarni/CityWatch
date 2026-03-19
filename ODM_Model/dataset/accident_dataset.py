# dataset/accident_dataset.py
"""
Accident Dataset Loader
────────────────────────
Loads Roboflow vehicle crash dataset.
Handles category id=0 which pycocotools
ignores by default.
"""

import os
import torch
from torch.utils.data import Dataset, DataLoader
from pycocotools.coco import COCO
from PIL import Image


class AccidentDataset(Dataset):
    """
    Loads Roboflow accident dataset.

    Key difference from COCODataset:
    Roboflow uses category id=0 which is normally
    reserved for background in COCO format.
    We remap all category IDs to start from 1.

    Args:
        img_dir    : path to images folder
        ann_file   : path to annotation JSON
        transforms : transform pipeline
    """

    def __init__(
        self,
        img_dir:   str,
        ann_file:  str,
        transforms = None,
    ):
        self.img_dir    = img_dir
        self.transforms = transforms
        self.coco       = COCO(ann_file)

        # Build category remapping
        # Roboflow: id=0,1 → our compact: id=1,2
        cats = self.coco.loadCats(self.coco.getCatIds())
        self.cat_id_to_label = {}
        self.label_to_name   = {0: "background"}

        print("\n[AccidentDataset] Category mapping:")
        for i, cat in enumerate(
            sorted(cats, key=lambda x: x["id"]),
            start=1
        ):
            self.cat_id_to_label[cat["id"]] = i
            self.label_to_name[i]           = cat["name"]
            print(f"  cat_id={cat['id']} → "
                  f"label={i} : {cat['name']}")

        # Get all image IDs
        self.img_ids = list(self.coco.imgs.keys())
        print(f"[AccidentDataset] "
              f"{len(self.img_ids)} images\n")

    def __len__(self):
        return len(self.img_ids)

    def __getitem__(self, idx):
        img_id   = self.img_ids[idx]
        img_info = self.coco.loadImgs(img_id)[0]
        img_path = os.path.join(
            self.img_dir, img_info["file_name"]
        )

        # Handle missing images gracefully
        if not os.path.exists(img_path):
            # Return empty sample
            image = Image.new("RGB", (640, 640))
            target = {
                "boxes":    torch.zeros((0,4),
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
            if self.transforms:
                image, target = self.transforms(
                    image, target
                )
            return image, target

        image = Image.open(img_path).convert("RGB")

        # Load annotations
        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        anns    = self.coco.loadAnns(ann_ids)

        boxes, labels, areas, iscrowd = [], [], [], []

        for ann in anns:
            x, y, w, h = ann["bbox"]
            if w <= 1 or h <= 1:
                continue

            # Remap category id → compact label
            cat_id = ann["category_id"]
            label  = self.cat_id_to_label.get(cat_id, 1)

            boxes.append([x, y, x + w, y + h])
            labels.append(label)
            areas.append(float(ann.get("area", w * h)))
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
            image, target = self.transforms(
                image, target
            )
        return image, target


def build_accident_dataloaders(config):
    """Build train/val DataLoaders for accident dataset."""
    from dataset.coco_dataset import collate_fn
    from dataset.transforms   import (get_train_transforms,
                                       get_val_transforms)

    train_ds = AccidentDataset(
        config.TRAIN_IMG_DIR,
        config.TRAIN_ANN,
        transforms = get_train_transforms(),
    )

    val_ds = AccidentDataset(
        config.VAL_IMG_DIR,
        config.VAL_ANN,
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

    print(f"Train: {len(train_ds)} images → "
          f"{len(train_loader)} batches")
    print(f"Val  : {len(val_ds)} images → "
          f"{len(val_loader)} batches\n")

    return train_loader, val_loader