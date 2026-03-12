from ultralytics import YOLO
import cv2
from pathlib import Path
import json
from datetime import datetime

# Config
MODEL_PATH = r"C:\Users\SiumNSL\Pi_Journal\runs\detect\train\weights\best.pt"
IMG_PATH = r"C:\Users\SiumNSL\Pi_Journal\test_image.jpg"
CONF = 0.25
OUTPUT_DIR = Path(r"C:\Users\SiumNSL\Pi_Journal\test_results")

# Create output dir
OUTPUT_DIR.mkdir(exist_ok=True)

# Load & predict
model = YOLO(MODEL_PATH)
results = model(IMG_PATH, conf=CONF, verbose=False, save=True)

# Save annotated image
annotated = results[0].plot()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_img = OUTPUT_DIR / f"yolov12n_test_{Path(IMG_PATH).stem}_{timestamp}.jpg"
cv2.imwrite(str(output_img), annotated)
print(f"💾 Annotated image: {output_img}")

# Show results
cv2.imshow("YOLOv12n Detection", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save detailed results JSON
detections = []
boxes = results[0].boxes
for i, box in enumerate(boxes):
    detection = {
        "id": i+1,
        "class": model.names[int(box.cls[0])],
        "confidence": float(box.conf[0]),
        "bbox": box.xyxy[0].tolist()
    }
    detections.append(detection)

result_json = {
    "image": str(IMG_PATH),
    "model": str(MODEL_PATH),
    "conf_threshold": CONF,
    "timestamp": timestamp,
    "detections": detections,
    "total_detections": len(detections)
}

json_path = OUTPUT_DIR / f"yolov12n_test_{Path(IMG_PATH).stem}_{timestamp}.json"
with open(json_path, 'w') as f:
    json.dump(result_json, f, indent=2)
print(f"💾 Results JSON: {json_path}")

# Print summary
print(f"\n📊 Detections (conf>{CONF}):")
for det in detections:
    print(f"  {det['id']}: {det['class']} ({det['confidence']:.3f})")

print("✅ Test complete! Files saved.")
