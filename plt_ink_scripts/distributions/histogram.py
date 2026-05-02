"""
Histogram
Frequency distribution of a single variable with optional KDE overlay.
"""

import numpy as np

try:
    data = x_data.astype(float)
except NameError:
    rng  = np.random.default_rng(3)
    data = np.concatenate([rng.normal(0, 1, 300), rng.normal(4, 0.8, 200)])

cmap = get_cmap(_colormap)

n, bins, patches = ax.hist(data, bins=30, color=cmap(0.55),
                           edgecolor='white', linewidth=0.5, alpha=0.8)

ax.set_title('Histogram', fontsize=14, fontweight='bold')
ax.set_xlabel('Value')
ax.set_ylabel('Frequency')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
