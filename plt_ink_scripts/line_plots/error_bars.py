"""
Line Plot with Error Bars
Displays data trends with uncertainty bands.
"""

try:
    x = x_data
    y = y_data
    try:
        yerr = yerr_data
    except NameError:
        import numpy as np
        yerr = np.abs(y) * 0.1 + 0.05
except NameError:
    import numpy as np
    x = np.linspace(0, 10, 20)
    y = np.sin(x) + np.random.normal(0, 0.1, len(x))
    yerr = np.abs(np.cos(x)) * 0.3 + 0.05

ax.errorbar(x, y, yerr=yerr, fmt='o-', linewidth=2, markersize=6,
            capsize=4, capthick=1.5, elinewidth=1.5,
            color='#2E86AB', ecolor='#555555', label='Data ± error')

ax.set_title('Measurement with Uncertainty', fontsize=14, fontweight='bold')
ax.set_xlabel('X Variable')
ax.set_ylabel('Y Variable')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
