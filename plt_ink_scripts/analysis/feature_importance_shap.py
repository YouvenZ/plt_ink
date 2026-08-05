"""
Feature Importance (SHAP-style beeswarm)
Per-sample attributions as a beeswarm coloured by feature value, beside the
mean absolute importance as a ranked bar. The beeswarm is what distinguishes
"this feature matters" from "this feature matters, and high values push risk up".
requires_data: true
data_columns: feature, sample_id, shap_value, feature_value
sample_data: feature_importance.csv
tags: analysis, interpretability, shap, clinical, machine-learning
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(feature='feature', sample='sample_id', shap='shap_value',
            value='feature_value')
SAMPLE = 'feature_importance.csv'
TOP_N = 12                 # features to show, ranked by mean |attribution|
OUTCOME = 'predicted risk'


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

importance = (df.groupby(COLS['feature'])[COLS['shap']]
              .apply(lambda s: s.abs().mean())
              .sort_values(ascending=False))
features = list(importance.index[:TOP_N])[::-1]     # most important on top

W = _opt('_fig_width', 11.0)
H = _opt('_fig_height', 6.5)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(1, 2, width_ratios=[2.5, 1.0], wspace=0.04)
ax = fig.add_subplot(gs[0, 0])
ax_bar = fig.add_subplot(gs[0, 1], sharey=ax)

cmap = plt.get_cmap('coolwarm')
rng = np.random.default_rng(3)


def beeswarm_offsets(values, width=0.38, bins=48):
    """Spread overlapping points vertically instead of hiding them.

    Points are binned along x and each bin is dealt out symmetrically about
    the row centre, which is what makes density visible in a beeswarm.
    """
    offsets = np.zeros(values.size)
    if values.size == 0:
        return offsets
    edges = np.linspace(values.min(), values.max() + 1e-12, bins + 1)
    which = np.clip(np.digitize(values, edges[1:-1]), 0, bins - 1)
    for b in range(bins):
        idx = np.flatnonzero(which == b)
        if idx.size < 2:
            continue
        # Densest bins get the full width; sparse bins stay near the centre.
        spread = min(1.0, idx.size / 40.0) * width
        ladder = np.linspace(-spread, spread, idx.size)
        offsets[idx] = rng.permutation(ladder)
    return offsets


for row, feature in enumerate(features):
    sub = df[df[COLS['feature']] == feature]
    shap = sub[COLS['shap']].to_numpy(float)
    value = sub[COLS['value']].to_numpy(float)
    # Rank-normalise the colour so a single outlier cannot flatten the scale.
    ranks = value.argsort().argsort() / max(value.size - 1, 1)
    ax.scatter(shap, row + beeswarm_offsets(shap), c=ranks, cmap=cmap,
               s=9, alpha=0.75, linewidths=0, vmin=0, vmax=1, zorder=3)

ax.axvline(0, color='#666666', linewidth=1.0, zorder=2)
ax.set_yticks(range(len(features)))
ax.set_yticklabels(features, fontsize=9)
ax.set_ylim(-0.7, len(features) - 0.3)
ax.set_xlabel(f'SHAP value  (impact on {OUTCOME})')
ax.set_title('a   Per-sample attributions', fontsize=10, loc='left',
             fontweight='bold')

sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.015)
cbar.set_ticks([0.02, 0.98])
cbar.set_ticklabels(['Low', 'High'])
cbar.set_label('Feature value (percentile)', fontsize=8.5)
cbar.ax.tick_params(labelsize=8)

# ── Ranked mean |SHAP| with a bootstrap CI ───────────────────────────────────
means, errors = [], []
for feature in features:
    shap = df[df[COLS['feature']] == feature][COLS['shap']].abs().to_numpy(float)
    means.append(shap.mean())
    boot = np.array([np.mean(rng.choice(shap, shap.size)) for _ in range(400)])
    errors.append([means[-1] - np.percentile(boot, 2.5),
                   np.percentile(boot, 97.5) - means[-1]])

errors = np.array(errors).T
ax_bar.barh(range(len(features)), means, xerr=errors, height=0.62,
            color='#0173B2', alpha=0.85, capsize=2.5,
            error_kw=dict(elinewidth=0.9, ecolor='#333333'))
for i, m in enumerate(means):
    ax_bar.text(m + errors[1][i] + max(means) * 0.02, i, f'{m:.3f}',
                va='center', fontsize=7, color='#444444')

ax_bar.tick_params(labelleft=False)
ax_bar.set_xlabel('mean |SHAP|')
ax_bar.set_xlim(0, max(means) * 1.32)
ax_bar.set_title('b   Global importance', fontsize=10, loc='left',
                 fontweight='bold')

n_samples = df[COLS['sample']].nunique()
n_features = df[COLS['feature']].nunique()
fig.suptitle(f'Feature attributions over {n_samples} samples '
             f'(top {len(features)} of {n_features} features)',
             fontsize=10.5, y=1.03)
