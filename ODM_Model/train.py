# train.py
"""
Full Training Script — Object Detection + Density System
─────────────────────────────────────────────────────────
Trains Faster-RCNN with ResNet50+FPN backbone on your
filtered COCO dataset with proper train/val split.

Usage:
  python train.py                    # fresh training
  python train.py --resume checkpoints/best_model.pth
  python train.py --unfreeze 8       # unfreeze backbone at epoch 8
  python train.py --no-amp           # disable mixed precision
"""

import os
import sys
import argparse
import torch
from torch.amp    import GradScaler
from pathlib      import Path

sys.path.insert(0, str(Path(__file__).parent))

import configs.config as cfg
from model.detector           import build_detector
from model.backbone           import unfreeze_all
from dataset.split_dataset    import build_split_dataloaders
from training.trainer         import (train_one_epoch,
                                       save_checkpoint,
                                       load_checkpoint)
from training.scheduler       import (build_warmup_scheduler,
                                       build_scheduler,
                                       get_current_lr)
from training.evaluator       import (evaluate_one_epoch,
                                       format_eval_summary)
from utils.split              import (get_existing_image_ids,
                                       split_image_ids,
                                       save_split,
                                       load_split)

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD = True
except ImportError:
    TENSORBOARD = False


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--resume",
                   type=str, default=None)
    p.add_argument("--unfreeze",
                   type=int, default=5)
    p.add_argument("--no-amp",
                   action="store_true")
    p.add_argument("--split-file",
                   type=str, default="data_split.json")
    p.add_argument("--eval-freq",
                   type=int, default=2,
                   help="Evaluate every N epochs")
    return p.parse_args()


def build_optimizer(model, cfg, phase="frozen"):
    if phase == "frozen":
        params = [p for p in model.parameters()
                  if p.requires_grad]
        opt = torch.optim.SGD(
            params,
            lr           = cfg.LR,
            momentum     = cfg.MOMENTUM,
            weight_decay = cfg.WEIGHT_DECAY,
        )
        print(f"[Optimizer] Frozen backbone — "
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
        print(f"[Optimizer] Full model — "
              f"backbone LR={cfg.LR*0.1}, "
              f"head LR={cfg.LR}")
    return opt


def main():
    args   = parse_args()
    device = torch.device(cfg.DEVICE)

    print(f"\n{'='*55}")
    print(f"  ODM — Object Detection Model Training")
    print(f"{'='*55}")
    print(f"  Device    : {device}")
    print(f"  Backbone  : {cfg.BACKBONE}")
    print(f"  Classes   : {cfg.NUM_CLASSES}")
    print(f"  Epochs    : {cfg.NUM_EPOCHS}")
    print(f"  Batch     : {cfg.BATCH_SIZE}")
    print(f"  LR        : {cfg.LR}")
    print(f"{'='*55}\n")

    # ── Step 1: Create/load data split ────────────────────
    if not os.path.exists(args.split_file):
        print("[Split] Creating new train/val split...")
        image_ids = get_existing_image_ids(
            cfg.TRAIN_ANN,
            cfg.TRAIN_IMG_DIR,
        )
        train_ids, val_ids = split_image_ids(
            image_ids, val_ratio=0.2, seed=42
        )
        save_split(train_ids, val_ids, args.split_file)
    else:
        print(f"[Split] Using existing split: "
              f"{args.split_file}")

    # ── Step 2: Build DataLoaders ─────────────────────────
    train_loader, val_loader = build_split_dataloaders(
        cfg, args.split_file
    )

    # ── Step 3: Build model ───────────────────────────────
    model = build_detector(
        num_classes         = cfg.NUM_CLASSES,
        backbone_name       = cfg.BACKBONE,
        pretrained_backbone = cfg.PRETRAINED,
    ).to(device)

    # ── Step 4: Training components ───────────────────────
    optimizer = build_optimizer(model, cfg, "frozen")
    scheduler = build_warmup_scheduler(optimizer, cfg)
    scaler    = GradScaler(
        "cuda",
        enabled=(device.type == "cuda"
                 and not args.no_amp)
    )
    writer = (SummaryWriter(cfg.LOG_DIR)
              if TENSORBOARD else None)

    # ── Step 5: Resume if checkpoint given ───────────────
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
        best_val_loss = ckpt.get("val_loss",
                                  float("inf"))
        if start_epoch > args.unfreeze:
            unfreeze_all(model.backbone)
            optimizer = build_optimizer(
                model, cfg, "unfrozen"
            )
            backbone_unfrozen = True

    # ── Step 6: Training loop ─────────────────────────────
    print(f"Starting training from epoch "
          f"{start_epoch}...\n")

    for epoch in range(start_epoch,
                       cfg.NUM_EPOCHS + 1):

        # Unfreeze backbone at specified epoch
        if (epoch == args.unfreeze
                and not backbone_unfrozen):
            print(f"\n[Train] Epoch {epoch}: "
                  f"Unfreezing backbone\n")
            unfreeze_all(model.backbone)
            optimizer = build_optimizer(
                model, cfg, "unfrozen"
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
                epoch, val_metrics, train_losses
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
    print(f"  Best val loss : {best_val_loss:.4f}")
    print(f"  Checkpoints   : {cfg.CHECKPOINT_DIR}/")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()