"""
Model Comparison with Significance
Mean score per method with 95% CI, every seed shown as a dot, and permutation
tests against the baseline drawn as brackets. Faceted by dataset. Bars without
per-seed points and a test are the single most over-claimed figure in ML.
requires_data: true
data_columns: dataset, model, seed, score
sample_data: benchmark_seeds.csv
tags: evaluation, comparison, statistics, benchmark
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(dataset='dataset', model='model', seed='seed', score='score')
SAMPLE = 'benchmark_seeds.csv'
BASELINE = None            # None = the first method found; else e.g. 'Baseline CNN'
N_PERM = 20000             # permutations per comparison
METRIC_NAME = 'Accuracy'
# Bars zoomed to the data exaggerate small gaps. That is the convention in ML
# papers and is defensible here because every seed is plotted, but set this to
# True for an axis anchored at zero if your venue expects it.
ZERO_BASELINE = False


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


def permutation_p(a, b, n_perm=N_PERM, seed=0):
    """Two-sided permutation test on the difference in means.

    Exact under the null by construction and free of the normality assumption
    a t-test makes — which rarely holds for a handful of seeds.
    """
    rng = np.random.default_rng(seed)
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    observed = abs(a.mean() - b.mean())
    pool = np.concatenate([a, b])
    order = np.argsort(rng.random((n_perm, pool.size)), axis=1)
    shuffled = pool[order]
    null = np.abs(shuffled[:, :a.size].mean(axis=1)
                  - shuffled[:, a.size:].mean(axis=1))
    # +1 correction: a permutation p-value is never legitimately zero.
    return (np.sum(null >= observed) + 1) / (n_perm + 1)


def stars(p):
    return ('***' if p < 0.001 else '**' if p < 0.01
            else '*' if p < 0.05 else 'n.s.')


def cohens_d(a, b):
    """Standardised mean difference, pooled s.d."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    pooled = np.sqrt(((a.size - 1) * a.var(ddof=1)
                      + (b.size - 1) * b.var(ddof=1)) / (a.size + b.size - 2))
    return (a.mean() - b.mean()) / pooled if pooled > 0 else 0.0


datasets = list(pd.unique(df[COLS['dataset']]))
models = list(pd.unique(df[COLS['model']]))
baseline = BASELINE or models[0]

W = _opt('_fig_width', 13.0)
H = _opt('_fig_height', 5.5)
fig, axes = plt.subplots(1, len(datasets), figsize=(W, H), layout='constrained')
axes = np.atleast_1d(axes)

PALETTE = ['#949494', '#0173B2', '#029E73', '#DE8F05', '#D55E00', '#CC78BC']
rng = np.random.default_rng(7)

for ax, dataset in zip(axes, datasets):
    block = df[df[COLS['dataset']] == dataset]
    means, cis, samples = [], [], []
    for model in models:
        values = block[block[COLS['model']] == model][COLS['score']].to_numpy(float)
        samples.append(values)
        means.append(values.mean())
        # Normal-approximation CI on the mean over seeds.
        sem = values.std(ddof=1) / np.sqrt(values.size) if values.size > 1 else 0.0
        cis.append(1.96 * sem)
    means = np.array(means)
    cis = np.array(cis)

    x = np.arange(len(models))
    ax.bar(x, means, yerr=cis, width=0.66, capsize=3.5,
           color=[PALETTE[i % len(PALETTE)] for i in range(len(models))],
           edgecolor='white', linewidth=1.0, zorder=3,
           error_kw=dict(elinewidth=1.1, ecolor='#333333', zorder=5))

    # Every seed as a jittered dot — the honest denominator of the bar.
    for i, values in enumerate(samples):
        jitter = rng.uniform(-0.16, 0.16, values.size)
        ax.scatter(x[i] + jitter, values, s=13, color='#222222', alpha=0.55,
                   zorder=6, linewidths=0)

    lo = min(v.min() for v in samples)
    hi = max(v.max() for v in samples)
    span = hi - lo
    ax.set_ylim(0 if ZERO_BASELINE else lo - span * 0.25, hi + span * 0.75)

    # Significance brackets: every method against the baseline.
    base_idx = models.index(baseline)
    step = span * 0.13
    level = hi + span * 0.10
    for i, model in enumerate(models):
        if i == base_idx:
            continue
        p = permutation_p(samples[i], samples[base_idx], seed=i)
        d = cohens_d(samples[i], samples[base_idx])
        x0, x1 = sorted((x[base_idx], x[i]))
        ax.plot([x0, x0, x1, x1],
                [level, level + step * 0.22, level + step * 0.22, level],
                color='#444444', linewidth=0.9, zorder=7)
        label = stars(p)
        if p < 0.05:
            label += f'  d={d:.2f}'
        ax.text((x0 + x1) / 2, level + step * 0.26, label, ha='center',
                va='bottom', fontsize=7, color='#333333')
        level += step

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=30, ha='right', fontsize=8)
    ax.set_title(dataset, fontsize=10, loc='left', fontweight='bold')
    if ax is axes[0]:
        ax.set_ylabel(METRIC_NAME)

n_seeds = df[COLS['seed']].nunique()
fig.suptitle(f'Method comparison over {n_seeds} seeds — bars are means with '
             f'95% CI, brackets are two-sided permutation tests vs "{baseline}"',
             fontsize=10, y=1.03)
