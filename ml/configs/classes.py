# Single source of truth for the 6 NEU-DET defect classes.
# Order matters: it defines the class index used everywhere (YOLO labels, model output, API).
CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]
