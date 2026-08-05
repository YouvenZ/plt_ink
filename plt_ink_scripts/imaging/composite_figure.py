"""
Multi-Panel Composite Figure
The assembly template: mixed panel types (image, curves, distribution, bars),
bold A/B/C/D labels in the corner, one shared figure legend, a journal caption
block and exact column-width sizing. Edit the panel functions, keep the frame.
requires_data: true
data_columns: model, y_true, y_score
sample_data: predictions_binary.csv
requires_image: true
sample_image: images/case01_image.png
tags: publication, multi-panel, composite, layout, figure-assembly
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Figure specification ─────────────────────────────────────────────────────
# Journal column widths in inches: Nature 89 mm / 183 mm, IEEE 3.5" / 7.16".
COLUMN_WIDTH = 7.2         # double column
ASPECT = 0.62              # height / width
PANEL_LABEL_SIZE = 11
CAPTION = (
    'Figure 1 | Model performance on the held-out cohort. '
    '(a) Representative input with the annotated region outlined. '
    '(b) Discrimination measured by ROC; the shaded region is the '
    'bootstrap 95% interval for the best model. '
    '(c) Distribution of predicted scores by true class; the dashed line is '
    'the operating threshold. '
    '(d) Sensitivity and specificity at that threshold, per model. '
    'n = 900 cases, 205 positive.')

SAMPLE_CSV = 'predictions_binary.csv'
SAMPLE_IMAGE = 'images/case01_image.png'
SAMPLE_MASK = 'images/case01_mask_gt.png'
COLS = dict(model='model', y_true='y_true', y_score='y_score')
THRESHOLD = 0.5


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


def _resolve(path):
    if os.path.isabs(path):
        return path
    return os.path.join(_sample_dir(), *path.replace('\\', '/').split('/'))


def _load(sample, needed):
    frame = globals().get('data')
    if frame is not None and not set(needed) - set(map(str, frame.columns)):
        return frame.copy()
    return pd.read_csv(_resolve(sample))


def read_gray(path):
    array = plt.imread(_resolve(path))
    if array.ndim == 3:
        array = array[..., 0]
    return array.astype(float)


df = _load(SAMPLE_CSV, COLS.values())
models = list(pd.unique(df[COLS['model']]))
PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC']
colour_of = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(models)}

# ── Layout ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', COLUMN_WIDTH)
H = _opt('_fig_height', COLUMN_WIDTH * ASPECT * 1.55)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.85])
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, 0])
ax_d = fig.add_subplot(gs[1, 1])


def label_panel(ax, letter):
    """Bold letter in the top-left, outside the axes — the journal convention."""
    ax.annotate(letter, xy=(0, 1), xycoords='axes fraction',
                xytext=(-22, 10), textcoords='offset points',
                fontsize=PANEL_LABEL_SIZE, fontweight='bold', va='bottom',
                ha='left', annotation_clip=False)


# ── a: representative image ──────────────────────────────────────────────────
image = read_gray(SAMPLE_IMAGE)
ax_a.imshow(image, cmap='gray', interpolation='nearest')
try:
    mask = read_gray(SAMPLE_MASK)
    ax_a.contour((mask > mask.max() * 0.6).astype(float), levels=[0.5],
                 colors=['#DE8F05'], linewidths=1.4)
except Exception:
    pass
ax_a.set_axis_off()
ax_a.set_title('Representative case', fontsize=8.5, loc='left')
# Scale bar instead of pixel ticks.
ax_a.plot([12, 12 + 38], [image.shape[0] - 14] * 2, color='white', linewidth=2.4,
          solid_capstyle='butt')
ax_a.text(12 + 19, image.shape[0] - 20, '1 cm', color='white', ha='center',
          va='bottom', fontsize=7)
label_panel(ax_a, 'a')


# ── b: ROC ───────────────────────────────────────────────────────────────────
def roc(y, s):
    order = np.argsort(-s, kind='mergesort')
    y = y[order]
    tps, fps = np.cumsum(y), np.cumsum(1 - y)
    if tps[-1] == 0 or fps[-1] == 0:
        return np.array([0, 1]), np.array([0, 1]), 0.5
    fpr = np.concatenate([[0.0], fps / fps[-1]])
    tpr = np.concatenate([[0.0], tps / tps[-1]])
    area = getattr(np, 'trapezoid', None) or np.trapz
    return fpr, tpr, float(area(tpr, fpr))


aucs = {}
for model in models:
    sub = df[df[COLS['model']] == model]
    y = sub[COLS['y_true']].to_numpy(float)
    s = sub[COLS['y_score']].to_numpy(float)
    fpr, tpr, auc = roc(y, s)
    aucs[model] = auc
    ax_b.plot(fpr, tpr, color=colour_of[model], linewidth=1.6, zorder=4,
              label=f'{model} ({auc:.2f})')

best = max(aucs, key=aucs.get)
sub = df[df[COLS['model']] == best]
rng = np.random.default_rng(0)
grid = np.linspace(0, 1, 80)
boot = []
y_best = sub[COLS['y_true']].to_numpy(float)
s_best = sub[COLS['y_score']].to_numpy(float)
for _ in range(200):
    idx = rng.integers(0, y_best.size, y_best.size)
    if y_best[idx].sum() in (0, idx.size):
        continue
    fpr, tpr, _ = roc(y_best[idx], s_best[idx])
    boot.append(np.interp(grid, fpr, tpr))
if boot:
    boot = np.array(boot)
    ax_b.fill_between(grid, np.percentile(boot, 2.5, axis=0),
                      np.percentile(boot, 97.5, axis=0),
                      color=colour_of[best], alpha=0.18, linewidth=0, zorder=3)

ax_b.plot([0, 1], [0, 1], color='#999999', linewidth=0.9, linestyle='--',
          zorder=2)
ax_b.set_xlabel('1 - specificity', fontsize=8.5)
ax_b.set_ylabel('Sensitivity', fontsize=8.5)
ax_b.set_xlim(0, 1)
ax_b.set_ylim(0, 1)
ax_b.set_aspect('equal')
ax_b.tick_params(labelsize=7.5)
label_panel(ax_b, 'b')

# ── c: score distributions for the best model ────────────────────────────────
bins = np.linspace(0, 1, 34)
for value, name, colour in ((0, 'Negative', '#0173B2'),
                            (1, 'Positive', '#D55E00')):
    ax_c.hist(s_best[y_best == value], bins=bins, color=colour, alpha=0.55,
              label=f'{name} (n={int((y_best == value).sum())})', zorder=3)
ax_c.axvline(THRESHOLD, color='#333333', linewidth=1.1, linestyle='--',
             zorder=4)
# Log counts: a well-separated model puts most negatives in the first bin,
# which on a linear axis flattens everything else to invisibility.
ax_c.set_yscale('log')
ax_c.set_xlabel(f'Predicted score — {best}', fontsize=8.5)
ax_c.set_ylabel('Cases', fontsize=8.5)
ax_c.tick_params(labelsize=7.5)
ax_c.legend(fontsize=7, framealpha=0.9, loc='upper center')
label_panel(ax_c, 'c')

# ── d: operating-point metrics ───────────────────────────────────────────────
x = np.arange(len(models))
width = 0.36
sens, spec = [], []
for model in models:
    sub = df[df[COLS['model']] == model]
    y = sub[COLS['y_true']].to_numpy(float)
    s = sub[COLS['y_score']].to_numpy(float)
    predicted = s >= THRESHOLD
    sens.append(np.sum(predicted & (y == 1)) / max(np.sum(y == 1), 1))
    spec.append(np.sum(~predicted & (y == 0)) / max(np.sum(y == 0), 1))

ax_d.bar(x - width / 2, sens, width, color='#D55E00', label='Sensitivity',
         zorder=3)
ax_d.bar(x + width / 2, spec, width, color='#0173B2', label='Specificity',
         zorder=3)
for i, (a, b) in enumerate(zip(sens, spec)):
    ax_d.text(i - width / 2, a + 0.02, f'{a:.2f}', ha='center', fontsize=6.5)
    ax_d.text(i + width / 2, b + 0.02, f'{b:.2f}', ha='center', fontsize=6.5)
ax_d.set_xticks(x)
ax_d.set_xticklabels([m.replace(' ', '\n') for m in models], fontsize=7)
ax_d.set_ylim(0, 1.15)
ax_d.set_ylabel(f'At threshold {THRESHOLD:g}', fontsize=8.5)
ax_d.tick_params(labelsize=7.5)
label_panel(ax_d, 'd')

# ── One shared legend for the models, plus the caption block ─────────────────
handles = [plt.Line2D([], [], color=colour_of[m], linewidth=2, label=m)
           for m in models]
handles += [plt.Rectangle((0, 0), 1, 1, color='#D55E00', alpha=0.7,
                          label='Sensitivity'),
            plt.Rectangle((0, 0), 1, 1, color='#0173B2', alpha=0.7,
                          label='Specificity')]
fig.legend(handles=handles, loc='outside upper center', ncol=len(handles),
           fontsize=7.5, frameon=False)

fig.text(0.0, -0.015, CAPTION, ha='left', va='top', fontsize=7.2,
         color='#333333', wrap=True)
