from ultralytics import YOLO
import os
import cv2

# =========================================================
# SETTINGS
# =========================================================

MODEL_PATH = r"C:\Users\George\uni\380\sheepmodel\weights\best.pt"

TEST_FOLDER = r"C:\Users\George\uni\380\sheep photos\test\images"

# Size used BY THE MODEL
MODEL_IMAGE_SIZE = 320

# Size used ONLY FOR DISPLAY
DISPLAY_WIDTH = 900

CONFIDENCE = 0.4
IOU_THRESHOLD = 0.45

USE_GPU = False


# =========================================================
# SETUP
# =========================================================

device = 0 if USE_GPU else "cpu"

model = YOLO(MODEL_PATH)

image_extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp"
)


# =========================================================
# LOOP THROUGH TEST IMAGES
# =========================================================

for filename in sorted(os.listdir(TEST_FOLDER)):

    if not filename.lower().endswith(image_extensions):
        continue

    image_path = os.path.join(TEST_FOLDER, filename)

    # -----------------------------------------------------
    # RUN MODEL
    #
    # IMPORTANT:
    # YOLO performs inference at 320.
    # Do NOT resize the image to 900 before this.
    # -----------------------------------------------------

    results = model.predict(
        source=image_path,
        imgsz=MODEL_IMAGE_SIZE,
        conf=CONFIDENCE,
        iou=IOU_THRESHOLD,
        device=device,
        verbose=False
    )

    result = results[0]

    # -----------------------------------------------------
    # COUNT SHEEP
    # -----------------------------------------------------

    sheep_count = len(result.boxes)

    print(f"{filename}: {sheep_count} sheep")

    # -----------------------------------------------------
    # DRAW BOXES
    # -----------------------------------------------------

    annotated_image = result.plot()

    # Add sheep count BEFORE display resizing
    cv2.putText(
        annotated_image,
        f"Sheep count: {sheep_count}",
        (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    if sheep_count == 10:
        cv2.putText(
            annotated_image,
            "TARGET REACHED",
            (10, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

    # -----------------------------------------------------
    # RESIZE ONLY FOR DISPLAY
    # -----------------------------------------------------

    height, width = annotated_image.shape[:2]

    # Preserve aspect ratio
    scale = DISPLAY_WIDTH / width

    display_height = int(height * scale)

    display_image = cv2.resize(
        annotated_image,
        (DISPLAY_WIDTH, display_height),
        interpolation=cv2.INTER_AREA
    )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    cv2.imshow("Sheep Detection", display_image)

    # Any key = next image
    # ESC = exit
    key = cv2.waitKey(0)

    if key == 27:
        break


cv2.destroyAllWindows()