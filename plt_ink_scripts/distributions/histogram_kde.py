"""
Histogram + KDE Overlay
Histogram with a smooth density curve on top.
"""

import numpy as np
from scipy.stats import gaussian_kde

try:
    data = x_data.astype(float)
except NameError:
    rng  = np.random.default_rng(6)
    data = rng.normal(5, 1.5, 500)

cmap = get_cmap(_colormap)

# Histogram (density normalised so KDE overlaps cleanly)
ax.hist(data, bins=30, density=True, color=cmap(0.5),
        edgecolor='white', linewidth=0.5, alpha=0.6, label='Histogram')

# KDE overlay
kde = gaussian_kde(data)
xs  = np.linspace(data.min() - 1, data.max() + 1, 300)
ax.plot(xs, kde(xs), linewidth=2.5, color=cmap(0.15), label='KDE')

ax.set_title('Histogram with KDE', fontsize=14, fontweight='bold')
ax.set_xlabel('Value')
ax.set_ylabel('Density')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
