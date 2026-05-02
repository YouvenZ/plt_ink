"""
Fill Between Lines
Shows the area between two curves, useful for confidence intervals or range data.
"""

try:
    x  = x_data
    y1 = y_data
    try:
        y2 = y2_data
    except NameError:
        import numpy as np
        y2 = y1 * 0.7 - 0.2
except NameError:
    import numpy as np
    x  = np.linspace(0, 4 * np.pi, 200)
    y1 = np.sin(x) + 1.2
    y2 = np.sin(x) * 0.5

cmap = get_cmap(_colormap)
color_main = cmap(0.6)
color_fill = cmap(0.3)

ax.plot(x, y1, linewidth=2, color=color_main, label='Upper bound')
ax.plot(x, y2, linewidth=2, color=cmap(0.15), label='Lower bound')
ax.fill_between(x, y1, y2, alpha=0.3, color=color_fill, label='Range')

ax.set_title('Area Between Curves', fontsize=14, fontweight='bold')
ax.set_xlabel('X Variable')
ax.set_ylabel('Y Variable')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
