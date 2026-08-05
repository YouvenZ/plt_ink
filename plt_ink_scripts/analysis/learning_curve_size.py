"""
Learning Curve vs Training-Set Size
Score against the number of training examples on a log axis, with a 95% CI
band over seeds and a fitted power law extrapolating how much more data each
method would need. Answers "should we label more data or change the model?".
requires_data: true
data_columns: model, train_size, seed, score
sample_data: learning_curve.csv
tags: analysis, sample-efficiency, scaling, deep-learning
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(model='model', size='train_size', seed='seed', score='score')
SAMPLE = 'learning_curve.csv'
METRIC_NAME = 'Test accuracy'
TARGET = 0.90              # horizontal goal line; None to hide
EXTRAPOLATE = 4.0          # extend the fit this many times past the largest n


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


def fit_power_law(n, y):
    """Least-squares fit of y = c - a * n^(-b) by scanning the exponent.

    Given b the model is linear in (c, a), so a 1-D scan with an exact inner
    solve is both faster and more robust than a general optimiser — and needs
    no scipy.
    """
    best = None
    for b in np.linspace(0.05, 1.5, 300):
        basis = np.column_stack([np.ones_like(n), -n ** (-b)])
        coef, *_ = np.linalg.lstsq(basis, y, rcond=None)
        residual = float(np.sum((basis @ coef - y) ** 2))
        if best is None or residual < best[0]:
            best = (residual, float(coef[0]), float(coef[1]), float(b))
    _, c, a, b = best
    return c, a, b


W = _opt('_fig_width', 9.0)
H = _opt('_fig_height', 6.0)
fig, ax = plt.subplots(figsize=(W, H), layout='constrained')

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#949494']
models = list(pd.unique(df[COLS['model']]))
notes = []

for i, model in enumerate(models):
    sub = df[df[COLS['model']] == model]
    stat = sub.groupby(COLS['size'])[COLS['score']].agg(['mean', 'std', 'count'])
    n = stat.index.to_numpy(float)
    mean = stat['mean'].to_numpy()
    sem = (stat['std'].fillna(0).to_numpy()
           / np.sqrt(np.maximum(stat['count'].to_numpy(), 1)))
    color = PALETTE[i % len(PALETTE)]

    ax.fill_between(n, mean - 1.96 * sem, mean + 1.96 * sem, color=color,
                    alpha=0.18, linewidth=0)
    ax.plot(n, mean, 'o-', color=color, linewidth=1.9, markersize=5,
            zorder=4, label=model)

    ceiling, amplitude, exponent = fit_power_law(n, mean)
    grid = np.geomspace(n.min(), n.max() * EXTRAPOLATE, 200)
    ax.plot(grid, ceiling - amplitude * grid ** (-exponent), color=color,
            linewidth=1.1, linestyle=':', alpha=0.85, zorder=3)

    # How much data to reach the target, read off the fitted law.
    if TARGET is not None and ceiling > TARGET:
        needed = (amplitude / (ceiling - TARGET)) ** (1.0 / exponent)
        notes.append(f'{model}: ~{needed:,.0f} examples for {TARGET:.0%}'
                     if needed < n.max() * 50
                     else f'{model}: >{n.max() * 50:,.0f} examples for {TARGET:.0%}')
    else:
        notes.append(f'{model}: plateaus at {ceiling:.3f}, never reaches '
                     f'{TARGET:.0%}' if TARGET else f'{model}: ceiling {ceiling:.3f}')

ax.set_xscale('log')

if TARGET is not None:
    # Placed in axes coordinates and only after the scale is set — reading
    # get_xlim() on a linear axis and then switching to log puts the label
    # far outside the data, which bbox_inches='tight' then expands to fit.
    ax.axhline(TARGET, color='#444444', linewidth=1.0, linestyle='--',
               zorder=2)
    ax.annotate(f'target {TARGET:.0%}', xy=(0.005, TARGET),
                xycoords=ax.get_yaxis_transform(), fontsize=7.5,
                va='bottom', ha='left', color='#444444')
ax.set_xlabel('Training examples (log scale)')
ax.set_ylabel(METRIC_NAME)
ax.set_title('Sample efficiency', fontsize=10.5, loc='left', fontweight='bold')
ax.legend(fontsize=8.5, loc='lower right', framealpha=0.93)

# Explanatory text belongs under the axes, not floating over the data where it
# would collide with the target line and the leftmost points.
n_seeds = df[COLS['seed']].nunique()
caption = (f'Bands are 95% CI over {n_seeds} seeds. Dotted lines are a fitted '
           'power law $s = c - a\\,n^{-b}$, extrapolated past the largest run. '
           + '  •  '.join(notes))
fig.text(0.0, -0.02, caption, ha='left', va='top', fontsize=7.4,
         color='#555555', wrap=True)
