from ml.configs.classes import CLASS_NAMES
from ml.preprocessing.synthetic import main as generate_synthetic
import sys


def test_synthetic_generates_expected_layout(tmp_path, monkeypatch):
    out = tmp_path / "data"
    argv = ["synthetic.py", "--out", str(out), "--per-class", "2", "--seed", "1"]
    monkeypatch.setattr(sys, "argv", argv)
    generate_synthetic()

    for split in ("train", "val", "test"):
        images = list((out / split / "images").glob("*.jpg"))
        labels = list((out / split / "labels").glob("*.txt"))
        assert len(images) == len(labels) > 0
        for label_file in labels:
            for line in label_file.read_text().splitlines():
                cls_id = int(line.split()[0])
                assert 0 <= cls_id < len(CLASS_NAMES)

    assert (out / "SYNTHETIC_DATA_NOTICE.md").exists()
