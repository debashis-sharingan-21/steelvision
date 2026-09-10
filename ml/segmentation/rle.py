"""Run-length encoding matching the Severstal Steel Defect Detection Kaggle competition's
format: 1-indexed pixel positions, column-major (Fortran) flattening, pairs of
(start, length) space-separated in a single string.

https://www.kaggle.com/competitions/severstal-steel-defect-detection/data
"""
import numpy as np


def rle_decode(rle: str, shape: tuple[int, int]) -> np.ndarray:
    """rle: 'start length start length ...' (1-indexed, column-major). shape: (height, width)."""
    if not rle or not rle.strip():
        return np.zeros(shape, dtype=np.uint8)

    tokens = rle.split()
    starts = np.array(tokens[0::2], dtype=int) - 1
    lengths = np.array(tokens[1::2], dtype=int)

    mask = np.zeros(shape[0] * shape[1], dtype=np.uint8)
    for start, length in zip(starts, lengths):
        mask[start : start + length] = 1
    return mask.reshape(shape, order="F")


def rle_encode(mask: np.ndarray) -> str:
    """Inverse of rle_decode. mask: 2D array of 0/1 (or bool)."""
    pixels = mask.flatten(order="F")
    pixels = np.concatenate([[0], pixels, [0]])
    runs = np.where(pixels[1:] != pixels[:-1])[0] + 1
    runs[1::2] -= runs[::2]
    return " ".join(str(x) for x in runs)
