# utils/split.py
"""
Train/Val split utility.
Splits filtered_images into train and val sets
without moving any files — just splits image IDs.
"""

import os
import random
import json
from pycocotools.coco import COCO


def get_existing_image_ids(
    ann_file:  str,
    img_dir:   str,
) -> list:
    """
    Get image IDs that actually exist in img_dir.
    Filters out COCO images that weren't downloaded.

    Args:
        ann_file : path to COCO annotation JSON
        img_dir  : path to images folder

    Returns:
        list of valid image IDs
    """
    coco           = COCO(ann_file)
    existing_files = set(os.listdir(img_dir))
    valid_ids      = []

    for img_id in coco.getImgIds():
        info      = coco.loadImgs(img_id)[0]
        file_name = info["file_name"]
        if file_name in existing_files:
            valid_ids.append(img_id)

    print(f"[Split] Total images in annotation : "
          f"{len(coco.getImgIds())}")
    print(f"[Split] Images found in folder     : "
          f"{len(valid_ids)}")
    return valid_ids


def split_image_ids(
    image_ids:   list,
    val_ratio:   float = 0.2,
    seed:        int   = 42,
) -> tuple:
    """
    Split image IDs into train and val sets.

    Args:
        image_ids : list of all valid image IDs
        val_ratio : fraction to use for validation
        seed      : random seed for reproducibility

    Returns:
        train_ids, val_ids
    """
    random.seed(seed)
    ids       = image_ids.copy()
    random.shuffle(ids)

    n_val     = int(len(ids) * val_ratio)
    val_ids   = ids[:n_val]
    train_ids = ids[n_val:]

    print(f"[Split] Train images : {len(train_ids)}")
    print(f"[Split] Val images   : {len(val_ids)}")
    print(f"[Split] Val ratio    : {len(val_ids)/len(ids):.1%}")

    return train_ids, val_ids


def save_split(
    train_ids: list,
    val_ids:   list,
    save_path: str = "data_split.json",
):
    """Save split to JSON so it's reproducible across runs."""
    split = {"train": train_ids, "val": val_ids}
    with open(save_path, "w") as f:
        json.dump(split, f, indent=2)
    print(f"[Split] Saved → {save_path}")


def load_split(path: str) -> tuple:
    """Load a previously saved split."""
    with open(path, "r") as f:
        split = json.load(f)
    train_ids = split["train"]
    val_ids   = split["val"]
    print(f"[Split] Loaded — train={len(train_ids)}, "
          f"val={len(val_ids)}")
    return train_ids, val_ids