"""
Dual-Axis Time Series
Two y-axes sharing the same time x-axis — ideal for comparing differently scaled series.
"""

import numpy as np

try:
    import pandas as _pd
    t  = _pd.to_datetime(x_data)
    y1 = np.asarray(y_data, dtype=float)
    try:
        y2 = np.asarray(y2_data, dtype=float)
    except NameError:
        y2 = y1 * 0.05 + np.random.normal(0, 0.2, len(y1))
except NameError:
    import pandas as _pd
    rng = np.random.default_rng(21)
    t   = _pd.date_range('2023-01-01', periods=90, freq='D')
    y1  = np.cumsum(rng.normal(0, 1, 90)) + 50   # temperature-like
    y2  = np.cumsum(rng.normal(0, 0.5, 90))       # precipitation-like

color1 = '#2E86AB'
color2 = '#E84855'

ax.plot(t, y1, color=color1, linewidth=2, label='Series 1')
ax.set_ylabel('Series 1', color=color1)
ax.tick_params(axis='y', labelcolor=color1)

ax2 = ax.twinx()
ax2.plot(t, y2, color=color2, linewidth=2, linestyle='--', label='Series 2')
ax2.set_ylabel('Series 2', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

fig.autofmt_xdate(rotation=30)
ax.set_title('Dual-Axis Time Series', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

# Combined legend
lines1, labs1 = ax.get_legend_handles_labels()
lines2, labs2 = ax2.get_legend_handles_labels()
if _show_legend:
    ax.legend(lines1 + lines2, labs1 + labs2, loc=_legend_position, framealpha=0.9)
