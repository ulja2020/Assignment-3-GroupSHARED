"""Signal preparation shared by Parts I and II; preserve the audited window definition."""

import numpy as np
from scipy.signal import resample_poly, butter, sosfiltfilt

FS = 12000

WINDOW_SECONDS = 0.25

WINDOW_SAMPLES = int(FS * WINDOW_SECONDS)

EDGE_SAMPLES = int(FS * 0.05)

LOWPASS = butter(4, 4500, btype='lowpass', fs=FS, output='sos')

def prepare_signal(values, sample_rate):
    """Resample to 12 kHz, apply the common low-pass filter, and trim both edges."""
    if sample_rate not in (12000, 48000):
        raise ValueError('Unsupported sampling rate; verify source documentation.')
    resampled = resample_poly(values, 1, sample_rate // FS, padtype='line') if sample_rate != FS else values.copy()
    filtered = sosfiltfilt(LOWPASS, resampled)
    return filtered[EDGE_SAMPLES:-EDGE_SAMPLES]
