import numpy as np

from ml.segmentation.mask_utils import mask_to_yolo_polygons


def test_mask_to_polygons_finds_one_rectangle():
    mask = np.zeros((50, 50), dtype=np.uint8)
    mask[10:30, 10:40] = 1
    polygons = mask_to_yolo_polygons(mask)
    assert len(polygons) == 1
    coords = polygons[0]
    assert len(coords) % 2 == 0
    assert all(0.0 <= v <= 1.0 for v in coords)


def test_mask_to_polygons_drops_tiny_specks():
    mask = np.zeros((50, 50), dtype=np.uint8)
    mask[0, 0] = 1  # single-pixel speck
    assert mask_to_yolo_polygons(mask, min_area=20) == []


def test_mask_to_polygons_empty_mask_returns_no_polygons():
    mask = np.zeros((20, 20), dtype=np.uint8)
    assert mask_to_yolo_polygons(mask) == []
