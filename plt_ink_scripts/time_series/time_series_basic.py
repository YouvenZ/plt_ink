"""
Basic Time Series
Line plot optimised for datetime x-axis data.
Demo usecase: 10-year monthly mean-temperature trend with 12-month rolling average.
"""

import numpy as np

try:
    import pandas as _pd
    t = _pd.to_datetime(x_data)
    y = np.asarray(y_data, dtype=float)
    y_label = 'Value'
except NameError:
    import pandas as _pd
    # Synthetic 10-year monthly climate data (2014-2024)
    t = _pd.date_range('2014-01-01', periods=121, freq='MS')
    rng = np.random.default_rng(20)
    months = np.arange(1, 122)
    y = (12 + 10 * np.sin((months % 12 - 3) * np.pi / 6)
         + 0.018 * months          # gentle warming trend
         + rng.normal(0, 0.8, 121))
    y_label = 'Mean Temperature (°C)'

# Raw monthly data
ax.plot(t, y, linewidth=1.0, color='#aec6cf', alpha=0.6, label='Monthly')

# 12-month rolling mean for trend
try:
    import pandas as _pd2
    y_roll = _pd2.Series(y).rolling(12, center=True).mean().values
    ax.plot(t, y_roll, linewidth=2.2, color='#1B4F72', label='12-month avg')
except Exception:
    pass

ax.fill_between(t, y.min() - 0.5, y, alpha=0.08, color='#1B4F72')

fig.autofmt_xdate(rotation=30)
ax.set_title('Monthly Temperature Trend (2014–2024)', fontsize=13, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel(y_label)

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)

