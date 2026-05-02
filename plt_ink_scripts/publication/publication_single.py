"""
Publication-Ready Single Panel
High-quality single figure formatted for journals: clean typography,
tight layout, minimal chrome.
"""

import numpy as np

try:
    x = x_data.astype(float)
    y = y_data.astype(float)
except NameError:
    x = np.linspace(0, 2 * np.pi, 200)
    y = np.sin(x) * np.exp(-x / 8)

# Publication styling overrides
plt.rcParams.update({
    'font.family':       'serif',
    'font.size':         10,
    'axes.labelsize':    11,
    'axes.titlesize':    12,
    'axes.linewidth':    1.0,
    'xtick.direction':   'in',
    'ytick.direction':   'in',
    'xtick.major.size':  4,
    'ytick.major.size':  4,
})

# Re-create figure at publication size (single column ~ 3.5 in wide)
plt.close()
fig, ax = plt.subplots(figsize=(3.5, 2.6))

ax.plot(x, y, linewidth=1.5, color='black')
ax.set_xlabel('Variable (units)')
ax.set_ylabel('Response (units)')
ax.set_title('Single-Panel Figure', pad=6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
