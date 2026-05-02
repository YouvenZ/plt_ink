"""
Subplot Comparison
Side-by-side plots sharing the same axis for direct comparison.
"""

import numpy as np

try:
    if hasattr(y_data[0], '__len__'):
        series = [np.asarray(s) for s in y_data]
        x_arr  = np.asarray(x_data)
    else:
        series = [np.asarray(y_data)]
        x_arr  = np.asarray(x_data) if 'x_data' in dir() else np.arange(len(series[0]))
    n_panels = min(len(series), 4)
except NameError:
    n_panels = 3
    x_arr = np.linspace(0, 10, 150)
    series = [np.sin(x_arr), np.cos(x_arr), np.sin(2 * x_arr)]

# Override with fresh figure sized for the comparison
fig, axes = plt.subplots(1, n_panels, figsize=(_fig_width, _fig_height),
                         sharey=True, constrained_layout=True)
if n_panels == 1:
    axes = [axes]

cmap = get_cmap(_colormap)

for i, (a, s) in enumerate(zip(axes, series[:n_panels])):
    color = cmap(i / max(n_panels - 1, 1))
    a.plot(x_arr, s, linewidth=2, color=color)
    a.set_title(f'Series {i+1}', fontweight='bold')
    a.set_xlabel('X')
    if i == 0:
        a.set_ylabel('Value')
    if _show_grid:
        a.grid(True, alpha=0.3, linestyle='--')
