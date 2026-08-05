"""
Forest Plot (meta-analysis / subgroup)
Per-study effect estimates with confidence intervals, weight-scaled markers,
subgroup headers, random-effects pooled diamonds and heterogeneity statistics.
The standard figure of a systematic review, and of any subgroup analysis.
requires_data: true
data_columns: study, subgroup, estimate, ci_low, ci_high, weight
sample_data: forest_studies.csv
tags: clinical, meta-analysis, forest, biostatistics, epidemiology
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(study='study', subgroup='subgroup', estimate='estimate',
            low='ci_low', high='ci_high', weight='weight',
            n_treat='n_treatment', n_ctrl='n_control')
SAMPLE = 'forest_studies.csv'
EFFECT_LABEL = 'Hazard ratio (95% CI)'
LOG_SCALE = True           # ratio measures (HR, OR, RR) belong on a log axis
NULL_VALUE = 1.0
FAVOURS = ('favours treatment', 'favours control')


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


df = _load(SAMPLE, [COLS['study'], COLS['estimate'], COLS['low'],
                    COLS['high']])
has_subgroups = COLS['subgroup'] in df.columns


def pool(estimates, low, high):
    """DerSimonian-Laird random-effects pool on the log scale.

    Returns the pooled estimate, its CI, I^2 and Cochran's Q.
    """
    y = np.log(estimates) if LOG_SCALE else np.asarray(estimates, float)
    hi = np.log(high) if LOG_SCALE else np.asarray(high, float)
    lo = np.log(low) if LOG_SCALE else np.asarray(low, float)
    se = (hi - lo) / (2 * 1.96)
    w = 1.0 / se ** 2
    fixed = np.sum(w * y) / np.sum(w)
    q = float(np.sum(w * (y - fixed) ** 2))
    dof = max(len(y) - 1, 1)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (q - dof) / c) if c > 0 else 0.0
    w_re = 1.0 / (se ** 2 + tau2)
    pooled = np.sum(w_re * y) / np.sum(w_re)
    se_pooled = np.sqrt(1.0 / np.sum(w_re))
    i2 = max(0.0, (q - dof) / q * 100) if q > 0 else 0.0
    out = (pooled, pooled - 1.96 * se_pooled, pooled + 1.96 * se_pooled)
    if LOG_SCALE:
        out = tuple(np.exp(v) for v in out)
    return out, i2, q


# ── Row layout: one row per study, plus headers and pooled rows ──────────────
rows = []          # (kind, label, estimate, low, high, weight, extra)
groups = (list(pd.unique(df[COLS['subgroup']])) if has_subgroups else [None])

for group in groups:
    block = df if group is None else df[df[COLS['subgroup']] == group]
    if group is not None:
        rows.append(('header', group, None, None, None, None, ''))
    for _, r in block.iterrows():
        extra = ''
        if COLS['n_treat'] in block.columns and COLS['n_ctrl'] in block.columns:
            extra = f"{int(r[COLS['n_treat']])}/{int(r[COLS['n_ctrl']])}"
        weight = r[COLS['weight']] if COLS['weight'] in block.columns else 1.0
        rows.append(('study', str(r[COLS['study']]), r[COLS['estimate']],
                     r[COLS['low']], r[COLS['high']], weight, extra))
    (est, lo, hi), i2, q = pool(block[COLS['estimate']].to_numpy(float),
                                block[COLS['low']].to_numpy(float),
                                block[COLS['high']].to_numpy(float))
    label = 'Subtotal' if group is not None else 'Overall'
    rows.append(('pooled', label, est, lo, hi, None, f'$I^2$ = {i2:.0f}%'))

if has_subgroups:
    (est, lo, hi), i2, q = pool(df[COLS['estimate']].to_numpy(float),
                                df[COLS['low']].to_numpy(float),
                                df[COLS['high']].to_numpy(float))
    rows.append(('pooled', 'Overall (random effects)', est, lo, hi, None,
                 f'$I^2$ = {i2:.0f}%'))

n_rows = len(rows)
W = _opt('_fig_width', 10.0)
H = max(_opt('_fig_height', 7.0), 0.32 * n_rows + 1.8)
fig, ax = plt.subplots(figsize=(W, H), layout='constrained')

weights = np.array([r[5] for r in rows if r[0] == 'study'], dtype=float)
max_weight = weights.max() if weights.size else 1.0

# Study names live in a column to the LEFT of the plotting area, as in every
# published forest plot — inside the axes they collide with the CI whiskers.
LABEL_X = -0.34

for i, (kind, label, est, lo, hi, weight, extra) in enumerate(rows):
    y = n_rows - 1 - i
    if kind == 'header':
        ax.text(LABEL_X, y, label, transform=ax.get_yaxis_transform(),
                ha='left', va='center', fontsize=9, fontweight='bold',
                color='#222222')
        continue

    if kind == 'study':
        # Marker area proportional to study weight — the visual cue that a
        # tight CI and a big square are the same information.
        size = 30 + 220 * (weight / max_weight)
        ax.plot([lo, hi], [y, y], color='#333333', linewidth=1.2, zorder=3)
        ax.plot([lo, lo], [y - 0.16, y + 0.16], color='#333333', linewidth=1.0)
        ax.plot([hi, hi], [y - 0.16, y + 0.16], color='#333333', linewidth=1.0)
        ax.scatter([est], [y], s=size, marker='s', color='#0173B2', zorder=4,
                   edgecolors='white', linewidths=0.8)
        indent = LABEL_X + (0.02 if has_subgroups else 0.0)
        ax.text(indent, y, label, transform=ax.get_yaxis_transform(),
                ha='left', va='center', fontsize=8.5)
    else:
        # Pooled estimate as a diamond whose width is the CI.
        colour = '#D55E00' if label.startswith('Overall') else '#666666'
        ax.fill([lo, est, hi, est], [y, y + 0.28, y, y - 0.28], color=colour,
                zorder=5)
        ax.text(LABEL_X, y, label, transform=ax.get_yaxis_transform(),
                ha='left', va='center', fontsize=8.5, fontweight='bold',
                color=colour)

    text = f'{est:.2f} ({lo:.2f}-{hi:.2f})'
    ax.text(1.005, y, text, transform=ax.get_yaxis_transform(), ha='left',
            va='center', fontsize=8, family='monospace')
    if extra:
        ax.text(1.20, y, extra, transform=ax.get_yaxis_transform(), ha='left',
                va='center', fontsize=7.5, color='#666666')

ax.axvline(NULL_VALUE, color='#444444', linewidth=1.0, linestyle='--',
           zorder=2)
if LOG_SCALE:
    ax.set_xscale('log')
    ticks = [0.25, 0.5, 1.0, 2.0, 4.0]
    ax.set_xticks([t for t in ticks
                   if df[COLS['low']].min() / 1.5 <= t <= df[COLS['high']].max() * 1.5])
    ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
    # Under one decade of range, matplotlib also labels the minor log ticks,
    # which litters the axis with "4x10^-1" next to the chosen ticks.
    ax.set_xticks([], minor=True)

ax.set_ylim(-0.8, n_rows - 0.2)
ax.set_yticks([])
ax.set_xlabel(EFFECT_LABEL)
ax.grid(False)
for side in ('left', 'right', 'top'):
    ax.spines[side].set_visible(False)

# "Favours" arrows below the axis: the one thing readers get backwards.
for direction, colour, label, align in ((0.55, '#0173B2', FAVOURS[0], 'right'),
                                        (1 / 0.55, '#D55E00', FAVOURS[1], 'left')):
    ax.annotate('', xy=(NULL_VALUE * direction, -0.055),
                xytext=(NULL_VALUE, -0.055),
                xycoords=ax.get_xaxis_transform(),
                arrowprops=dict(arrowstyle='-|>', color=colour, linewidth=1.2))
    ax.text(NULL_VALUE * direction, -0.075, label,
            transform=ax.get_xaxis_transform(), ha=align, va='top',
            fontsize=7.5, color=colour)

ax.set_title(f'Random-effects meta-analysis of {int((df.shape[0]))} studies',
             fontsize=10.5, loc='left', fontweight='bold')
