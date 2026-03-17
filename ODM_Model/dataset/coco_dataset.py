# dataset/coco_dataset.py
"""
COCO Dataset loader filtered to person + vehicle classes.

Key concepts:
  - Reads COCO JSON annotations via pycocotools
  - Converts bbox format: [x, y, w, h] → [x1, y1, x2, y2]
  - Remaps sparse COCO category IDs to compact 1-based label indices
  - Returns torchvision Faster-RCNN compatible targets
"""

import os
import torch
from torch.utils.data import Dataset, DataLoader
from pycocotools.coco import COCO
from PIL import Image


# ── Class definitions ─────────────────────────────────────────────────────────

# COCO category IDs we care about
# (person=1, bicycle=2, car=3, motorcycle=4, bus=6, truck=8)
TARGET_COCO_IDS = {1, 2, 3, 4, 6, 8}

# Human-readable names for each COCO ID
COCO_ID_TO_NAME = {
    1: "person", 2: "bicycle", 3: "car",
    4: "motorcycle", 6: "bus", 8: "truck"
}

# Remap sparse COCO IDs → compact sequential labels (1-based, 0 = background)
# Result: person=1, bicycle=2, car=3, motorcycle=4, bus=5, truck=6
COCO_ID_TO_LABEL = {
    coco_id: label
    for label, coco_id in enumerate(sorted(TARGET_COCO_IDS), start=1)
}

# Reverse map: label index → class name (useful for display during inference)
LABEL_TO_NAME = {
    label: COCO_ID_TO_NAME[coco_id]
    for coco_id, label in COCO_ID_TO_LABEL.items()
}
LABEL_TO_NAME[0] = "background"

NUM_CLASSES = len(TARGET_COCO_IDS) + 1   # 7 (including background)


# ── Dataset class ─────────────────────────────────────────────────────────────

class COCODataset(Dataset):
    """
    Args:
        img_dir   : Path to folder containing images (e.g. data/train/images/)
        ann_file  : Path to COCO annotation JSON  (e.g. data/train/annotations.json)
        transforms: Callable from transforms.py (or None)

    Returns per __getitem__:
        image  : FloatTensor [3, H, W]  values in ~[-2, 2] after normalisation
        target : dict
            "boxes"    FloatTensor [N, 4]   xyxy format
            "labels"   LongTensor  [N]      1-based class index
            "image_id" LongTensor  [1]
            "area"     FloatTensor [N]      pixel area of each box
            "iscrowd"  ByteTensor  [N]      1 = crowd annotation (skip in eval)
    """

    def __init__(self, img_dir: str, ann_file: str, transforms=None):
        self.img_dir    = img_dir
        self.transforms = transforms

        # pycocotools COCO object — parses the JSON and builds lookup tables
        print(f"  Loading annotations from {ann_file} ...")
        self.coco = COCO(ann_file)

        # Get image IDs that contain at least one of our target classes
        # (avoids loading images with zero useful annotations)
        img_ids_sets = [
            set(self.coco.getImgIds(catIds=[cid]))
            for cid in TARGET_COCO_IDS
        ]
        self.img_ids = sorted(set().union(*img_ids_sets))
        print(f"  Found {len(self.img_ids)} images with target classes")

    def __len__(self):
        return len(self.img_ids)

    def __getitem__(self, idx: int):
        img_id   = self.img_ids[idx]
        img_info = self.coco.loadImgs(img_id)[0]
        img_path = os.path.join(self.img_dir, img_info["file_name"])

        # Load as RGB PIL image
        image = Image.open(img_path).convert("RGB")

        # ── Load and filter annotations ───────────────────────────────────────
        ann_ids = self.coco.getAnnIds(
            imgIds=img_id,
            catIds=list(TARGET_COCO_IDS),
            iscrowd=None    # include both crowd and non-crowd
        )
        anns = self.coco.loadAnns(ann_ids)

        boxes, labels, areas, iscrowd = [], [], [], []

        for ann in anns:
            # Skip annotations for classes we don't want
            if ann["category_id"] not in TARGET_COCO_IDS:
                continue

            # COCO bbox = [x_topleft, y_topleft, width, height]
            x, y, w, h = ann["bbox"]

            # Skip degenerate boxes (zero or negative size)
            if w <= 1 or h <= 1:
                continue

            # Convert to [x1, y1, x2, y2] (torchvision format)
            boxes.append([x, y, x + w, y + h])
            labels.append(COCO_ID_TO_LABEL[ann["category_id"]])
            areas.append(ann["area"])
            iscrowd.append(int(ann.get("iscrowd", 0)))

        # ── Build target dict ─────────────────────────────────────────────────
        # Handle edge case: image has annotations but all were degenerate
        if len(boxes) == 0:
            target = {
                "boxes":    torch.zeros((0, 4), dtype=torch.float32),
                "labels":   torch.zeros((0,),   dtype=torch.int64),
                "area":     torch.zeros((0,),   dtype=torch.float32),
                "iscrowd":  torch.zeros((0,),   dtype=torch.uint8),
                "image_id": torch.tensor([img_id], dtype=torch.int64),
            }
        else:
            target = {
                "boxes":    torch.tensor(boxes,   dtype=torch.float32),
                "labels":   torch.tensor(labels,  dtype=torch.int64),
                "area":     torch.tensor(areas,   dtype=torch.float32),
                "iscrowd":  torch.tensor(iscrowd, dtype=torch.uint8),
                "image_id": torch.tensor([img_id], dtype=torch.int64),
            }

        # ── Apply transforms ──────────────────────────────────────────────────
        if self.transforms is not None:
            image, target = self.transforms(image, target)

        return image, target


# ── Collate function ──────────────────────────────────────────────────────────

def collate_fn(batch):
    """
    Why this exists:
    PyTorch's default collate tries to stack all tensors into a single
    batch tensor [B, ...]. This works for classification (every image
    has exactly 1 label). Detection can't do this because:
      - Images may have different H, W
      - Each image has a different number of boxes

    Solution: return a tuple of lists. Each element is one sample.
    The model (Faster-RCNN) expects exactly this format.
    """
    images  = [item[0] for item in batch]
    targets = [item[1] for item in batch]
    return images, targets


# ── DataLoader factory ────────────────────────────────────────────────────────

def build_dataloaders(config):
    """
    Create train and val DataLoaders from config settings.

    Args:
        config: your configs/config.py module

    Returns:
        train_loader, val_loader
    """
    from dataset.transforms import get_train_transforms, get_val_transforms

    train_dataset = COCODataset(
        img_dir    = config.TRAIN_IMG_DIR,
        ann_file   = config.TRAIN_ANN,
        transforms = get_train_transforms(),
    )

    val_dataset = COCODataset(
        img_dir    = config.VAL_IMG_DIR,
        ann_file   = config.VAL_ANN,
        transforms = get_val_transforms(),
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size  = config.BATCH_SIZE,
        shuffle     = True,              # randomise order each epoch
        num_workers = config.NUM_WORKERS,
        collate_fn  = collate_fn,
        pin_memory  = True,              # faster CPU→GPU transfer
        drop_last   = True,              # avoid incomplete final batch
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size  = 1,                 # evaluate one image at a time
        shuffle     = False,
        num_workers = config.NUM_WORKERS,
        collate_fn  = collate_fn,
        pin_memory  = True,
    )

    print(f"\n  Train: {len(train_dataset)} images → {len(train_loader)} batches")
    print(f"  Val:   {len(val_dataset)}   images → {len(val_loader)} batches\n")

    return train_loader, val_loader