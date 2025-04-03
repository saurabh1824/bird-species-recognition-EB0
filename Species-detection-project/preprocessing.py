import cv2
import numpy as np
import torch
from ultralytics import YOLO
import os




# Function to detect and crop birds
def preprocess_image(image_path, target_size=(224, 224)):

    # Load YOLOv8 model (pre-trained on COCO dataset)
    model = YOLO("export\\yolov8n.pt") # Use "yolov8s.pt" for better accuracy

    # Define bird class IDs from COCO dataset (YOLOv8 labels birds as class 14)
    BIRD_CLASS_ID = 14


    image = cv2.imread(image_path)
    if image is None:
        return None

    # Run YOLO detection
    results = model(image)

    # Get bounding boxes for birds
    birds = [box for box in results[0].boxes.data if int(box[5]) == BIRD_CLASS_ID]

    if not birds:
        return None  # Skip images with no detected birds


    # Choose the largest bird (in case multiple birds are detected)
    birds.sort(key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)
    x1, y1, x2, y2, _, _ = birds[0].tolist()
    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

    # Crop the detected bird
    bird_crop = image[y1:y2, x1:x2]

    # Resize while maintaining aspect ratio
    bird_h, bird_w, _ = bird_crop.shape
    scale = min(target_size[0] / bird_w, target_size[1] / bird_h)
    new_w, new_h = int(bird_w * scale), int(bird_h * scale)
    bird_resized = cv2.resize(bird_crop, (new_w, new_h))

    # Pad to maintain aspect ratio
    pad_top = (target_size[1] - new_h) // 2
    pad_bottom = target_size[1] - new_h - pad_top
    pad_left = (target_size[0] - new_w) // 2
    pad_right = target_size[0] - new_w - pad_left

    bird_padded = cv2.copyMakeBorder(bird_resized, pad_top, pad_bottom, pad_left, pad_right,
                                     cv2.BORDER_CONSTANT, value=(0, 0, 0))
    # bird_padded = cv2.fastNlMeansDenoisingColored(bird_padded, None, 10, 10, 7, 21)
    cv2.imwrite(image_path, bird_padded)
    return 1