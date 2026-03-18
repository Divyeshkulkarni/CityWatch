from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class AlertStatus(str, Enum):
    OPEN = "Open"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"

class AlertType(str, Enum):
    HIGH_CROWD_DENSITY = "High Crowd Density"
    ABNORMAL_CONGESTION = "Abnormal Congestion"
    VEHICLE_ACCIDENT = "Vehicle Accident"
    WRONG_LANE = "Wrong Lane Vehicle"
    TRAFFIC_FLOW_ANOMALY = "Traffic Flow Anomaly"

class Alert(BaseModel):
    alert_id: str
    type: AlertType
    severity: AlertSeverity
    camera_id: str
    timestamp: datetime
    description: str
    status: AlertStatus = AlertStatus.OPEN
    metadata: Dict[str, Any] = {}

class AlertStatusUpdate(BaseModel):
    status: AlertStatus