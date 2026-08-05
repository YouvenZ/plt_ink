"""
Hyperparameter Sweep Heatmap
Two-factor grid of a validation metric with the best cell called out, plus
marginal best-of curves along each axis. Shows whether an optimum is a genuine
basin or a single lucky run sitting next to a cliff.
requires_data: true
data_columns: lr, batch_size, val_score
sample_data: hparam_sweep.csv
tags: analysis, hyperparameters, sweep, heatmap, deep-learning
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(row='lr', col='batch_size', value='val_score')
SAMPLE = 'hparam_sweep.csv'
ROW_LABEL, COL_LABEL = 'Learning rate', 'Batch size'
VALUE_LABEL = 'Validation accuracy'
ROW_LOG = True             # format the row axis as powers of ten
AGGREGATE = 'max'          # how to collapse repeats in the remaining columns


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

grid = df.pivot_table(index=COLS['row'], columns=COLS['col'],
                      values=COLS['value'], aggfunc=AGGREGATE)
grid = grid.sort_index(ascending=False)          # largest row value on top
values = grid.to_numpy(float)
rows = grid.index.to_numpy()
cols = grid.columns.to_numpy()

# ── Figure ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', 9.0)
H = _opt('_fig_height', 7.0)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 2, width_ratios=[3.2, 1.0], height_ratios=[3.2, 1.0],
                      hspace=0.05, wspace=0.05)
ax = fig.add_subplot(gs[0, 0])
ax_right = fig.add_subplot(gs[0, 1], sharey=ax)
ax_below = fig.add_subplot(gs[1, 0], sharex=ax)

cmap = _opt('_colormap', 'viridis')
try:
    plt.get_cmap(cmap)
except (ValueError, KeyError):
    cmap = 'viridis'

im = ax.imshow(values, cmap=cmap, aspect='auto', origin='upper',
               interpolation='nearest')
fig.colorbar(im, ax=[ax_right], location='right', fraction=0.25, pad=0.06,
             label=VALUE_LABEL)

for i in range(values.shape[0]):
    for j in range(values.shape[1]):
        if np.isnan(values[i, j]):
            continue
        r, g, b = im.cmap(im.norm(values[i, j]))[:3]
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        ax.text(j, i, f'{values[i, j]:.3f}', ha='center', va='center',
                fontsize=7.5, color='white' if luminance < 0.55 else '#111111')

# Ring the winner rather than relying on the reader to scan for the max. The
# value goes in the title, not a floating callout that would cover a cell.
best = np.unravel_index(np.nanargmax(values), values.shape)
ax.add_patch(plt.Rectangle((best[1] - 0.5, best[0] - 0.5), 1, 1, fill=False,
                           edgecolor='#D55E00', linewidth=2.6, zorder=5))


def fmt_row(v):
    """Log labels that survive non-decade values: 3e-4 must not read as 1e-3."""
    if not ROW_LOG:
        return f'{v:g}'
    exponent = int(np.floor(np.log10(v)))
    mantissa = v / 10.0 ** exponent
    if abs(mantissa - 1.0) < 1e-6:
        return f'$10^{{{exponent}}}$'
    return f'${mantissa:g}\\times10^{{{exponent}}}$'


ax.set_xticks(range(len(cols)))
ax.set_xticklabels([f'{c:g}' for c in cols])
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([fmt_row(r) for r in rows])
ax.set_ylabel(ROW_LABEL)
ax.tick_params(labelbottom=False)
ax.grid(False)
ax.set_title(f'Two-factor sweep — best {values[best]:.3f} at '
             f'{ROW_LABEL.lower()} {fmt_row(rows[best[0]])}, '
             f'{COL_LABEL.lower()} {cols[best[1]]:g}',
             fontsize=10.5, loc='left', fontweight='bold')

# ── Marginals: the best achievable score for each setting of one factor ──────
row_best = np.nanmax(values, axis=1)
col_best = np.nanmax(values, axis=0)

ax_right.plot(row_best, np.arange(len(rows)), 'o-', color='#0173B2',
              linewidth=1.6, markersize=4)
ax_right.set_xlabel(f'best over\n{COL_LABEL.lower()}', fontsize=8)
ax_right.tick_params(labelleft=False, labelsize=7.5)
ax_right.set_ylim(len(rows) - 0.5, -0.5)

ax_below.plot(np.arange(len(cols)), col_best, 'o-', color='#0173B2',
              linewidth=1.6, markersize=4)
ax_below.set_ylabel(f'best over\n{ROW_LABEL.lower()}', fontsize=8)
ax_below.set_xlabel(COL_LABEL)
ax_below.tick_params(labelsize=7.5)

for marginal_ax, best_index in ((ax_right, best[0]), (ax_below, best[1])):
    line = (marginal_ax.axhline if marginal_ax is ax_right
            else marginal_ax.axvline)
    line(best_index, color='#D55E00', linewidth=1.0, linestyle=':')

n_runs = len(df)
# Only genuine factors, not other metric columns that happen to be present.
extra = [c for c in df.columns
         if c not in COLS.values() and 1 < df[c].nunique() <= 12]
note = f'{n_runs} runs'
if extra:
    note += f'; collapsed over {", ".join(extra)} with {AGGREGATE}'
fig.suptitle(note, fontsize=8.5, y=-0.01, color='#555555')
