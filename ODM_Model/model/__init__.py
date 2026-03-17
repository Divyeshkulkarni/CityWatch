# model/__init__.py
from .backbone import (
    build_backbone,
    freeze_backbone_layers,
    unfreeze_all,
    get_backbone_info
)
from .detector import build_detector, get_model_summary