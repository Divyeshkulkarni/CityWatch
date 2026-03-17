# losses/__init__.py
from .detection_loss import (
    compute_total_loss,
    LossTracker,
    DEFAULT_LOSS_WEIGHTS,
)