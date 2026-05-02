"""
Seaborn violin + strip plot (distribution comparison across categories).
Requires: pip install seaborn
Available variables: sns (if installed), seaborn_available
"""
if not seaborn_available:
    raise ImportError("seaborn is not installed. Run: pip install seaborn")

import pandas as pd
sns.set_theme(style="ticks")

# Sample data
np.random.seed(1)
categories = ["A", "B", "C", "D"]
df_plot = pd.DataFrame({
    "Category": np.repeat(categories, 40),
    "Value":    np.concatenate([
        np.random.normal(0,   1.0, 40),
        np.random.normal(1.5, 0.8, 40),
        np.random.normal(-0.5, 1.5, 40),
        np.random.normal(2.0,  0.6, 40),
    ])
})

sns.violinplot(data=df_plot, x="Category", y="Value",
               palette="Set2", inner=None, ax=ax, alpha=0.7)
sns.stripplot(data=df_plot, x="Category", y="Value",
              color="black", size=2.5, jitter=True, ax=ax, alpha=0.5)

ax.set_title("Seaborn Violin + Strip Plot")
ax.set_xlabel("Category")
ax.set_ylabel("Value")
