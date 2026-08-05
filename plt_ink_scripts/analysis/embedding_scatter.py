"""
Embedding Scatter (t-SNE / UMAP)
Two-dimensional projection coloured by class, with per-class density contours,
labelled centroids and misclassified points marked. Built for single-cell
atlases and learned representations alike.
requires_data: true
data_columns: x, y, label
sample_data: embedding_2d.csv
tags: analysis, embedding, tsne, umap, single-cell, deep-learning
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(x='x', y='y', label='label', pred='pred')
SAMPLE = 'embedding_2d.csv'
METHOD = 't-SNE'
SHOW_CONTOURS = True
SHOW_ERRORS = True         # ring points whose `pred` disagrees with `label`
POINT_SIZE = 7


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


df = _load(SAMPLE, [COLS['x'], COLS['y'], COLS['label']])

x = df[COLS['x']].to_numpy(float)
y = df[COLS['y']].to_numpy(float)
labels = df[COLS['label']].astype(str).to_numpy()
classes = list(pd.unique(labels))

W = _opt('_fig_width', 9.0)
H = _opt('_fig_height', 7.5)
fig, ax = plt.subplots(figsize=(W, H), layout='constrained')

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#CA9161',
           '#FBAFE4', '#949494', '#ECE133', '#56B4E9']
color_of = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(classes)}


def density(px, py, gridsize=64, bandwidth=None):
    """Gaussian kernel density on a grid — no scipy, and fast enough here."""
    if bandwidth is None:
        # Silverman's rule, averaged over the two axes.
        bandwidth = 1.06 * np.mean([px.std(), py.std()]) * px.size ** (-0.2)
    gx = np.linspace(px.min() - 2 * bandwidth, px.max() + 2 * bandwidth, gridsize)
    gy = np.linspace(py.min() - 2 * bandwidth, py.max() + 2 * bandwidth, gridsize)
    mx, my = np.meshgrid(gx, gy)
    z = np.zeros_like(mx)
    # Chunked so a large class does not allocate an n x gridsize^2 array.
    for start in range(0, px.size, 256):
        cx = px[start:start + 256][:, None, None]
        cy = py[start:start + 256][:, None, None]
        z += np.exp(-((mx - cx) ** 2 + (my - cy) ** 2) / (2 * bandwidth ** 2)).sum(0)
    return gx, gy, z / (z.max() or 1.0)


for cls in classes:
    mask = labels == cls
    color = color_of[cls]
    ax.scatter(x[mask], y[mask], s=POINT_SIZE, color=color, alpha=0.55,
               linewidths=0, zorder=3)
    if SHOW_CONTOURS and mask.sum() > 12:
        gx, gy, z = density(x[mask], y[mask])
        ax.contour(gx, gy, z, levels=[0.28, 0.6], colors=[color],
                   linewidths=[0.8, 1.2], alpha=0.75, zorder=4)

# Centroid labels sit on the cluster, in the cluster's colour, on a white pill
# — legible over dense points without needing a legend lookup.
for cls in classes:
    mask = labels == cls
    cx, cy = np.median(x[mask]), np.median(y[mask])
    ax.text(cx, cy, f'{cls}\nn={mask.sum()}', ha='center', va='center',
            fontsize=8, fontweight='bold', color=color_of[cls], zorder=7,
            bbox=dict(boxstyle='round,pad=0.28', facecolor='white',
                      edgecolor=color_of[cls], linewidth=0.9, alpha=0.88))

n_wrong = 0
if SHOW_ERRORS and COLS['pred'] in df.columns:
    wrong = labels != df[COLS['pred']].astype(str).to_numpy()
    n_wrong = int(wrong.sum())
    ax.scatter(x[wrong], y[wrong], s=POINT_SIZE * 4.5, facecolors='none',
               edgecolors='#333333', linewidths=0.6, alpha=0.8, zorder=6)

ax.set_xlabel(f'{METHOD} 1')
ax.set_ylabel(f'{METHOD} 2')
ax.set_aspect('equal')
# Projection axes carry no units — ticks invite over-reading of the distances.
ax.set_xticks([])
ax.set_yticks([])
ax.grid(False)
ax.set_title(f'{METHOD} projection — {len(classes)} classes, {len(df):,} points',
             fontsize=10.5, loc='left', fontweight='bold')

caption = 'Contours: 28% and 60% of peak class density'
if n_wrong:
    caption += (f'.  Ringed points ({n_wrong}, {n_wrong / len(df):.1%}) are '
                'misclassified')
ax.text(0.0, -0.04, caption, transform=ax.transAxes, fontsize=7.5,
        color='#666666', va='top')
