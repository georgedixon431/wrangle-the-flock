import cv2
import numpy as np
import requests
from ultralytics import YOLO
import os
import time

# =========================================================
# SETTINGS
# =========================================================

MODEL_PATH = r"C:\Users\George\uni\380\sheepmodel\weights\best.pt"

ESP32_URL = "http://10.0.0.16/cam.jpg"

# Same image size used during training
MODEL_IMAGE_SIZE = 320

# Display window width
DISPLAY_WIDTH = 900

USE_GPU = False
device = 0 if USE_GPU else "cpu"

CONFIDENCE = 0.80
IOU_THRESHOLD = 0.45


# =========================================================
# CHECK MODEL EXISTS
# =========================================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model weights not found:\n{MODEL_PATH}"
    )

print("Loading model:")
print(MODEL_PATH)

model = YOLO(MODEL_PATH)

print("Model loaded.")
print("Connecting to ESP32:")
print(ESP32_URL)
print("Press Q to quit.")


# =========================================================
# CREATE HTTP SESSION
# =========================================================

session = requests.Session()


# =========================================================
# MAIN CAMERA LOOP
# =========================================================

while True:

    try:
        # Get new image from ESP32-CAM
        response = session.get(
            ESP32_URL,
            timeout=3
        )

        response.raise_for_status()

        # Convert JPEG bytes to OpenCV image
        img_array = np.frombuffer(
            response.content,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            img_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            print("Could not decode ESP32 image.")
            continue


        # =================================================
        # YOLO DETECTION
        # =================================================

        results = model.predict(
            source=frame,
            imgsz=MODEL_IMAGE_SIZE,
            conf=CONFIDENCE,
            iou=IOU_THRESHOLD,
            device=device,
            verbose=False
        )

        result = results[0]

        # Number of detected sheep
        sheep_count = len(result.boxes)

        print(f"Sheep detected: {sheep_count}")


        # =================================================
        # DRAW YOLO DETECTIONS
        # =================================================

        annotated_image = result.plot()

        # Add sheep count to image
        cv2.putText(
            annotated_image,
            f"Sheep Count: {sheep_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )


        # =================================================
        # RESIZE FOR DISPLAY
        # =================================================

        height, width = annotated_image.shape[:2]

        scale = DISPLAY_WIDTH / width

        display_height = int(height * scale)

        display_image = cv2.resize(
            annotated_image,
            (DISPLAY_WIDTH, display_height),
            interpolation=cv2.INTER_AREA
        )


        # =================================================
        # SHOW CAMERA + DETECTIONS
        # =================================================

        cv2.imshow(
            "ESP32 Sheep Detection",
            display_image
        )


    except requests.exceptions.RequestException as e:

        print("ESP32 connection error:", e)
        time.sleep(0.5)


    except Exception as e:

        print("Error:", e)
        time.sleep(0.5)


    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# =========================================================
# CLEAN UP
# =========================================================

session.close()
cv2.destroyAllWindows()