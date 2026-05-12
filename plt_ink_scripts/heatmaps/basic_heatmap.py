"""
Basic Heatmap
2-D colour map for grid/matrix data.
Demo usecase: mean temperature by year (rows) × month (columns) — climate calendar view.
"""

import numpy as np

try:
    # Expect 2-D numpy array or pandas DataFrame
    import pandas as _pd
    matrix = data.values if isinstance(data, _pd.DataFrame) else np.asarray(data)
    row_labels = list(data.index)   if isinstance(data, _pd.DataFrame) else [f'Row {i+1}' for i in range(matrix.shape[0])]
    col_labels = list(data.columns) if isinstance(data, _pd.DataFrame) else [f'Col {j+1}' for j in range(matrix.shape[1])]
    title = 'Heatmap'
except NameError:
    # Climate calendar: 10 years × 12 months mean temperature
    rng = np.random.default_rng(11)
    years  = list(range(2014, 2024))
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    m_idx  = np.arange(1, 13)
    matrix = np.array([
        [round(12 + 10 * np.sin((m - 3) * np.pi / 6) + 0.02 * (yr - 2014) * 12
               + rng.normal(0, 0.7), 1)
         for m in m_idx]
        for yr in years
    ])
    row_labels = [str(y) for y in years]
    col_labels = months
    title = 'Monthly Mean Temperature (°C) — Climate Calendar'

im = ax.imshow(matrix, cmap='RdYlBu_r', aspect='auto')
cbar = fig.colorbar(im, ax=ax, label='°C', shrink=0.8)

ax.set_xticks(range(len(col_labels)))
ax.set_yticks(range(len(row_labels)))
ax.set_xticklabels(col_labels, rotation=0, fontsize=9)
ax.set_yticklabels(row_labels, fontsize=9)

# Annotate cells
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        val = matrix[i, j]
        color = 'white' if val < matrix.mean() - 3 or val > matrix.mean() + 7 else '#333333'
        ax.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=7, color=color)

ax.set_title(title, fontsize=12, fontweight='bold')

