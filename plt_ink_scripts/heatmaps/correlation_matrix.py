"""
Correlation Matrix Heatmap
Heatmap of pairwise correlations for multi-column data.
"""

import numpy as np

try:
    # Expect 'data' (pandas DataFrame) or a 2D numpy array
    import pandas as _pd
    if isinstance(data, _pd.DataFrame):
        corr = data.corr().values
        col_names = list(data.columns)
    else:
        corr = np.corrcoef(data, rowvar=False)
        col_names = [f'Var {i+1}' for i in range(corr.shape[0])]
except NameError:
    rng = np.random.default_rng(10)
    raw = rng.multivariate_normal(
        [0, 0, 0, 0],
        [[1, 0.8, -0.3, 0.1],
         [0.8, 1, 0.2, -0.5],
         [-0.3, 0.2, 1, 0.6],
         [0.1, -0.5, 0.6, 1]],
        200
    )
    corr      = np.corrcoef(raw, rowvar=False)
    col_names = ['Feature A', 'Feature B', 'Feature C', 'Feature D']

im = ax.imshow(corr, cmap='RdYlBu_r', vmin=-1, vmax=1, aspect='auto')
fig.colorbar(im, ax=ax, shrink=0.8, label='Pearson r')

ax.set_xticks(range(len(col_names)))
ax.set_yticks(range(len(col_names)))
ax.set_xticklabels(col_names, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(col_names, fontsize=9)

# Annotate cells
for i in range(len(col_names)):
    for j in range(len(col_names)):
        val = corr[i, j]
        text_color = 'white' if abs(val) > 0.6 else 'black'
        ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                fontsize=8, color=text_color)

ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
