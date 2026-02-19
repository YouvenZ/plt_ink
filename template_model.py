"""
ML Model Comparison - Two Clear Histograms
Clean side-by-side comparison of Accuracy and F1 Score
Requires: load_all_columns=True
"""

# Calculate mean metrics per model, sorted by accuracy
model_stats = data.groupby('Model').agg({
    'Accuracy': 'mean',
    'F1_Score': 'mean'
}).sort_values('Accuracy', ascending=False)

models = model_stats.index.tolist()
n_models = len(models)

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(_fig_width, _fig_height))
fig.subplots_adjust(left=0.08, right=0.96, top=0.85, bottom=0.22, wspace=0.25)

# Color palette - consistent across both charts
colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.85, n_models))

# ============================================================================
# Left: Accuracy Histogram
# ============================================================================
x_pos = np.arange(n_models)
bars1 = ax1.bar(x_pos, model_stats['Accuracy'], width=0.7,
                color=colors, edgecolor='white', linewidth=1.5)

# Add value labels on top
for bar, val in zip(bars1, model_stats['Accuracy']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.008,
             f'{val:.1%}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax1.set_xticks(x_pos)
ax1.set_xticklabels(models, rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Accuracy', fontsize=12, fontweight='medium')
ax1.set_ylim(0.75, 1.05)
ax1.set_title('Mean Accuracy', fontsize=14, fontweight='bold', pad=12)

if _show_grid:
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax1.set_axisbelow(True)

# ============================================================================
# Right: F1 Score Histogram
# ============================================================================
bars2 = ax2.bar(x_pos, model_stats['F1_Score'], width=0.7,
                color=colors, edgecolor='white', linewidth=1.5)

# Add value labels on top
for bar, val in zip(bars2, model_stats['F1_Score']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.008,
             f'{val:.1%}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax2.set_xticks(x_pos)
ax2.set_xticklabels(models, rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('F1 Score', fontsize=12, fontweight='medium')
ax2.set_ylim(0.75, 1.05)
ax2.set_title('Mean F1 Score', fontsize=14, fontweight='bold', pad=12)

if _show_grid:
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_axisbelow(True)

# ============================================================================
# Main Title
# ============================================================================
fig.suptitle('Model Performance Comparison', 
             fontsize=16, fontweight='bold', y=0.95)