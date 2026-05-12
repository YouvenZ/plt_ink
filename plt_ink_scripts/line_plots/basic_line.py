"""
Basic Line Plot
Simple line plot with markers - ideal for time series or continuous data.
Demo usecase: atmospheric CO₂ concentration trend 2014-2024 (Keeling-curve style).
"""

import numpy as np

try:
    x = np.asarray(x_data, dtype=float)
    y = np.asarray(y_data, dtype=float)
    x_label, y_label = 'X Variable', 'Y Variable'
except NameError:
    # Synthetic monthly CO2 data with Keeling-curve seasonal oscillation
    rng = np.random.default_rng(12)
    months = np.arange(121)
    x = months
    y = (398 + 0.22 * months                         # long-term rise
         + 3 * np.sin(months * np.pi / 6)             # seasonal cycle
         + rng.normal(0, 0.4, 121))                   # measurement noise
    x_label = 'Months since Jan 2014'
    y_label = 'CO₂ (ppm)'

ax.plot(x, y, linewidth=2, color='#C0392B', label='Measured CO₂')

# Trend line
m, b = np.polyfit(x, y, 1)
ax.plot(x, m * x + b, 'k--', linewidth=1, alpha=0.6,
        label=f'Trend (+{m * 12:.2f} ppm/yr)')

ax.set_title('Atmospheric CO₂ Concentration Trend', fontsize=13, fontweight='bold')
ax.set_xlabel(x_label)
ax.set_ylabel(y_label)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position, framealpha=0.9)
