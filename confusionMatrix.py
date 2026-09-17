from ultralytics import YOLO
import os

# =========================================================
# SETTINGS
# =========================================================

MODEL_PATH = r"C:\Users\George\AppData\Local\Programs\Microsoft VS Code\runs\detect\train\weights\best.pt"

DATA_ROOT = r"C:\Users\George\uni\380\sheep photos"

YAML_PATH = os.path.join(DATA_ROOT, "sheep.yaml")

IMAGE_SIZE = 320

USE_GPU = False

device = 0 if USE_GPU else "cpu"


# =========================================================
# LOAD MODEL
# =========================================================

model = YOLO(MODEL_PATH)


# =========================================================
# VALIDATE AND CREATE CONFUSION MATRIX
# =========================================================

metrics = model.val(
    data=YAML_PATH,
    imgsz=IMAGE_SIZE,
    device=device,
    workers=0,
    plots=True,
    conf=0.4,
    iou=0.45
)


# =========================================================
# PRINT RESULTS
# =========================================================

print("\n========================================")
print("VALIDATION RESULTS")
print("========================================")

print(f"Precision:   {metrics.box.mp:.4f}")
print(f"Recall:      {metrics.box.mr:.4f}")
print(f"mAP@50:      {metrics.box.map50:.4f}")
print(f"mAP@50-95:   {metrics.box.map:.4f}")

print("\nConfusion matrix:")
print(metrics.confusion_matrix.matrix)

print("\nResults saved to:")
print(metrics.save_dir)