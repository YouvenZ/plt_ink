"""
Basic Seaborn scatter plot with regression line.
Requires: pip install seaborn
Available variables: sns (if installed), seaborn_available, df/data (if data file loaded)
"""
if not seaborn_available:
    raise ImportError("seaborn is not installed. Run: pip install seaborn")

# Use seaborn theme for styling
sns.set_theme(style="whitegrid")

# Generate sample data
np.random.seed(42)
n = 80
x = np.random.randn(n)
y = 0.7 * x + np.random.randn(n) * 0.5

# Scatter with regression line
ax.scatter(x, y, alpha=0.6, edgecolors='white', linewidth=0.5, label='Data')
# Regression line
m, b = np.polyfit(x, y, 1)
x_line = np.linspace(x.min(), x.max(), 100)
ax.plot(x_line, m * x_line + b, color='crimson', linewidth=2, label=f'y = {m:.2f}x + {b:.2f}')

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Seaborn-Styled Scatter with Regression")
if _show_legend:
    ax.legend(loc=_legend_position)
