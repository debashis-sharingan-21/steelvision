from ml.configs.classes import CLASS_NAMES
from ml.preprocessing.prepare_dataset import parse_annotation, stratified_split, voc_to_yolo_line


def test_voc_to_yolo_line_center_and_normalized():
    line = voc_to_yolo_line("scratches", xmin=10, ymin=20, xmax=30, ymax=60, img_w=200, img_h=200)
    cls_id, cx, cy, w, h = line.split()
    assert int(cls_id) == CLASS_NAMES.index("scratches")
    assert float(cx) == (10 + 30) / 2 / 200
    assert float(cy) == (20 + 60) / 2 / 200
    assert float(w) == (30 - 10) / 200
    assert float(h) == (60 - 20) / 200


def test_voc_to_yolo_line_rejects_unknown_class():
    try:
        voc_to_yolo_line("not_a_defect", 0, 0, 10, 10, 100, 100)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_parse_annotation_reads_multiple_objects(tmp_path):
    xml = """<annotation>
        <size><width>200</width><height>200</height></size>
        <object><name>crazing</name><bndbox><xmin>1</xmin><ymin>1</ymin><xmax>20</xmax><ymax>20</ymax></bndbox></object>
        <object><name>inclusion</name><bndbox><xmin>30</xmin><ymin>30</ymin><xmax>50</xmax><ymax>50</ymax></bndbox></object>
    </annotation>"""
    path = tmp_path / "sample.xml"
    path.write_text(xml)
    lines = parse_annotation(path)
    assert len(lines) == 2
    assert lines[0].startswith(f"{CLASS_NAMES.index('crazing')} ")
    assert lines[1].startswith(f"{CLASS_NAMES.index('inclusion')} ")


def test_stratified_split_covers_all_files_no_overlap(tmp_path):
    files = [tmp_path / f"crazing_{i}.jpg" for i in range(10)] + [tmp_path / f"scratches_{i}.jpg" for i in range(10)]
    for f in files:
        f.touch()
    splits = stratified_split(files, train=0.7, val=0.15, seed=1)
    all_out = splits["train"] + splits["val"] + splits["test"]
    assert sorted(all_out) == sorted(files)
    assert len(set(all_out)) == len(files)
    assert len(splits["train"]) > 0 and len(splits["test"]) > 0
