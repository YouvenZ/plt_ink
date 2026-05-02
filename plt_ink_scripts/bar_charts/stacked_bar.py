"""
Stacked Bar Chart
Bars divided into segments to show part-to-whole relationships.
"""

import numpy as np

try:
    if hasattr(y_data[0], '__len__'):
        groups = [np.asarray(g) for g in y_data]
    else:
        groups = [np.asarray(y_data)]
    try:
        categories = list(x_data)
    except NameError:
        categories = [f'Cat {i+1}' for i in range(len(groups[0]))]
    group_labels = [f'Segment {i+1}' for i in range(len(groups))]
except NameError:
    categories   = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    groups       = [
        np.array([10, 12, 9,  14, 11]),
        np.array([6,  8,  10, 7,  9]),
        np.array([4,  5,  6,  5,  7]),
    ]
    group_labels = ['Direct', 'Organic', 'Referral']

x = np.arange(len(categories))
cmap   = get_cmap(_colormap)
bottom = np.zeros(len(categories))

for i, (vals, label) in enumerate(zip(groups, group_labels)):
    color = cmap(i / max(len(groups) - 1, 1))
    ax.bar(x, vals, bottom=bottom, label=label, color=color, alpha=0.85)
    bottom += np.asarray(vals)

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_title('Stacked Bar Chart', fontsize=14, fontweight='bold')
ax.set_xlabel('Category')
ax.set_ylabel('Total Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
