"""
cwru_data.py -- shared data layer for MOD550 Assignment 3.

Both notebooks import this module so that Part I (SVM) and Part II (1-D CNN)
are trained and tested on *exactly* the same windows and the same split.
That is what makes the two parts comparable: if the two notebooks each built
their own windows, any difference in score could come from the data rather
than from the model.

What this module does
---------------------
1.  Reads the CWRU drive-end accelerometer channel out of the .mat files.
2.  Resamples the Normal baseline recordings from 48 kHz to 12 kHz so that
    every signal in the study shares one sampling rate (see `load_recording`).
3.  Cuts each recording into non-overlapping windows of 2048 samples.
4.  Labels every window with its fault class, motor load and -- importantly --
    the recording it came from, so that splits can be made without leakage.

Reference
---------
Case Western Reserve University Bearing Data Center seeded fault test data.
https://engineering.case.edu/bearingdatacenter
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass

import numpy as np
import scipy.io as sio
from scipy.signal import decimate

# --------------------------------------------------------------------------
# Acquisition constants
# --------------------------------------------------------------------------
FS = 12_000                 # Hz, the sampling rate every signal is brought to
FS_NORMAL_RAW = 48_000      # Hz, the rate the Normal baseline was recorded at
WINDOW = 2048               # samples per window = 170.7 ms = ~5 shaft turns

# Fault diameters kept. 0.028" is excluded because the Bearing Data Center only
# published it for Ball and Inner-Race faults at 12 kHz; keeping it would give
# those two fault types a severity level the Outer-Race type does not have.
FAULT_SIZES = ("007", "014", "021")

# The target is fault LOCATION and SEVERITY together, ten classes.
#
# Location alone (Normal / Ball / Inner / Outer) is close to trivial on this
# rig: a tuned RBF SVM on the features of Part I reaches macro-F1 0.999 on a
# completely held-out motor load, which leaves nothing to compare models on.
# Severity is also the part a maintenance planner actually needs, since it
# drives how urgently the bearing has to come out. Splitting each fault type
# by seeded defect diameter gives a problem that is hard enough to separate
# methods and still answers a real question.
CLASSES = ("Normal",
           "Ball_007", "Ball_014", "Ball_021",
           "Inner_007", "Inner_014", "Inner_021",
           "Outer_007", "Outer_014", "Outer_021")
CLASS_TO_INT = {c: i for i, c in enumerate(CLASSES)}
LOCATIONS = ("Normal", "Ball", "Inner", "Outer")
DIR_TO_LOCATION = {"B": "Ball", "IR": "Inner", "OR": "Outer"}

# Nominal shaft speed per motor load, used only for the two Normal recordings
# that carry no RPM field in the .mat file (98 and 99).
NOMINAL_RPM = {0: 1797, 1: 1772, 2: 1750, 3: 1730}

# SKF 6205-2RS JEM deep-groove ball bearing (the drive-end bearing).
# Defect-frequency multipliers, expressed as multiples of shaft speed.
BEARING = dict(n_balls=9, d_ball=0.3126, d_pitch=1.537)   # inches
BPFI_MULT = 5.4152    # ball pass frequency, inner race
BPFO_MULT = 3.5848    # ball pass frequency, outer race
BSF_MULT = 2.3568     # ball spin frequency
FTF_MULT = 0.3983     # fundamental train (cage) frequency

DATA_ROOT = "data"


# --------------------------------------------------------------------------
# Recording-level reading
# --------------------------------------------------------------------------
@dataclass
class Recording:
    """One .mat file: a single ~10 s run at one fault condition and load."""
    rec_id: str          # unique key, e.g. "IR_007_load1"
    path: str
    cls: str             # one of CLASSES, e.g. "Inner_014"
    location: str        # Normal | Ball | Inner | Outer
    load: int            # motor load, 0-3 hp
    fault_size: str      # "007" | "014" | "021" | "none"
    or_position: str     # outer-race clock position: "@3" | "@6" | "@12" | "-"
    rpm: int
    signal: np.ndarray   # drive-end acceleration at 12 kHz

    @property
    def shaft_hz(self) -> float:
        return self.rpm / 60.0

    @property
    def duration_s(self) -> float:
        return len(self.signal) / FS


def _read_mat(path: str):
    """
    Return (drive-end signal, rpm or None) from one CWRU .mat file.

    The channel must be selected by the file's own record number, not simply by
    taking the first key that ends in `DE_time`. At least one published file,
    `Normal/99_Normal_2.mat`, carries a stray copy of the *previous* record's
    variables alongside its own::

        99_Normal_2.mat -> ['ans', 'X098_DE_time', 'X098_FE_time',
                                   'X099_DE_time', 'X099_FE_time']

    Taking the first match there silently loads record 98 -- the 1 hp baseline --
    in place of the 2 hp one. Since this study splits by motor load, that would
    put a byte-identical copy of a training recording into the validation set and
    quietly inflate every validation score. The `build_dataset` duplicate check is
    what catches it if this ever regresses.
    """
    mat = sio.loadmat(path)
    de_keys = [k for k in mat if k.endswith("DE_time")]
    if not de_keys:
        raise KeyError(f"no drive-end channel in {path}")
    if len(de_keys) > 1:
        record = re.match(r"(\d+)", os.path.basename(path))
        if record is None:
            raise KeyError(f"cannot resolve the record number of {path}")
        wanted = f"X{int(record.group(1)):03d}_DE_time"
        if wanted not in de_keys:
            raise KeyError(f"{path} holds {de_keys} but not the expected {wanted}")
        de_keys = [wanted]
    signal = np.asarray(mat[de_keys[0]], dtype=np.float64).ravel()
    rpm_keys = [k for k in mat if re.fullmatch(r"X\d+RPM", k)]
    rpm = int(np.asarray(mat[rpm_keys[0]]).ravel()[0]) if rpm_keys else None
    return signal, rpm


def load_recording(path: str, data_root: str = DATA_ROOT) -> Recording:
    """
    Read one .mat file into a Recording, resampling if required.

    The Normal baseline runs were acquired at 48 kHz while the 12k Drive-End
    fault runs were acquired at 12 kHz. Both sets are ~10 s long, which is how
    the difference shows up: a Normal file holds ~484 000 samples where a fault
    file holds ~122 000. Feeding both to a model unchanged would let it
    recognise the Normal class from its sampling rate rather than from the
    bearing, so the Normal signals are decimated by 4 with the anti-alias
    filter that `scipy.signal.decimate` applies by default.
    """
    rel = os.path.relpath(path, data_root).replace(os.sep, "/")
    signal, rpm = _read_mat(path)

    if rel.startswith("Normal"):
        location, cls, fault_size, or_position = "Normal", "Normal", "none", "-"
        load = int(re.search(r"_(\d)\.mat$", rel).group(1))
        signal = decimate(signal, FS_NORMAL_RAW // FS, ftype="fir", zero_phase=True)
        rec_id = f"Normal_load{load}"
    else:
        parts = rel.split("/")           # 12k_..._Data / <B|IR|OR> / <size> [/ @pos] / file
        location = DIR_TO_LOCATION[parts[1]]
        fault_size = parts[2]
        cls = f"{location}_{fault_size}"
        or_position = parts[3] if parts[3].startswith("@") else "-"
        load = int(re.search(r"_(\d)\.mat$", rel).group(1))
        tag = f"{parts[1]}_{fault_size}"
        if or_position != "-":
            tag += f"_{or_position.lstrip('@')}oclock"
        rec_id = f"{tag}_load{load}"

    if rpm is None:
        rpm = NOMINAL_RPM[load]

    return Recording(rec_id, path, cls, location, load, fault_size,
                     or_position, rpm, signal.astype(np.float64))


def list_recordings(data_root: str = DATA_ROOT) -> list[Recording]:
    """Every recording used in this study, in a deterministic order."""
    paths = sorted(glob.glob(os.path.join(data_root, "Normal", "*.mat")))
    for size in FAULT_SIZES:
        paths += sorted(glob.glob(os.path.join(
            data_root, "12k_Drive_End_Bearing_Fault_Data", "*", size, "**", "*.mat"),
            recursive=True))
    recs = [load_recording(p, data_root) for p in sorted(set(paths))]
    recs.sort(key=lambda r: (CLASS_TO_INT[r.cls], r.or_position, r.load))
    return recs


# --------------------------------------------------------------------------
# Windowing
# --------------------------------------------------------------------------
def window_signal(signal: np.ndarray, window: int = WINDOW) -> np.ndarray:
    """Cut a signal into non-overlapping windows; drop the short remainder.

    Non-overlapping is a deliberate choice. Overlapping windows share samples,
    so two windows that overlap are near-duplicates of each other; if one lands
    in training and the other in test, the test score is inflated.
    """
    n = (len(signal) // window) * window
    return signal[:n].reshape(-1, window)


def build_dataset(data_root: str = DATA_ROOT, window: int = WINDOW):
    """
    Build the full window-level dataset.

    Returns
    -------
    X        (n_windows, window) float32  -- raw acceleration, unscaled
    y        (n_windows,) int             -- class index into CLASSES
    meta     dict of per-window arrays: rec_id, load, fault_size, or_position,
             rpm, shaft_hz
    recs     list[Recording]
    """
    recs = list_recordings(data_root)
    Xs, ys, rec_ids, loads, sizes, positions, rpms, locs = ([] for _ in range(8))

    for r in recs:
        w = window_signal(r.signal, window)
        Xs.append(w)
        ys.append(np.full(len(w), CLASS_TO_INT[r.cls], dtype=np.int64))
        rec_ids.append(np.full(len(w), r.rec_id, dtype=object))
        loads.append(np.full(len(w), r.load, dtype=np.int64))
        sizes.append(np.full(len(w), r.fault_size, dtype=object))
        positions.append(np.full(len(w), r.or_position, dtype=object))
        rpms.append(np.full(len(w), r.rpm, dtype=np.int64))
        locs.append(np.full(len(w), r.location, dtype=object))

    X = np.concatenate(Xs).astype(np.float32)
    y = np.concatenate(ys)
    meta = dict(
        rec_id=np.concatenate(rec_ids),
        load=np.concatenate(loads),
        fault_size=np.concatenate(sizes),
        or_position=np.concatenate(positions),
        rpm=np.concatenate(rpms),
        location=np.concatenate(locs),
    )
    meta["shaft_hz"] = meta["rpm"] / 60.0
    return X, y, meta, recs


# --------------------------------------------------------------------------
# The split
# --------------------------------------------------------------------------
TRAIN_LOADS = (0, 1)    # 0 hp and 1 hp
VAL_LOAD = 2            # 2 hp -- every model-selection decision is made here
TEST_LOAD = 3           # 3 hp -- held out, scored once, at the very end


def make_split(meta: dict,
               train_loads=TRAIN_LOADS,
               val_load: int = VAL_LOAD,
               test_load: int = TEST_LOAD):
    """
    Split by motor load, not at random.

    Every recording was made at one motor load, so holding out a load holds out
    whole recordings: no window in validation or test shares a recording -- let
    alone overlapping samples -- with any window used for fitting.

    It is also the question an asset-management team actually has to answer. A
    classifier is commissioned on the operating points available at the time;
    it then has to keep working when the machine is run at a load it was never
    shown. Testing on a held-out load measures that directly, where a random
    split over windows does not: windows cut from one 10-second recording are
    near-duplicates of each other, so a random split puts near-copies of the
    test windows into training and the reported score stops meaning anything.

    Both notebooks call this function, so Part I and Part II are fitted,
    tuned and scored on exactly the same windows.

    Returns three boolean masks (train, val, test) over the window arrays.
    """
    train = np.isin(meta["load"], list(train_loads))
    val = meta["load"] == val_load
    test = meta["load"] == test_load
    return train, val, test
