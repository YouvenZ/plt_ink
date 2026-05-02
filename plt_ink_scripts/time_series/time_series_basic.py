"""
Basic Time Series
Line plot optimised for datetime x-axis data.
"""

import numpy as np

try:
    import pandas as _pd
    t = _pd.to_datetime(x_data)
    y = np.asarray(y_data, dtype=float)
except NameError:
    import pandas as _pd
    t = _pd.date_range('2023-01-01', periods=90, freq='D')
    rng = np.random.default_rng(20)
    y   = np.cumsum(rng.normal(0, 1, 90)) + 100

ax.plot(t, y, linewidth=2, color='#2E86AB', label='Value')
ax.fill_between(t, y.min(), y, alpha=0.15, color='#2E86AB')

fig.autofmt_xdate(rotation=30)
ax.set_title('Time Series', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
