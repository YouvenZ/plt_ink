"""
Vector Field (Quiver Plot)
Arrows showing direction and magnitude across a 2-D grid.
"""

import numpy as np

try:
    # Expect U and V component arrays (2-D)
    U = np.asarray(x_data, dtype=float)
    V = np.asarray(y_data, dtype=float)
    n = U.shape[0]
    Xg, Yg = np.meshgrid(np.arange(U.shape[1]), np.arange(n))
except (NameError, AttributeError):
    n = 20
    Xg, Yg = np.meshgrid(np.linspace(-2, 2, n), np.linspace(-2, 2, n))
    U = -Yg
    V =  Xg

speed = np.sqrt(U**2 + V**2)
speed_norm = speed / speed.max() if speed.max() > 0 else speed

q = ax.quiver(Xg, Yg, U, V, speed_norm, cmap=_colormap,
              scale=25, width=0.003, alpha=0.9)
fig.colorbar(q, ax=ax, label='Relative speed')

ax.set_title('Vector Field', fontsize=14, fontweight='bold')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_aspect('equal')

if _show_grid:
    ax.grid(True, alpha=0.2, linestyle='--')
