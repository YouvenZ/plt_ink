"""
Contour Plot
Filled contour plot for 2-D scalar fields.
"""

import numpy as np

try:
    # Expect a 2-D array or (X, Y, Z) triple
    Z = np.asarray(data)
    n = Z.shape[0]
    x_1d = np.linspace(0, 1, Z.shape[1])
    y_1d = np.linspace(0, 1, n)
    X, Y = np.meshgrid(x_1d, y_1d)
except NameError:
    x_1d = np.linspace(-3, 3, 200)
    y_1d = np.linspace(-3, 3, 200)
    X, Y = np.meshgrid(x_1d, y_1d)
    Z    = np.sin(np.sqrt(X**2 + Y**2))

cf = ax.contourf(X, Y, Z, levels=20, cmap=_colormap)
ax.contour(X, Y, Z, levels=10, colors='white', linewidths=0.4, alpha=0.5)
fig.colorbar(cf, ax=ax, label='Value')

ax.set_title('Contour Plot', fontsize=14, fontweight='bold')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_aspect('equal')
