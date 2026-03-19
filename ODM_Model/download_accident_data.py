# download_accident_data.py
from roboflow import Roboflow
import os

API_KEY = "XRmucfcbP5VHLJBKfalbMFRYSXURGyFa4NKqVjRuMkKE2"   # ← paste your key here

rf      = Roboflow(api_key=API_KEY)
project = rf.workspace("object-detection-3iugc") \
             .project("vehicle-crash-dataset")
dataset = project.version(1).download(
    "coco",
    location="accident_dataset"
)

print("\nDownload complete!")
print("Structure:")
for root, dirs, files in os.walk("accident_dataset"):
    dirs[:] = [d for d in dirs
               if d != "__pycache__"]
    level   = root.replace(
                "accident_dataset", ""
              ).count(os.sep)
    indent  = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    for f in files[:3]:
        print(f"{indent}  {f}")