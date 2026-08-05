"""
Parity Plot with Residual Diagnostics
Predicted against measured on a 1:1 axis with a tolerance band, beside
residuals versus fitted and a normal Q-Q plot. R², RMSE, MAE and bias are
reported per split. The standard regression-model report figure.
requires_data: true
data_columns: y_true, y_pred, split
sample_data: pred_vs_measured.csv
tags: statistics, regression, parity, residuals, engineering
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(true='y_true', pred='y_pred', split='split')
SAMPLE = 'pred_vs_measured.csv'
UNITS = 'MPa'
TOLERANCE = 0.10           # relative band drawn around the 1:1 line; None hides
HIGHLIGHT = 'test'         # which split drives the residual panels


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


df = _load(SAMPLE, [COLS['true'], COLS['pred']])
has_split = COLS['split'] in df.columns
splits = list(pd.unique(df[COLS['split']])) if has_split else [None]

W = _opt('_fig_width', 13.0)
H = _opt('_fig_height', 5.0)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.0, 1.0])
ax = fig.add_subplot(gs[0, 0])
ax_res = fig.add_subplot(gs[0, 1])
ax_qq = fig.add_subplot(gs[0, 2])

PALETTE = ['#BBBBBB', '#DE8F05', '#0173B2', '#029E73']
lim = [df[[COLS['true'], COLS['pred']]].to_numpy().min(),
       df[[COLS['true'], COLS['pred']]].to_numpy().max()]
pad = (lim[1] - lim[0]) * 0.05
lim = [lim[0] - pad, lim[1] + pad]
summary = []

if TOLERANCE is not None:
    band = np.array(lim)
    ax.fill_between(band, band * (1 - TOLERANCE), band * (1 + TOLERANCE),
                    color='#029E73', alpha=0.08, linewidth=0, zorder=1)
ax.plot(lim, lim, color='#333333', linewidth=1.3, linestyle='--', zorder=3,
        label='1:1')

for i, split in enumerate(splits):
    block = df if split is None else df[df[COLS['split']] == split]
    y = block[COLS['true']].to_numpy(float)
    p = block[COLS['pred']].to_numpy(float)
    color = PALETTE[i % len(PALETTE)]
    ax.scatter(y, p, s=16, color=color, alpha=0.6, linewidths=0, zorder=4,
               label=split)

    residual = p - y
    rmse = float(np.sqrt(np.mean(residual ** 2)))
    mae = float(np.mean(np.abs(residual)))
    bias = float(np.mean(residual))
    ss_res = float(np.sum(residual ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    summary.append(f'{str(split or "all"):<6s} n={y.size:<4d} R²={r2:.3f}  '
                   f'RMSE={rmse:6.3f}  MAE={mae:6.3f}  bias={bias:+.3f}')

ax.set_xlim(lim)
ax.set_ylim(lim)
ax.set_aspect('equal')
ax.set_xlabel(f'Measured ({UNITS})')
ax.set_ylabel(f'Predicted ({UNITS})')
ax.set_title('a   Parity', fontsize=10, loc='left', fontweight='bold')
ax.legend(fontsize=8, loc='upper left', framealpha=0.93)
ax.text(0.985, 0.02, '\n'.join(summary), transform=ax.transAxes, ha='right',
        va='bottom', fontsize=7.2, family='monospace',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                  edgecolor='#CCCCCC', alpha=0.95))

# ── Residual diagnostics on one split ────────────────────────────────────────
focus = HIGHLIGHT if has_split and HIGHLIGHT in splits else splits[-1]
block = df if focus is None else df[df[COLS['split']] == focus]
y = block[COLS['true']].to_numpy(float)
p = block[COLS['pred']].to_numpy(float)
residual = p - y

ax_res.axhline(0, color='#333333', linewidth=1.1, linestyle='--', zorder=3)
ax_res.scatter(p, residual, s=16, color='#0173B2', alpha=0.6, linewidths=0,
               zorder=4)
# A running mean exposes curvature the eye misses in a cloud of points.
order = np.argsort(p)
window = max(5, p.size // 12)
smooth = np.convolve(residual[order], np.ones(window) / window, mode='valid')
ax_res.plot(p[order][window - 1:], smooth, color='#D55E00', linewidth=1.6,
            zorder=5, label=f'running mean ({window})')
ax_res.set_xlabel(f'Predicted ({UNITS})')
ax_res.set_ylabel(f'Residual ({UNITS})')
ax_res.set_title(f'b   Residuals vs fitted — {focus or "all"}', fontsize=10,
                 loc='left', fontweight='bold')
ax_res.legend(fontsize=7.5, loc='upper left', framealpha=0.9)

# ── Normal Q-Q ───────────────────────────────────────────────────────────────
def norm_ppf(p):
    """Inverse standard normal CDF (Acklam) — avoids a scipy dependency."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    p = np.asarray(p, float)
    out = np.empty_like(p)
    low, high = p < 0.02425, p > 1 - 0.02425
    mid = ~(low | high)
    q = np.sqrt(-2 * np.log(np.where(low, p, 0.5)))
    out[low] = ((((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q
                 + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1))[low]
    q = np.sqrt(-2 * np.log(np.where(high, 1 - p, 0.5)))
    out[high] = -((((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q
                   + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1))[high]
    q = np.where(mid, p, 0.5) - 0.5
    r = q * q
    out[mid] = ((((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r
                 + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r
                                 + b[4]) * r + 1))[mid]
    return out


standardised = (residual - residual.mean()) / residual.std(ddof=1)
observed = np.sort(standardised)
# Blom plotting positions.
theoretical = norm_ppf((np.arange(1, observed.size + 1) - 0.375)
                       / (observed.size + 0.25))
ax_qq.scatter(theoretical, observed, s=14, color='#0173B2', alpha=0.65,
              linewidths=0, zorder=4)
qq_lim = [min(theoretical.min(), observed.min()) - 0.3,
          max(theoretical.max(), observed.max()) + 0.3]
ax_qq.plot(qq_lim, qq_lim, color='#333333', linewidth=1.2, linestyle='--',
           zorder=3)
ax_qq.set_xlim(qq_lim)
ax_qq.set_ylim(qq_lim)
ax_qq.set_aspect('equal')
ax_qq.set_xlabel('Theoretical quantiles')
ax_qq.set_ylabel('Standardised residual')
ax_qq.set_title('c   Normal Q-Q', fontsize=10, loc='left', fontweight='bold')

skew = float(np.mean(standardised ** 3))
kurtosis = float(np.mean(standardised ** 4) - 3)
ax_qq.text(0.97, 0.03, f'skew {skew:+.2f}\nexcess kurtosis {kurtosis:+.2f}',
           transform=ax_qq.transAxes, ha='right', va='bottom', fontsize=7.5,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='#CCCCCC', alpha=0.95))
