"""
Calibration / Reliability Diagram
Observed frequency against predicted probability with a histogram of the
predictions underneath, plus ECE, MCE and Brier score per model. A model can
rank cases perfectly (high AUC) and still be badly calibrated — this is the
figure that shows it, and the one clinical reviewers ask for.
requires_data: true
data_columns: model, y_true, y_score
sample_data: predictions_binary.csv
tags: evaluation, calibration, uncertainty, clinical
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(model='model', y_true='y_true', y_score='y_score')
SAMPLE = 'predictions_binary.csv'
N_BINS = 12
STRATEGY = 'quantile'      # 'quantile' (equal count) or 'uniform' (equal width)


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


df = _load(SAMPLE, COLS.values())


def calibration(y, s, n_bins, strategy):
    """Bin centres, observed frequency, bin counts, ECE and MCE."""
    if strategy == 'quantile':
        edges = np.unique(np.quantile(s, np.linspace(0, 1, n_bins + 1)))
    else:
        edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(s, edges[1:-1]), 0, len(edges) - 2)
    mean_pred, frac_pos, counts = [], [], []
    for b in range(len(edges) - 1):
        m = idx == b
        if not m.any():
            continue
        mean_pred.append(s[m].mean())
        frac_pos.append(y[m].mean())
        counts.append(int(m.sum()))
    mean_pred = np.array(mean_pred)
    frac_pos = np.array(frac_pos)
    counts = np.array(counts)
    gap = np.abs(frac_pos - mean_pred)
    ece = float(np.sum(counts / counts.sum() * gap))
    return mean_pred, frac_pos, counts, ece, float(gap.max())


# ── Figure ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', 7.5)
H = _opt('_fig_height', 7.5)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 1, height_ratios=[3.0, 1.1], hspace=0.04)
ax = fig.add_subplot(gs[0])
ax_hist = fig.add_subplot(gs[1], sharex=ax)

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#949494']
models = list(pd.unique(df[COLS['model']]))
summary = []

ax.plot([0, 1], [0, 1], color='#666666', linewidth=1.2, linestyle='--',
        zorder=2, label='Perfectly calibrated')

for i, model in enumerate(models):
    sub = df[df[COLS['model']] == model]
    y = sub[COLS['y_true']].to_numpy(float)
    s = sub[COLS['y_score']].to_numpy(float)
    color = PALETTE[i % len(PALETTE)]

    mean_pred, frac_pos, counts, ece, mce = calibration(y, s, N_BINS, STRATEGY)
    brier = float(np.mean((s - y) ** 2))
    summary.append((model, ece, mce, brier))

    # Wilson interval on each bin — small bins deserve visible uncertainty.
    z = 1.96
    denom = 1 + z ** 2 / counts
    centre = (frac_pos + z ** 2 / (2 * counts)) / denom
    half = z * np.sqrt(frac_pos * (1 - frac_pos) / counts
                       + z ** 2 / (4 * counts ** 2)) / denom
    ax.errorbar(mean_pred, frac_pos, yerr=[frac_pos - np.maximum(centre - half, 0),
                                           np.minimum(centre + half, 1) - frac_pos],
                fmt='o-', color=color, linewidth=1.8, markersize=5,
                capsize=2.5, elinewidth=0.9, zorder=4,
                label=f'{model}  (ECE {ece:.3f})')

    ax_hist.hist(s, bins=np.linspace(0, 1, 41), histtype='step',
                 color=color, linewidth=1.5, log=True)

# The gap between a curve and the diagonal is the miscalibration; shade it for
# the worst model so the reader sees the direction of the error.
worst = max(summary, key=lambda r: r[1])
sub = df[df[COLS['model']] == worst[0]]
mp, fp, _, _, _ = calibration(sub[COLS['y_true']].to_numpy(float),
                              sub[COLS['y_score']].to_numpy(float),
                              N_BINS, STRATEGY)
ax.fill_between(mp, fp, mp, color='#D55E00', alpha=0.12, zorder=3)
if len(mp):
    # Point at the widest gap and say which way it leans, so the shading is
    # self-explanatory without a second legend.
    j = int(np.argmax(np.abs(fp - mp)))
    lean = 'under-confident' if fp[j] > mp[j] else 'over-confident'
    ax.annotate(f'{worst[0]} is {lean} here\n(gap {abs(fp[j] - mp[j]):.2f})',
                xy=(mp[j], (fp[j] + mp[j]) / 2),
                xytext=(0.52, 0.16), textcoords='axes fraction',
                fontsize=7.5, color='#444444', ha='left',
                arrowprops=dict(arrowstyle='-|>', color='#D55E00',
                                linewidth=1.0,
                                connectionstyle='arc3,rad=0.25'))

ax.set_ylabel('Observed frequency of positives')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.legend(fontsize=8, loc='upper left', framealpha=0.92)
ax.tick_params(labelbottom=False)
ax.set_title('Calibration on the held-out set', fontsize=10.5, loc='left',
             fontweight='bold')

ax_hist.set_xlabel('Predicted probability')
ax_hist.set_ylabel('Count')
ax_hist.set_xlim(0, 1)

table = '\n'.join(f'{m:<22s} {e:.3f}  {x:.3f}  {b:.4f}'
                  for m, e, x, b in summary)
ax.text(0.98, 0.03,
        f'{"model":<22s} {"ECE":>5s}  {"MCE":>5s}  {"Brier":>6s}\n{table}',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=7,
        family='monospace',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor='#CCCCCC', alpha=0.95))
