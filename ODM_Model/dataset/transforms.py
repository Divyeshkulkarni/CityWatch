# dataset/transforms.py
"""
Image + bounding box transforms.
All transforms operate on BOTH the image and its boxes together
so spatial consistency is preserved.
"""

import torch
import torchvision.transforms.functional as F
import random


class Compose:
    """Chain multiple transforms together."""
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, image, target):
        for t in self.transforms:
            image, target = t(image, target)
        return image, target


class ToTensor:
    """
    Convert PIL image → FloatTensor [C, H, W] in range [0.0, 1.0].
    Boxes don't need changing here (already float).
    """
    def __call__(self, image, target):
        image = F.to_tensor(image)   # handles HWC→CHW and /255 automatically
        return image, target


class Normalize:
    """
    Normalize image channels using ImageNet mean/std.
    Why? The backbone (ResNet) was pretrained on ImageNet with these values.
    Matching the distribution helps transfer learning work better.
    """
    def __init__(self,
                 mean=(0.485, 0.456, 0.406),
                 std=(0.229, 0.224, 0.225)):
        self.mean = mean
        self.std  = std

    def __call__(self, image, target):
        image = F.normalize(image, mean=self.mean, std=self.std)
        return image, target


class RandomHorizontalFlip:
    """
    Flip image + all bounding boxes horizontally with probability p.

    Box flip formula (for a box [x1, y1, x2, y2] in an image of width W):
        new_x1 = W - old_x2
        new_x2 = W - old_x1
    Y coordinates are unchanged.
    """
    def __init__(self, prob=0.5):
        self.prob = prob

    def __call__(self, image, target):
        if random.random() < self.prob:
            # image is a tensor [C, H, W] at this point
            image = F.hflip(image)

            if "boxes" in target and len(target["boxes"]) > 0:
                boxes = target["boxes"].clone()   # [N, 4]  x1 y1 x2 y2
                W     = image.shape[-1]           # tensor width
                boxes[:, 0] = W - target["boxes"][:, 2]   # new x1
                boxes[:, 2] = W - target["boxes"][:, 0]   # new x2
                target["boxes"] = boxes

        return image, target


class RandomColorJitter:
    """
    Randomly adjust brightness, contrast, saturation.
    Helps the model generalise across lighting conditions.
    Only applied to the image — boxes are unchanged.
    """
    def __init__(self, brightness=0.3, contrast=0.3, saturation=0.2):
        self.brightness = brightness
        self.contrast   = contrast
        self.saturation = saturation

    def __call__(self, image, target):
        # Apply each jitter randomly
        if random.random() < 0.5:
            factor = 1 + random.uniform(-self.brightness, self.brightness)
            image  = F.adjust_brightness(image, factor)
        if random.random() < 0.5:
            factor = 1 + random.uniform(-self.contrast, self.contrast)
            image  = F.adjust_contrast(image, factor)
        if random.random() < 0.5:
            factor = 1 + random.uniform(-self.saturation, self.saturation)
            image  = F.adjust_saturation(image, factor)
        return image, target


def get_train_transforms():
    """Full augmentation pipeline for training."""
    return Compose([
        ToTensor(),
        RandomHorizontalFlip(prob=0.5),
        RandomColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        Normalize(),
    ])


def get_val_transforms():
    """No augmentation for validation — only normalise."""
    return Compose([
        ToTensor(),
        Normalize(),
    ])