"""
Saliency / Grad-CAM Overlay Grid
Original image, heatmap and overlay per case with one shared colorbar, plus
the fraction of attention landing inside the annotated lesion. Quantifying the
overlap is what separates an evidence figure from a pretty picture.
requires_image: true
sample_image: images/case01_image.png
sample_mask: images/case01_cam.png
tags: imaging, interpretability, grad-cam, saliency, medical-imaging
note: reads PNG cases from sample_data/images; point CASES at your own files
"""

import os

import numpy as np
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
# (label, image, saliency map, optional lesion mask, predicted, true)
CASES = [
    ('Case 01', 'images/case01_image.png', 'images/case01_cam.png',
     'images/case01_mask_gt.png', 'Malignant', 'Malignant'),
    ('Case 02', 'images/case02_image.png', 'images/case02_cam.png',
     'images/case02_mask_gt.png', 'Malignant', 'Malignant'),
    ('Case 03', 'images/case03_image.png', 'images/case03_cam.png',
     'images/case03_mask_gt.png', 'Benign', 'Malignant'),
    ('Case 04', 'images/case04_image.png', 'images/case04_cam.png',
     'images/case04_mask_gt.png', 'Malignant', 'Malignant'),
]
LESION_VALUE = 2           # label value marking the lesion in the mask
CAM_CMAP = 'inferno'
ALPHA = 0.45
THRESHOLD = 0.5            # contour drawn at this fraction of peak attention


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
    array = plt.imread(_resolve(path))
    if array.ndim == 3:
        array = array[..., 0]
    return array.astype(float)


W = _opt('_fig_width', 3.0 * len(CASES) + 1.0)
H = _opt('_fig_height', 8.0)
fig, axes = plt.subplots(3, len(CASES), figsize=(W, H), layout='constrained')
axes = np.atleast_2d(axes)
if axes.shape[0] != 3:
    axes = axes.T

images = []
for column, (label, image_path, cam_path, mask_path, pred, true) in enumerate(CASES):
    image = read_gray(image_path)
    cam = read_gray(cam_path)
    # Normalise per case so the shared colorbar means "fraction of this case's
    # peak activation" — comparing raw activations across cases is meaningless.
    # np.ptp(), not cam.ptp(): the ndarray method was removed in numpy 2.0.
    cam = (cam - cam.min()) / (float(np.ptp(cam)) or 1.0)
    mask = read_gray(mask_path) if mask_path else None

    axes[0, column].imshow(image, cmap='gray', interpolation='nearest')
    im = axes[1, column].imshow(cam, cmap=CAM_CMAP, vmin=0, vmax=1,
                                interpolation='bilinear')
    images.append(im)

    axes[2, column].imshow(image, cmap='gray', interpolation='nearest')
    axes[2, column].imshow(cam, cmap=CAM_CMAP, vmin=0, vmax=1, alpha=ALPHA,
                           interpolation='bilinear')
    axes[2, column].contour(cam, levels=[THRESHOLD], colors=['white'],
                            linewidths=1.2)

    # Does the attention land on the annotated lesion?
    caption = f'{label}'
    if mask is not None:
        lesion = np.isclose(mask * (LESION_VALUE if mask.max() <= 1.0 + 1e-6
                                    else 1.0), LESION_VALUE, atol=0.4)
        if lesion.any():
            hot = cam >= THRESHOLD
            # Enrichment, not share: a small lesion holds a small *share* of
            # total attention however well the model localises it, so the
            # share reads as failure. Mean activation inside over mean
            # overall answers the question actually being asked.
            enrichment = (float(cam[lesion].mean() / cam.mean())
                          if cam.mean() else 0.0)
            iou = (np.logical_and(hot, lesion).sum()
                   / max(np.logical_or(hot, lesion).sum(), 1))
            caption += (f'\nattention {enrichment:.1f}x enriched on lesion, '
                        f'IoU {iou:.2f}')
            for ax in (axes[0, column], axes[2, column]):
                ax.contour(lesion.astype(float), levels=[0.5],
                           colors=['#029E73'], linewidths=1.2)

    correct = pred == true
    axes[0, column].set_title(
        f'{label}\npredicted: {pred}' + ('' if correct else f'  (true: {true})'),
        fontsize=8.5, pad=4,
        color='#222222' if correct else '#D55E00',
        fontweight='normal' if correct else 'bold')
    axes[2, column].set_xlabel(caption, fontsize=7.5)

    for row in range(3):
        axes[row, column].set_xticks([])
        axes[row, column].set_yticks([])
        for spine in axes[row, column].spines.values():
            spine.set_visible(False)
        axes[row, column].grid(False)

for row, name in enumerate(('Input', 'Saliency', 'Overlay')):
    axes[row, 0].set_ylabel(name, fontsize=9.5, fontweight='bold')

cbar = fig.colorbar(images[0], ax=axes[:, -1], fraction=0.05, pad=0.02)
cbar.set_label('Normalised activation (fraction of per-case peak)', fontsize=8.5)
cbar.ax.tick_params(labelsize=8)

fig.suptitle(f'Grad-CAM attribution  •  white contour at {THRESHOLD:.0%} of '
             'peak activation, green contour is the annotated lesion',
             fontsize=9.5, x=0.02, ha='left')
