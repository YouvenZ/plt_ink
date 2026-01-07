"""
Basic Time Series Plot
Plot data over time with date axis formatting
"""

try:
    # Try to parse first column as dates
    dates = pd.to_datetime(data.iloc[:, 0])
    values = y_data
except:
    # Generate sample time series
    dates = pd.date_range(start='2024-01-01', periods=365, freq='D')
    trend = np.linspace(100, 150, len(dates))
    seasonal = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
    noise = np.random.normal(0, 5, len(dates))
    values = trend + seasonal + noise

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

ax.plot(dates, values, linewidth=1.5, color='#2E86AB')

# Format x-axis for dates
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')

ax.set_title('Time Series Analysis', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')