"""
Error Bar Plot (categorical)
Bar chart with error bars — shows mean ± std dev per category.
"""

import numpy as np

try:
    if hasattr(y_data[0], '__len__'):
        data_groups = [np.asarray(g, dtype=float) for g in y_data]
        means  = np.array([g.mean() for g in data_groups])
        errors = np.array([g.std()  for g in data_groups])
    else:
        means  = np.asarray(y_data, dtype=float)
        errors = np.abs(means) * 0.1 + 0.05
    try:
        categories = list(x_data)
    except NameError:
        categories = [f'Cat {i+1}' for i in range(len(means))]
except NameError:
    rng = np.random.default_rng(2)
    categories = ['A', 'B', 'C', 'D', 'E']
    raw = [rng.normal(m, 0.5, 40) for m in [3, 5, 4, 7, 6]]
    means  = np.array([g.mean() for g in raw])
    errors = np.array([g.std()  for g in raw])

cmap   = get_cmap(_colormap)
colors = [cmap(i / max(len(means) - 1, 1)) for i in range(len(means))]
x      = np.arange(len(categories))

ax.bar(x, means, color=colors, alpha=0.8, edgecolor='white', zorder=2)
ax.errorbar(x, means, yerr=errors, fmt='none', color='black',
            capsize=5, capthick=1.5, elinewidth=1.5, zorder=3)

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_title('Mean ± Std Dev', fontsize=14, fontweight='bold')
ax.set_xlabel('Category')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y', zorder=1)
