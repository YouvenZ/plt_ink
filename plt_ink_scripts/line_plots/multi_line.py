# Use loaded data or generate sample
try:
    x = x_data
    # Assume multiple y columns in dataframe
    y_series = [data.iloc[:, i].values for i in range(1, min(5, len(data.columns)))]
except NameError:
    x = np.linspace(0, 10, 100)
    y_series = [
        np.sin(x),
        np.cos(x),
        np.sin(x) * np.exp(-x/10),
        np.cos(x) * np.exp(-x/10)
    ]

colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(y_series)))
labels = ['Series A', 'Series B', 'Series C', 'Series D']

for i, (y, color, label) in enumerate(zip(y_series, colors, labels)):
    plt.plot(x, y, linewidth=2, color=color, label=label)

plt.title('Multi-Series Comparison', fontsize=14, fontweight='bold')
plt.xlabel('X Variable')
plt.ylabel('Y Variable')

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position, framealpha=0.9)
