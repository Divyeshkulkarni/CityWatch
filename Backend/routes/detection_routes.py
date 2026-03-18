from fastapi import APIRouter
from models.detection_model import DetectionInput
from services.detection_processor import process_detection

router = APIRouter(prefix="/detections", tags=["Detections"])

@router.post("/")
async def receive_detection(data: DetectionInput):
    result = await process_detection(data)
    return result