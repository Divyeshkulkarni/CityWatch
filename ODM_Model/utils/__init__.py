# utils/__init__.py
from .iou           import compute_iou, compute_iou_single, match_boxes_to_gt
from .nms           import apply_nms, apply_nms_per_class
from .box_utils     import (xyxy_to_xywh, xywh_to_xyxy,
                             xyxy_to_cxcywh, cxcywh_to_xyxy,
                             clip_boxes_to_image,
                             filter_small_boxes, box_area)
from .metrics       import compute_map, compute_ap
from .visualization import visualize_predictions
from .density       import (DetectionResult,
                             detections_from_model_output,
                             build_gaussian_density_map,
                             build_grid_density,
                             overlay_heatmap_on_frame,
                             overlay_grid_on_frame,
                             build_hybrid_frame,
                             GridDensityResult)