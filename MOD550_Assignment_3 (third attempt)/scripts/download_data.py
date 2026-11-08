#!/usr/bin/env python3
"""
Fetch the CWRU bearing recordings this assignment uses.

The raw .mat files total about 187 MB, which is over the ~50 MB the assignment
allows to be committed, so they are not in the repository. This script puts them
where the notebooks expect them:

    data/Normal/                               4 files   (healthy baseline, 48 kHz)
    data/12k_Drive_End_Bearing_Fault_Data/    60 files   (seeded faults, 12 kHz)

Primary source
--------------
Case Western Reserve University Bearing Data Center, Seeded Fault Test Data
https://engineering.case.edu/bearingdatacenter

The Data Center publishes the files one at a time through a web form, which does
not automate cleanly, so this script pulls them from a public GitHub mirror that
preserves the original file names and directory structure. If you would rather
take them from the primary source, download the 12 kHz Drive End Bearing Fault
Data and the Normal Baseline Data by hand and arrange them in the two folders
above; nothing else in the repository needs to change.

Usage
-----
    python scripts/download_data.py            # fetch into ./data
    python scripts/download_data.py --check    # only verify what is already there
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MIRROR = "https://github.com/s-whynot/CWRU-dataset.git"
WANTED = ["Normal", "12k_Drive_End_Bearing_Fault_Data"]
EXPECTED = {"Normal": 4, "12k_Drive_End_Bearing_Fault_Data": 60}


def count_mat(root: Path) -> dict[str, int]:
    return {d: len(list((root / d).rglob("*.mat"))) if (root / d).is_dir() else 0
            for d in WANTED}


def check(root: Path) -> bool:
    counts = count_mat(root)
    ok = True
    print(f"checking {root.resolve()}")
    for d, n in counts.items():
        want = EXPECTED[d]
        mark = "ok " if n == want else "MISSING"
        if n != want:
            ok = False
        print(f"  [{mark:>7}] {d:<38} {n:>3} / {want} .mat files")
    size = sum(f.stat().st_size for d in WANTED
               for f in (root / d).rglob("*.mat")) if ok else 0
    if ok:
        print(f"  total {size/1e6:.0f} MB -- the notebooks will run")
    return ok


def download(root: Path) -> None:
    if shutil.which("git") is None:
        sys.exit("git is required. Install git, or download the files by hand "
                 "from https://engineering.case.edu/bearingdatacenter")

    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "cwru"
        print(f"cloning {MIRROR}\n  (blobless + sparse: only the two folders we need)")
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1",
             MIRROR, str(clone)], check=True)
        subprocess.run(["git", "-C", str(clone), "sparse-checkout", "set", *WANTED],
                       check=True)
        subprocess.run(["git", "-C", str(clone), "checkout"], check=True)

        for d in WANTED:
            src, dst = clone / d, root / d
            if not src.is_dir():
                sys.exit(f"the mirror did not contain {d} -- its layout may have changed")
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  wrote {dst}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default="data", type=Path,
                    help="where to put the recordings (default: ./data)")
    ap.add_argument("--check", action="store_true",
                    help="verify an existing download instead of fetching")
    args = ap.parse_args()

    if args.check:
        sys.exit(0 if check(args.data_dir) else 1)

    if check(args.data_dir):
        print("\nalready complete -- nothing to do")
        sys.exit(0)

    print()
    download(args.data_dir)
    print()
    sys.exit(0 if check(args.data_dir) else 1)
