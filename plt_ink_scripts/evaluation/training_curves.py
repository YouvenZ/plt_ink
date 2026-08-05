"""
Training Curves (multi-seed)
Accuracy and loss for train/validation with a mean +/- s.d. band across seeds,
best-epoch markers and the learning-rate schedule underneath. The honest way to
report a training run: one line per model, not one line per seed.
requires_data: true
data_columns: model, seed, epoch, split, loss, accuracy, lr
sample_data: training_runs.csv
tags: deep-learning, training, curves, evaluation
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
# Point these at your own column names; nothing below uses raw strings.
COLS = dict(model='model', seed='seed', epoch='epoch', split='split',
            loss='loss', metric='accuracy', lr='lr')
SAMPLE = 'training_runs.csv'
TRAIN_LABEL, VAL_LABEL = 'train', 'val'      # values found in the split column
METRIC_NAME = 'Accuracy'


def _opt(name, default):
    """Read an extension setting, with a fallback when run standalone."""
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
    """Use the extension's `data` when it carries the needed columns, else the
    bundled example CSV — so the template always renders something."""
    frame = globals().get('data')
    if frame is not None and not set(needed) - set(map(str, frame.columns)):
        return frame.copy()
    return pd.read_csv(os.path.join(_sample_dir(), sample))


df = _load(SAMPLE, COLS.values())

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#949494']
models = list(pd.unique(df[COLS['model']]))
colors = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(models)}

# ── Layout ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', 10.0)
H = _opt('_fig_height', 6.5)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 2, height_ratios=[3.0, 1.0])
ax_metric = fig.add_subplot(gs[0, 0])
ax_loss = fig.add_subplot(gs[0, 1], sharex=ax_metric)
ax_lr = fig.add_subplot(gs[1, :], sharex=ax_metric)


def band(ax, sub, value_col, color, style, label):
    """Mean line with a +/- 1 s.d. ribbon over seeds. Returns (epochs, mean)."""
    stat = sub.groupby(COLS['epoch'])[value_col].agg(['mean', 'std', 'count'])
    stat['std'] = stat['std'].fillna(0.0)
    x = stat.index.values
    if (stat['count'] > 1).any():
        ax.fill_between(x, stat['mean'] - stat['std'], stat['mean'] + stat['std'],
                        color=color, alpha=0.18, linewidth=0)
    ax.plot(x, stat['mean'], color=color, linestyle=style, linewidth=1.9,
            label=label, zorder=4)
    return x, stat['mean'].values


n_seeds = df[COLS['seed']].nunique()
best_of = {}

for ax, value_col, ylabel in ((ax_metric, COLS['metric'], METRIC_NAME),
                              (ax_loss, COLS['loss'], 'Loss')):
    for model in models:
        rows = df[df[COLS['model']] == model]
        for split, style, suffix in ((TRAIN_LABEL, '--', ' (train)'),
                                     (VAL_LABEL, '-', ' (val)')):
            sub = rows[rows[COLS['split']] == split]
            if sub.empty:
                continue
            x, mean = band(ax, sub, value_col, colors[model], style,
                           f'{model}{suffix}' if ax is ax_metric else None)
            if ax is ax_metric and split == VAL_LABEL:
                best_of[model] = (x[int(np.argmax(mean))], float(np.max(mean)))
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Epoch')
    ax.margins(x=0.01)

# Best validation epoch: a marker for every model, a label for the winner only.
for model, (bx, by) in best_of.items():
    ax_metric.scatter([bx], [by], s=44, color=colors[model], zorder=6,
                      edgecolors='white', linewidths=1.2)
if best_of:
    champion = max(best_of, key=lambda m: best_of[m][1])
    bx, by = best_of[champion]
    ax_metric.annotate(
        f'best {METRIC_NAME.lower()} {by:.3f}\n{champion}, epoch {bx:g}',
        xy=(bx, by), xytext=(-14, -46), textcoords='offset points',
        fontsize=8, ha='right',
        arrowprops=dict(arrowstyle='-|>', color='#444444', linewidth=1.0,
                        connectionstyle='arc3,rad=0.25'),
        bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                  edgecolor='#BBBBBB', alpha=0.95))

ax_loss.set_yscale('log')
ax_loss.set_title('Loss', fontsize=10, loc='left', fontweight='bold')
ax_metric.set_title(f'{METRIC_NAME} (mean $\\pm$ s.d., n={n_seeds} seeds)',
                    fontsize=10, loc='left', fontweight='bold')
ax_metric.legend(fontsize=7.5, ncol=1, loc='lower right', framealpha=0.92)

# ── Learning-rate schedule ───────────────────────────────────────────────────
if COLS['lr'] in df.columns:
    lr = (df.groupby(COLS['epoch'])[COLS['lr']].mean())
    ax_lr.step(lr.index.values, lr.values, where='post', color='#444444',
               linewidth=1.6)
    ax_lr.fill_between(lr.index.values, lr.values, step='post',
                       color='#444444', alpha=0.12)
    ax_lr.set_yscale('log')
    ax_lr.set_ylabel('LR')
    # Mark each decay so the steps in the curves above have an explanation.
    drops = lr.index.values[1:][np.diff(lr.values) < 0]
    for d in drops:
        for ax in (ax_metric, ax_loss, ax_lr):
            ax.axvline(d, color='#999999', linewidth=0.7, linestyle=':',
                       zorder=1)
else:
    ax_lr.set_visible(False)
ax_lr.set_xlabel('Epoch')
