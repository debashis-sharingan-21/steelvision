from ml.segmentation.prepare_severstal import read_annotations


def test_read_annotations_groups_by_image_and_zero_indexes_class(tmp_path):
    csv_path = tmp_path / "train.csv"
    csv_path.write_text(
        "ImageId_ClassId,EncodedPixels\n"
        "0002cc93b.jpg_1,29102 12 29346 24\n"
        "0002cc93b.jpg_2,\n"
        "0002cc93b.jpg_3,\n"
        "0002cc93b.jpg_4,\n"
        "0007a71bf.jpg_1,\n"
        "0007a71bf.jpg_2,18661 28 18863 82\n"
        "0007a71bf.jpg_3,\n"
        "0007a71bf.jpg_4,\n"
    )

    annotations = read_annotations(csv_path)

    assert set(annotations.keys()) == {"0002cc93b.jpg", "0007a71bf.jpg"}
    assert annotations["0002cc93b.jpg"] == {0: "29102 12 29346 24"}
    assert annotations["0007a71bf.jpg"] == {1: "18661 28 18863 82"}


def test_read_annotations_skips_images_with_no_defects(tmp_path):
    csv_path = tmp_path / "train.csv"
    csv_path.write_text(
        "ImageId_ClassId,EncodedPixels\n"
        "clean.jpg_1,\n"
        "clean.jpg_2,\n"
        "clean.jpg_3,\n"
        "clean.jpg_4,\n"
    )
    assert read_annotations(csv_path) == {}
