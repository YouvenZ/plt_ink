"""
Grouped Bar Chart
Side-by-side bars for comparing multiple categories across groups.
"""

import numpy as np

try:
    # Expect y_data as list of arrays, each array one group
    if hasattr(y_data[0], '__len__'):
        groups = [np.asarray(g) for g in y_data]
    else:
        groups = [np.asarray(y_data)]
    try:
        categories = list(x_data)
    except NameError:
        categories = [f'Cat {i+1}' for i in range(len(groups[0]))]
    group_labels = [f'Group {i+1}' for i in range(len(groups))]
except NameError:
    categories   = ['Q1', 'Q2', 'Q3', 'Q4']
    groups       = [
        np.array([12, 18, 15, 22]),
        np.array([19, 14, 21, 17]),
        np.array([8,  11, 13, 16]),
    ]
    group_labels = ['Product A', 'Product B', 'Product C']

n_groups = len(groups)
n_cats   = len(categories)
x        = np.arange(n_cats)
width    = 0.8 / n_groups

cmap = get_cmap(_colormap)
colors = [cmap(i / max(n_groups - 1, 1)) for i in range(n_groups)]

for i, (vals, label, color) in enumerate(zip(groups, group_labels, colors)):
    offset = (i - n_groups / 2 + 0.5) * width
    ax.bar(x + offset, vals, width * 0.95, label=label, color=color, alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_title('Grouped Bar Chart', fontsize=14, fontweight='bold')
ax.set_xlabel('Category')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
