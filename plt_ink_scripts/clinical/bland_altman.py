"""
Bland-Altman Agreement
Difference against mean with bias, 95% limits of agreement and their CIs, a
proportional-bias regression, and a scatter of the two methods against the line
of identity. Correlation is not agreement — this is the figure that shows it.
requires_data: true
data_columns: method_a, method_b
sample_data: method_agreement.csv
tags: clinical, agreement, bland-altman, method-comparison, biostatistics
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(a='method_a', b='method_b', group='reader')
SAMPLE = 'method_agreement.csv'
NAME_A, NAME_B = 'Manual', 'Automated'
UNITS = '% LVEF'
CLINICAL_LIMIT = 5.0       # acceptable difference; None to hide the band


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


df = _load(SAMPLE, [COLS['a'], COLS['b']])

a = df[COLS['a']].to_numpy(float)
b = df[COLS['b']].to_numpy(float)
mean = (a + b) / 2.0
diff = a - b
n = diff.size

bias = float(diff.mean())
sd = float(diff.std(ddof=1))
loa_low, loa_high = bias - 1.96 * sd, bias + 1.96 * sd
# CIs for the bias and for each limit (Bland & Altman 1986).
se_bias = sd / np.sqrt(n)
se_loa = sd * np.sqrt(3.0 / n)

# Proportional bias: does the disagreement grow with the magnitude?
slope, intercept = np.polyfit(mean, diff, 1)
residual = diff - (slope * mean + intercept)
se_slope = np.sqrt(np.sum(residual ** 2) / (n - 2)
                   / np.sum((mean - mean.mean()) ** 2))
t_slope = slope / se_slope if se_slope > 0 else 0.0

W = _opt('_fig_width', 12.0)
H = _opt('_fig_height', 5.5)
fig, (ax, ax_id) = plt.subplots(1, 2, figsize=(W, H), layout='constrained',
                                width_ratios=[1.45, 1.0])

groups = (df[COLS['group']].astype(str).to_numpy()
          if COLS['group'] in df.columns else np.array([''] * n))
unique_groups = list(dict.fromkeys(groups))
PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00']

# ── Panel a: difference vs mean ──────────────────────────────────────────────
if CLINICAL_LIMIT is not None:
    ax.axhspan(-CLINICAL_LIMIT, CLINICAL_LIMIT, color='#029E73', alpha=0.07,
               zorder=0)
    ax.text(0.995, CLINICAL_LIMIT, f' acceptable $\\pm${CLINICAL_LIMIT:g}',
            transform=ax.get_yaxis_transform(), ha='right', va='bottom',
            fontsize=7.5, color='#029E73')

for i, g in enumerate(unique_groups):
    m = groups == g
    ax.scatter(mean[m], diff[m], s=26, color=PALETTE[i % len(PALETTE)],
               alpha=0.75, edgecolors='white', linewidths=0.5, zorder=4,
               label=g or None)

for value, colour, style, label in (
        (bias, '#D55E00', '-', f'Bias {bias:+.2f}'),
        (loa_high, '#444444', '--', f'Upper LoA {loa_high:+.2f}'),
        (loa_low, '#444444', '--', f'Lower LoA {loa_low:+.2f}')):
    ax.axhline(value, color=colour, linewidth=1.4, linestyle=style, zorder=3)
    ax.text(0.005, value, f' {label}', transform=ax.get_yaxis_transform(),
            ha='left', va='bottom', fontsize=8, color=colour,
            fontweight='bold' if colour == '#D55E00' else 'normal')

# Confidence bands on the three reference lines.
for value, se in ((bias, se_bias), (loa_low, se_loa), (loa_high, se_loa)):
    ax.axhspan(value - 1.96 * se, value + 1.96 * se, color='#888888',
               alpha=0.14, zorder=1)

xs = np.linspace(mean.min(), mean.max(), 100)
ax.plot(xs, slope * xs + intercept, color='#0173B2', linewidth=1.3,
        linestyle=':', zorder=5)

ax.set_xlabel(f'Mean of {NAME_A} and {NAME_B} ({UNITS})')
ax.set_ylabel(f'{NAME_A} − {NAME_B} ({UNITS})')
ax.set_title('a   Bland-Altman', fontsize=10, loc='left', fontweight='bold')
if len(unique_groups) > 1:
    ax.legend(fontsize=8, loc='lower left', framealpha=0.92)

proportional = ('yes' if abs(t_slope) > 2 else 'no')
inside = int(np.sum(np.abs(diff) <= CLINICAL_LIMIT)) if CLINICAL_LIMIT else None
summary = (f'n = {n}\n'
           f'Bias {bias:+.2f} (95% CI {bias - 1.96 * se_bias:+.2f} to '
           f'{bias + 1.96 * se_bias:+.2f})\n'
           f'95% LoA {loa_low:+.2f} to {loa_high:+.2f}\n'
           f'Proportional bias: {proportional} (slope {slope:+.3f}, '
           f't = {t_slope:.1f})')
if inside is not None:
    summary += f'\nWithin $\\pm${CLINICAL_LIMIT:g}: {inside}/{n} ({inside / n:.0%})'
ax.text(0.995, 0.02, summary, transform=ax.transAxes, ha='right', va='bottom',
        fontsize=7.5, family='monospace',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor='#CCCCCC', alpha=0.95))

# ── Panel b: the two methods against the line of identity ────────────────────
lim = [min(a.min(), b.min()) * 0.95, max(a.max(), b.max()) * 1.03]
ax_id.plot(lim, lim, color='#444444', linewidth=1.2, linestyle='--',
           zorder=2, label='Line of identity')
for i, g in enumerate(unique_groups):
    m = groups == g
    ax_id.scatter(b[m], a[m], s=26, color=PALETTE[i % len(PALETTE)], alpha=0.75,
                  edgecolors='white', linewidths=0.5, zorder=4)

fit_slope, fit_intercept = np.polyfit(b, a, 1)
ax_id.plot(np.array(lim), fit_slope * np.array(lim) + fit_intercept,
           color='#0173B2', linewidth=1.5, zorder=5,
           label=f'Fit: y = {fit_slope:.2f}x {fit_intercept:+.2f}')

r = float(np.corrcoef(a, b)[0, 1])
# Lin's concordance correlation: agreement, not just association.
ccc = (2 * np.cov(a, b, ddof=1)[0, 1]
       / (a.var(ddof=1) + b.var(ddof=1) + (a.mean() - b.mean()) ** 2))
ax_id.set_xlim(lim)
ax_id.set_ylim(lim)
ax_id.set_aspect('equal')
ax_id.set_xlabel(f'{NAME_B} ({UNITS})')
ax_id.set_ylabel(f'{NAME_A} ({UNITS})')
ax_id.set_title('b   Method vs method', fontsize=10, loc='left',
                fontweight='bold')
ax_id.legend(fontsize=8, loc='upper left', framealpha=0.92)
ax_id.text(0.98, 0.03, f'Pearson r = {r:.3f}\nLin\'s CCC = {ccc:.3f}',
           transform=ax_id.transAxes, ha='right', va='bottom', fontsize=8,
           bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                     edgecolor='#CCCCCC', alpha=0.95))
