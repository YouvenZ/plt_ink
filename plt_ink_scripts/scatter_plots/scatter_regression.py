"""
Scatter Plot with Linear Regression
Scatter plot overlaid with a best-fit regression line and R² annotation.
"""

import numpy as np

try:
    x = x_data.astype(float)
    y = y_data.astype(float)
except NameError:
    rng = np.random.default_rng(42)
    x = rng.uniform(0, 10, 60)
    y = 2.5 * x + 1 + rng.normal(0, 3, 60)

# Regression
coeffs = np.polyfit(x, y, 1)
x_line = np.array([x.min(), x.max()])
y_line = np.polyval(coeffs, x_line)

# R²
y_hat  = np.polyval(coeffs, x)
ss_res = np.sum((y - y_hat) ** 2)
ss_tot = np.sum((y - y.mean()) ** 2)
r2     = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')

cmap = get_cmap(_colormap)

ax.scatter(x, y, alpha=0.7, color=cmap(0.6), edgecolors='white',
           linewidth=0.5, s=60, label='Data')
ax.plot(x_line, y_line, '--', color=cmap(0.2), linewidth=2,
        label=f'Fit  (R²={r2:.3f})')

ax.set_title('Scatter with Regression', fontsize=14, fontweight='bold')
ax.set_xlabel('X Variable')
ax.set_ylabel('Y Variable')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
