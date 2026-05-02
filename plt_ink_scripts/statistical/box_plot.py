"""
Box Plot
Shows distribution summary (median, quartiles, outliers) per group.
"""

import numpy as np

try:
    if hasattr(y_data[0], '__len__'):
        data_groups = [np.asarray(g) for g in y_data]
    else:
        data_groups = [np.asarray(y_data)]
    try:
        labels = list(x_data)
    except NameError:
        labels = [f'Group {i+1}' for i in range(len(data_groups))]
except NameError:
    rng = np.random.default_rng(0)
    data_groups = [
        rng.normal(0,   1,   80),
        rng.normal(0.5, 1.3, 80),
        rng.normal(1,   0.8, 80),
        rng.normal(2,   1.5, 80),
    ]
    labels = ['Control', 'Low dose', 'Med dose', 'High dose']

cmap   = get_cmap(_colormap)
colors = [cmap(i / max(len(data_groups) - 1, 1)) for i in range(len(data_groups))]

bp = ax.boxplot(data_groups, patch_artist=True, notch=False,
                medianprops=dict(color='black', linewidth=2))

for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_xticklabels(labels)
ax.set_title('Box Plot Comparison', fontsize=14, fontweight='bold')
ax.set_xlabel('Group')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
