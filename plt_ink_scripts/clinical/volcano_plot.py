"""
Volcano Plot (differential expression)
Fold change against significance with FDR and effect thresholds, up/down
counts, and the top hits labelled with leader lines that do not overlap.
Works for RNA-seq, proteomics, metabolomics or any two-group contrast.
requires_data: true
data_columns: gene, log2fc, pvalue, padj
sample_data: differential_expression.csv
tags: clinical, omics, volcano, rna-seq, bioinformatics
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(label='gene', fc='log2fc', p='pvalue', padj='padj')
SAMPLE = 'differential_expression.csv'
FDR = 0.05                 # threshold on the adjusted p-value
FC_THRESHOLD = 1.0         # |log2 fold change| required to call a hit
N_LABELS = 12              # how many hits to name
GROUP_NAMES = ('control', 'treated')


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


df = _load(SAMPLE, [COLS['label'], COLS['fc'], COLS['p']])

fc = df[COLS['fc']].to_numpy(float)
p = df[COLS['p']].to_numpy(float)
padj = (df[COLS['padj']].to_numpy(float) if COLS['padj'] in df.columns else p)
labels = df[COLS['label']].astype(str).to_numpy()

# Plot raw p on the y-axis but threshold on the adjusted p — the convention,
# and the reason the significance line is not flat when FDR is used.
y = -np.log10(np.clip(p, 1e-300, None))
significant = padj < FDR
up = significant & (fc >= FC_THRESHOLD)
down = significant & (fc <= -FC_THRESHOLD)
rest = ~(up | down)

# The y position where padj crosses FDR, for the horizontal guide.
crossing = y[significant].min() if significant.any() else np.nan

W = _opt('_fig_width', 8.5)
H = _opt('_fig_height', 7.0)
fig, ax = plt.subplots(figsize=(W, H), layout='constrained')

ax.scatter(fc[rest], y[rest], s=7, color='#BBBBBB', alpha=0.5, linewidths=0,
           zorder=2, label=f'Not significant ({int(rest.sum()):,})')
ax.scatter(fc[down], y[down], s=13, color='#0173B2', alpha=0.8, linewidths=0,
           zorder=3, label=f'Down in {GROUP_NAMES[1]} ({int(down.sum()):,})')
ax.scatter(fc[up], y[up], s=13, color='#D55E00', alpha=0.8, linewidths=0,
           zorder=3, label=f'Up in {GROUP_NAMES[1]} ({int(up.sum()):,})')

for x in (-FC_THRESHOLD, FC_THRESHOLD):
    ax.axvline(x, color='#666666', linewidth=0.9, linestyle='--', zorder=1)
if np.isfinite(crossing):
    ax.axhline(crossing, color='#666666', linewidth=0.9, linestyle='--',
               zorder=1)
    # Centred between the fold-change thresholds: both edges are occupied by
    # the stacked hit labels.
    ax.text(0, crossing, f'FDR {FDR:g}', ha='center', va='bottom',
            fontsize=7.5, color='#666666')

# ── Label the top hits, pushing labels apart so none collide ─────────────────
hits = np.flatnonzero(up | down)
if hits.size:
    score = y[hits] * np.abs(fc[hits])           # rank by both axes, not one
    chosen = hits[np.argsort(-score)[:N_LABELS]]
    left = [i for i in chosen if fc[i] < 0]
    right = [i for i in chosen if fc[i] >= 0]
    for side, indices in (('left', left), ('right', right)):
        indices = sorted(indices, key=lambda i: y[i])
        if not indices:
            continue
        # Stack the labels in a column at the edge, in y order. The column
        # spans only the range the labelled hits occupy, so the leader lines
        # stay short instead of raking across the whole panel.
        low = min(y[i] for i in indices)
        high = max(y[i] for i in indices)
        margin = max((high - low) * 0.15, y.max() * 0.05)
        slots = np.linspace(max(low - margin, 0), min(high + margin, y.max()),
                            len(indices))
        x_text = fc.min() * 1.02 if side == 'left' else fc.max() * 1.02
        for i, slot in zip(indices, slots):
            ax.annotate(labels[i], xy=(fc[i], y[i]), xytext=(x_text, slot),
                        fontsize=7.5,
                        ha='right' if side == 'left' else 'left',
                        va='center', color='#333333',
                        arrowprops=dict(arrowstyle='-', color='#AAAAAA',
                                        linewidth=0.6,
                                        shrinkA=2, shrinkB=2))

ax.set_xlabel(f'$\\log_2$ fold change  ({GROUP_NAMES[1]} vs {GROUP_NAMES[0]})')
ax.set_ylabel('$-\\log_{10}$ p-value')
ax.set_xlim(fc.min() * 1.22, fc.max() * 1.22)
ax.set_ylim(-0.5, y.max() * 1.08)
# Counts go in the subtitle line, not a separate text at the same height as
# the title — those two overlap as soon as the title is long.
ax.set_title(
    'Differential expression\n'
    f'{len(df):,} features tested  •  {int(significant.sum()):,} pass '
    f'FDR < {FDR:g}  •  {int((up | down).sum()):,} also pass '
    f'|log2FC| $\\geq$ {FC_THRESHOLD:g}',
    fontsize=10.5, loc='left', fontweight='bold')
ax.legend(fontsize=8, loc='upper center', ncol=3, framealpha=0.93,
          bbox_to_anchor=(0.5, -0.09))
