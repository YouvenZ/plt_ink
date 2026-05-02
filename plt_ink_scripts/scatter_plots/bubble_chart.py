"""
Bubble Chart
Scatter plot where marker size encodes a third variable (z).
"""

import numpy as np

try:
    x = x_data.astype(float)
    y = y_data.astype(float)
    try:
        z = z_data.astype(float)
    except NameError:
        z = np.abs(x * y) + 1
except NameError:
    rng = np.random.default_rng(7)
    x = rng.uniform(0, 100, 40)
    y = rng.uniform(0, 100, 40)
    z = rng.uniform(50, 1500, 40)

cmap = get_cmap(_colormap)
scatter = ax.scatter(x, y, s=z * 0.15, c=z, cmap=_colormap,
                     alpha=0.7, edgecolors='white', linewidth=0.5)

fig.colorbar(scatter, ax=ax, label='Bubble magnitude')

ax.set_title('Bubble Chart', fontsize=14, fontweight='bold')
ax.set_xlabel('X Variable')
ax.set_ylabel('Y Variable')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')
