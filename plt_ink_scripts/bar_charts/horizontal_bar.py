"""
Horizontal Bar Chart
Horizontal bars — ideal for long category labels or ranked comparisons.
"""

import numpy as np

try:
    values     = np.asarray(y_data, dtype=float)
    categories = list(x_data)
except NameError:
    categories = ['Category A', 'Category B', 'Category C',
                  'Category D', 'Category E', 'Category F']
    values     = np.array([42, 78, 55, 91, 34, 63])

# Sort by value for a ranked look
order      = np.argsort(values)
values     = values[order]
categories = [categories[i] for i in order]

cmap   = get_cmap(_colormap)
colors = [cmap(v / values.max()) for v in values]

y_pos = np.arange(len(categories))
ax.barh(y_pos, values, color=colors, alpha=0.85, edgecolor='white')
ax.set_yticks(y_pos)
ax.set_yticklabels(categories)

ax.set_title('Horizontal Bar Chart', fontsize=14, fontweight='bold')
ax.set_xlabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
