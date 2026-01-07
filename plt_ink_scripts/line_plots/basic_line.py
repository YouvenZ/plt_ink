"""
Basic Line Plot
Simple line plot with markers - ideal for time series or continuous data
"""

# Create the plot using loaded data (x_data, y_data) or generate sample data
try:
    x = x_data
    y = y_data
except NameError:
    import numpy as np
    # Sample data if no file loaded
    x = np.linspace(0, 10, 50)
    y = np.sin(x) + np.random.normal(0, 0.1, len(x))

plt.plot(x, y, marker='o', linestyle='-', linewidth=2, markersize=6, 
         color='#2E86AB', label='Data')

plt.title('Data Trend Analysis', fontsize=14, fontweight='bold')
plt.xlabel('X Variable')
plt.ylabel('Y Variable')

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position, framealpha=0.9)