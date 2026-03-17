# utils/density.py
"""
Density Map Generation
──────────────────────
Two complementary techniques:

1. Gaussian Point Spread
   Places a 2D Gaussian at each detected person centroid.
   Produces smooth density maps suitable for visualization
   and crowd counting research.

2. Grid Cell Aggregation
   Divides frame into NxM cells, counts detections per cell.
   Fast, interpretable, directly maps to alert thresholds.

Both outputs can be overlaid on the original frame.
"""

import cv2
import torch
import numpy as np
from scipy.ndimage import gaussian_filter
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


# ── Detection container ───────────────────────────────────────────────────────

@dataclass
class DetectionResult:
    """
    Lightweight container for one detection.
    Bridges inference output → density input.
    """
    box:        np.ndarray    # [x1, y1, x2, y2]
    label:      int
    score:      float
    class_name: str = ""

    @property
    def centroid(self) -> Tuple[int, int]:
        """Centre point of the bounding box."""
        cx = int((self.box[0] + self.box[2]) / 2)
        cy = int((self.box[1] + self.box[3]) / 2)
        return cx, cy

    @property
    def width(self) -> float:
        return float(self.box[2] - self.box[0])

    @property
    def height(self) -> float:
        return float(self.box[3] - self.box[1])


def detections_from_model_output(output: dict) -> List[DetectionResult]:
    """
    Convert model inference output dict →
    list of DetectionResult objects.

    Args:
        output : postprocessed dict with boxes, labels,
                 scores, class_names

    Returns:
        list of DetectionResult
    """
    results = []
    boxes       = output["boxes"]
    labels      = output["labels"]
    scores      = output["scores"]
    class_names = output.get("class_names", [])

    for i in range(len(boxes)):
        name = (class_names[i]
                if i < len(class_names)
                else f"cls_{labels[i].item()}")
        results.append(DetectionResult(
            box        = boxes[i].cpu().numpy(),
            label      = labels[i].item(),
            score      = scores[i].item(),
            class_name = name,
        ))
    return results


# ── Gaussian density map ──────────────────────────────────────────────────────

def build_gaussian_density_map(
    detections:  List[DetectionResult],
    frame_hw:    Tuple[int, int],
    sigma:       float = 15.0,
    person_only: bool  = True,
) -> np.ndarray:
    """
    Build a smooth density map using Gaussian point spread.

    Places a Gaussian blob at each detected centroid.
    The integral of the map ≈ number of people.

    Args:
        detections  : list of DetectionResult objects
        frame_hw    : (height, width) of source frame
        sigma       : Gaussian spread in pixels
                      small=15 precise, large=30 smooth
        person_only : if True only persons contribute

    Returns:
        density_map : float32 array [H, W]
                      higher values = more people nearby
    """
    H, W        = frame_hw
    density_map = np.zeros((H, W), dtype=np.float32)

    for det in detections:
        if person_only and det.class_name.lower() != "person":
            continue

        cx, cy = det.centroid

        # Skip centroids outside frame
        if not (0 <= cx < W and 0 <= cy < H):
            continue

        # Place a unit impulse at centroid
        density_map[cy, cx] += 1.0

    # Apply Gaussian blur to spread each impulse into a blob
    # scipy's gaussian_filter is equivalent to convolving
    # with a 2D Gaussian kernel of std=sigma
    if density_map.sum() > 0:
        density_map = gaussian_filter(density_map, sigma=sigma)

    return density_map


# ── Grid density ──────────────────────────────────────────────────────────────

@dataclass
class GridDensityResult:
    """
    Result of grid-based density analysis.
    Contains all info needed for alerts and visualization.
    """
    grid:         np.ndarray        # [rows, cols] int32 count per cell
    cell_size:    int               # pixel size of each cell
    frame_hw:     Tuple[int, int]   # (H, W) of source frame
    occupancy:    float             # fraction of cells that are non-empty
    max_count:    int               # highest count in any single cell
    total_count:  int               # total detections in grid
    hotspots:     List[Tuple[int, int]] = field(
                    default_factory=list)  # (row, col) of dense cells

    @property
    def rows(self): return self.grid.shape[0]

    @property
    def cols(self): return self.grid.shape[1]

    def cell_to_pixels(self, row: int, col: int) -> Tuple:
        """Convert grid cell (row, col) → pixel (x1,y1,x2,y2)."""
        cs  = self.cell_size
        H, W = self.frame_hw
        x1 = col * cs
        y1 = row * cs
        x2 = min(x1 + cs, W)
        y2 = min(y1 + cs, H)
        return x1, y1, x2, y2


def build_grid_density(
    detections:      List[DetectionResult],
    frame_hw:        Tuple[int, int],
    cell_size:       int   = 32,
    hotspot_thresh:  int   = 3,
    class_filter:    Optional[List[str]] = None,
) -> GridDensityResult:
    """
    Divide frame into grid cells and count detections per cell.

    Args:
        detections     : list of DetectionResult objects
        frame_hw       : (H, W) of source frame
        cell_size      : pixel size of each grid cell
        hotspot_thresh : min detections to flag cell as hotspot
        class_filter   : only count these classes
                         (None = count all)

    Returns:
        GridDensityResult with grid, occupancy, hotspots
    """
    H, W  = frame_hw
    rows  = (H + cell_size - 1) // cell_size
    cols  = (W + cell_size - 1) // cell_size
    grid  = np.zeros((rows, cols), dtype=np.int32)

    for det in detections:
        # Apply class filter if specified
        if class_filter is not None:
            if det.class_name.lower() not in [
                c.lower() for c in class_filter
            ]:
                continue

        cx, cy = det.centroid

        if not (0 <= cx < W and 0 <= cy < H):
            continue

        r = cy // cell_size
        c = cx // cell_size
        grid[r, c] += 1

    # Compute summary statistics
    non_empty   = int(np.count_nonzero(grid))
    total_cells = rows * cols
    occupancy   = non_empty / total_cells if total_cells > 0 else 0.0
    max_count   = int(grid.max()) if grid.size > 0 else 0
    total_count = int(grid.sum())

    # Find hotspot cells
    hotspots = []
    if hotspot_thresh > 0:
        hot_rows, hot_cols = np.where(grid >= hotspot_thresh)
        hotspots = list(zip(hot_rows.tolist(), hot_cols.tolist()))

    return GridDensityResult(
        grid        = grid,
        cell_size   = cell_size,
        frame_hw    = frame_hw,
        occupancy   = occupancy,
        max_count   = max_count,
        total_count = total_count,
        hotspots    = hotspots,
    )


# ── Visualisation ─────────────────────────────────────────────────────────────

def density_to_heatmap(
    density_map: np.ndarray,
    colormap:    int  = cv2.COLORMAP_JET,
    normalize:   bool = True,
) -> np.ndarray:
    """
    Convert float32 density map → BGR colour heatmap.

    Args:
        density_map : float32 [H, W]
        colormap    : OpenCV colormap constant
        normalize   : if True scale to [0, 255]

    Returns:
        heatmap : uint8 BGR [H, W, 3]
    """
    dm = density_map.copy()

    if normalize and dm.max() > 0:
        dm = dm / dm.max()

    dm_uint8 = (dm * 255).astype(np.uint8)
    return cv2.applyColorMap(dm_uint8, colormap)


def overlay_heatmap_on_frame(
    frame:       np.ndarray,
    density_map: np.ndarray,
    alpha:       float = 0.5,
    colormap:    int   = cv2.COLORMAP_JET,
) -> np.ndarray:
    """
    Blend the Gaussian density heatmap onto the BGR frame.

    Args:
        frame       : BGR uint8 [H, W, 3]
        density_map : float32 [H, W]
        alpha       : heatmap opacity (0=invisible, 1=opaque)
        colormap    : OpenCV colormap

    Returns:
        blended BGR frame
    """
    H, W  = frame.shape[:2]
    heat  = density_to_heatmap(density_map, colormap)
    heat  = cv2.resize(heat, (W, H))

    # Mask: only blend where density is non-trivial
    # This prevents the blue (zero) areas from washing out the image
    mask        = density_map > (density_map.max() * 0.05 + 1e-6)
    mask_resized = cv2.resize(
        mask.astype(np.uint8), (W, H)
    ).astype(bool)

    blended = frame.copy().astype(np.float32)
    blended[mask_resized] = (
        (1 - alpha) * frame[mask_resized].astype(np.float32) +
        alpha * heat[mask_resized].astype(np.float32)
    )

    return blended.astype(np.uint8)


def overlay_grid_on_frame(
    frame:         np.ndarray,
    grid_result:   GridDensityResult,
    alpha:         float = 0.35,
    hotspot_color: Tuple = (0, 0, 255),
    show_counts:   bool  = False,
) -> np.ndarray:
    """
    Draw grid cells coloured by density count.

    Args:
        frame         : BGR uint8 frame
        grid_result   : GridDensityResult from build_grid_density
        alpha         : cell fill opacity
        hotspot_color : BGR color for hotspot borders
        show_counts   : draw count number in each cell

    Returns:
        annotated BGR frame
    """
    overlay  = frame.copy()
    H, W     = grid_result.frame_hw
    cs       = grid_result.cell_size
    max_c    = max(grid_result.max_count, 1)

    for r in range(grid_result.rows):
        for c in range(grid_result.cols):
            count = grid_result.grid[r, c]
            if count == 0:
                continue

            x1, y1, x2, y2 = grid_result.cell_to_pixels(r, c)

            # Color: green (low) → red (high)
            ratio     = count / max_c
            green     = int(255 * (1 - ratio))
            red       = int(255 * ratio)
            cell_color = (0, green, red)

            cv2.rectangle(overlay, (x1, y1), (x2, y2),
                          cell_color, -1)

            if show_counts:
                cv2.putText(
                    overlay, str(count),
                    (x1 + 2, y1 + cs - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (255, 255, 255), 1
                )

    # Blend overlay with original
    blended = cv2.addWeighted(frame, 1 - alpha,
                               overlay, alpha, 0)

    # Draw hotspot borders on top
    for (r, c) in grid_result.hotspots:
        x1, y1, x2, y2 = grid_result.cell_to_pixels(r, c)
        cv2.rectangle(blended, (x1, y1), (x2, y2),
                      hotspot_color, 2)

    return blended


def build_hybrid_frame(
    frame:        np.ndarray,
    detections:   List[DetectionResult],
    show_heatmap: bool  = True,
    show_grid:    bool  = True,
    show_boxes:   bool  = True,
    sigma:        float = 15.0,
    cell_size:    int   = 32,
    heatmap_alpha: float = 0.45,
    grid_alpha:   float  = 0.30,
) -> Tuple[np.ndarray, GridDensityResult, np.ndarray]:
    """
    Build the complete hybrid output frame.
    Combines heatmap + grid + bounding boxes in one call.

    Args:
        frame        : BGR uint8 original frame
        detections   : list of DetectionResult
        show_heatmap : overlay Gaussian heatmap
        show_grid    : overlay grid density
        show_boxes   : draw bounding boxes
        sigma        : Gaussian spread
        cell_size    : grid cell size in pixels
        heatmap_alpha: heatmap opacity
        grid_alpha   : grid opacity

    Returns:
        hybrid_frame  : annotated BGR frame
        grid_result   : GridDensityResult for alert engine
        density_map   : raw float32 density map
    """
    H, W   = frame.shape[:2]
    output = frame.copy()

    # Build density map (persons only for crowd analysis)
    density_map = build_gaussian_density_map(
        detections, (H, W),
        sigma       = sigma,
        person_only = True,
    )

    # Build grid (persons only)
    grid_result = build_grid_density(
        detections, (H, W),
        cell_size      = cell_size,
        hotspot_thresh = 3,
        class_filter   = ["person"],
    )

    # Layer 1: Heatmap
    if show_heatmap and density_map.max() > 0:
        output = overlay_heatmap_on_frame(
            output, density_map, alpha=heatmap_alpha
        )

    # Layer 2: Grid
    if show_grid:
        output = overlay_grid_on_frame(
            output, grid_result,
            alpha      = grid_alpha,
            show_counts= True,
        )

    # Layer 3: Bounding boxes
    if show_boxes:
        from inference import draw_detections_cv2
        det_dict = {
            "boxes":       torch.tensor(
                               np.array([d.box for d in detections])
                           ) if detections else torch.zeros((0,4)),
            "labels":      torch.tensor(
                               [d.label for d in detections]
                           ) if detections else torch.zeros((0,),
                               dtype=torch.long),
            "scores":      torch.tensor(
                               [d.score for d in detections]
                           ) if detections else torch.zeros((0,)),
            "class_names": [d.class_name for d in detections],
        }
        output = draw_detections_cv2(output, det_dict)

    return output, grid_result, density_map