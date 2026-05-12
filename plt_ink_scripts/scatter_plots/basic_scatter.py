"""
Basic Scatter Plot
Relationship between two continuous variables with optional regression line.
Demo usecase: temperature vs. solar radiation from monthly climate data.
"""

import numpy as np

try:
    x = np.asarray(x_data, dtype=float)
    y = np.asarray(y_data, dtype=float)
    x_label = columns[0] if 'columns' in dir() and columns else 'X Variable'
    y_label = columns[1] if 'columns' in dir() and len(columns) > 1 else 'Y Variable'
except NameError:
    # Sample: mean temperature vs solar radiation (seasonal pattern)
    rng = np.random.default_rng(7)
    months = np.arange(1, 13)
    x = 12 + 10 * np.sin((months - 3) * np.pi / 6) + rng.normal(0, 0.5, 12)
    y = 200 + 180 * np.sin((months - 3) * np.pi / 6) + rng.normal(0, 8, 12)
    x_label = 'Mean Temperature (°C)'
    y_label = 'Solar Radiation (W/m²)'

# Scatter
sc = ax.scatter(x, y, s=60, alpha=0.8, zorder=3,
                c=np.arange(len(x)), cmap=_colormap, edgecolors='white', linewidths=0.5)

# Linear regression line
if len(x) > 2:
    m, b = np.polyfit(x, y, 1)
    x_fit = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_fit, m * x_fit + b, 'k--', linewidth=1.2, alpha=0.6, label=f'y = {m:.2f}x + {b:.1f}')
    r = np.corrcoef(x, y)[0, 1]
    ax.text(0.05, 0.92, f'r = {r:.3f}', transform=ax.transAxes,
            fontsize=9, color='#333333')

ax.set_xlabel(x_label)
ax.set_ylabel(y_label)
ax.set_title('Scatter: Temperature vs Solar Radiation', fontsize=13, fontweight='bold')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
