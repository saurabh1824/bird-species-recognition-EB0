from ultralytics import YOLO


def detect_bird(image_path):
    # Load the YOLOv8 model (pre-trained on COCO dataset)
    model = YOLO("export\\yolov8n.pt")
    """Runs YOLOv8 on the given image and returns results."""
    results = model(image_path)  # Run detection
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            if class_id == 14:  # COCO dataset class ID for "bird"
                return True
    
    return False

# check detect_bird manually
# print("give path")
# img_path = input()
# print(detect_bird(img_path))
