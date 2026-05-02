"""
Seaborn heatmap with annotation.
Requires: pip install seaborn
Available variables: sns (if installed), seaborn_available
"""
if not seaborn_available:
    raise ImportError("seaborn is not installed. Run: pip install seaborn")

sns.set_theme()

# Sample correlation matrix
np.random.seed(0)
data = np.random.randn(6, 6)
matrix = np.corrcoef(data)
labels = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]

sns.heatmap(
    matrix,
    annot=True, fmt=".2f",
    cmap=_colormap,
    xticklabels=labels,
    yticklabels=labels,
    ax=ax,
    linewidths=0.5,
    vmin=-1, vmax=1,
)
ax.set_title("Correlation Heatmap")
