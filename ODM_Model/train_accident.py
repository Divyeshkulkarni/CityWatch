# train_accident.py
"""
Train Model 2 — Accident Detection
────────────────────────────────────
Trains Faster-RCNN on Roboflow vehicle crash dataset.
Reuses ALL components from Model 1.

Usage:
  python train_accident.py
  python train_accident.py --resume checkpoints_accident/best_model.pth
"""

import os
import sys
import argparse
import torch
from torch.amp  import GradScaler
from pathlib    import Path

sys.path.insert(0, str(Path(__file__).parent))

import configs.accident_config as cfg
from model.detector           import build_detector
from model.backbone           import unfreeze_all
from dataset.accident_dataset import build_accident_dataloaders
from training.trainer         import (train_one_epoch,
                                       save_checkpoint,
                                       load_checkpoint)
from training.scheduler       import (build_warmup_scheduler,
                                       build_scheduler,
                                       get_current_lr)
from training.evaluator       import (evaluate_one_epoch,
                                       format_eval_summary)

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD = True
except ImportError:
    TENSORBOARD = False
    print("[Warning] TensorBoard not available")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--resume",
                   type=str, default=None,
                   help="Path to checkpoint to resume from")
    p.add_argument("--unfreeze",
                   type=int, default=5,
                   help="Epoch to unfreeze backbone")
    p.add_argument("--no-amp",
                   action="store_true",
                   help="Disable mixed precision")
    p.add_argument("--eval-freq",
                   type=int, default=2,
                   help="Evaluate every N epochs")
    return p.parse_args()


def build_optimizer(model, phase="frozen"):
    if phase == "frozen":
        params = [p for p in model.parameters()
                  if p.requires_grad]
        opt = torch.optim.SGD(
            params,
            lr           = cfg.LR,
            momentum     = cfg.MOMENTUM,
            weight_decay = cfg.WEIGHT_DECAY,
        )
        print(f"[Optimizer] Frozen backbone "
              f"LR={cfg.LR}")
    else:
        backbone_params = list(
            model.backbone.parameters()
        )
        backbone_ids = {id(p) for p in backbone_params}
        head_params  = [
            p for p in model.parameters()
            if id(p) not in backbone_ids
        ]
        opt = torch.optim.SGD(
            [
                {"params": backbone_params,
                 "lr": cfg.LR * 0.1},
                {"params": head_params,
                 "lr": cfg.LR},
            ],
            momentum     = cfg.MOMENTUM,
            weight_decay = cfg.WEIGHT_DECAY,
        )
        print(f"[Optimizer] Full model "
              f"backbone LR={cfg.LR*0.1} "
              f"head LR={cfg.LR}")
    return opt


def main():
    args   = parse_args()
    device = torch.device(cfg.DEVICE)

    print(f"\n{'='*55}")
    print(f"  Accident Detection Model — Training")
    print(f"{'='*55}")
    print(f"  Device     : {device}")
    print(f"  Backbone   : {cfg.BACKBONE}")
    print(f"  Classes    : {cfg.NUM_CLASSES}")
    print(f"  Epochs     : {cfg.NUM_EPOCHS}")
    print(f"  Batch size : {cfg.BATCH_SIZE}")
    print(f"  LR         : {cfg.LR}")
    print(f"{'='*55}\n")

    # ── Data ──────────────────────────────────────────
    train_loader, val_loader = \
        build_accident_dataloaders(cfg)

    # ── Model ─────────────────────────────────────────
    model = build_detector(
        num_classes         = cfg.NUM_CLASSES,
        backbone_name       = cfg.BACKBONE,
        pretrained_backbone = cfg.PRETRAINED,
    ).to(device)

    # ── Training components ───────────────────────────
    optimizer = build_optimizer(model, "frozen")
    scheduler = build_warmup_scheduler(optimizer, cfg)
    scaler    = GradScaler(
        "cuda",
        enabled = (device.type == "cuda"
                   and not args.no_amp)
    )
    writer = (SummaryWriter(cfg.LOG_DIR)
              if TENSORBOARD else None)

    # ── Resume ────────────────────────────────────────
    start_epoch       = 1
    best_val_loss     = float("inf")
    backbone_unfrozen = False

    if args.resume:
        ckpt = load_checkpoint(
            args.resume, model,
            optimizer, scheduler,
            scaler, device
        )
        start_epoch   = ckpt["epoch"] + 1
        best_val_loss = ckpt.get(
            "val_loss", float("inf")
        )
        if start_epoch > args.unfreeze:
            unfreeze_all(model.backbone)
            optimizer = build_optimizer(
                model, "unfrozen"
            )
            backbone_unfrozen = True

    # ── Training Loop ─────────────────────────────────
    print(f"Starting from epoch {start_epoch}...\n")

    for epoch in range(start_epoch,
                       cfg.NUM_EPOCHS + 1):

        # Unfreeze backbone at specified epoch
        if (epoch == args.unfreeze
                and not backbone_unfrozen):
            print(f"\n[Train] Epoch {epoch}: "
                  f"Unfreezing backbone\n")
            unfreeze_all(model.backbone)
            optimizer = build_optimizer(
                model, "unfrozen"
            )
            scheduler = build_scheduler(
                optimizer, cfg
            )
            backbone_unfrozen = True

        # Train one epoch
        train_losses = train_one_epoch(
            model       = model,
            optimizer   = optimizer,
            data_loader = train_loader,
            device      = device,
            epoch       = epoch,
            scaler      = scaler,
            writer      = writer,
        )

        # Evaluate periodically
        if (epoch % args.eval_freq == 0
                or epoch == cfg.NUM_EPOCHS):
            val_metrics = evaluate_one_epoch(
                model        = model,
                data_loader  = val_loader,
                device       = device,
                epoch        = epoch,
                score_thresh = cfg.SCORE_THRESHOLD,
                writer       = writer,
            )
            val_loss = 1.0 - val_metrics["mAP"]
            print(format_eval_summary(
                epoch,
                val_metrics,
                train_losses,
            ))
        else:
            val_loss = sum(train_losses.values())

        # LR step
        scheduler.step()
        print(f"  LR: {get_current_lr(optimizer):.6f}")

        # Save checkpoint
        is_best = val_loss < best_val_loss
        if is_best:
            best_val_loss = val_loss

        save_checkpoint(
            model     = model,
            optimizer = optimizer,
            scheduler = scheduler,
            scaler    = scaler,
            epoch     = epoch,
            val_loss  = val_loss,
            config    = cfg,
            is_best   = is_best,
            save_dir  = cfg.CHECKPOINT_DIR,
        )

    if writer:
        writer.close()

    print(f"\n{'='*55}")
    print(f"  Training complete!")
    print(f"  Best val loss  : {best_val_loss:.4f}")
    print(f"  Checkpoints    : {cfg.CHECKPOINT_DIR}/")
    print(f"  Best model     : "
          f"{cfg.CHECKPOINT_DIR}/best_model.pth")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()