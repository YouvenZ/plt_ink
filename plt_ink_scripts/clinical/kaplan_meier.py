"""
Kaplan-Meier Survival Curves
Step curves with censoring ticks, 95% confidence bands, a numbers-at-risk
table and a log-rank test. Estimator, variance and test are implemented in
numpy — no lifelines or scipy needed.
requires_data: true
data_columns: time, event, group
sample_data: survival.csv
tags: clinical, survival, kaplan-meier, biostatistics, oncology
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Data ─────────────────────────────────────────────────────────────────────
COLS = dict(time='time', event='event', group='group')
SAMPLE = 'survival.csv'
TIME_LABEL = 'Months since randomisation'
EVENT_LABEL = 'Progression-free survival'
RISK_TICKS = 7             # number of columns in the numbers-at-risk table
SHOW_CI = True


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


def kaplan_meier(time, event):
    """Survival estimate with Greenwood standard errors.

    Returns times, survival, lower CI, upper CI, and the censoring times.
    """
    order = np.argsort(time)
    time, event = np.asarray(time)[order], np.asarray(event)[order]
    unique = np.unique(time[event == 1])
    surv, var_sum = 1.0, 0.0
    ts, ss, lo, hi = [0.0], [1.0], [1.0], [1.0]
    for t in unique:
        at_risk = np.sum(time >= t)
        deaths = np.sum((time == t) & (event == 1))
        if at_risk == 0:
            continue
        surv *= 1.0 - deaths / at_risk
        # Greenwood's formula, accumulated on the log scale.
        if at_risk > deaths:
            var_sum += deaths / (at_risk * (at_risk - deaths))
        se = surv * np.sqrt(var_sum)
        ts.append(float(t))
        ss.append(surv)
        # Log-log transform keeps the band inside [0, 1].
        if 0 < surv < 1 and var_sum > 0:
            c = 1.96 * np.sqrt(var_sum) / abs(np.log(surv))
            lo.append(surv ** np.exp(c))
            hi.append(surv ** np.exp(-c))
        else:
            lo.append(max(surv - 1.96 * se, 0.0))
            hi.append(min(surv + 1.96 * se, 1.0))
    return (np.array(ts), np.array(ss), np.array(lo), np.array(hi),
            time[event == 0])


def logrank(time, event, group):
    """Two-or-more-sample log-rank chi-square and its degrees of freedom."""
    groups = list(pd.unique(group))
    times = np.unique(time[event == 1])
    observed = np.zeros(len(groups))
    expected = np.zeros(len(groups))
    variance = np.zeros(len(groups))
    for t in times:
        at_risk_total = np.sum(time >= t)
        deaths_total = np.sum((time == t) & (event == 1))
        if at_risk_total <= 1:
            continue
        for i, g in enumerate(groups):
            in_group = group == g
            at_risk = np.sum((time >= t) & in_group)
            observed[i] += np.sum((time == t) & (event == 1) & in_group)
            share = at_risk / at_risk_total
            expected[i] += deaths_total * share
            variance[i] += (deaths_total * share * (1 - share)
                            * (at_risk_total - deaths_total)
                            / (at_risk_total - 1))
    with np.errstate(divide='ignore', invalid='ignore'):
        chi2 = float(np.nansum((observed - expected) ** 2
                               / np.where(variance > 0, variance, np.nan)))
    return chi2, len(groups) - 1, observed, expected


def chi2_sf(x, k):
    """Upper tail of the chi-square distribution (series + continued fraction).

    Implemented directly so the template has no scipy dependency.
    """
    if x <= 0:
        return 1.0
    a, xx = k / 2.0, x / 2.0
    # Lanczos log-gamma.
    g = [676.5203681218851, -1259.1392167224028, 771.32342877765313,
         -176.61502916214059, 12.507343278686905, -0.13857109526572012,
         9.9843695780195716e-6, 1.5056327351493116e-7]

    def lgamma(z):
        if z < 0.5:
            return np.log(np.pi / abs(np.sin(np.pi * z))) - lgamma(1 - z)
        z -= 1
        s = 0.99999999999980993 + sum(c / (z + i + 1) for i, c in enumerate(g))
        t = z + len(g) - 0.5
        return 0.5 * np.log(2 * np.pi) + (z + 0.5) * np.log(t) - t + np.log(s)

    if xx < a + 1:
        # Lower incomplete gamma by series expansion.
        term, total, n = 1.0 / a, 1.0 / a, 0
        while abs(term) > abs(total) * 1e-14 and n < 10000:
            n += 1
            term *= xx / (a + n)
            total += term
        return 1.0 - total * np.exp(-xx + a * np.log(xx) - lgamma(a))
    # Upper incomplete gamma by the Lentz continued fraction.
    tiny = 1e-300
    b, c, d = xx + 1 - a, 1 / tiny, 1 / (xx + 1 - a)
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = d if abs(d) > tiny else tiny
        c = b + an / c
        c = c if abs(c) > tiny else tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-14:
            break
    return float(np.exp(-xx + a * np.log(xx) - lgamma(a)) * h)


# ── Figure ───────────────────────────────────────────────────────────────────
W = _opt('_fig_width', 8.5)
H = _opt('_fig_height', 7.5)
fig = plt.figure(figsize=(W, H), layout='constrained')
gs = fig.add_gridspec(2, 1, height_ratios=[3.4, 1.0], hspace=0.06)
ax = fig.add_subplot(gs[0])
ax_risk = fig.add_subplot(gs[1], sharex=ax)

PALETTE = ['#0173B2', '#D55E00', '#029E73', '#DE8F05', '#CC78BC']
groups = list(pd.unique(df[COLS['group']]))
t_max = float(df[COLS['time']].max())
grid = np.linspace(0, t_max, RISK_TICKS)
medians = {}

for i, group in enumerate(groups):
    sub = df[df[COLS['group']] == group]
    time = sub[COLS['time']].to_numpy(float)
    event = sub[COLS['event']].to_numpy(int)
    color = PALETTE[i % len(PALETTE)]

    ts, ss, lo, hi, censored = kaplan_meier(time, event)
    ax.step(np.append(ts, t_max), np.append(ss, ss[-1]), where='post',
            color=color, linewidth=2.0, zorder=4,
            label=f'{group}  (n={len(sub)}, {int(event.sum())} events)')
    if SHOW_CI:
        ax.fill_between(np.append(ts, t_max), np.append(lo, lo[-1]),
                        np.append(hi, hi[-1]), step='post', color=color,
                        alpha=0.14, linewidth=0)

    # Censoring ticks sit on the curve at the height they were censored at.
    if censored.size:
        # Step lookup, not interpolation — survival is constant between events.
        heights = ss[np.clip(np.searchsorted(ts, censored, 'right') - 1, 0, None)]
        ax.plot(censored, heights, '|', color=color, markersize=6,
                markeredgewidth=1.1, zorder=5)

    below = np.flatnonzero(ss <= 0.5)
    medians[group] = float(ts[below[0]]) if below.size else None

# Median survival: the standard read-off, drawn rather than left to the eye.
if any(m is not None for m in medians.values()):
    ax.axhline(0.5, color='#999999', linewidth=0.8, linestyle=':', zorder=2)
    for i, (group, median) in enumerate(medians.items()):
        if median is None:
            continue
        ax.plot([median, median], [0, 0.5], color=PALETTE[i % len(PALETTE)],
                linewidth=0.8, linestyle=':', zorder=2)

chi2, dof, observed, expected = logrank(df[COLS['time']].to_numpy(float),
                                        df[COLS['event']].to_numpy(int),
                                        df[COLS['group']].to_numpy())
p = chi2_sf(chi2, dof)
p_text = 'p < 0.001' if p < 0.001 else f'p = {p:.3f}'

# Hazard ratio from the log-rank O/E, valid for two groups.
hr_text = ''
if len(groups) == 2 and expected.min() > 0:
    hr = (observed[1] / expected[1]) / (observed[0] / expected[0])
    se = np.sqrt(1 / expected[0] + 1 / expected[1])
    hr_text = (f'\nHR {hr:.2f} (95% CI {hr * np.exp(-1.96 * se):.2f}-'
               f'{hr * np.exp(1.96 * se):.2f})')

median_text = '\n'.join(
    f'Median {g}: {m:.1f}' if m is not None else f'Median {g}: not reached'
    for g, m in medians.items())
ax.text(0.985, 0.97,
        f'Log-rank $\\chi^2$ = {chi2:.2f}, {p_text}{hr_text}\n{median_text}',
        transform=ax.transAxes, ha='right', va='top', fontsize=8,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor='#CCCCCC', alpha=0.95))

ax.set_ylim(0, 1.02)
ax.set_xlim(0, t_max)
ax.set_ylabel(f'{EVENT_LABEL} probability')
ax.tick_params(labelbottom=False)
ax.legend(fontsize=8.5, loc='lower left', framealpha=0.93)
ax.set_title('Kaplan-Meier estimate', fontsize=10.5, loc='left',
             fontweight='bold')

# ── Numbers at risk ──────────────────────────────────────────────────────────
for i, group in enumerate(groups):
    sub = df[df[COLS['group']] == group]
    time = sub[COLS['time']].to_numpy(float)
    counts = [int(np.sum(time >= t)) for t in grid]
    y = len(groups) - 1 - i
    for t, c in zip(grid, counts):
        ax_risk.text(t, y, str(c), ha='center', va='center', fontsize=8,
                     color=PALETTE[i % len(PALETTE)])
    # Far enough left that the arm name clears the count sitting at t = 0.
    ax_risk.text(-0.055, y, group, transform=ax_risk.get_yaxis_transform(),
                 ha='right', va='center', fontsize=8.5,
                 color=PALETTE[i % len(PALETTE)], fontweight='bold')

ax_risk.set_ylim(-0.6, len(groups) - 0.4)
ax_risk.set_yticks([])
ax_risk.set_xticks(grid)
ax_risk.set_xlabel(TIME_LABEL)
ax_risk.set_title('Number at risk', fontsize=9, loc='left', color='#444444')
ax_risk.grid(False)
for spine in ax_risk.spines.values():
    spine.set_visible(False)
