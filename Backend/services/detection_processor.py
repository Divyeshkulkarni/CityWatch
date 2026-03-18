from database import detections_collection, alerts_collection, analytics_collection
from services.alert_engine import analyze_detections
from utils.helpers import current_utc_time
from models.detection_model import DetectionInput

async def process_detection(data: DetectionInput):

    # Step A: Save raw detection to database
    detection_doc = {
        "camera_id": data.camera_id,
        "timestamp": data.timestamp,
        "detections": [
            {
                "class_name": d.class_name,
                "bbox": d.bbox,
                "confidence": d.confidence
            }
            for d in data.detections
        ],
        "received_at": current_utc_time()
    }
    await detections_collection.insert_one(detection_doc)

    # Step B: Run alert engine
    generated_alerts = analyze_detections(
        camera_id=data.camera_id,
        timestamp=data.timestamp,
        detections=data.detections
    )

    # Step C: Save each alert to database
    saved_alerts = []
    for alert in generated_alerts:
        alert_doc = {**alert}
        alert_doc["type"] = alert["type"].value
        alert_doc["severity"] = alert["severity"].value
        alert_doc["status"] = alert["status"].value
        await alerts_collection.insert_one(alert_doc)
        # Remove _id before returning — ObjectId is not JSON serializable
        alert_doc.pop("_id", None)
        saved_alerts.append(alert_doc)

    # Step D: Log analytics
    humans = [d for d in data.detections if d.class_name == "human"]
    vehicles = [d for d in data.detections if d.class_name == "vehicle"]
    await analytics_collection.insert_one({
        "camera_id": data.camera_id,
        "timestamp": data.timestamp,
        "human_count": len(humans),
        "vehicle_count": len(vehicles),
        "total_detections": len(data.detections),
        "alerts_generated": len(saved_alerts)
    })

    return {
        "status": "processed",
        "detections_received": len(data.detections),
        "alerts_generated": len(saved_alerts),
        "alerts": saved_alerts
    }
