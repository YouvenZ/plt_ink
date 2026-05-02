"""
Violin Plot
Combines box plot with a kernel density estimate to reveal the full distribution.
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
    rng = np.random.default_rng(1)
    data_groups = [
        rng.normal(0,   1,   120),
        rng.normal(0.8, 1.2, 120),
        rng.normal(1.5, 0.7, 120),
    ]
    labels = ['Method A', 'Method B', 'Method C']

cmap   = get_cmap(_colormap)
colors = [cmap(i / max(len(data_groups) - 1, 1)) for i in range(len(data_groups))]

parts = ax.violinplot(data_groups, showmedians=True, showextrema=True)

for i, body in enumerate(parts['bodies']):
    body.set_facecolor(colors[i])
    body.set_alpha(0.7)
parts['cmedians'].set_color('black')
parts['cmedians'].set_linewidth(2)

ax.set_xticks(range(1, len(labels) + 1))
ax.set_xticklabels(labels)
ax.set_title('Violin Plot Comparison', fontsize=14, fontweight='bold')
ax.set_xlabel('Group')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
