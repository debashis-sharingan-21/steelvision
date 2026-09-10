"""One-time helper to fetch the real NEU-DET dataset via the Kaggle API and lay it out
the way ml/preprocessing/prepare_dataset.py expects.

Requires a Kaggle account + API token (~/.kaggle/kaggle.json) and internet access —
neither is available in the sandbox this project was built in, so this script is meant
to be run on your own machine.

Usage:
    pip install kaggle
    python scripts/download_neu_det.py --out data/raw
"""
import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

DATASET = "danielfinez/neu-det-steel-surface-defect-detection-dataset"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/raw")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {DATASET} via Kaggle API...")
    subprocess.run(
        [sys.executable, "-m", "kaggle", "datasets", "download", "-d", DATASET, "-p", str(out)],
        check=True,
    )

    zip_path = next(out.glob("*.zip"), None)
    if zip_path is None:
        raise SystemExit("Expected a downloaded .zip in " + str(out))

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out)
    zip_path.unlink()

    # Normalize into out/NEU-DET/{IMAGES,ANNOTATIONS} regardless of the zip's internal layout.
    images_dir = next(out.rglob("IMAGES"), None)
    ann_dir = next(out.rglob("ANNOTATIONS"), None)
    if images_dir is None or ann_dir is None:
        raise SystemExit(
            f"Could not find IMAGES/ and ANNOTATIONS/ under {out} — inspect the extracted "
            "archive and adjust this script if Kaggle changed the layout."
        )

    target = out / "NEU-DET"
    target.mkdir(exist_ok=True)
    if images_dir.resolve() != (target / "IMAGES").resolve():
        shutil.move(str(images_dir), str(target / "IMAGES"))
    if ann_dir.resolve() != (target / "ANNOTATIONS").resolve():
        shutil.move(str(ann_dir), str(target / "ANNOTATIONS"))

    print(f"Ready: {target}/IMAGES and {target}/ANNOTATIONS")
    print(f"Next: python -m ml.preprocessing.prepare_dataset --source {target} --out data")


if __name__ == "__main__":
    main()
