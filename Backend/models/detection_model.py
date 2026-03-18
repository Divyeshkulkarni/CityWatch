from pydantic import BaseModel
from typing import List
from datetime import datetime

class Detection(BaseModel):
    class_name: str        # "vehicle" or "human"
    bbox: List[float]      # [x1, y1, x2, y2]
    confidence: float      # e.g. 0.92

class DetectionInput(BaseModel):
    camera_id: str         # e.g. "cam_01"
    timestamp: datetime    # e.g. "2026-02-27T09:20:00Z"
    detections: List[Detection]