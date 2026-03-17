# model/backbone.py

import torch
import torch.nn as nn
from torchvision.models.detection.backbone_utils import resnet_fpn_backbone
from torchvision.ops.feature_pyramid_network import LastLevelMaxPool


def build_backbone(backbone_name: str = "resnet50", pretrained: bool = True):
    backbone = resnet_fpn_backbone(
        backbone_name    = backbone_name,
        weights          = "IMAGENET1K_V1" if pretrained else None,
        trainable_layers = 3,
        returned_layers  = [1, 2, 3, 4],
        extra_blocks     = LastLevelMaxPool(),
    )
    print(f"[Backbone] Built {backbone_name} + FPN")
    print(f"[Backbone] Output channels: {backbone.out_channels}")
    print(f"[Backbone] Pretrained: {pretrained}")
    return backbone


def freeze_backbone_layers(backbone, freeze_until_layer: int = 2):
    layers_to_freeze = [
        backbone.body.layer1,
        backbone.body.layer2,
        backbone.body.layer3,
        backbone.body.layer4,
    ]

    # Always freeze stem
    for param in backbone.body.conv1.parameters():
        param.requires_grad = False
    for param in backbone.body.bn1.parameters():
        param.requires_grad = False

    # Freeze requested layers
    for i, layer in enumerate(layers_to_freeze):
        if i < freeze_until_layer:
            for param in layer.parameters():
                param.requires_grad = False

    frozen    = sum(1 for p in backbone.parameters() if not p.requires_grad)
    trainable = sum(1 for p in backbone.parameters() if p.requires_grad)
    print(f"[Backbone] Frozen params: {frozen} | Trainable params: {trainable}")


def unfreeze_all(backbone):
    for param in backbone.parameters():
        param.requires_grad = True
    trainable = sum(1 for p in backbone.parameters() if p.requires_grad)
    print(f"[Backbone] All unfrozen — Trainable params: {trainable}")


def get_backbone_info(backbone):
    total  = sum(p.numel() for p in backbone.parameters())
    frozen = sum(p.numel() for p in backbone.parameters() if not p.requires_grad)

    print("\n=== Backbone Summary ===")
    print(f"  Output channels : {backbone.out_channels}")
    print(f"  Total params    : {total:,}")
    print(f"  Frozen params   : {frozen:,}")
    print(f"  Trainable params: {total - frozen:,}")
    print("========================\n")