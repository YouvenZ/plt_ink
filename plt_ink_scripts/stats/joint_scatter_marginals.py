"""
Joint Scatter with Marginals
Scatter with per-group regression lines and confidence bands, marginal
distributions on both axes, and r, R^2, slope and p reported per group. The
workhorse figure for "does X relate to Y, and is it the same in both cohorts?".
requires_data: true
data_columns: x, y, group
sample_data: regression_xy.csv
tags: statistics, regression, correlation, scatter, joint
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(x='x', y='y', group='group')
SAMPLE = 'regression_xy.csv'
X_LABEL = 'Age (years)'
Y_LABEL = 'Biomarker (ng/mL)'
SHOW_BAND = True           # 95% CI of the fitted line
N_PERM = 10000             # permutations for the correlation p-value


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


df = _load(SAMPLE, [COLS['x'], COLS['y']])
has_groups = COLS['group'] in df.columns
groups = list(pd.unique(df[COLS['group']])) if has_groups else [None]


def fit_line(x, y):
    """Slope, intercept, and the standard error of the fitted value at each x."""
    n = x.size
    slope, intercept = np.polyfit(x, y, 1)
    residual = y - (slope * x + intercept)
    s2 = np.sum(residual ** 2) / (n - 2)
    sxx = np.sum((x - x.mean()) ** 2)
    se_slope = np.sqrt(s2 / sxx)
    return slope, intercept, se_slope, s2, sxx


def permutation_p(x, y, n_perm=N_PERM, seed=0):
    """Two-sided test of zero correlation by shuffling one variable."""
    rng = np.random.default_rng(seed)
    observed = abs(np.corrcoef(x, y)[0, 1])
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = abs(np.corrcoef(x, rng.permutation(y))[0, 1])
    return (np.sum(null >= observed) + 1) / (n_perm + 1)


def kde(values, grid):
    iqr = np.subtract(*np.percentile(values, [75, 25]))
    spread = min(values.std(ddof=1), iqr / 1.349) or values.std(ddof=1) or 1.0
    bandwidth = 0.9 * spread * values.size ** (-0.2)
    z = (grid[:, None] - values[None, :]) / bandwidth
    return np.exp(-0.5 * z ** 2).sum(axis=1) / (values.size * bandwidth
                                                * np.sqrt(2 * np.pi))


W = _opt('_fig_width', 8.5)
H = _opt('_fig_height', 8.0)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 2, width_ratios=[4.0, 1.0], height_ratios=[1.0, 4.0],
                      hspace=0.04, wspace=0.04)
ax = fig.add_subplot(gs[1, 0])
ax_top = fig.add_subplot(gs[0, 0], sharex=ax)
ax_right = fig.add_subplot(gs[1, 1], sharey=ax)

PALETTE = ['#0173B2', '#D55E00', '#029E73', '#DE8F05', '#CC78BC']
summary = []

for i, group in enumerate(groups):
    block = df if group is None else df[df[COLS['group']] == group]
    x = block[COLS['x']].to_numpy(float)
    y = block[COLS['y']].to_numpy(float)
    color = PALETTE[i % len(PALETTE)]

    ax.scatter(x, y, s=20, color=color, alpha=0.6, linewidths=0, zorder=3,
               label=group)

    slope, intercept, se_slope, s2, sxx = fit_line(x, y)
    grid = np.linspace(x.min(), x.max(), 120)
    fitted = slope * grid + intercept
    ax.plot(grid, fitted, color=color, linewidth=2.0, zorder=5)
    if SHOW_BAND:
        # CI of the mean response, widest away from the centre of x.
        se_fit = np.sqrt(s2 * (1.0 / x.size + (grid - x.mean()) ** 2 / sxx))
        ax.fill_between(grid, fitted - 1.96 * se_fit, fitted + 1.96 * se_fit,
                        color=color, alpha=0.18, linewidth=0, zorder=4)

    r = float(np.corrcoef(x, y)[0, 1])
    p = permutation_p(x, y, seed=i)
    p_text = 'p < 0.001' if p < 0.001 else f'p = {p:.3f}'
    summary.append(f'{group or "all"}: r = {r:.3f}, R² = {r ** 2:.3f}, '
                   f'slope = {slope:.3f} ± {se_slope:.3f}, {p_text}, n = {x.size}')

    # Marginals: KDE on top, KDE on the right, same colour as the scatter.
    gx = np.linspace(x.min(), x.max(), 200)
    ax_top.fill_between(gx, kde(x, gx), color=color, alpha=0.3, linewidth=0)
    ax_top.plot(gx, kde(x, gx), color=color, linewidth=1.2)
    gy = np.linspace(y.min(), y.max(), 200)
    ax_right.fill_betweenx(gy, kde(y, gy), color=color, alpha=0.3, linewidth=0)
    ax_right.plot(kde(y, gy), gy, color=color, linewidth=1.2)

ax.set_xlabel(X_LABEL)
ax.set_ylabel(Y_LABEL)
if has_groups:
    ax.legend(fontsize=9, loc='upper left', framealpha=0.93, title=COLS['group'],
              title_fontsize=8.5)

for marginal in (ax_top, ax_right):
    marginal.grid(False)
    for side in ('top', 'right', 'left', 'bottom'):
        marginal.spines[side].set_visible(False)
ax_top.set_yticks([])
ax_top.tick_params(labelbottom=False)
ax_right.set_xticks([])
ax_right.tick_params(labelleft=False)

ax.text(0.0, -0.10, '\n'.join(summary), transform=ax.transAxes, fontsize=8,
        va='top', color='#333333', family='monospace')
ax_top.set_title('Association with 95% CI of the fitted line', fontsize=10.5,
                 loc='left', fontweight='bold')
