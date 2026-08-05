"""
Confusion Matrix with Per-Class Metrics
Raw counts and row-normalised rates side by side, plus per-class precision,
recall and F1 as bars. Two panels because counts alone hide the rare classes
and rates alone hide how few samples a rate is based on.
requires_data: true
data_columns: y_true, y_pred
sample_data: predictions_multiclass.csv
tags: evaluation, classification, confusion, medical-imaging
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(y_true='y_true', y_pred='y_pred')
SAMPLE = 'predictions_multiclass.csv'
CLASS_ORDER = None         # e.g. ['Normal', 'Pneumonia', ...]; None = as found


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

y_true = df[COLS['y_true']].astype(str)
y_pred = df[COLS['y_pred']].astype(str)
classes = CLASS_ORDER or sorted(set(y_true) | set(y_pred))
k = len(classes)
index = {c: i for i, c in enumerate(classes)}

cm = np.zeros((k, k), dtype=int)
for t, p in zip(y_true, y_pred):
    cm[index[t], index[p]] += 1

support = cm.sum(axis=1)
normalised = cm / np.maximum(support, 1)[:, None]
accuracy = np.trace(cm) / cm.sum()

tp = np.diag(cm).astype(float)
precision = tp / np.maximum(cm.sum(axis=0), 1)
recall = tp / np.maximum(support, 1)
f1 = 2 * precision * recall / np.maximum(precision + recall, 1e-12)
# Cohen's kappa: agreement corrected for what chance alone would produce.
expected = (cm.sum(axis=0) * support).sum() / cm.sum() ** 2
kappa = (accuracy - expected) / (1 - expected) if expected < 1 else 0.0

# ── Figure ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', 13.0)
H = _opt('_fig_height', 5.2)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.75])
ax_counts = fig.add_subplot(gs[0, 0])
ax_rates = fig.add_subplot(gs[0, 1])
ax_bars = fig.add_subplot(gs[0, 2])

cmap = _opt('_colormap', 'Blues')
try:
    plt.get_cmap(cmap)
except (ValueError, KeyError):
    cmap = 'Blues'


def draw_matrix(ax, matrix, fmt, title, vmax):
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=vmax, aspect='equal')
    # Pick the label colour from the cell's actual luminance rather than from
    # the value — colormaps run dark-to-light (viridis) or light-to-dark
    # (Blues), so a fixed threshold is unreadable in one of the two.
    for i in range(k):
        for j in range(k):
            value = matrix[i, j]
            if fmt == 'd' and value == 0:
                continue
            r, g, b = im.cmap(im.norm(value))[:3]
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            ax.text(j, i, format(value, fmt), ha='center', va='center',
                    fontsize=8,
                    color='white' if luminance < 0.55 else '#111111')
    ax.set_xticks(range(k))
    ax.set_yticks(range(k))
    ax.set_xticklabels(classes, rotation=40, ha='right', fontsize=8)
    ax.set_yticklabels(classes, fontsize=8)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    ax.set_title(title, fontsize=10, loc='left', fontweight='bold')
    ax.grid(False)
    ax.set_xticks(np.arange(-0.5, k, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, k, 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.2)
    ax.tick_params(which='minor', length=0)
    return im


draw_matrix(ax_counts, cm, 'd', 'a   Counts', float(cm.max()))
im = draw_matrix(ax_rates, normalised, '.2f', 'b   Row-normalised', 1.0)
fig.colorbar(im, ax=ax_rates, fraction=0.046, pad=0.03,
             label='Fraction of true class')

# Row labels carry the support so a 0.83 recall on n=12 is not read as solid.
ax_counts.set_yticklabels([f'{c}  (n={s})' for c, s in zip(classes, support)],
                          fontsize=8)
# Panel b repeats panel a's rows — drop the duplicate labels.
ax_rates.set_yticklabels([])
ax_rates.set_ylabel('')

# ── Per-class metrics ────────────────────────────────────────────────────────
y = np.arange(k)
height = 0.26
for offset, values, label, color in ((height, precision, 'Precision', '#0173B2'),
                                     (0.0, recall, 'Recall', '#DE8F05'),
                                     (-height, f1, 'F1', '#029E73')):
    ax_bars.barh(y + offset, values, height=height, color=color, label=label)
for i in range(k):
    ax_bars.text(f1[i] + 0.02, i - height, f'{f1[i]:.2f}', va='center',
                 fontsize=7, color='#333333')

ax_bars.set_yticks(y)
ax_bars.set_yticklabels(classes, fontsize=8)
ax_bars.invert_yaxis()
ax_bars.set_xlim(0, 1.12)
ax_bars.set_xlabel('Score')
ax_bars.set_title('c   Per-class performance', fontsize=10, loc='left',
                  fontweight='bold')
ax_bars.legend(fontsize=7.5, ncol=3, loc='upper center',
               bbox_to_anchor=(0.5, -0.09), frameon=False)
ax_bars.axvline(1.0, color='#CCCCCC', linewidth=0.8)

macro_f1 = f1.mean()
fig.suptitle(f'Confusion matrix — accuracy {accuracy:.3f}   '
             f'macro-F1 {macro_f1:.3f}   Cohen\'s $\\kappa$ {kappa:.3f}   '
             f'(n={cm.sum()})', fontsize=10.5, y=1.04)
