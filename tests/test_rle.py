import numpy as np

from ml.segmentation.rle import rle_decode, rle_encode


def test_roundtrip_simple_rectangle():
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[2:5, 3:7] = 1
    encoded = rle_encode(mask)
    decoded = rle_decode(encoded, (10, 10))
    assert np.array_equal(mask, decoded)


def test_decode_empty_string_gives_blank_mask():
    mask = rle_decode("", (5, 5))
    assert mask.sum() == 0
    assert mask.shape == (5, 5)


def test_decode_known_rle_matches_column_major_layout():
    # A 3x3 all-zero mask with a single pixel at (row=0, col=1) set.
    # Column-major flatten of a 3x3 image: col0(3px), col1(3px), col2(3px).
    # Pixel (0,1) is index 3 (0-indexed) -> 1-indexed start=4, length=1.
    mask = rle_decode("4 1", (3, 3))
    expected = np.zeros((3, 3), dtype=np.uint8)
    expected[0, 1] = 1
    assert np.array_equal(mask, expected)


def test_encode_decode_roundtrip_random_mask():
    rng = np.random.default_rng(0)
    mask = (rng.random((20, 30)) > 0.7).astype(np.uint8)
    encoded = rle_encode(mask)
    decoded = rle_decode(encoded, (20, 30))
    assert np.array_equal(mask, decoded)
