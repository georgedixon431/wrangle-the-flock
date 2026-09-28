

from ultralytics import YOLO
import cv2
import urllib.request
import numpy as np
import socket
import time

# =========================================================
# SETTINGS
# =========================================================

MODEL_PATH = r"C:\Users\George\uni\380\380 code\sheepmodel\weights\best.pt"

CAMERA_URL = "http://10.0.0.25/cam.jpg"

# IP address of MOTOR ESP32
ESP32_IP = "10.0.0.XX"   # CHANGE THIS
ESP32_PORT = 8080

MODEL_IMAGE_SIZE = 640
DISPLAY_WIDTH = 900

CONFIDENCE = 0.9
IOU_THRESHOLD = 0.45

USE_GPU = False

TARGET_SHEEP = 1


# Require 10 sheep for this many consecutive frames
REQUIRED_FRAMES = 3


# =========================================================
# SETUP
# =========================================================

device = 0 if USE_GPU else "cpu"

model = YOLO(MODEL_PATH)

target_frames = 0
signal_sent = False

print("Model loaded")
print(f"Camera: {CAMERA_URL}")
print(f"Target: {TARGET_SHEEP} sheep")
print("Starting detection...")


# =========================================================
# SEND COMMAND TO ESP32
# =========================================================

def send_cmd(cmd):
    try:
        with socket.create_connection((ESP32_IP, ESP32_PORT), timeout=2) as s:
            s.sendall((cmd + "\n").encode("utf-8"))

        print(f"COMMAND SENT TO ESP32: {cmd}")
        return True

    except Exception as e:
        print(f"ESP32 CONNECTION ERROR: {e}")
        return False


# =========================================================
# LIVE CAMERA LOOP
# =========================================================

while True:

    try:

        # -------------------------------------------------
        # GET IMAGE FROM ESP32-CAM
        # -------------------------------------------------

        response = urllib.request.urlopen(CAMERA_URL, timeout=5)
        image_data = np.asarray(bytearray(response.read()), dtype=np.uint8)

        frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        if frame is None:
            print("Failed to decode camera image")
            continue


        # -------------------------------------------------
        # RUN YOLO
        # -------------------------------------------------

        results = model.predict(
            source=frame,
            imgsz=MODEL_IMAGE_SIZE,
            conf=CONFIDENCE,
            iou=IOU_THRESHOLD,
            device=device,
            verbose=False
        )

        result = results[0]


        # -------------------------------------------------
        # COUNT SHEEP
        # -------------------------------------------------

        sheep_count = len(result.boxes)

        print(f"Sheep detected: {sheep_count}")


        # -------------------------------------------------
        # CHECK FOR TARGET OF 10 SHEEP
        # -------------------------------------------------

        if sheep_count == TARGET_SHEEP:

            target_frames += 1

            print(f"TARGET CHECK: {target_frames}/{REQUIRED_FRAMES}")

            if target_frames >= REQUIRED_FRAMES and not signal_sent:

                print("10 SHEEP CONFIRMED")

                if send_cmd("10SHEEP"):
                    signal_sent = True

        else:

            # Reset confirmation if count changes
            target_frames = 0


        # -------------------------------------------------
        # DRAW BOXES
        # -------------------------------------------------

        annotated_image = result.plot()

        cv2.putText(
            annotated_image,
            f"Sheep count: {sheep_count}",
            (10, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        if target_frames > 0 and not signal_sent:
            cv2.putText(
                annotated_image,
                f"Confirming 10 sheep: {target_frames}/{REQUIRED_FRAMES}",
                (10, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

        if signal_sent:
            cv2.putText(
                annotated_image,
                "10 SHEEP - SIGNAL SENT",
                (10, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )


        # -------------------------------------------------
        # RESIZE FOR DISPLAY
        # -------------------------------------------------

        height, width = annotated_image.shape[:2]

        scale = DISPLAY_WIDTH / width
        display_height = int(height * scale)

        display_image = cv2.resize(
            annotated_image,
            (DISPLAY_WIDTH, display_height),
            interpolation=cv2.INTER_AREA
        )


        # -------------------------------------------------
        # DISPLAY
        # -------------------------------------------------

        cv2.imshow("ESP32 Sheep Detection", display_image)

        if cv2.waitKey(1) & 0xFF == 27:
            break


    except Exception as e:

        print(f"ERROR: {e}")
        time.sleep(1)


cv2.destroyAllWindows()