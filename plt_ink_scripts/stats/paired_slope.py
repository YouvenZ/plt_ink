"""
Paired Before/After Slope Plot
One line per subject between two timepoints, coloured by direction of change,
with group means, a paired permutation test and Cohen's dz. Group means alone
can hide that half the subjects moved the other way.
requires_data: true
data_columns: subject, group, timepoint, value
sample_data: paired_prepost.csv
tags: statistics, paired, before-after, clinical, trial
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(subject='subject', group='group', timepoint='timepoint',
            value='value')
SAMPLE = 'paired_prepost.csv'
TIMEPOINTS = ('Pre', 'Post')        # order matters: change = second - first
VALUE_LABEL = '6-minute walk distance (m)'
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


df = _load(SAMPLE, [COLS['subject'], COLS['timepoint'], COLS['value']])
has_groups = COLS['group'] in df.columns
groups = list(pd.unique(df[COLS['group']])) if has_groups else [None]

wide = df.pivot_table(index=[COLS['subject']] + ([COLS['group']] if has_groups
                                                 else []),
                      columns=COLS['timepoint'], values=COLS['value'])
wide = wide.reset_index()
first, second = TIMEPOINTS


def paired_permutation_p(delta, n_perm=N_PERM, seed=0):
    """Sign-flip test: under the null, each subject's change could go either
    way, so flipping signs generates the exact null for a paired design."""
    rng = np.random.default_rng(seed)
    observed = abs(delta.mean())
    signs = rng.choice([-1.0, 1.0], size=(n_perm, delta.size))
    null = np.abs((signs * delta).mean(axis=1))
    return (np.sum(null >= observed) + 1) / (n_perm + 1)


W = _opt('_fig_width', 4.6 * len(groups) + 1.6)
H = _opt('_fig_height', 6.0)
fig, axes = plt.subplots(1, len(groups), figsize=(W, H), sharey=True,
                         layout='constrained')
axes = np.atleast_1d(axes)

UP, DOWN, FLAT = '#029E73', '#D55E00', '#BBBBBB'
rng = np.random.default_rng(2)

for ax, group in zip(axes, groups):
    block = wide if group is None else wide[wide[COLS['group']] == group]
    a = block[first].to_numpy(float)
    b = block[second].to_numpy(float)
    delta = b - a

    for ai, bi, d in zip(a, b, delta):
        colour = UP if d > 0 else DOWN if d < 0 else FLAT
        ax.plot([0, 1], [ai, bi], color=colour, linewidth=1.0, alpha=0.55,
                zorder=3)
    # Slight jitter so identical values do not stack into one dot.
    ax.scatter(np.zeros(a.size) + rng.uniform(-0.012, 0.012, a.size), a, s=22,
               color='#555555', alpha=0.7, linewidths=0, zorder=4)
    ax.scatter(np.ones(b.size) + rng.uniform(-0.012, 0.012, b.size), b, s=22,
               color='#555555', alpha=0.7, linewidths=0, zorder=4)

    # Group mean with a 95% CI, drawn heavy so it reads over the spaghetti.
    for x, values in ((0, a), (1, b)):
        sem = values.std(ddof=1) / np.sqrt(values.size)
        ax.errorbar(x, values.mean(), yerr=1.96 * sem, fmt='o', color='#1A1A1A',
                    markersize=8, capsize=5, elinewidth=1.6, zorder=6,
                    markeredgecolor='white', markeredgewidth=1.0)
    ax.plot([0, 1], [a.mean(), b.mean()], color='#1A1A1A', linewidth=2.4,
            zorder=5)

    p = paired_permutation_p(delta)
    sd_delta = delta.std(ddof=1)
    dz = delta.mean() / sd_delta if sd_delta > 0 else 0.0
    sem_delta = sd_delta / np.sqrt(delta.size)
    n_up = int(np.sum(delta > 0))
    p_text = 'p < 0.001' if p < 0.001 else f'p = {p:.3f}'

    ax.set_title(group or 'All subjects', fontsize=10, loc='left',
                 fontweight='bold')
    ax.text(0.5, 0.015,
            f'$\\Delta$ = {delta.mean():+.1f} '
            f'(95% CI {delta.mean() - 1.96 * sem_delta:+.1f} to '
            f'{delta.mean() + 1.96 * sem_delta:+.1f})\n'
            f'{p_text},  Cohen\'s $d_z$ = {dz:.2f}\n'
            f'{n_up}/{delta.size} improved',
            transform=ax.transAxes, ha='center', va='bottom', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                      edgecolor='#CCCCCC', alpha=0.95))

    ax.set_xticks([0, 1])
    ax.set_xticklabels(TIMEPOINTS, fontsize=10)
    ax.set_xlim(-0.22, 1.22)

axes[0].set_ylabel(VALUE_LABEL)
handles = [plt.Line2D([], [], color=UP, linewidth=1.6, label='Increased'),
           plt.Line2D([], [], color=DOWN, linewidth=1.6, label='Decreased'),
           plt.Line2D([], [], color='#1A1A1A', linewidth=2.4, marker='o',
                      label='Mean (95% CI)')]
axes[-1].legend(handles=handles, fontsize=8, loc='upper right',
                framealpha=0.93)
fig.suptitle(f'Paired change from {first} to {second}', fontsize=10.5, y=1.03)
