from ml.inference.predict import Detection, compute_severity


def test_severity_zero_with_no_detections():
    assert compute_severity([], 200, 200) == 0.0


def test_severity_increases_with_confidence_and_count():
    low = [Detection("scratches", 0.3, (0, 0, 10, 10))]
    high = [Detection("scratches", 0.95, (0, 0, 10, 10))]
    many = [Detection("scratches", 0.95, (0, 0, 10, 10)) for _ in range(6)]

    s_low = compute_severity(low, 200, 200)
    s_high = compute_severity(high, 200, 200)
    s_many = compute_severity(many, 200, 200)

    assert s_low < s_high
    assert s_high < s_many
    assert 0.0 <= s_many <= 100.0


def test_severity_scales_with_defect_area():
    small = [Detection("patches", 0.8, (0, 0, 10, 10))]
    large = [Detection("patches", 0.8, (0, 0, 100, 100))]
    assert compute_severity(small, 200, 200) < compute_severity(large, 200, 200)
