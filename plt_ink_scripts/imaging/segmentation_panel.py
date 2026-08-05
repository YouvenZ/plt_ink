"""
Segmentation Qualitative Panel
One row per case: image, ground-truth overlay, prediction overlay and a
false-positive/false-negative error map, with per-case Dice. The figure every
segmentation paper needs and no library produces.
requires_image: true
sample_image: images/case01_image.png
sample_mask: images/case01_mask_gt.png
tags: imaging, segmentation, medical-imaging, qualitative, overlay
note: reads PNG cases from sample_data/images; point CASES at your own files
"""

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ── Data ─────────────────────────────────────────────────────────────────────
# Each case is (label, image, ground truth, prediction). Paths are relative to
# the sample-data folder; absolute paths work too.
CASES = [
    ('Case 01', 'images/case01_image.png', 'images/case01_mask_gt.png',
     'images/case01_mask_pred.png'),
    ('Case 02', 'images/case02_image.png', 'images/case02_mask_gt.png',
     'images/case02_mask_pred.png'),
    ('Case 03', 'images/case03_image.png', 'images/case03_mask_gt.png',
     'images/case03_mask_pred.png'),
]
# Mask value -> (structure name, overlay colour).
STRUCTURES = {1: ('Liver', '#0173B2'), 2: ('Tumour', '#DE8F05')}
ALPHA = 0.40
SCALE_BAR = (2.0, 'cm')    # (length in the image's units, unit label); None hides
PIXELS_PER_UNIT = 38.0     # pixels per SCALE_BAR unit


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


def read_gray(path):
    """Read a PNG as a 2-D float array, dropping any colour/alpha channels."""
    array = plt.imread(_resolve(path))
    if array.ndim == 3:
        array = array[..., 0]
    return array.astype(float)


def read_mask(path):
    """Read a label map, undoing the 0..1 scaling matplotlib applies to PNGs."""
    array = read_gray(path)
    if array.max() <= 1.0 + 1e-6:
        # Written with vmin=0, vmax=max(label); recover integer labels.
        array = array * max(STRUCTURES)
    return np.rint(array).astype(int)


def dice(a, b):
    total = a.sum() + b.sum()
    return 2.0 * np.logical_and(a, b).sum() / total if total else np.nan


def overlay(ax, image, mask, title):
    """Grayscale image with translucent, outlined label regions."""
    ax.imshow(image, cmap='gray', interpolation='nearest')
    for value, (name, colour) in STRUCTURES.items():
        region = mask == value
        if not region.any():
            continue
        rgba = np.zeros(region.shape + (4,))
        rgba[..., :3] = plt.matplotlib.colors.to_rgb(colour)
        rgba[..., 3] = region * ALPHA
        ax.imshow(rgba, interpolation='nearest')
        # A crisp boundary as well as the fill — fills alone hide thin errors.
        ax.contour(region.astype(float), levels=[0.5], colors=[colour],
                   linewidths=1.1)
    ax.set_title(title, fontsize=9, pad=4)
    ax.set_axis_off()


W = _opt('_fig_width', 11.0)
H = _opt('_fig_height', 3.0 * len(CASES))
fig, axes = plt.subplots(len(CASES), 4, figsize=(W, H), layout='constrained')
axes = np.atleast_2d(axes)

FP_COLOUR, FN_COLOUR, TP_COLOUR = '#D55E00', '#0173B2', '#029E73'

for row, (label, image_path, gt_path, pred_path) in enumerate(CASES):
    image = read_gray(image_path)
    gt = read_mask(gt_path)
    pred = read_mask(pred_path)

    overlay(axes[row, 0], image, np.zeros_like(gt),
            'Image' if row == 0 else '')
    overlay(axes[row, 1], image, gt, 'Ground truth' if row == 0 else '')
    overlay(axes[row, 2], image, pred, 'Prediction' if row == 0 else '')

    # Error map: agreement in grey, false positives and negatives in colour.
    ax_err = axes[row, 3]
    fg_gt, fg_pred = gt > 0, pred > 0
    rgb = np.zeros(image.shape + (3,))
    rgb[...] = (image[..., None] * 0.55)
    rgb[np.logical_and(fg_gt, fg_pred)] = plt.matplotlib.colors.to_rgb(TP_COLOUR)
    rgb[np.logical_and(~fg_gt, fg_pred)] = plt.matplotlib.colors.to_rgb(FP_COLOUR)
    rgb[np.logical_and(fg_gt, ~fg_pred)] = plt.matplotlib.colors.to_rgb(FN_COLOUR)
    ax_err.imshow(np.clip(rgb, 0, 1), interpolation='nearest')
    ax_err.set_title('Error map' if row == 0 else '', fontsize=9, pad=4)
    ax_err.set_axis_off()

    # Per-structure Dice, printed on the error map where it is read.
    scores = []
    for value, (name, _) in STRUCTURES.items():
        d = dice(gt == value, pred == value)
        if np.isfinite(d):
            scores.append(f'{name} {d:.3f}')
    ax_err.text(0.98, 0.02, 'Dice\n' + '\n'.join(scores),
                transform=ax_err.transAxes, ha='right', va='bottom',
                fontsize=7.5, color='white',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#000000',
                          edgecolor='none', alpha=0.55))

    axes[row, 0].text(-0.04, 0.5, label, transform=axes[row, 0].transAxes,
                      rotation=90, va='center', ha='right', fontsize=9.5,
                      fontweight='bold')

    if SCALE_BAR is not None and row == len(CASES) - 1:
        length_px = SCALE_BAR[0] * PIXELS_PER_UNIT
        y = image.shape[0] * 0.94
        x0 = image.shape[1] * 0.06
        axes[row, 0].plot([x0, x0 + length_px], [y, y], color='white',
                          linewidth=2.6, solid_capstyle='butt')
        axes[row, 0].text(x0 + length_px / 2, y - image.shape[0] * 0.035,
                          f'{SCALE_BAR[0]:g} {SCALE_BAR[1]}', color='white',
                          ha='center', va='bottom', fontsize=7.5)

handles = [Patch(facecolor=colour, alpha=0.6, label=name)
           for name, colour in STRUCTURES.values()]
handles += [Patch(facecolor=TP_COLOUR, label='True positive'),
            Patch(facecolor=FP_COLOUR, label='False positive'),
            Patch(facecolor=FN_COLOUR, label='False negative')]
fig.legend(handles=handles, loc='outside lower center', ncol=len(handles),
           fontsize=8.5, frameon=False)
fig.suptitle('Segmentation results', fontsize=11, fontweight='bold', x=0.02,
             ha='left')
