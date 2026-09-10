"""Binary mask <-> YOLO-seg normalized polygon conversion, shared by the real Severstal
converter and the synthetic generator."""
import cv2
import numpy as np


def mask_to_yolo_polygons(mask: np.ndarray, min_area: int = 20) -> list[list[float]]:
    """Returns one flat [x1, y1, x2, y2, ...] normalized-coordinate polygon per contour,
    dropping specks smaller than min_area pixels (RLE masks are noisy at the pixel level)."""
    h, w = mask.shape
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            continue
        contour = contour.reshape(-1, 2)
        if len(contour) < 3:
            continue
        norm = []
        for x, y in contour:
            norm.append(x / w)
            norm.append(y / h)
        polygons.append(norm)
    return polygons
