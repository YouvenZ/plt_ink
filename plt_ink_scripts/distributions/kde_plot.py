"""
KDE Plot (Kernel Density Estimate)
Smooth probability density estimate for one or more distributions.
"""

import numpy as np
from scipy.stats import gaussian_kde

try:
    if hasattr(y_data, '__len__') and hasattr(y_data[0], '__len__'):
        series = [np.asarray(s, dtype=float) for s in y_data]
    else:
        series = [np.asarray(y_data if 'y_data' in dir() else x_data, dtype=float)]
    labels = [f'Series {i+1}' for i in range(len(series))]
except NameError:
    rng    = np.random.default_rng(5)
    series = [rng.normal(0, 1, 400), rng.normal(2, 0.7, 400)]
    labels = ['Group A', 'Group B']

cmap = get_cmap(_colormap)

for i, (data, label) in enumerate(zip(series, labels)):
    color = cmap(i / max(len(series) - 1, 1))
    kde   = gaussian_kde(data)
    xs    = np.linspace(data.min() - 0.5, data.max() + 0.5, 300)
    ax.plot(xs, kde(xs), linewidth=2.5, color=color, label=label)
    ax.fill_between(xs, kde(xs), alpha=0.15, color=color)

ax.set_title('Kernel Density Estimate', fontsize=14, fontweight='bold')
ax.set_xlabel('Value')
ax.set_ylabel('Density')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
