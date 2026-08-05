"""
Raincloud Group Comparison
Half-violin, box and jittered points per group, with pairwise permutation
tests and effect sizes. Shows the distribution, the summary and every raw
observation at once — a box plot alone hides bimodality and small n.
requires_data: true
data_columns: group, value
sample_data: group_measurements.csv
tags: statistics, distribution, raincloud, comparison, biostatistics
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(group='group', value='value', subject='subject')
SAMPLE = 'group_measurements.csv'
VALUE_LABEL = 'Biomarker concentration (ng/mL)'
GROUP_ORDER = None         # None = order of appearance
COMPARE_TO_FIRST = True    # test each group against the first, not all pairs
N_PERM = 20000


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


df = _load(SAMPLE, [COLS['group'], COLS['value']])
groups = GROUP_ORDER or list(pd.unique(df[COLS['group']]))
samples = [df[df[COLS['group']] == g][COLS['value']].to_numpy(float)
           for g in groups]


def permutation_p(a, b, n_perm=N_PERM, seed=0):
    """Two-sided permutation test on the difference in means."""
    rng = np.random.default_rng(seed)
    observed = abs(a.mean() - b.mean())
    pool = np.concatenate([a, b])
    order = np.argsort(rng.random((n_perm, pool.size)), axis=1)
    shuffled = pool[order]
    null = np.abs(shuffled[:, :a.size].mean(axis=1)
                  - shuffled[:, a.size:].mean(axis=1))
    return (np.sum(null >= observed) + 1) / (n_perm + 1)


def hedges_g(a, b):
    """Standardised mean difference with the small-sample correction."""
    n1, n2 = a.size, b.size
    pooled = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1))
                     / (n1 + n2 - 2))
    if pooled == 0:
        return 0.0
    d = (a.mean() - b.mean()) / pooled
    return d * (1 - 3 / (4 * (n1 + n2) - 9))


def kde(values, grid, bandwidth=None):
    """Gaussian KDE with Silverman's bandwidth — no scipy."""
    if bandwidth is None:
        iqr = np.subtract(*np.percentile(values, [75, 25]))
        spread = min(values.std(ddof=1), iqr / 1.349) or values.std(ddof=1) or 1.0
        bandwidth = 0.9 * spread * values.size ** (-0.2)
    z = (grid[:, None] - values[None, :]) / bandwidth
    return np.exp(-0.5 * z ** 2).sum(axis=1) / (values.size * bandwidth
                                                * np.sqrt(2 * np.pi))


W = _opt('_fig_width', 9.5)
H = _opt('_fig_height', 6.5)
fig, ax = plt.subplots(figsize=(W, H), layout='constrained')

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#949494']
rng = np.random.default_rng(5)
lo = min(v.min() for v in samples)
hi = max(v.max() for v in samples)
pad = (hi - lo) * 0.12

for i, (group, values) in enumerate(zip(groups, samples)):
    color = PALETTE[i % len(PALETTE)]

    # Cloud: half violin above the row.
    grid = np.linspace(values.min() - pad, values.max() + pad, 200)
    density = kde(values, grid)
    density = density / density.max() * 0.36
    ax.fill_betweenx(grid, i, i + density, color=color, alpha=0.35,
                     linewidth=0, zorder=2)
    ax.plot(i + density, grid, color=color, linewidth=1.1, zorder=3)

    # Rain: jittered raw observations below the row.
    jitter = rng.uniform(-0.20, -0.04, values.size)
    ax.scatter(i + jitter, values, s=15, color=color, alpha=0.65,
               linewidths=0, zorder=4)

    # Box: median, IQR and 1.5x IQR whiskers, drawn between the two.
    q1, median, q3 = np.percentile(values, [25, 50, 75])
    iqr = q3 - q1
    whisker_lo = values[values >= q1 - 1.5 * iqr].min()
    whisker_hi = values[values <= q3 + 1.5 * iqr].max()
    ax.plot([i - 0.015, i - 0.015], [whisker_lo, whisker_hi], color='#333333',
            linewidth=1.0, zorder=5)
    ax.add_patch(plt.Rectangle((i - 0.05, q1), 0.07, iqr, facecolor='white',
                               edgecolor='#333333', linewidth=1.1, zorder=6))
    ax.plot([i - 0.05, i + 0.02], [median, median], color='#333333',
            linewidth=1.8, zorder=7)
    # Mean as a diamond — medians and means diverging is worth seeing.
    ax.scatter([i - 0.015], [values.mean()], marker='D', s=22, color=color,
               edgecolors='#333333', linewidths=0.8, zorder=8)

    ax.text(i, lo - pad * 1.6, f'n = {values.size}', ha='center', va='top',
            fontsize=7.5, color='#666666')

# ── Pairwise tests ───────────────────────────────────────────────────────────
pairs = ([(0, j) for j in range(1, len(groups))] if COMPARE_TO_FIRST
         else [(i, j) for i in range(len(groups)) for j in range(i + 1, len(groups))])
span = hi - lo
level = hi + span * 0.08
for k, (i, j) in enumerate(pairs):
    p = permutation_p(samples[i], samples[j], seed=k)
    g = hedges_g(samples[j], samples[i])
    star = ('***' if p < 0.001 else '**' if p < 0.01
            else '*' if p < 0.05 else 'n.s.')
    ax.plot([i, i, j, j],
            [level, level + span * 0.02, level + span * 0.02, level],
            color='#444444', linewidth=0.9, zorder=9)
    text = star if p >= 0.05 else f'{star}  g = {g:.2f}'
    ax.text((i + j) / 2, level + span * 0.028, text, ha='center', va='bottom',
            fontsize=7.5, color='#333333')
    level += span * 0.10

ax.set_xticks(range(len(groups)))
ax.set_xticklabels(groups, fontsize=9.5)
ax.set_xlim(-0.55, len(groups) - 0.25)
ax.set_ylim(lo - span * 0.22, level + span * 0.02)
ax.set_ylabel(VALUE_LABEL)
ax.set_title('Group comparison', fontsize=10.5, loc='left', fontweight='bold')

reference = groups[0] if COMPARE_TO_FIRST else 'each pair'
ax.text(0.0, -0.115,
        f'Box: median and IQR, whiskers 1.5x IQR, diamond: mean. '
        f'Brackets: two-sided permutation test vs {reference} '
        f'(Hedges\' g for significant pairs).',
        transform=ax.transAxes, fontsize=7.5, color='#666666')
