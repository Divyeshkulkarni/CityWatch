# training/trainer.py
"""
Training Loop
─────────────
Orchestrates the full training process:
  - One epoch of training (train_one_epoch)
  - Checkpoint saving and loading
  - Two-phase training (frozen → unfrozen backbone)
  - Mixed precision (AMP)
  - Gradient clipping
  - LossTracker integration
"""

import os
import time
import torch
from torch.cuda.amp import GradScaler, autocast
from pathlib import Path

from losses.detection_loss import compute_total_loss, LossTracker
from training.scheduler import get_current_lr
from model.backbone import freeze_backbone_layers, unfreeze_all


def train_one_epoch(
    model,
    optimizer,
    data_loader,
    device,
    epoch,
    scaler,
    loss_weights   = None,
    print_freq     = 20,
    writer         = None,
) -> dict:
    """
    Train for one complete epoch.

    Args:
        model       : FasterRCNN model in train mode
        optimizer   : torch optimizer
        data_loader : training DataLoader
        device      : torch device
        epoch       : current epoch number (for logging)
        scaler      : GradScaler for AMP
        loss_weights: optional dict of per-loss weights
        print_freq  : print progress every N batches
        writer      : TensorBoard SummaryWriter (optional)

    Returns:
        dict of average losses for this epoch
    """
    model.train()
    tracker     = LossTracker()
    num_batches = len(data_loader)
    epoch_start = time.time()

    for batch_idx, (images, targets) in enumerate(data_loader):

        # ── Move data to device ───────────────────────────────────────────────
        images  = [img.to(device) for img in images]
        targets = [
            {k: v.to(device) for k, v in t.items()}
            for t in targets
        ]

        # ── Forward pass with AMP ─────────────────────────────────────────────
        # autocast automatically uses float16 where safe
        with autocast(enabled=(device.type == "cuda")):
            loss_dict  = model(images, targets)
            total_loss = compute_total_loss(loss_dict, loss_weights)

        # ── Backward pass ─────────────────────────────────────────────────────
        # zero_grad BEFORE backward — never after
        optimizer.zero_grad()

        # scaler.scale multiplies loss by scale factor
        # prevents float16 gradients from becoming zero (underflow)
        scaler.scale(total_loss).backward()

        # Unscale before clipping so clip threshold is meaningful
        scaler.unscale_(optimizer)

        # Gradient clipping — prevents exploding gradients
        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm = 1.0
        )

        # scaler.step checks for inf/nan gradients
        # if found: skips the update (safe recovery)
        scaler.step(optimizer)

        # Update scale factor for next iteration
        scaler.update()

        # ── Track losses ──────────────────────────────────────────────────────
        tracker.update(loss_dict)

        # ── Logging ───────────────────────────────────────────────────────────
        if (batch_idx + 1) % print_freq == 0 or batch_idx == 0:
            elapsed  = time.time() - epoch_start
            avg_loss = tracker.get_total_average()
            lr       = get_current_lr(optimizer)

            print(f"  Epoch [{epoch:3d}] "
                  f"Batch [{batch_idx+1:4d}/{num_batches}] "
                  f"Loss: {total_loss.item():.4f} "
                  f"Avg: {avg_loss:.4f} "
                  f"LR: {lr:.6f} "
                  f"Time: {elapsed:.1f}s")

            # TensorBoard logging
            if writer is not None:
                global_step = (epoch - 1) * num_batches + batch_idx
                writer.add_scalar("Loss/batch_total", total_loss.item(), global_step)
                writer.add_scalar("LR/batch", lr, global_step)

    # ── End of epoch ──────────────────────────────────────────────────────────
    epoch_time = time.time() - epoch_start
    tracker.print_epoch_summary(epoch)
    print(f"  Epoch {epoch} completed in {epoch_time:.1f}s")

    # Log epoch averages to TensorBoard
    if writer is not None:
        for name, value in tracker.get_tensorboard_dict().items():
            writer.add_scalar(f"Loss/epoch_{name}", value, epoch)

    return tracker.get_averages()


def save_checkpoint(
    model,
    optimizer,
    scheduler,
    scaler,
    epoch,
    val_loss,
    config,
    is_best  = False,
    save_dir = "checkpoints",
):
    """
    Save complete training state to disk.

    Args:
        model     : the detection model
        optimizer : optimizer with current state
        scheduler : LR scheduler with current state
        scaler    : AMP scaler with current state
        epoch     : current epoch number
        val_loss  : validation loss for this epoch
        config    : config module (saved for reproducibility)
        is_best   : if True, also save as 'best_model.pth'
        save_dir  : directory to save checkpoints
    """
    os.makedirs(save_dir, exist_ok=True)

    checkpoint = {
        "epoch":           epoch,
        "model_state":     model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "scheduler_state": scheduler.state_dict(),
        "scaler_state":    scaler.state_dict(),
        "val_loss":        val_loss,
        "config": {
            "num_classes":  config.NUM_CLASSES,
            "backbone":     config.BACKBONE,
            "batch_size":   config.BATCH_SIZE,
            "lr":           config.LR,
        }
    }

    # Regular checkpoint
    path = os.path.join(
        save_dir,
        f"epoch_{epoch:03d}_loss{val_loss:.4f}.pth"
    )
    torch.save(checkpoint, path)
    print(f"  [Checkpoint] Saved → {path}")

    # Best model
    if is_best:
        best_path = os.path.join(save_dir, "best_model.pth")
        torch.save(checkpoint, best_path)
        print(f"  [Checkpoint] New best model → {best_path}")

    return path


def load_checkpoint(
    path,
    model,
    optimizer  = None,
    scheduler  = None,
    scaler     = None,
    device     = None,
) -> dict:
    """
    Load a checkpoint and restore training state.

    Args:
        path      : path to .pth checkpoint file
        model     : model to load weights into
        optimizer : optional — restore optimizer state
        scheduler : optional — restore scheduler state
        scaler    : optional — restore scaler state
        device    : torch device

    Returns:
        checkpoint dict (contains epoch, val_loss, config)
    """
    if device is None:
        device = torch.device("cpu")

    print(f"  [Checkpoint] Loading from {path} ...")
    checkpoint = torch.load(path, map_location=device)

    model.load_state_dict(checkpoint["model_state"])
    print(f"  [Checkpoint] Model weights restored")

    if optimizer and "optimizer_state" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        print(f"  [Checkpoint] Optimizer state restored")

    if scheduler and "scheduler_state" in checkpoint:
        scheduler.load_state_dict(checkpoint["scheduler_state"])
        print(f"  [Checkpoint] Scheduler state restored")

    if scaler and "scaler_state" in checkpoint:
        scaler.load_state_dict(checkpoint["scaler_state"])
        print(f"  [Checkpoint] Scaler state restored")

    epoch    = checkpoint.get("epoch", 0)
    val_loss = checkpoint.get("val_loss", float("inf"))
    print(f"  [Checkpoint] Resumed from epoch {epoch}, "
          f"val_loss={val_loss:.4f}")

    return checkpoint