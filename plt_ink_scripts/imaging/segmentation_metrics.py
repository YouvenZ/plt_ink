"""
Segmentation Metrics by Structure
Per-structure Dice and HD95 as box plots across cases and models, with paired
per-case lines, mean markers and a paired test against the baseline model.
The quantitative half of a segmentation paper.
requires_data: true
data_columns: case_id, model, structure, dice, hd95
sample_data: segmentation_metrics.csv
tags: imaging, segmentation, metrics, medical-imaging, evaluation
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(case='case_id', model='model', structure='structure',
            primary='dice', secondary='hd95')
SAMPLE = 'segmentation_metrics.csv'
PRIMARY_LABEL = 'Dice similarity coefficient'
SECONDARY_LABEL = 'HD95 (mm)'
SECONDARY_LOG = True
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


df = _load(SAMPLE, [COLS['model'], COLS['structure'], COLS['primary']])
models = list(pd.unique(df[COLS['model']]))
structures = list(pd.unique(df[COLS['structure']]))


def paired_permutation_p(delta, n_perm=N_PERM, seed=0):
    """Sign-flip test on the per-case differences."""
    rng = np.random.default_rng(seed)
    delta = delta[np.isfinite(delta)]
    if delta.size < 2:
        return np.nan
    observed = abs(delta.mean())
    signs = rng.choice([-1.0, 1.0], size=(n_perm, delta.size))
    return (np.sum(np.abs((signs * delta).mean(axis=1)) >= observed) + 1) / (n_perm + 1)


W = _opt('_fig_width', 13.0)
H = _opt('_fig_height', 6.0)
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, H), layout='constrained')

PALETTE = ['#949494', '#0173B2', '#029E73', '#DE8F05', '#D55E00']
width = 0.8 / len(models)
rng = np.random.default_rng(4)


def panel(target_ax, value_col, ylabel, log, annotate):
    for si, structure in enumerate(structures):
        block = df[df[COLS['structure']] == structure]
        positions, series = [], []
        for mi, model in enumerate(models):
            values = block[block[COLS['model']] == model][value_col].to_numpy(float)
            position = si + (mi - (len(models) - 1) / 2) * width
            positions.append(position)
            series.append(values)

            bp = target_ax.boxplot(
                [values], positions=[position], widths=width * 0.78,
                patch_artist=True, showfliers=False, whis=1.5,
                medianprops=dict(color='#111111', linewidth=1.3),
                boxprops=dict(facecolor=PALETTE[mi % len(PALETTE)], alpha=0.65,
                              edgecolor='#333333', linewidth=0.9),
                whiskerprops=dict(color='#333333', linewidth=0.9),
                capprops=dict(color='#333333', linewidth=0.9))
            del bp
            target_ax.scatter(position + rng.uniform(-width * 0.22,
                                                     width * 0.22, values.size),
                              values, s=5, color='#222222', alpha=0.3,
                              linewidths=0, zorder=5)
            target_ax.scatter([position], [values.mean()], marker='D', s=20,
                              color='white', edgecolors='#111111',
                              linewidths=1.0, zorder=6)

        if annotate and len(models) > 1 and COLS['case'] in block.columns:
            # Paired across cases: the same scan segmented by each model.
            wide = block.pivot_table(index=COLS['case'], columns=COLS['model'],
                                     values=value_col)
            if models[0] in wide.columns and models[-1] in wide.columns:
                delta = (wide[models[-1]] - wide[models[0]]).to_numpy(float)
                p = paired_permutation_p(delta, seed=si)
                star = ('***' if p < 0.001 else '**' if p < 0.01
                        else '*' if p < 0.05 else 'n.s.')
                top = max(np.percentile(s, 97) for s in series)
                target_ax.plot([positions[0], positions[0], positions[-1],
                                positions[-1]],
                               [top * 1.02, top * 1.05, top * 1.05, top * 1.02],
                               color='#444444', linewidth=0.9, zorder=7)
                target_ax.text((positions[0] + positions[-1]) / 2, top * 1.055,
                               star, ha='center', va='bottom', fontsize=7.5)

    target_ax.set_xticks(range(len(structures)))
    target_ax.set_xticklabels(structures, fontsize=9, rotation=15, ha='right')
    target_ax.set_ylabel(ylabel)
    if log:
        target_ax.set_yscale('log')


panel(ax, COLS['primary'], PRIMARY_LABEL, False, annotate=True)
ax.set_title('a   Overlap', fontsize=10, loc='left', fontweight='bold')

if COLS['secondary'] in df.columns:
    panel(ax2, COLS['secondary'], SECONDARY_LABEL, SECONDARY_LOG,
          annotate=False)
    ax2.set_title('b   Boundary distance (lower is better)', fontsize=10,
                  loc='left', fontweight='bold')
else:
    ax2.set_visible(False)

handles = [plt.Rectangle((0, 0), 1, 1, facecolor=PALETTE[i % len(PALETTE)],
                         alpha=0.65, edgecolor='#333333', label=m)
           for i, m in enumerate(models)]
handles.append(plt.Line2D([], [], marker='D', linestyle='', color='white',
                          markeredgecolor='#111111', label='mean'))
ax.legend(handles=handles, fontsize=8, loc='lower left', ncol=2,
          framealpha=0.93)

n_cases = df[COLS['case']].nunique() if COLS['case'] in df.columns else 0
fig.suptitle(f'Segmentation performance across {n_cases} cases — '
             f'boxes are median and IQR, whiskers 1.5x IQR; brackets are '
             f'paired permutation tests ({models[0]} vs {models[-1]})',
             fontsize=9.5, y=1.04)
