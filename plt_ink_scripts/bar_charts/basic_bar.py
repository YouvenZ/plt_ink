"""
Basic Bar Chart
Vertical bar chart for comparing categories.
Demo usecase: average monthly rainfall by season from climate data.
"""

import numpy as np

try:
    categories = list(x_data)
    values     = np.asarray(y_data, dtype=float)
except NameError:
    # Sample: average monthly rainfall (mm) — seasonal aggregation
    categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    rng = np.random.default_rng(5)
    # Seasonal rainfall pattern (northern hemisphere)
    base = [62, 48, 52, 55, 58, 45, 38, 42, 55, 70, 72, 65]
    values = np.array([b + rng.normal(0, 5) for b in base])

cmap = get_cmap(_colormap)
colors = [cmap(v / max(values)) for v in values]

bars = ax.bar(categories, values, color=colors, edgecolor='white',
              linewidth=0.6, alpha=0.88)

# Value labels on top of bars
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
            f'{val:.0f}', ha='center', va='bottom', fontsize=8, color='#333333')

ax.set_title('Monthly Rainfall (mm)', fontsize=13, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('Rainfall (mm)')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
