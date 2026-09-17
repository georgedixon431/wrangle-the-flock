# train_sheep_full.py

from ultralytics import YOLO
import os
import textwrap
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# SETTINGS
# =========================================================

DATA_ROOT = r"C:\Users\George\uni\380\sheep photos"

NAMES = ["sheep"]

# Change to True only if CUDA GPU is installed and working
USE_GPU = False

# Smaller image size is more realistic for embedded deployment
IMGSZ = 320

# Small dataset, so use early stopping
EPOCHS = 120

BATCH = 8


# =========================================================
# EXPECTED FOLDER STRUCTURE
# =========================================================
#
# sheep photos/
#     train/
#         images/
#         labels/
#     val/
#         images/
#         labels/
#     test/
#         images/
#
# =========================================================


YAML_PATH = os.path.join(DATA_ROOT, "sheep.yaml")


# =========================================================
# CREATE DATASET YAML
# =========================================================

yaml_text = textwrap.dedent(
    f"""
    path: {DATA_ROOT.replace(os.sep, '/')}

    train: train/images
    val: val/images
    test: test/images

    names:
      0: sheep
    """
)

with open(YAML_PATH, "w", encoding="utf-8") as f:
    f.write(yaml_text)

print("\nDataset YAML created:")
print(YAML_PATH)

print("\n" + "=" * 60)
print(yaml_text)
print("=" * 60)


# =========================================================
# DEVICE
# =========================================================

device = 0 if USE_GPU else "cpu"

print("\nTraining device:", device)


# =========================================================
# LOAD PRETRAINED YOLO MODEL
# =========================================================

model = YOLO("yolov8n.pt")


# =========================================================
# TRAIN
# =========================================================

print("\n" + "=" * 60)
print("STARTING TRAINING")
print("=" * 60)

model.train(
    data=YAML_PATH,

    imgsz=IMGSZ,

    epochs=EPOCHS,

    batch=BATCH,

    device=device,
    # Save training outputs here
    project=r"C:\Users\George\uni\380",
    name="sheepmodel",
    exist_ok=True,

    # Stop training if validation fitness does not improve
    patience=25,

    # Freeze early pretrained layers for small dataset
    freeze=10,

    # Windows-safe
    workers=0,

    # Faster epochs if enough RAM
    cache=True,

    # Save Ultralytics graphs
    plots=True,

    # Moderate augmentations
    degrees=8,
    translate=0.10,
    scale=0.20,

    fliplr=0.5,
    flipud=0.0,

    hsv_h=0.015,
    hsv_s=0.4,
    hsv_v=0.3,

    mosaic=0.5,

    # Disable mosaic near end of training
    close_mosaic=10
)


# =========================================================
# FIND BEST MODEL
# =========================================================

best_weights = model.trainer.best
run_dir = model.trainer.save_dir

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)

print("Best weights:")
print(best_weights)

print("\nTraining output folder:")
print(run_dir)


# =========================================================
# VALIDATE BEST MODEL
# =========================================================

best_model = YOLO(best_weights)

print("\n" + "=" * 60)
print("VALIDATING BEST MODEL")
print("=" * 60)

metrics = best_model.val(
    data=YAML_PATH,
    imgsz=IMGSZ,
    device=device,
    workers=0,
    plots=True
)


# =========================================================
# PRINT FINAL VALIDATION METRICS
# =========================================================

print("\n" + "=" * 60)
print("FINAL VALIDATION RESULTS")
print("=" * 60)

print(f"Precision:       {metrics.box.mp:.4f}")
print(f"Recall:          {metrics.box.mr:.4f}")
print(f"mAP@50:          {metrics.box.map50:.4f}")
print(f"mAP@50-95:       {metrics.box.map:.4f}")

print("=" * 60)


# =========================================================
# READ TRAINING RESULTS CSV
# =========================================================

results_csv = os.path.join(run_dir, "results.csv")

if os.path.exists(results_csv):

    df = pd.read_csv(results_csv)

    # Remove spaces that can sometimes appear in column headings
    df.columns = df.columns.str.strip()

    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)

    print("Epochs completed:", len(df))

    best_epoch_index = df["metrics/mAP50(B)"].idxmax()

    best_epoch = best_epoch_index + 1

    best_map50 = df.loc[
        best_epoch_index,
        "metrics/mAP50(B)"
    ]

    best_map5095 = df.loc[
        best_epoch_index,
        "metrics/mAP50-95(B)"
    ]

    best_precision = df.loc[
        best_epoch_index,
        "metrics/precision(B)"
    ]

    best_recall = df.loc[
        best_epoch_index,
        "metrics/recall(B)"
    ]

    print(f"Best epoch:      {best_epoch}")
    print(f"Best mAP@50:     {best_map50:.4f}")
    print(f"Best mAP@50-95:  {best_map5095:.4f}")
    print(f"Precision:       {best_precision:.4f}")
    print(f"Recall:          {best_recall:.4f}")


    # =====================================================
    # CREATE CLEAN REPORT PERFORMANCE CHART
    # =====================================================

    epochs = range(1, len(df) + 1)

    plt.figure(figsize=(9, 5))

    plt.plot(
        epochs,
        df["metrics/precision(B)"],
        label="Precision"
    )

    plt.plot(
        epochs,
        df["metrics/recall(B)"],
        label="Recall"
    )

    plt.plot(
        epochs,
        df["metrics/mAP50(B)"],
        label="mAP@50"
    )

    plt.plot(
        epochs,
        df["metrics/mAP50-95(B)"],
        label="mAP@50-95"
    )

    plt.xlabel("Epoch")
    plt.ylabel("Score")

    plt.title(
        "Sheep Detection Performance During Training"
    )

    plt.legend()

    plt.grid(alpha=0.3)

    plt.tight_layout()

    report_chart = os.path.join(
        run_dir,
        "sheep_detection_performance.png"
    )

    plt.savefig(
        report_chart,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    print("\nPerformance chart saved to:")
    print(report_chart)

else:

    print(
        "\nWARNING: results.csv could not be found."
    )


# =========================================================
# PRINT USEFUL ULTRALYTICS REPORT FILES
# =========================================================

print("\n" + "=" * 60)
print("USEFUL FILES FOR FINAL REPORT")
print("=" * 60)

useful_files = [
    "results.png",
    "confusion_matrix.png",
    "confusion_matrix_normalized.png",
    "PR_curve.png",
    "P_curve.png",
    "R_curve.png",
    "F1_curve.png"
]

for filename in useful_files:

    filepath = os.path.join(
        run_dir,
        filename
    )

    if os.path.exists(filepath):
        print("[FOUND]", filepath)

    else:
        print("[NOT FOUND]", filepath)


# =========================================================
# RUN TEST IMAGE PREDICTIONS
# =========================================================

test_folder = os.path.join(
    DATA_ROOT,
    "test",
    "images"
)

if os.path.exists(test_folder):

    print("\n" + "=" * 60)
    print("RUNNING TEST IMAGE PREDICTIONS")
    print("=" * 60)

    predictions = best_model.predict(
        source=test_folder,

        imgsz=IMGSZ,

        device=device,

        # Initial threshold — tune later if needed
        conf=0.30,

        # NMS overlap threshold
        iou=0.45,

        save=True,

        workers=0
    )


    # =====================================================
    # COUNT SHEEP
    # =====================================================

    print("\n" + "=" * 60)
    print("SHEEP COUNTS")
    print("=" * 60)

    for result in predictions:

        sheep_count = len(result.boxes)

        image_name = os.path.basename(
            result.path
        )

        print(
            f"{image_name:<30} "
            f"Predicted sheep: {sheep_count}"
        )


        # Machine target condition
        if sheep_count == 10:

            print(
                "   >>> TARGET REACHED: 10 sheep"
            )


    if predictions:

        print(
            "\nAnnotated predictions saved to:"
        )

        print(
            predictions[0].save_dir
        )

else:

    print(
        "\nNo test/images folder found. "
        "Skipping test predictions."
    )


# =========================================================
# EXPORT INT8 TFLITE MODEL
# =========================================================

print("\n" + "=" * 60)
print("EXPORTING INT8 TFLITE MODEL")
print("=" * 60)

try:

    export_path = best_model.export(
        format="tflite",

        imgsz=IMGSZ,

        int8=True,

        data=YAML_PATH
    )

    print(
        "\nTFLite model exported to:"
    )

    print(export_path)

except Exception as e:

    print(
        "\nTFLite export failed."
    )

    print(
        "This does not affect the trained YOLO weights."
    )

    print("Reason:")
    print(e)


# =========================================================
# FINAL REPORT SUMMARY
# =========================================================

print("\n" + "=" * 60)
print("PROJECT MODEL SUMMARY")
print("=" * 60)

print("Model:          YOLOv8n")
print("Classes:        1 (sheep)")
print("Image size:    ", IMGSZ)
print("Batch size:    ", BATCH)
print("Max epochs:    ", EPOCHS)

print(
    "Epochs trained:",
    len(df) if os.path.exists(results_csv)
    else "Unknown"
)

print(f"Final Precision: {metrics.box.mp:.4f}")
print(f"Final Recall:    {metrics.box.mr:.4f}")
print(f"Final mAP@50:    {metrics.box.map50:.4f}")
print(f"Final mAP50-95:  {metrics.box.map:.4f}")

print("\nBest weights:")
print(best_weights)

print("\nAll training/report outputs:")
print(run_dir)

print("=" * 60)