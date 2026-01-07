```python
"""
Matplotlib Script Bank for Inkscape Extension
Research-focused plotting scripts
"""

SCRIPT_CATEGORIES = {
    'line_plots': 'Line Plots',
    'scatter_plots': 'Scatter Plots', 
    'bar_charts': 'Bar Charts',
    'statistical': 'Statistical Plots',
    'scientific': 'Scientific Plots',
    'time_series': 'Time Series',
    'publication': 'Publication Ready',
}
```

### Line Plots Category

```python
"""
Basic Line Plot
Simple line plot with markers - ideal for time series or continuous data
"""

# Create the plot using loaded data (x_data, y_data) or generate sample data
try:
    x = x_data
    y = y_data
except NameError:
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
```

```python
"""
Multi-Line Comparison Plot
Compare multiple data series on the same axes
"""

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
```

```python
"""
Line Plot with Error Bands (Confidence Intervals)
Show uncertainty in your data with shaded regions
"""

# Use loaded data or generate sample
try:
    x = x_data
    y = y_data
    # Try to get error/std from data
    y_err = data.iloc[:, 2].values if len(data.columns) > 2 else y * 0.1
except NameError:
    x = np.linspace(0, 10, 50)
    y = np.sin(x) * np.exp(-x/15) + 2
    y_err = 0.2 + 0.1 * np.random.rand(len(x))

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

# Plot mean line
ax.plot(x, y, 'b-', linewidth=2, label='Mean')

# Plot error bands (±1 std)
ax.fill_between(x, y - y_err, y + y_err, alpha=0.3, color='blue', label='±1 SD')

# Plot ±2 std for 95% CI
ax.fill_between(x, y - 2*y_err, y + 2*y_err, alpha=0.15, color='blue', label='95% CI')

ax.set_title('Measurement with Confidence Intervals', fontsize=14, fontweight='bold')
ax.set_xlabel('Independent Variable')
ax.set_ylabel('Dependent Variable')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
```

### Scatter Plots Category

```python
"""
Basic Scatter Plot
Simple scatter plot for correlation analysis
"""

try:
    x = x_data
    y = y_data
except NameError:
    np.random.seed(42)
    x = np.random.randn(100)
    y = 0.5 * x + np.random.randn(100) * 0.5

plt.scatter(x, y, alpha=0.7, s=50, c='#2E86AB', edgecolors='white', linewidth=0.5)

# Add trend line
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
x_line = np.linspace(min(x), max(x), 100)
plt.plot(x_line, p(x_line), 'r--', linewidth=2, label=f'Trend: y = {z[0]:.2f}x + {z[1]:.2f}')

# Calculate R²
correlation = np.corrcoef(x, y)[0, 1]
r_squared = correlation ** 2

plt.title(f'Correlation Analysis (R² = {r_squared:.3f})', fontsize=14, fontweight='bold')
plt.xlabel('X Variable')
plt.ylabel('Y Variable')

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position, framealpha=0.9)
```

```python
"""
Scatter Plot with Color Mapping
Visualize a third variable using color
"""

try:
    x = x_data
    y = y_data
    c = data.iloc[:, 2].values if len(data.columns) > 2 else y
except NameError:
    np.random.seed(42)
    x = np.random.randn(150)
    y = np.random.randn(150)
    c = x**2 + y**2  # Color by distance from origin

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

scatter = ax.scatter(x, y, c=c, cmap=_colormap, alpha=0.7, s=60, 
                      edgecolors='white', linewidth=0.5)

cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
cbar.set_label('Color Variable', fontsize=11)

ax.set_title('Multi-Variable Scatter Plot', fontsize=14, fontweight='bold')
ax.set_xlabel('X Variable')
ax.set_ylabel('Y Variable')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')
```

```python
"""
Bubble Chart
Scatter plot with variable marker sizes for 4D visualization
"""

try:
    x = x_data
    y = y_data
    sizes = data.iloc[:, 2].values if len(data.columns) > 2 else np.abs(y) * 100
    colors = data.iloc[:, 3].values if len(data.columns) > 3 else x
except NameError:
    np.random.seed(42)
    n = 50
    x = np.random.rand(n) * 10
    y = np.random.rand(n) * 10
    sizes = np.random.rand(n) * 500 + 50
    colors = np.random.rand(n)

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

scatter = ax.scatter(x, y, s=sizes, c=colors, cmap=_colormap, alpha=0.6, 
                      edgecolors='black', linewidth=0.5)

cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
cbar.set_label('Category', fontsize=11)

ax.set_title('Bubble Chart Analysis', fontsize=14, fontweight='bold')
ax.set_xlabel('X Variable')
ax.set_ylabel('Y Variable')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

# Add size legend
sizes_legend = [100, 300, 500]
for s in sizes_legend:
    ax.scatter([], [], s=s, c='gray', alpha=0.5, label=f'Size = {s}')
if _show_legend:
    ax.legend(loc='upper left', title='Bubble Size', framealpha=0.9)
```

### Statistical Plots Category

```python
"""
Histogram with Statistics
Distribution analysis with statistical annotations
"""

try:
    data_vals = y_data
except NameError:
    np.random.seed(42)
    data_vals = np.random.normal(50, 15, 500)

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

# Create histogram
n, bins, patches = ax.hist(data_vals, bins=30, density=True, alpha=0.7, 
                            color='#2E86AB', edgecolor='white', linewidth=0.5)

# Fit and plot normal distribution
from scipy import stats
mu, std = stats.norm.fit(data_vals)
x_fit = np.linspace(min(data_vals), max(data_vals), 100)
y_fit = stats.norm.pdf(x_fit, mu, std)
ax.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Normal fit\nμ={mu:.2f}, σ={std:.2f}')

# Add vertical lines for mean and median
ax.axvline(mu, color='red', linestyle='--', linewidth=1.5, label=f'Mean: {mu:.2f}')
ax.axvline(np.median(data_vals), color='green', linestyle='--', linewidth=1.5, 
           label=f'Median: {np.median(data_vals):.2f}')

ax.set_title('Distribution Analysis', fontsize=14, fontweight='bold')
ax.set_xlabel('Value')
ax.set_ylabel('Density')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
```

```python
"""
Box Plot Comparison
Compare distributions across groups
"""

try:
    # Assume data has multiple columns for groups
    groups = [data.iloc[:, i].dropna().values for i in range(len(data.columns))]
    labels = list(data.columns)
except NameError:
    np.random.seed(42)
    groups = [
        np.random.normal(100, 10, 50),
        np.random.normal(90, 15, 50),
        np.random.normal(105, 12, 50),
        np.random.normal(95, 8, 50)
    ]
    labels = ['Control', 'Treatment A', 'Treatment B', 'Treatment C']

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

bp = ax.boxplot(groups, labels=labels, patch_artist=True, notch=True)

# Color the boxes
colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(groups)))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Style whiskers and caps
for element in ['whiskers', 'caps']:
    for item in bp[element]:
        item.set_color('gray')
        item.set_linewidth(1.5)

# Style medians
for median in bp['medians']:
    median.set_color('black')
    median.set_linewidth(2)

ax.set_title('Group Distribution Comparison', fontsize=14, fontweight='bold')
ax.set_xlabel('Group')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

# Add mean markers
means = [np.mean(g) for g in groups]
ax.scatter(range(1, len(groups)+1), means, marker='D', color='red', s=50, 
           zorder=5, label='Mean')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
```

```python
"""
Violin Plot
Show full distribution shape for group comparisons
"""

try:
    groups = [data.iloc[:, i].dropna().values for i in range(len(data.columns))]
    labels = list(data.columns)
except NameError:
    np.random.seed(42)
    groups = [
        np.concatenate([np.random.normal(0, 1, 100), np.random.normal(3, 0.5, 50)]),
        np.random.normal(1, 1.5, 150),
        np.random.exponential(2, 150),
        np.random.normal(2, 0.8, 150)
    ]
    labels = ['Bimodal', 'Normal', 'Exponential', 'Narrow']

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

parts = ax.violinplot(groups, positions=range(1, len(groups)+1), 
                       showmeans=True, showmedians=True, showextrema=True)

# Color the violins
colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(groups)))
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(colors[i])
    pc.set_alpha(0.7)

# Style the lines
parts['cmeans'].set_color('red')
parts['cmeans'].set_linewidth(2)
parts['cmedians'].set_color('black')
parts['cmedians'].set_linewidth(2)

ax.set_xticks(range(1, len(groups)+1))
ax.set_xticklabels(labels)

ax.set_title('Distribution Shape Comparison', fontsize=14, fontweight='bold')
ax.set_xlabel('Group')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
```

### Scientific Plots Category

```python
"""
Spectrum/Spectral Plot
For spectroscopy, chromatography, or frequency analysis
"""

try:
    wavelength = x_data
    intensity = y_data
except NameError:
    # Simulate absorption spectrum with multiple peaks
    wavelength = np.linspace(200, 800, 1000)
    peaks = [(350, 20, 0.8), (420, 15, 0.6), (550, 25, 1.0), (650, 18, 0.4)]
    intensity = np.zeros_like(wavelength)
    for center, width, height in peaks:
        intensity += height * np.exp(-((wavelength - center) ** 2) / (2 * width ** 2))
    intensity += np.random.normal(0, 0.02, len(wavelength))

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

ax.plot(wavelength, intensity, 'b-', linewidth=1.5)
ax.fill_between(wavelength, 0, intensity, alpha=0.3, color='blue')

# Mark peaks
from scipy.signal import find_peaks
peaks_idx, _ = find_peaks(intensity, height=0.2, distance=50)
ax.scatter(wavelength[peaks_idx], intensity[peaks_idx], color='red', s=50, 
           zorder=5, marker='v', label='Peaks')

# Annotate peaks
for idx in peaks_idx:
    ax.annotate(f'{wavelength[idx]:.0f}', 
                xy=(wavelength[idx], intensity[idx]),
                xytext=(0, 10), textcoords='offset points',
                ha='center', fontsize=9)

ax.set_title('Spectral Analysis', fontsize=14, fontweight='bold')
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Intensity (a.u.)')
ax.set_xlim(wavelength.min(), wavelength.max())
ax.set_ylim(0, None)

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
```

```python
"""
Dose-Response Curve
Sigmoidal fit for pharmacology and toxicology studies
"""

try:
    dose = x_data
    response = y_data
except NameError:
    # Generate sigmoidal dose-response data
    np.random.seed(42)
    dose = np.array([0.001, 0.01, 0.1, 1, 10, 100, 1000])
    EC50 = 10
    Hill = 1.5
    response = 100 / (1 + (EC50/dose)**Hill) + np.random.normal(0, 3, len(dose))

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

# Plot data points
ax.semilogx(dose, response, 'o', markersize=10, color='#2E86AB', 
            markeredgecolor='white', markeredgewidth=1.5, label='Data')

# Fit sigmoidal curve
from scipy.optimize import curve_fit

def sigmoid(x, bottom, top, ec50, hill):
    return bottom + (top - bottom) / (1 + (ec50/x)**hill)

try:
    popt, _ = curve_fit(sigmoid, dose, response, p0=[0, 100, 10, 1], maxfev=5000)
    x_fit = np.logspace(np.log10(dose.min()), np.log10(dose.max()), 100)
    y_fit = sigmoid(x_fit, *popt)
    ax.semilogx(x_fit, y_fit, '-', linewidth=2, color='red', 
                label=f'Fit (EC₅₀ = {popt[2]:.2f})')
except:
    pass

ax.set_title('Dose-Response Relationship', fontsize=14, fontweight='bold')
ax.set_xlabel('Dose (log scale)')
ax.set_ylabel('Response (%)')
ax.set_ylim(-5, 110)

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', which='both')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
```

```python
"""
Correlation Heatmap
Visualize correlation matrix for multiple variables
"""

try:
    # Use loaded dataframe
    corr_matrix = data.corr()
    labels = list(data.columns)
except NameError:
    # Generate sample correlation matrix
    np.random.seed(42)
    n_vars = 8
    labels = [f'Var {i+1}' for i in range(n_vars)]
    # Create a random positive semi-definite matrix
    A = np.random.randn(n_vars, n_vars)
    corr_matrix = np.corrcoef(A)

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

# Add colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Correlation Coefficient', fontsize=11)

# Set ticks and labels
ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.set_yticklabels(labels)

# Add correlation values as text
for i in range(len(labels)):
    for j in range(len(labels)):
        val = corr_matrix.iloc[i, j] if hasattr(corr_matrix, 'iloc') else corr_matrix[i, j]
        color = 'white' if abs(val) > 0.5 else 'black'
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=9)

ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
```

### Time Series Category

```python
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
```

```python
"""
Time Series with Trend and Moving Average
Show underlying trends in noisy data
"""

try:
    dates = pd.to_datetime(data.iloc[:, 0])
    values = y_data
except:
    dates = pd.date_range(start='2024-01-01', periods=200, freq='D')
    trend = np.linspace(100, 150, len(dates))
    seasonal = 15 * np.sin(2 * np.pi * np.arange(len(dates)) / 30)
    noise = np.random.normal(0, 8, len(dates))
    values = trend + seasonal + noise

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

# Plot raw data
ax.plot(dates, values, alpha=0.5, linewidth=1, color='gray', label='Raw data')

# Calculate and plot moving averages
window_short = 7
window_long = 30

ma_short = pd.Series(values).rolling(window=window_short, center=True).mean()
ma_long = pd.Series(values).rolling(window=window_long, center=True).mean()

ax.plot(dates, ma_short, linewidth=2, color='#2E86AB', 
        label=f'{window_short}-day MA')
ax.plot(dates, ma_long, linewidth=2.5, color='#E94F37', 
        label=f'{window_long}-day MA')

# Format dates
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.xaxis.set_major_locator(mdates.WeekLocator(interval=2))
plt.xticks(rotation=45, ha='right')

ax.set_title('Trend Analysis with Moving Averages', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
```

### Bar Charts Category

```python
"""
Grouped Bar Chart
Compare categories across multiple groups
"""

try:
    categories = data.iloc[:, 0].values
    groups = {col: data[col].values for col in data.columns[1:]}
except NameError:
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    groups = {
        'Group 1': np.array([25, 32, 28, 35]),
        'Group 2': np.array([30, 28, 35, 32]),
        'Group 3': np.array([22, 35, 30, 28])
    }

fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))

x = np.arange(len(categories))
n_groups = len(groups)
width = 0.8 / n_groups

colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, n_groups))

for i, (name, values) in enumerate(groups.items()):
    offset = (i - n_groups/2 + 0.5) * width
    bars = ax.bar(x + offset, values, width, label=name, color=colors[i], 
                   edgecolor='white', linewidth=0.5)

ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha='right')

ax.set_title('Grouped Comparison', fontsize=14, fontweight='bold')
ax.set_xlabel('Category')
ax.set_ylabel('Value')

if _show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    ax.legend(loc=_legend_position, framealpha=0.9)
```

```python
"""
Stacked Bar Chart
Show composition of totals across categories
"""

try:
    categories = data.iloc[:, 0].values
    components = {col: data[col].values for col in data.columns[1:]}
except NameError:
    categories = ['2020', '2021', '2022', '2023', '2024']
    components = {
        'Component A': np.array([20, 25, 22, 28, 30]),
        'Component B': np.array([15, 18, 20, 22, 25]),
        'Component C': np.array([10, 12, 15, 18, 20]),
        'Component D': np.array([8, 10, 12, 15, 18])// filepath: c:\Users\youve\AppData\Roaming\inkscape\extensions\plt_ink_scripts\bar_charts\stacked_bar.py
"""
Stacked Bar Chart
Show composition of totals across categories
"""

try:
    categories = data.iloc[:, 0].values
    components = {col: data[col].values for col in data.columns[1:]}
except NameError:
    categories = ['2020', '2021', '2022', '2023', '2024']
    components = {
        'Component A': np.array([20, 25, 22, 28, 30]),
        'Component B': np.array([15, 18, 20, 22, 25]),
        'Component C': np.array([10, 12, 15, 18, 20]),
        'Component D': np.array([8, 10, 12, 15, 18])