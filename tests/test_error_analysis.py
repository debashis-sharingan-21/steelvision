from ml.configs.classes import CLASS_NAMES
from ml.evaluation.error_analysis import iou, load_ground_truth


def test_iou_identical_boxes_is_one():
    box = (10, 10, 50, 50)
    assert iou(box, box) == 1.0


def test_iou_disjoint_boxes_is_zero():
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_iou_partial_overlap():
    # Two 20x20 boxes overlapping in a 10x10 region: intersection 100, union 700.
    a = (0, 0, 20, 20)
    b = (10, 10, 30, 30)
    assert abs(iou(a, b) - (100 / 700)) < 1e-6


def test_load_ground_truth_denormalizes_correctly(tmp_path):
    label_path = tmp_path / "sample.txt"
    cls_idx = CLASS_NAMES.index("scratches")
    # center (0.5, 0.5), size (0.2, 0.4) in a 100x200 image
    label_path.write_text(f"{cls_idx} 0.5 0.5 0.2 0.4")

    boxes = load_ground_truth(label_path, img_w=100, img_h=200)
    assert len(boxes) == 1
    cls_name, (xmin, ymin, xmax, ymax) = boxes[0]
    assert cls_name == "scratches"
    assert (xmin, ymin, xmax, ymax) == (40.0, 60.0, 60.0, 140.0)


def test_load_ground_truth_missing_file_returns_empty(tmp_path):
    assert load_ground_truth(tmp_path / "missing.txt", 100, 100) == []
