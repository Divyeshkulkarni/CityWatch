# training/scheduler.py
"""
Learning rate scheduler utilities.
Controls how the learning rate changes during training.
"""

import torch
from torch.optim.lr_scheduler import (
    StepLR,
    MultiStepLR,
    CosineAnnealingLR,
    LinearLR,
    SequentialLR,
)


def build_scheduler(optimizer, config):
    """
    Build learning rate scheduler from config.

    Supports three strategies:
      "step"     : reduce LR by gamma every step_size epochs
      "multistep": reduce LR at specific milestone epochs
      "cosine"   : smoothly anneal LR following cosine curve

    Args:
        optimizer : torch optimizer
        config    : configs/config.py module

    Returns:
        scheduler : LR scheduler
    """
    strategy = getattr(config, "LR_SCHEDULE", "step")

    if strategy == "step":
        scheduler = StepLR(
            optimizer,
            step_size = config.LR_STEP_SIZE,
            gamma     = config.LR_GAMMA,
        )
        print(f"[Scheduler] StepLR — step={config.LR_STEP_SIZE}, "
              f"gamma={config.LR_GAMMA}")

    elif strategy == "multistep":
        milestones = getattr(config, "LR_MILESTONES", [8, 14])
        scheduler  = MultiStepLR(
            optimizer,
            milestones = milestones,
            gamma      = config.LR_GAMMA,
        )
        print(f"[Scheduler] MultiStepLR — milestones={milestones}, "
              f"gamma={config.LR_GAMMA}")

    elif strategy == "cosine":
        scheduler = CosineAnnealingLR(
            optimizer,
            T_max = config.NUM_EPOCHS,
            eta_min = config.LR * 0.01,
        )
        print(f"[Scheduler] CosineAnnealingLR — "
              f"T_max={config.NUM_EPOCHS}")

    else:
        raise ValueError(f"Unknown LR schedule: {strategy}")

    return scheduler


def build_warmup_scheduler(optimizer, config):
    """
    Linear warmup followed by step decay.
    Warmup: LR increases linearly for first N epochs
    Then: StepLR kicks in

    Why warmup?
    At the start of training weights are random.
    A large LR immediately can cause instability.
    Warmup gradually increases LR giving the model
    time to settle before full-speed training.
    """
    warmup_epochs = getattr(config, "WARMUP_EPOCHS", 1)

    warmup = LinearLR(
        optimizer,
        start_factor = 0.1,    # start at 10% of base LR
        end_factor   = 1.0,    # reach 100% of base LR
        total_iters  = warmup_epochs,
    )

    main = StepLR(
        optimizer,
        step_size = config.LR_STEP_SIZE,
        gamma     = config.LR_GAMMA,
    )

    # Chain: warmup first, then main scheduler
    scheduler = SequentialLR(
        optimizer,
        schedulers = [warmup, main],
        milestones = [warmup_epochs],
    )

    print(f"[Scheduler] Warmup({warmup_epochs} epochs) "
          f"→ StepLR(step={config.LR_STEP_SIZE})")
    return scheduler


def get_current_lr(optimizer) -> float:
    """Get current learning rate from optimizer."""
    return optimizer.param_groups[0]["lr"]