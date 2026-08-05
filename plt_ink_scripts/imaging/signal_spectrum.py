"""
Signal, Spectrum and Spectrogram
Time trace, Welch power spectral density with annotated peaks, and a
spectrogram showing how the content evolves. Welch and the STFT are
implemented in numpy, so this runs without scipy.
requires_data: true
data_columns: channel, t, amplitude
sample_data: signal_timeseries.csv
tags: imaging, signal-processing, spectrum, engineering, vibration
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(channel='channel', t='t', amplitude='amplitude')
SAMPLE = 'signal_timeseries.csv'
FOCUS = None               # channel for the spectrogram; None = the last one
SEGMENT = 256              # Welch/STFT window length in samples
AMPLITUDE_LABEL = 'Acceleration (g)'
N_PEAKS = 3


def _opt(name, default):
    value = globals().get(name)
    return default if value is None else value


def _sample_dir():
    """Folder holding the bundled example data.

    The extension injects `_sample_data_dir`; the `__file__` branch only
    matters when the template is run straight from the bank folder. Looked up
    lazily because `__file__` is undefined when the code is exec'd inline.
    """
    root = globals().get('_sample_data_dir')
    if root:
        return root
    here = globals().get('__file__')
    if here:
        return os.path.join(os.path.dirname(os.path.abspath(here)),
                            '..', '..', 'sample_data')
    return 'sample_data'


def _load(sample, needed):
    frame = globals().get('data')
    if frame is not None and not set(needed) - set(map(str, frame.columns)):
        return frame.copy()
    return pd.read_csv(os.path.join(_sample_dir(), sample))


df = _load(SAMPLE, [COLS['t'], COLS['amplitude']])
has_channels = COLS['channel'] in df.columns
channels = list(pd.unique(df[COLS['channel']])) if has_channels else [None]


def welch(x, fs, nperseg=SEGMENT, overlap=0.5):
    """Welch PSD: average the periodograms of overlapping Hann windows."""
    step = max(int(nperseg * (1 - overlap)), 1)
    window = np.hanning(nperseg)
    # Normalisation so the result is a density in units^2/Hz.
    scale = 1.0 / (fs * np.sum(window ** 2))
    segments = [x[i:i + nperseg] for i in range(0, x.size - nperseg + 1, step)]
    if not segments:
        segments = [np.pad(x, (0, nperseg - x.size))]
    psd = np.zeros(nperseg // 2 + 1)
    for segment in segments:
        spectrum = np.fft.rfft((segment - segment.mean()) * window)
        psd += np.abs(spectrum) ** 2 * scale
    psd /= len(segments)
    psd[1:-1] *= 2.0                       # one-sided
    return np.fft.rfftfreq(nperseg, 1 / fs), psd


def spectrogram(x, fs, nperseg=SEGMENT, overlap=0.75):
    """Short-time Fourier magnitude, in dB."""
    step = max(int(nperseg * (1 - overlap)), 1)
    window = np.hanning(nperseg)
    starts = range(0, x.size - nperseg + 1, step)
    columns = []
    for i in starts:
        spectrum = np.fft.rfft((x[i:i + nperseg] - x[i:i + nperseg].mean())
                               * window)
        columns.append(np.abs(spectrum) ** 2)
    power = np.array(columns).T
    times = (np.array(list(starts)) + nperseg / 2) / fs
    return times, np.fft.rfftfreq(nperseg, 1 / fs), 10 * np.log10(power + 1e-12)


def find_peaks(freq, psd, count, min_freq_bins=4):
    """Local maxima, strongest first, kept apart so one peak is not counted twice.

    The first few bins are skipped: 1/f noise and any residual DC offset pile
    up there and would otherwise outrank the tones that actually matter.
    """
    interior = np.flatnonzero((psd[1:-1] > psd[:-2]) & (psd[1:-1] > psd[2:])) + 1
    interior = interior[interior >= min_freq_bins]
    chosen = []
    for i in interior[np.argsort(-psd[interior])]:
        if all(abs(freq[i] - freq[j]) > (freq[1] - freq[0]) * 4 for j in chosen):
            chosen.append(i)
        if len(chosen) == count:
            break
    return chosen


W = _opt('_fig_width', 12.0)
H = _opt('_fig_height', 7.5)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.25], width_ratios=[1.0, 1.0])
ax_time = fig.add_subplot(gs[0, 0])
ax_psd = fig.add_subplot(gs[0, 1])
ax_spec = fig.add_subplot(gs[1, :])

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC']
focus = FOCUS if FOCUS in channels else channels[-1]

for i, channel in enumerate(channels):
    block = df if channel is None else df[df[COLS['channel']] == channel]
    t = block[COLS['t']].to_numpy(float)
    x = block[COLS['amplitude']].to_numpy(float)
    fs = 1.0 / np.median(np.diff(t))
    colour = PALETTE[i % len(PALETTE)]

    # A short window only: a few thousand overplotted samples read as a solid
    # band, and the point of this panel is to show the waveform shape.
    span = t.max() - t.min()
    window = min(0.25, 0.35 * span)
    show = t <= t.min() + window
    ax_time.plot(t[show], x[show], color=colour, linewidth=0.7, alpha=0.85,
                 label=str(channel) if channel is not None else None)

    freq, psd = welch(x, fs)
    ax_psd.semilogy(freq, psd, color=colour, linewidth=1.2, alpha=0.9,
                    label=str(channel) if channel is not None else None)

    if channel == focus:
        for j in find_peaks(freq, psd, N_PEAKS):
            ax_psd.annotate(f'{freq[j]:.0f} Hz', xy=(freq[j], psd[j]),
                            xytext=(0, 12), textcoords='offset points',
                            ha='center', fontsize=7.5, color='#333333',
                            arrowprops=dict(arrowstyle='-|>', color='#333333',
                                            linewidth=0.9))

# Headroom so the peak callouts do not run into the panel title.
ax_psd.set_ylim(top=ax_psd.get_ylim()[1] * 12)

ax_time.set_xlabel('Time (s)')
ax_time.set_ylabel(AMPLITUDE_LABEL)
ax_time.set_title(f'a   Time trace (first {window * 1000:.0f} ms)',
                  fontsize=10, loc='left', fontweight='bold')
if has_channels:
    ax_time.legend(fontsize=7.5, loc='upper right', framealpha=0.9, ncol=3)

ax_psd.set_xlabel('Frequency (Hz)')
ax_psd.set_ylabel(f'PSD ({AMPLITUDE_LABEL.split("(")[0].strip()}$^2$/Hz)')
ax_psd.set_title(f'b   Welch PSD ({SEGMENT}-sample Hann, 50% overlap)',
                 fontsize=10, loc='left', fontweight='bold')
if has_channels:
    ax_psd.legend(fontsize=7.5, loc='upper right', framealpha=0.9)

# ── Spectrogram of the focus channel ─────────────────────────────────────────
block = df if focus is None else df[df[COLS['channel']] == focus]
t = block[COLS['t']].to_numpy(float)
x = block[COLS['amplitude']].to_numpy(float)
fs = 1.0 / np.median(np.diff(t))
times, freqs, power = spectrogram(x, fs)

cmap = _opt('_colormap', 'magma')
try:
    plt.get_cmap(cmap)
except (ValueError, KeyError):
    cmap = 'magma'

mesh = ax_spec.pcolormesh(times, freqs, power, cmap=cmap, shading='auto',
                          vmin=np.percentile(power, 5),
                          vmax=np.percentile(power, 99.5))
fig.colorbar(mesh, ax=ax_spec, fraction=0.03, pad=0.012, label='Power (dB)')
ax_spec.set_xlabel('Time (s)')
ax_spec.set_ylabel('Frequency (Hz)')
ax_spec.set_title(f'c   Spectrogram — {focus}', fontsize=10, loc='left',
                  fontweight='bold')
ax_spec.grid(False)

fig.suptitle(f'Sampling rate {fs:.0f} Hz  •  {len(x):,} samples per channel  '
             f'•  resolution {fs / SEGMENT:.1f} Hz',
             fontsize=9, y=1.03, color='#555555')
