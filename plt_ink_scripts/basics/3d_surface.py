"""
3D Surface Plot
Three-dimensional surface — rendered with a 2-D projection-friendly backend.
"""

import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (registers 3d projection)

try:
    Z = np.asarray(data, dtype=float)
    n_r, n_c = Z.shape
    X, Y = np.meshgrid(np.linspace(0, 1, n_c), np.linspace(0, 1, n_r))
except NameError:
    x_1d = np.linspace(-3, 3, 80)
    y_1d = np.linspace(-3, 3, 80)
    X, Y = np.meshgrid(x_1d, y_1d)
    Z    = np.sin(np.sqrt(X**2 + Y**2))

# Replace the 2-D axis with a 3-D one
ax.remove()
ax3d = fig.add_subplot(111, projection='3d')

surf = ax3d.plot_surface(X, Y, Z, cmap=_colormap, alpha=0.9,
                          edgecolor='none', linewidth=0)
fig.colorbar(surf, ax=ax3d, shrink=0.5, pad=0.1, label='Value')

ax3d.set_title('3D Surface', fontsize=14, fontweight='bold')
ax3d.set_xlabel('X')
ax3d.set_ylabel('Y')
ax3d.set_zlabel('Z')
ax3d.view_init(elev=25, azim=-60)
