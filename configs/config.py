# configs/config.py

import torch

# ─────────────────────────────────────────────
# DEVICE
# ─────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ─────────────────────────────────────────────
# DATASET (COCO)
# ─────────────────────────────────────────────
COCO_ROOT     = r"D:\VS codes\ML Coding\People_vehicles dataset"

TRAIN_ANN     = r"D:\VS codes\ML Coding\People_vehicles dataset\annotations\annotations_trainval2017\annotations\instances_train2017.json"
VAL_ANN       = r"D:\VS codes\ML Coding\People_vehicles dataset\annotations\annotations_trainval2017\annotations\instances_val2017.json"

TRAIN_IMG_DIR = r"D:\VS codes\ML Coding\People_vehicles dataset\filtered_images"
VAL_IMG_DIR   = r"D:\VS codes\ML Coding\People_vehicles dataset\filtered_images"

# COCO class IDs we care about
TARGET_CLASSES = {1: "person", 2: "bicycle", 3: "car",
                  4: "motorcycle", 6: "bus", 8: "truck"}
NUM_CLASSES    = len(TARGET_CLASSES) + 1   # 7 (including background)

# ─────────────────────────────────────────────
# MODEL
# ─────────────────────────────────────────────
BACKBONE   = "resnet50"
PRETRAINED = True

# ─────────────────────────────────────────────
# TRAINING
# ─────────────────────────────────────────────
BATCH_SIZE    = 4
NUM_EPOCHS    = 20
LR            = 0.005
MOMENTUM      = 0.9
WEIGHT_DECAY  = 0.0005
LR_SCHEDULE   = "step"
LR_STEP_SIZE  = 5
LR_GAMMA      = 0.1
LR_MILESTONES = [8, 14]
WARMUP_EPOCHS = 1
NUM_WORKERS   = 0        # keep 0 for Windows — avoids multiprocessing errors

# ─────────────────────────────────────────────
# INFERENCE
# ─────────────────────────────────────────────
SCORE_THRESHOLD = 0.5
NMS_IOU_THRESH  = 0.4
MAX_DETECTIONS  = 100

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
CHECKPOINT_DIR = "checkpoints"
LOG_DIR        = "logs"
OUTPUT_DIR     = "outputs"
# ─────────────────────────────────────────────
# DENSITY / HEATMAP
# ─────────────────────────────────────────────
HEATMAP_SIGMA       = 15        # Gaussian spread radius (pixels)
HEATMAP_ALPHA       = 0.50      # heatmap overlay transparency
DENSITY_GRID_SIZE   = 32        # grid cell size in pixels

# ─────────────────────────────────────────────
# ALERT THRESHOLDS
# ─────────────────────────────────────────────
CROWD_DENSITY_HIGH  = 0.60      # >= 60% grid cells occupied → CRITICAL
CROWD_DENSITY_MED   = 0.35      # >= 35% grid cells occupied → MEDIUM