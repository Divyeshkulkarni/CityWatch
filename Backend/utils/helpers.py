import uuid
from datetime import datetime

def generate_alert_id() -> str:
    return f"ALT_{uuid.uuid4().hex[:6].upper()}"

def generate_report_id() -> str:
    return f"RPT_{uuid.uuid4().hex[:6].upper()}"

def current_utc_time() -> datetime:
    return datetime.utcnow()

def calculate_iou(box1: list, box2: list) -> float:
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    return intersection / union if union > 0 else 0.0