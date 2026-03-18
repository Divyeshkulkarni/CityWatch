from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "monitoring_system")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
alerts_collection = db["alerts"]
detections_collection = db["detections"]
reports_collection = db["reports"]
cameras_collection = db["cameras"]
analytics_collection = db["analytics_logs"]