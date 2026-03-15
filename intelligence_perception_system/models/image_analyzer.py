import torch
import cv2
import numpy as np
from ultralytics import YOLO
import config


class ImageAnalyzer:
    def __init__(self):
        print("Loading YOLO model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Load YOLOv8
        self.model = YOLO("yolov8n.pt")
        self.model.to(self.device)

    def _categorize(self, class_name):
        """Map YOLO class to our categories"""
        class_lower = class_name.lower()

        for category, keywords in config.DETECTION_CLASSES.items():
            if any(kw in class_lower for kw in keywords):
                return category
        return "other"

    def detect_objects(self, image_path):
        """Run YOLO detection"""
        print(f"Processing image: {image_path}")

        results = self.model(image_path, conf=config.YOLO_CONFIDENCE)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.model.names[cls]

                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(conf, 3),
                    "class": class_name,
                    "category": self._categorize(class_name)
                })

        return detections

    def aggregate(self, detections):
        """Count detections by category"""
        counts = {"person": 0, "vehicle": 0, "aircraft": 0}

        for det in detections:
            category = det["category"]
            if category in counts:
                counts[category] += 1

        return counts

    def analyze(self, image_path):
        """Main analysis function"""
        detections = self.detect_objects(image_path)
        counts = self.aggregate(detections)

        result = {
            "image_path": image_path,
            "total_detections": len(detections),
            "detections": detections,
            "counts": counts,
            "confidence": 0.80
        }

        return result