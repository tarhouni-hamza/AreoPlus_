from __future__ import annotations

import os
import urllib.request
import zipfile
from pathlib import Path

from app.config import DATA_DIR

# NASA Open Data Portal lists this public CMAPSSData.zip distribution.
DEFAULT_URL = "https://data.nasa.gov/docs/legacy/CMAPSSData.zip"


def main():
    raw_dir = DATA_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    archive = raw_dir / "CMAPSSData.zip"
    url = os.getenv("CMAPSS_DATA_URL", DEFAULT_URL)
    print(f"Downloading C-MAPSS dataset from: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "AeroPulse/1.0 (educational project)"})
    with urllib.request.urlopen(request, timeout=90) as response, archive.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    with zipfile.ZipFile(archive) as zipped:
        zipped.extractall(raw_dir)
    required = ["train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"]
    missing = [name for name in required if not (raw_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"The downloaded archive is missing expected files: {missing}")
    print(f"Dataset extracted to {raw_dir}")


if __name__ == "__main__":
    main()
