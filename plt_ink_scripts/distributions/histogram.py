"""
Histogram
Frequency distribution of a single variable with optional KDE overlay.
Demo usecase: distribution of monthly mean temperatures (bimodal: winter/summer).
"""

import numpy as np

try:
    data = x_data.astype(float)
    data_label = 'Value'
except NameError:
    rng = np.random.default_rng(3)
    # Bimodal: winter (low) + summer (high) temperatures
    data = np.concatenate([
        rng.normal(6,  3.5, 180),   # winter/spring months
        rng.normal(20, 3.0, 180),   # summer/autumn months
    ])
    data_label = 'Mean Temperature (°C)'

cmap = get_cmap(_colormap)

n, bins, patches = ax.hist(data, bins=30, color=cmap(0.55),
                           edgecolor='white', linewidth=0.5, alpha=0.8)

# Colour bars by value (cold→warm gradient)
norm = plt.Normalize(bins.min(), bins.max())
for patch, left in zip(patches, bins[:-1]):
    patch.set_facecolor(cmap(norm(left)))

# KDE overlay
try:
    from scipy.stats import gaussian_kde as _kde
    kde = _kde(data)
    x_kde = np.linspace(data.min(), data.max(), 200)
    scale = len(data) * (bins[1] - bins[0])
    ax.plot(x_kde, kde(x_kde) * scale, 'k-', linewidth=1.8, label='KDE')
except ImportError:
    pass

ax.set_title('Temperature Distribution (bimodal — seasonal pattern)',
             fontsize=13, fontweight='bold')
ax.set_xlabel(data_label)
ax.set_ylabel('Frequency')

if _show_legend:
    ax.legend(loc=_legend_position)

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

