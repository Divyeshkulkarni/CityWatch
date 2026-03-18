from utils.threshold_config import THRESHOLDS
from utils.helpers import generate_alert_id, current_utc_time, calculate_iou
from models.alert_model import AlertType, AlertSeverity, AlertStatus
from datetime import datetime
from typing import List, Dict, Any
import itertools

def analyze_detections(camera_id: str, timestamp: datetime, detections: list) -> List[Dict[str, Any]]:
    alerts = []

    humans = [d for d in detections if d.class_name == "human"]
    vehicles = [d for d in detections if d.class_name == "vehicle"]

    human_count = len(humans)
    vehicle_count = len(vehicles)

    # ── 1. HIGH CROWD DENSITY ──────────────────────────────────────────────
    crowd_threshold = THRESHOLDS["crowd_density"]["human_count_limit"]
    if human_count > crowd_threshold:
        alerts.append({
            "alert_id": generate_alert_id(),
            "type": AlertType.HIGH_CROWD_DENSITY,
            "severity": AlertSeverity.HIGH if human_count > crowd_threshold * 1.5 else AlertSeverity.MEDIUM,
            "camera_id": camera_id,
            "timestamp": timestamp,
            "description": f"High crowd density detected: {human_count} people in frame.",
            "status": AlertStatus.OPEN,
            "metadata": {
                "human_count": human_count,
                "vehicle_count": vehicle_count,
                "threshold_used": crowd_threshold
            }
        })

    # ── 2. VEHICLE ACCIDENT ────────────────────────────────────────────────
    iou_threshold = THRESHOLDS["vehicle_accident"]["iou_overlap_threshold"]
    if len(vehicles) >= 2:
        for v1, v2 in itertools.combinations(vehicles, 2):
            iou = calculate_iou(v1.bbox, v2.bbox)
            if iou > iou_threshold:
                alerts.append({
                    "alert_id": generate_alert_id(),
                    "type": AlertType.VEHICLE_ACCIDENT,
                    "severity": AlertSeverity.CRITICAL,
                    "camera_id": camera_id,
                    "timestamp": timestamp,
                    "description": f"Possible vehicle collision detected. Bounding box overlap (IoU): {iou:.2f}",
                    "status": AlertStatus.OPEN,
                    "metadata": {
                        "vehicle_count": vehicle_count,
                        "human_count": human_count,
                        "iou_score": round(iou, 3)
                    }
                })
                break

    # ── 3. TRAFFIC CONGESTION ──────────────────────────────────────────────
    congestion_threshold = THRESHOLDS["congestion"]["vehicle_count_limit"]
    if vehicle_count > congestion_threshold:
        alerts.append({
            "alert_id": generate_alert_id(),
            "type": AlertType.ABNORMAL_CONGESTION,
            "severity": AlertSeverity.MEDIUM,
            "camera_id": camera_id,
            "timestamp": timestamp,
            "description": f"Traffic congestion detected: {vehicle_count} vehicles in zone.",
            "status": AlertStatus.OPEN,
            "metadata": {
                "vehicle_count": vehicle_count,
                "human_count": human_count,
                "zone": "monitored_zone"
            }
        })

    return alerts