"""
Publication-Ready Multi-Panel (1×2)
Two side-by-side panels formatted for journal submissions.
"""

import numpy as np

# Publication styling
plt.rcParams.update({
    'font.family':       'serif',
    'font.size':         9,
    'axes.labelsize':    10,
    'axes.titlesize':    10,
    'axes.linewidth':    0.8,
    'xtick.direction':   'in',
    'ytick.direction':   'in',
    'xtick.major.size':  3.5,
    'ytick.major.size':  3.5,
})

# Double-column width ~ 7.0 in
plt.close()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.6), constrained_layout=True)

try:
    x  = x_data.astype(float)
    y1 = y_data.astype(float)
    try:
        y2 = y2_data.astype(float)
    except NameError:
        y2 = y1[::-1]
except NameError:
    x  = np.linspace(0, 4, 200)
    y1 = np.exp(-x) * np.cos(2 * np.pi * x)
    y2 = 1 - np.exp(-x)

for a in (ax1, ax2):
    a.spines['top'].set_visible(False)
    a.spines['right'].set_visible(False)
    if _show_grid:
        a.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

ax1.plot(x, y1, linewidth=1.5, color='black')
ax1.set_xlabel('Variable (units)')
ax1.set_ylabel('Response (units)')
ax1.set_title('(a) Panel A', loc='left')

ax2.plot(x, y2, linewidth=1.5, color='#444444', linestyle='--')
ax2.set_xlabel('Variable (units)')
ax2.set_title('(b) Panel B', loc='left')
