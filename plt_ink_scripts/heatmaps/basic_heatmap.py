"""
Basic Heatmap
2-D colour map for grid/matrix data.
"""

import numpy as np

try:
    # Expect 2-D numpy array or pandas DataFrame
    import pandas as _pd
    matrix = data.values if isinstance(data, _pd.DataFrame) else np.asarray(data)
    row_labels = list(data.index)    if isinstance(data, _pd.DataFrame) else [f'Row {i+1}' for i in range(matrix.shape[0])]
    col_labels = list(data.columns)  if isinstance(data, _pd.DataFrame) else [f'Col {j+1}' for j in range(matrix.shape[1])]
except NameError:
    rng = np.random.default_rng(11)
    matrix = rng.uniform(0, 100, (8, 10))
    row_labels = [f'Row {i+1}' for i in range(8)]
    col_labels = [f'Col {j+1}' for j in range(10)]

im = ax.imshow(matrix, cmap=_colormap, aspect='auto')
fig.colorbar(im, ax=ax, label='Value')

ax.set_xticks(range(len(col_labels)))
ax.set_yticks(range(len(row_labels)))
ax.set_xticklabels(col_labels, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(row_labels, fontsize=9)

ax.set_title('Heatmap', fontsize=14, fontweight='bold')
