# configs/accident_config.py
import torch

# ─────────────────────────────────────────────
# DEVICE
# ─────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ─────────────────────────────────────────────
# DATASET
# ─────────────────────────────────────────────
ACCIDENT_DATASET_ROOT = r"D:\VS codes\ML Coding\ODM_Model\accident_dataset"

TRAIN_IMG_DIR = r"D:\VS codes\ML Coding\ODM_Model\accident_dataset\train"
VAL_IMG_DIR   = r"D:\VS codes\ML Coding\ODM_Model\accident_dataset\train"

TRAIN_ANN     = r"D:\VS codes\ML Coding\ODM_Model\accident_dataset\train\_annotations_train.coco.json"
VAL_ANN       = r"D:\VS codes\ML Coding\ODM_Model\accident_dataset\valid\_annotations_valid.coco.json"

# Classes from Roboflow dataset
# id=0 Vehicle-Crash, id=1 Vehicle-Crash_Detected
ACCIDENT_CLASSES = {
    0: "Vehicle-Crash",
    1: "Vehicle-Crash_Detected",
}
NUM_CLASSES = len(ACCIDENT_CLASSES) + 1  # 3 (including background)

# ─────────────────────────────────────────────
# MODEL
# ─────────────────────────────────────────────
BACKBONE   = "resnet50"
PRETRAINED = True

# ─────────────────────────────────────────────
# TRAINING
# ─────────────────────────────────────────────
BATCH_SIZE    = 4
NUM_EPOCHS    = 25
LR            = 0.005
MOMENTUM      = 0.9
WEIGHT_DECAY  = 0.0005
LR_SCHEDULE   = "step"
LR_STEP_SIZE  = 5
LR_GAMMA      = 0.1
LR_MILESTONES = [8, 14]
WARMUP_EPOCHS = 1
NUM_WORKERS   = 0

# ─────────────────────────────────────────────
# INFERENCE
# ─────────────────────────────────────────────
SCORE_THRESHOLD          = 0.5
NMS_IOU_THRESH           = 0.4
MAX_DETECTIONS           = 50
ACCIDENT_CONF_THRESHOLD  = 0.6

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
CHECKPOINT_DIR = "checkpoints_accident"
LOG_DIR        = "logs_accident"
OUTPUT_DIR     = "outputs_accident"

# ─────────────────────────────────────────────
# DENSITY / ALERT
# ─────────────────────────────────────────────
CROWD_DENSITY_HIGH = 0.60
CROWD_DENSITY_MED  = 0.35
HEATMAP_SIGMA      = 15
HEATMAP_ALPHA      = 0.50
DENSITY_GRID_SIZE  = 32