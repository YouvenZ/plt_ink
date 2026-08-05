"""
Dose-Response Curves (4-parameter logistic)
Sigmoid fits per compound on a log-dose axis with replicate points, EC50
markers and bootstrap confidence bands. The fit is a grid search with an exact
inner least-squares solve, so it always converges and needs no scipy.
requires_data: true
data_columns: compound, dose, replicate, response
sample_data: dose_response.csv
tags: clinical, pharmacology, dose-response, ec50, assay
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(group='compound', dose='dose', replicate='replicate',
            response='response')
SAMPLE = 'dose_response.csv'
DOSE_UNITS = 'µM'
RESPONSE_LABEL = 'Response (% of control)'
N_BOOTSTRAP = 200


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


df = _load(SAMPLE, [COLS['group'], COLS['dose'], COLS['response']])


def fit_4pl(dose, response, n_ec50=90, n_hill=60):
    """Fit response = bottom + (top - bottom) / (1 + (EC50/dose)^hill).

    For fixed (EC50, hill) the model is linear in (bottom, top), so the whole
    grid is solved at once in closed form: a 2x2 normal-equation solve
    broadcast over every candidate pair. That beats a general optimiser on
    robustness — no initial guess, no failure to converge — and is fast enough
    to bootstrap. Needs no scipy.
    """
    log_dose = np.log10(dose)
    log_ec50 = np.linspace(log_dose.min() - 0.6, log_dose.max() + 0.6, n_ec50)
    hill = np.linspace(0.4, 4.0, n_hill)

    # f[i, j, k] = fraction from bottom to top for candidate (i, j) at dose k.
    ratio = 10.0 ** (log_ec50[:, None, None] - log_dose[None, None, :])
    f = 1.0 / (1.0 + ratio ** hill[None, :, None])
    u = 1.0 - f

    # Normal equations for the 2-parameter linear inner problem.
    a11 = np.sum(u * u, axis=2)
    a12 = np.sum(u * f, axis=2)
    a22 = np.sum(f * f, axis=2)
    b1 = np.sum(u * response, axis=2)
    b2 = np.sum(f * response, axis=2)
    det = a11 * a22 - a12 ** 2
    with np.errstate(divide='ignore', invalid='ignore'):
        bottom = np.where(det != 0, (a22 * b1 - a12 * b2) / det, np.nan)
        top = np.where(det != 0, (a11 * b2 - a12 * b1) / det, np.nan)
    residual = np.sum(response ** 2) - (bottom * b1 + top * b2)
    residual = np.where(np.isfinite(residual), residual, np.inf)

    i, j = np.unravel_index(np.argmin(residual), residual.shape)
    ss_total = float(np.sum((response - response.mean()) ** 2))
    r2 = 1.0 - float(residual[i, j]) / ss_total if ss_total > 0 else 0.0
    return dict(bottom=float(bottom[i, j]), top=float(top[i, j]),
                ec50=float(10.0 ** log_ec50[i]), hill=float(hill[j]), r2=r2)


def curve(params, dose):
    return params['bottom'] + (params['top'] - params['bottom']) / (
        1.0 + (params['ec50'] / dose) ** params['hill'])


W = _opt('_fig_width', 9.0)
H = _opt('_fig_height', 6.5)
fig, ax = plt.subplots(figsize=(W, H), layout='constrained')

PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC']
groups = list(pd.unique(df[COLS['group']]))
rng = np.random.default_rng(11)
summary = []

all_doses = df[COLS['dose']].to_numpy(float)
grid = np.geomspace(all_doses.min() * 0.6, all_doses.max() * 1.6, 300)

for i, group in enumerate(groups):
    sub = df[df[COLS['group']] == group]
    dose = sub[COLS['dose']].to_numpy(float)
    response = sub[COLS['response']].to_numpy(float)
    color = PALETTE[i % len(PALETTE)]

    params = fit_4pl(dose, response)
    ax.plot(grid, curve(params, grid), color=color, linewidth=2.0, zorder=4,
            label=f"{group}  EC50 {params['ec50']:.2f} {DOSE_UNITS}")

    # Replicate means with s.d. bars, plus the raw replicates behind them.
    stat = sub.groupby(COLS['dose'])[COLS['response']].agg(['mean', 'std'])
    ax.errorbar(stat.index.values, stat['mean'], yerr=stat['std'].fillna(0),
                fmt='o', color=color, markersize=5.5, capsize=3,
                elinewidth=1.0, zorder=5, markeredgecolor='white',
                markeredgewidth=0.8)
    ax.scatter(dose, response, s=9, color=color, alpha=0.35, linewidths=0,
               zorder=3)

    # Bootstrap over replicates for the band and the EC50 interval.
    curves, ec50s = [], []
    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, dose.size, dose.size)
        try:
            boot = fit_4pl(dose[idx], response[idx])
        except Exception:
            continue
        curves.append(curve(boot, grid))
        ec50s.append(boot['ec50'])
    if curves:
        curves = np.array(curves)
        ax.fill_between(grid, np.percentile(curves, 2.5, axis=0),
                        np.percentile(curves, 97.5, axis=0), color=color,
                        alpha=0.13, linewidth=0, zorder=2)
        ci = (np.percentile(ec50s, 2.5), np.percentile(ec50s, 97.5))
    else:
        ci = (np.nan, np.nan)

    # Drop line at the EC50 so the reader can read it off the axis.
    half = (params['bottom'] + params['top']) / 2
    ax.plot([params['ec50'], params['ec50']], [ax.get_ylim()[0], half],
            color=color, linewidth=0.9, linestyle=':', zorder=3)
    ax.scatter([params['ec50']], [half], s=52, marker='v', color=color,
               zorder=6, edgecolors='white', linewidths=1.0)

    summary.append(f"{group:<14s} {params['ec50']:>7.2f}  "
                   f"[{ci[0]:.2f}, {ci[1]:.2f}]  {params['hill']:>5.2f}  "
                   f"{params['r2']:.3f}")

ax.set_xscale('log')
ax.set_xlabel(f'Concentration ({DOSE_UNITS}, log scale)')
ax.set_ylabel(RESPONSE_LABEL)
ax.set_title('Dose-response, 4-parameter logistic fit', fontsize=10.5,
             loc='left', fontweight='bold')
ax.legend(fontsize=8.5, loc='upper left', framealpha=0.93)

n_rep = df[COLS['replicate']].nunique() if COLS['replicate'] in df.columns else 1
header = f"{'compound':<14s} {'EC50':>7s}  {'95% CI':^14s}  {'hill':>5s}  R²"
ax.text(0.995, 0.02, header + '\n' + '\n'.join(summary),
        transform=ax.transAxes, ha='right', va='bottom', fontsize=7.2,
        family='monospace',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor='#CCCCCC', alpha=0.95))
ax.text(0.0, -0.105, f'Points are means of {n_rep} replicates with s.d.; '
                     f'bands are {N_BOOTSTRAP}-sample bootstrap 95% intervals',
        transform=ax.transAxes, fontsize=7.5, color='#777777')
