# model/detector.py
"""
Full Faster-RCNN Detection Model
──────────────────────────────────
Wires together:
  - ResNet50/101 + FPN backbone  (from backbone.py)
  - Region Proposal Network (RPN)
  - ROI Align + classification/regression head

The model is built on top of torchvision's Faster-RCNN
with custom anchor configuration and head replacement
for our specific classes.
"""

import torch
import torch.nn as nn
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.rpn import AnchorGenerator, RPNHead
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import MultiScaleRoIAlign

from model.backbone import build_backbone, freeze_backbone_layers


def build_detector(num_classes: int, backbone_name: str = "resnet50",
                   pretrained_backbone: bool = True) -> FasterRCNN:
    """
    Build the complete Faster-RCNN detection model.

    Args:
        num_classes         : Total classes INCLUDING background
                              e.g. 7 = background + person + bicycle +
                                       car + motorcycle + bus + truck
        backbone_name       : "resnet50" or "resnet101"
        pretrained_backbone : Use ImageNet pretrained backbone weights

    Returns:
        model : FasterRCNN — complete end-to-end detection model
    """

    # ── Step 1: Build backbone ────────────────────────────────────────────────
    backbone = build_backbone(
        backbone_name = backbone_name,
        pretrained    = pretrained_backbone
    )

    # Freeze early layers — preserve pretrained low-level features
    freeze_backbone_layers(backbone, freeze_until_layer=2)

    # ── Step 2: Configure Anchor Generator ───────────────────────────────────
    # Anchors are defined per FPN level
    # Sizes match the receptive field of each FPN level:
    #   P2 → small objects  → size 32
    #   P3 → medium         → size 64
    #   P4 → medium-large   → size 128
    #   P5 → large          → size 256
    #   P6 → very large     → size 512
    anchor_generator = AnchorGenerator(
        sizes = (
            (32,),    # P2 — detects small objects
            (64,),    # P3
            (128,),   # P4
            (256,),   # P5
            (512,),   # P6 — detects large objects
        ),
        # aspect_ratios applied to EACH level
        # 0.5 = tall/narrow, 1.0 = square, 2.0 = wide/short
        aspect_ratios = ((0.5, 1.0, 2.0),) * 5
    )
    # Total anchors per position = 3 (ratios)
    # Total anchors per level    = H * W * 3
    # Total anchors per image    = sum across all 5 levels

    # ── Step 3: Configure ROI Align ───────────────────────────────────────────
    # MultiScaleRoIAlign automatically picks the right FPN level
    # for each proposal based on its size (small proposals → P2, large → P5)
    roi_pooler = MultiScaleRoIAlign(
        featmap_names = ["0", "1", "2", "3"],  # which FPN levels to use
        output_size   = 7,                      # output 7x7 feature per ROI
        sampling_ratio= 2                       # bilinear interpolation points
    )

    # ── Step 4: Build Faster-RCNN ─────────────────────────────────────────────
    model = FasterRCNN(
        backbone              = backbone,
        num_classes           = num_classes,
        rpn_anchor_generator  = anchor_generator,
        box_roi_pool          = roi_pooler,

        # RPN settings
        rpn_pre_nms_top_n_train  = 2000,  # proposals before NMS during training
        rpn_pre_nms_top_n_test   = 1000,  # proposals before NMS during inference
        rpn_post_nms_top_n_train = 2000,  # proposals after NMS during training
        rpn_post_nms_top_n_test  = 300,   # proposals after NMS during inference
        rpn_nms_thresh           = 0.7,   # NMS threshold for RPN
        rpn_fg_iou_thresh        = 0.7,   # IoU to consider anchor as foreground
        rpn_bg_iou_thresh        = 0.3,   # IoU to consider anchor as background
        rpn_batch_size_per_image = 256,   # anchors sampled per image for RPN loss
        rpn_positive_fraction    = 0.5,   # fraction of positive anchors in batch

        # ROI Head settings
        box_score_thresh    = 0.05,   # min score to keep detection (low during train)
        box_nms_thresh      = 0.5,    # NMS threshold for final detections
        box_detections_per_img = 100, # max detections per image
        box_fg_iou_thresh   = 0.5,    # IoU threshold for positive ROI
        box_bg_iou_thresh   = 0.5,    # IoU threshold for negative ROI
        box_batch_size_per_image = 512,  # ROIs sampled per image for head loss
        box_positive_fraction    = 0.25, # fraction of positive ROIs in batch
    )

    # ── Step 5: Replace classification head ───────────────────────────────────
    # The default head is built for 91 COCO classes
    # We replace it with one sized for our NUM_CLASSES
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    print(f"\n[Detector] Model built successfully")
    print(f"[Detector] Backbone    : {backbone_name} + FPN")
    print(f"[Detector] Num classes : {num_classes} (including background)")
    print(f"[Detector] Anchors     : 5 levels x 3 ratios = 15 anchor types")
    print(f"[Detector] ROI output  : 7x7 per proposal\n")

    return model


def get_model_summary(model: FasterRCNN):
    """Print parameter counts for each major component."""
    def count_params(module):
        total     = sum(p.numel() for p in module.parameters())
        trainable = sum(p.numel() for p in module.parameters() if p.requires_grad)
        return total, trainable

    backbone_total, backbone_train = count_params(model.backbone)
    rpn_total,      rpn_train      = count_params(model.rpn)
    head_total,     head_train     = count_params(model.roi_heads)
    total,          trainable      = count_params(model)

    print("\n========= Model Summary =========")
    print(f"  {'Component':<15} {'Total':>12} {'Trainable':>12}")
    print(f"  {'-'*40}")
    print(f"  {'Backbone':<15} {backbone_total:>12,} {backbone_train:>12,}")
    print(f"  {'RPN':<15} {rpn_total:>12,} {rpn_train:>12,}")
    print(f"  {'ROI Head':<15} {head_total:>12,} {head_train:>12,}")
    print(f"  {'-'*40}")
    print(f"  {'TOTAL':<15} {total:>12,} {trainable:>12,}")
    print("=================================\n")