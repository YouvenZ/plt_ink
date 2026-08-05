"""
ROC & Precision-Recall Curves
Multi-model ROC and PR side by side with bootstrap confidence bands, AUC/AP in
the legend and the Youden-optimal operating point marked. PR is the panel that
matters on imbalanced data — the chance line sits at the prevalence, not 0.5.
requires_data: true
data_columns: model, y_true, y_score
sample_data: predictions_binary.csv
tags: evaluation, classification, roc, imbalanced, deep-learning
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(model='model', y_true='y_true', y_score='y_score')
SAMPLE = 'predictions_binary.csv'
N_BOOTSTRAP = 300          # set to 0 to skip the confidence bands
CI = 95                    # percentile interval width


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

# numpy 2 renamed trapz -> trapezoid; support both.
_area = getattr(np, 'trapezoid', None) or np.trapz


# ── Curve maths (no sklearn / scipy needed) ──────────────────────────────────
def roc(y, s):
    """False-positive rate, true-positive rate, AUC."""
    order = np.argsort(-s, kind='mergesort')
    y = y[order]
    tps = np.cumsum(y)
    fps = np.cumsum(1 - y)
    if tps[-1] == 0 or fps[-1] == 0:          # only one class present
        return np.array([0, 1]), np.array([0, 1]), 0.5
    fpr = np.concatenate([[0.0], fps / fps[-1]])
    tpr = np.concatenate([[0.0], tps / tps[-1]])
    return fpr, tpr, float(_area(tpr, fpr))


def pr(y, s):
    """Recall, precision, average precision."""
    order = np.argsort(-s, kind='mergesort')
    y = y[order]
    tps = np.cumsum(y)
    if tps[-1] == 0:
        return np.array([0, 1]), np.array([1, 1]), 0.0
    precision = tps / np.arange(1, y.size + 1)
    recall = tps / tps[-1]
    # AP is the step-wise sum, not the trapezoid — trapezoid over-states it.
    ap = float(np.sum(np.diff(np.concatenate([[0.0], recall])) * precision))
    return recall, precision, ap


def bootstrap_band(y, s, grid, kind, n_boot, rng):
    """Percentile band of the curve at fixed grid positions."""
    if n_boot <= 0:
        return None
    curves = np.empty((n_boot, grid.size))
    n = y.size
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        yb, sb = y[idx], s[idx]
        if yb.sum() in (0, yb.size):
            curves[b] = np.nan
            continue
        # Both curves come back with x already increasing, which np.interp
        # requires — reversing them here silently produces a full-panel smear.
        x, v, _ = roc(yb, sb) if kind == 'roc' else pr(yb, sb)
        curves[b] = np.interp(grid, x, v)
    lo = np.nanpercentile(curves, (100 - CI) / 2, axis=0)
    hi = np.nanpercentile(curves, 100 - (100 - CI) / 2, axis=0)
    return lo, hi


# ── Figure ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', 11.0)
H = _opt('_fig_height', 5.0)
fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(W, H), layout='constrained')

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#949494']
rng = np.random.default_rng(0)
grid = np.linspace(0, 1, 101)
models = list(pd.unique(df[COLS['model']]))
prevalence = float(df.groupby(COLS['model'])[COLS['y_true']].mean().iloc[0])

for i, model in enumerate(models):
    sub = df[df[COLS['model']] == model]
    y = sub[COLS['y_true']].to_numpy(float)
    s = sub[COLS['y_score']].to_numpy(float)
    color = PALETTE[i % len(PALETTE)]

    fpr, tpr, auc = roc(y, s)
    ax_roc.plot(fpr, tpr, color=color, linewidth=2.0, zorder=4,
                label=f'{model}  (AUC {auc:.3f})')
    band = bootstrap_band(y, s, grid, 'roc', N_BOOTSTRAP, rng)
    if band:
        ax_roc.fill_between(grid, band[0], band[1], color=color, alpha=0.15,
                            linewidth=0)

    # Youden's J: the threshold maximising sensitivity + specificity - 1.
    j = int(np.argmax(tpr - fpr))
    ax_roc.scatter([fpr[j]], [tpr[j]], s=42, color=color, zorder=6,
                   edgecolors='white', linewidths=1.1)

    rec, prec, ap = pr(y, s)
    ax_pr.plot(rec, prec, color=color, linewidth=2.0, zorder=4,
               label=f'{model}  (AP {ap:.3f})')
    band = bootstrap_band(y, s, grid, 'pr', N_BOOTSTRAP, rng)
    if band:
        ax_pr.fill_between(grid, band[0], band[1], color=color, alpha=0.15,
                           linewidth=0)

ax_roc.plot([0, 1], [0, 1], color='#999999', linewidth=1.0, linestyle='--',
            zorder=1, label='Chance')
ax_pr.axhline(prevalence, color='#999999', linewidth=1.0, linestyle='--',
              zorder=1, label=f'Chance (prevalence {prevalence:.2f})')

ax_roc.set_xlabel('False positive rate  (1 - specificity)')
ax_roc.set_ylabel('True positive rate  (sensitivity)')
ax_roc.set_title('a   Receiver operating characteristic', fontsize=10,
                 loc='left', fontweight='bold')
ax_pr.set_xlabel('Recall')
ax_pr.set_ylabel('Precision')
ax_pr.set_title('b   Precision-recall', fontsize=10, loc='left',
                fontweight='bold')

for ax in (ax_roc, ax_pr):
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect('equal')
    ax.legend(fontsize=8, loc='lower left' if ax is ax_roc else 'upper right',
              framealpha=0.92)

n_pos = int(df[df[COLS['model']] == models[0]][COLS['y_true']].sum())
n_tot = int((df[COLS['model']] == models[0]).sum())
fig.suptitle(f'Discrimination on the held-out set '
             f'(n={n_tot}, {n_pos} positive, {CI}% bootstrap bands)',
             fontsize=10.5, y=1.02)
