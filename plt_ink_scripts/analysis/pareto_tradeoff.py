"""
Pareto Trade-off (accuracy vs cost)
Scatter of quality against a cost axis with the Pareto front traced, dominated
models greyed out, and marker area encoding model size. The figure to answer
"is the extra accuracy worth the latency?" instead of a table of numbers.
requires_data: true
data_columns: model, accuracy, latency_ms, params_m
sample_data: model_efficiency.csv
tags: analysis, efficiency, pareto, deployment, engineering
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(label='model', quality='accuracy', cost='latency_ms',
            size='params_m', group='family')
SAMPLE = 'model_efficiency.csv'
QUALITY_LABEL = 'Top-1 accuracy'
COST_LABEL = 'Latency (ms, batch 1)'
SIZE_LABEL = 'Parameters (M)'
COST_LOG = True


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


df = _load(SAMPLE, [COLS['label'], COLS['quality'], COLS['cost']])

quality = df[COLS['quality']].to_numpy(float)
cost = df[COLS['cost']].to_numpy(float)
labels = df[COLS['label']].astype(str).to_numpy()
sizes = (df[COLS['size']].to_numpy(float) if COLS['size'] in df.columns
         else np.full(len(df), 20.0))
groups = (df[COLS['group']].astype(str).to_numpy()
          if COLS['group'] in df.columns else np.array([''] * len(df)))


def pareto_mask(cost, quality):
    """True where no other point is cheaper *and* at least as good."""
    keep = np.ones(cost.size, dtype=bool)
    for i in range(cost.size):
        dominated = (cost <= cost[i]) & (quality >= quality[i]) & (
            (cost < cost[i]) | (quality > quality[i]))
        keep[i] = not dominated.any()
    return keep


front = pareto_mask(cost, quality)
order = np.argsort(cost[front])

# ── Figure ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', 9.5)
H = _opt('_fig_height', 6.5)
fig, ax = plt.subplots(figsize=(W, H), layout='constrained')

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#949494']
unique_groups = list(dict.fromkeys(groups))
color_of = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(unique_groups)}

# Marker area proportional to parameter count, area-true so a 4x bigger blob
# means 4x the parameters.
area = 60 + 900 * (sizes / sizes.max())

# Staircase showing what is actually attainable at each cost budget. The front
# is extended to the right so the last step reads as "no better option exists".
fx = np.concatenate([cost[front][order], [cost.max() * 3]])
fy = np.concatenate([quality[front][order], [quality[front][order][-1]]])
ax.step(fx, fy, where='post', color='#D55E00', linewidth=1.8, zorder=3)
ax.fill_between(fx, fy, quality.min() - 0.05, step='post', color='#D55E00',
                alpha=0.06, zorder=1)

ax.scatter(cost[~front], quality[~front], s=area[~front],
           c=[color_of[g] for g in groups[~front]], alpha=0.35,
           edgecolors='white', linewidths=1.0, zorder=4)
ax.scatter(cost[front], quality[front], s=area[front],
           c=[color_of[g] for g in groups[front]], alpha=0.95,
           edgecolors='#333333', linewidths=1.4, zorder=5)

# Label the front in full; label dominated points only where there is room.
for i in np.flatnonzero(front):
    ax.annotate(labels[i], (cost[i], quality[i]),
                xytext=(0, -np.sqrt(area[i]) / 2 - 9),
                textcoords='offset points', ha='center', fontsize=7.5,
                fontweight='bold', color='#222222')
for i in np.flatnonzero(~front):
    ax.annotate(labels[i], (cost[i], quality[i]),
                xytext=(np.sqrt(area[i]) / 2 + 4, 0),
                textcoords='offset points', ha='left', va='center',
                fontsize=6.5, color='#888888')

if COST_LOG:
    ax.set_xscale('log')
    ax.set_xlim(cost.min() * 0.65, cost.max() * 2.2)
ax.set_ylim(quality.min() - 0.02, quality.max() + 0.025)
ax.set_xlabel(COST_LABEL)
ax.set_ylabel(QUALITY_LABEL)
ax.set_title('Accuracy against inference cost', fontsize=10.5, loc='left',
             fontweight='bold')

handles = [plt.Line2D([], [], marker='o', linestyle='', markersize=7,
                      color=color_of[g], label=g) for g in unique_groups if g]
handles.append(plt.Line2D([], [], color='#D55E00', linewidth=1.8,
                          label='Pareto front'))
# A size legend, otherwise the third encoded variable is unreadable.
for ref in (np.percentile(sizes, 15), np.percentile(sizes, 95)):
    handles.append(plt.Line2D([], [], marker='o', linestyle='', color='#BBBBBB',
                              markersize=np.sqrt(60 + 900 * ref / sizes.max()) / 2,
                              label=f'{ref:.0f} M params'))
ax.legend(handles=handles, fontsize=8, loc='lower right', framealpha=0.93,
          labelspacing=1.0, borderpad=0.8)

n_front = int(front.sum())
ax.text(0.01, 0.99, f'{n_front} of {len(df)} models are Pareto-optimal;\n'
                    'greyed points are dominated on both axes',
        transform=ax.transAxes, va='top', ha='left', fontsize=7.5,
        color='#555555', style='italic')
