# create_accident_split.py
import json
import random
import os

# Load full annotation file
ann_path = r"accident_dataset\train\_annotations.coco.json"
with open(ann_path, "r") as f:
    data = json.load(f)

# Shuffle images reproducibly
random.seed(42)
images = data["images"].copy()
random.shuffle(images)

# 80/20 split
n_val      = int(len(images) * 0.2)
val_images = images[:n_val]
train_images = images[n_val:]

# Get image IDs for each split
train_ids = {img["id"] for img in train_images}
val_ids   = {img["id"] for img in val_images}

# Split annotations
train_anns = [a for a in data["annotations"]
              if a["image_id"] in train_ids]
val_anns   = [a for a in data["annotations"]
              if a["image_id"] in val_ids]

# Build train JSON
train_data = {
    "images":      train_images,
    "annotations": train_anns,
    "categories":  data["categories"],
}

# Build val JSON
val_data = {
    "images":      val_images,
    "annotations": val_anns,
    "categories":  data["categories"],
}

# Save
os.makedirs("accident_dataset/valid", exist_ok=True)

train_out = "accident_dataset/train/_annotations_train.coco.json"
val_out   = "accident_dataset/valid/_annotations_valid.coco.json"

with open(train_out, "w") as f:
    json.dump(train_data, f, indent=2)

with open(val_out, "w") as f:
    json.dump(val_data, f, indent=2)

print(f"Split complete!")
print(f"Train : {len(train_images)} images, "
      f"{len(train_anns)} annotations")
print(f"Val   : {len(val_images)} images, "
      f"{len(val_anns)} annotations")
print(f"Train JSON → {train_out}")
print(f"Val JSON   → {val_out}")