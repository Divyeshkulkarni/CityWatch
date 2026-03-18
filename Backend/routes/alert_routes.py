from fastapi import APIRouter, HTTPException
from database import alerts_collection, reports_collection
from models.alert_model import AlertStatusUpdate
from utils.helpers import generate_report_id, current_utc_time

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def clean_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/active")
async def get_active_alerts():
    cursor = alerts_collection.find({"status": "Open"})
    alerts = [clean_doc(doc) async for doc in cursor]
    return {"active_alerts": alerts, "count": len(alerts)}

@router.get("/history")
async def get_alert_history():
    cursor = alerts_collection.find().sort("timestamp", -1)
    alerts = [clean_doc(doc) async for doc in cursor]
    return {"alerts": alerts, "total": len(alerts)}

@router.patch("/{alert_id}")
async def update_alert_status(alert_id: str, update: AlertStatusUpdate):
    result = await alerts_collection.update_one(
        {"alert_id": alert_id},
        {"$set": {"status": update.status.value}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return {"message": f"Alert {alert_id} updated to {update.status.value}"}

@router.get("/{alert_id}/report")
async def download_alert_report(alert_id: str):
    alert = await alerts_collection.find_one({"alert_id": alert_id})
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    report = {
        "report_id": generate_report_id(),
        "alert_id": alert_id,
        "generated_at": current_utc_time().isoformat(),
        "camera_id": alert["camera_id"],
        "event_type": alert["type"],
        "severity": alert["severity"],
        "event_summary": alert["description"],
        "status_at_report_time": alert["status"],
        "statistics": {
            "vehicle_count": alert.get("metadata", {}).get("vehicle_count", 0),
            "human_count": alert.get("metadata", {}).get("human_count", 0),
        },
        "metadata": alert.get("metadata", {})
    }

    await reports_collection.insert_one({**report, "alert_id": alert_id})
    return report
