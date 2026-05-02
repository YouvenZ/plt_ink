"""
2×2 Subplot Panel
Four related plots in a 2×2 grid.
"""

import numpy as np

rng = np.random.default_rng(30)
x   = np.linspace(0, 10, 200)

# Override auto-created fig/axes with a fresh 2×2 grid
fig, axes = plt.subplots(2, 2, figsize=(_fig_width, _fig_height),
                         constrained_layout=True)

cmap = get_cmap(_colormap)

# Panel 1 — Line plot
axes[0, 0].plot(x, np.sin(x), color=cmap(0.8), linewidth=2)
axes[0, 0].set_title('Sine Wave', fontweight='bold')

# Panel 2 — Scatter
xs = rng.uniform(0, 10, 80)
ys = np.sin(xs) + rng.normal(0, 0.3, 80)
axes[0, 1].scatter(xs, ys, color=cmap(0.5), alpha=0.7, s=40)
axes[0, 1].set_title('Scatter', fontweight='bold')

# Panel 3 — Bar
categories = ['A', 'B', 'C', 'D']
values     = rng.uniform(2, 10, 4)
axes[1, 0].bar(categories, values, color=cmap(0.3), alpha=0.85)
axes[1, 0].set_title('Bar Chart', fontweight='bold')

# Panel 4 — Histogram
data4 = rng.normal(5, 1.5, 300)
axes[1, 1].hist(data4, bins=25, color=cmap(0.65), edgecolor='white', alpha=0.8)
axes[1, 1].set_title('Histogram', fontweight='bold')

for a in axes.flat:
    if _show_grid:
        a.grid(True, alpha=0.3, linestyle='--')
