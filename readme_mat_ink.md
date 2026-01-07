# Matplotlib Inkscape Extension - Complete Guide

## Table of Contents
1. [Template Functions Explained](#template-functions)
2. [Using CSV Data](#using-csv-data)
3. [Example Files](#example-files)
4. [Troubleshooting](#troubleshooting)

---

## Template Functions

The extension provides 8 pre-built templates for quick plotting:

### 1. **Line Plot** (Default)
- **Purpose**: Display trends over continuous data
- **Parameters Used**: 
  - Data Points: Number of points to generate
  - Title, X-label, Y-label: Chart labels
  - Legend: Show/hide legend
- **Example Use**: Time series, continuous measurements
- **Generated Code**:
  ```python
  x = np.linspace(0, 10, 100)
  y = np.sin(x)
  plt.plot(x, y, label='sin(x)')
  plt.title('My Plot')
  plt.xlabel('X')
  plt.ylabel('Y')
  plt.legend(loc='best')
  ```

### 2. **Scatter Plot**
- **Purpose**: Show correlation between two variables
- **Parameters Used**:
  - Data Points: Number of random points
  - Color Map: Color scheme (viridis, plasma, etc.)
- **Example Use**: Data distribution, correlation analysis
- **Generated Code**:
  ```python
  x = np.random.randn(100)
  y = np.random.randn(100)
  colors = np.random.rand(100)
  plt.scatter(x, y, c=colors, cmap='viridis', alpha=0.6)
  plt.colorbar()
  ```

### 3. **Bar Chart**
- **Purpose**: Compare discrete categories
- **Parameters Used**:
  - Color Map: Color scheme for bars
  - Title, labels
- **Example Use**: Category comparison, rankings
- **Generated Code**:
  ```python
  categories = ['A', 'B', 'C', 'D', 'E']
  values = np.random.randint(10, 100, 5)
  plt.bar(categories, values)
  ```

### 4. **Histogram**
- **Purpose**: Show data distribution
- **Parameters Used**:
  - Data Points: Sample size
  - Title, labels
- **Example Use**: Frequency distribution, statistical analysis
- **Generated Code**:
  ```python
  data = np.random.randn(100)
  plt.hist(data, bins=30, edgecolor='black', alpha=0.7)
  ```

### 5. **Pie Chart**
- **Purpose**: Show proportions of a whole
- **Parameters Used**:
  - Color Map: Slice colors
  - Title
- **Example Use**: Market share, budget allocation
- **Generated Code**:
  ```python
  labels = ['A', 'B', 'C', 'D']
  sizes = [25, 30, 25, 20]
  plt.pie(sizes, labels=labels, autopct='%1.1f%%')
  ```

### 6. **Heatmap**
- **Purpose**: Visualize matrix data with colors
- **Parameters Used**:
  - Color Map: Heat color scheme
  - Title, labels
- **Example Use**: Correlation matrices, intensity maps
- **Generated Code**:
  ```python
  data = np.random.rand(10, 10)
  plt.imshow(data, cmap='viridis', aspect='auto')
  plt.colorbar()
  ```

### 7. **3D Surface Plot**
- **Purpose**: Visualize functions of two variables
- **Parameters Used**:
  - Data Points: Grid resolution (sqrt used)
  - Color Map: Surface colors
- **Example Use**: Mathematical functions, terrain
- **Generated Code**:
  ```python
  from mpl_toolkits.mplot3d import Axes3D
  ax = fig.add_subplot(111, projection='3d')
  X, Y = np.meshgrid(x, y)
  Z = np.sin(np.sqrt(X**2 + Y**2))
  surf = ax.plot_surface(X, Y, Z, cmap='viridis')
  ```

### 8. **Subplots** (2x2 Grid)
- **Purpose**: Multiple plots in one figure
- **Parameters Used**:
  - Data Points: Points per subplot
  - Grid: Show/hide grid
  - Title: Overall title
- **Example Use**: Comparing multiple datasets
- **Generated Code**:
  ```python
  fig, axes = plt.subplots(2, 2)
  axes[0, 0].plot(x, np.sin(x))
  axes[0, 1].plot(x, np.cos(x), 'r')
  axes[1, 0].plot(x, x**2, 'g')
  axes[1, 1].plot(x, np.exp(-x/10), 'm')
  ```

---

## Using CSV Data

### Step-by-Step Guide

#### 1. Prepare Your CSV File
Create a CSV file with headers:

**Example: sales_data.csv**
```csv
Month,Revenue,Cost
Jan,15000,12000
Feb,18000,13500
Mar,22000,15000
```

**Rules:**
- First row = headers (optional, can skip with checkbox)
- Columns separated by delimiter (comma, semicolon, tab)
- Numeric data only (no currency symbols, % signs)
- Use decimal point (not comma) for decimals: `12.5` not `12,5`

#### 2. Configure Data Import in Extension

**In "Data Import" Tab:**
- ☑ **Use Data File**: Check this box
- **File Path**: Browse to your CSV file
- **Data Format**: Select "CSV"
- **Delimiter**: `,` (or `;` for European CSVs, `\t` for tab)
- ☑ **Skip Header**: Check if first row is headers
- **X Column**: 0 (first column = 0, second = 1, etc.)
- **Y Column**: 1 (which column to plot)

#### 3. Write Your Plot Code

After data is loaded, two variables are available:
- `x_data`: Values from X column
- `y_data`: Values from Y column

**Example inline code:**
```python
plt.plot(x_data, y_data, marker='o', linewidth=2)
plt.title('Monthly Revenue')
plt.xlabel('Month')
plt.ylabel('Revenue ($)')
plt.grid(True)
plt.xticks(rotation=45)  # Rotate x-axis labels
```

### CSV Format Examples

#### Temperature Data
```csv
Day,Temperature,Humidity,Pressure
1,22.5,65,1013
2,23.1,62,1015
3,24.3,58,1012
```

**To plot Temperature vs Day:**
- X Column: 0 (Day)
- Y Column: 1 (Temperature)

**To plot Humidity vs Day:**
- X Column: 0 (Day)
- Y Column: 2 (Humidity)

#### Stock Prices
```csv
Date,Open,High,Low,Close,Volume
2024-01-01,150.00,152.50,149.50,151.00,1000000
2024-01-02,151.00,153.00,150.00,152.50,1200000
```

**Note:** Dates must be in a format Python can parse, or use row numbers

#### Multiple Series (Advanced)
For multiple Y columns, use inline code:
```python
# After loading CSV with columns: Month, Sales, Expenses
data = np.loadtxt(r'C:/path/to/file.csv', delimiter=',', skiprows=1)
months = data[:, 0]
sales = data[:, 1]
expenses = data[:, 2]

plt.plot(months, sales, marker='o', label='Sales')
plt.plot(months, expenses, marker='s', label='Expenses')
plt.legend()
plt.title('Sales vs Expenses')
```

---

## Example Files Included

### 1. sample_data.csv
Monthly sales data with 3 columns:
- Month (numeric: 1-12)
- Sales (dollars)
- Expenses (dollars)

**How to use:**
1. Load this CSV file in Data Import tab
2. Set X Column = 0, Y Column = 1
3. Use template "Line Plot" or write custom code

### 2. temperature_data.csv
Daily weather data with 3 columns:
- Day (1-15)
- Temperature (Celsius)
- Humidity (percentage)

**How to use:**
1. Select this file
2. Choose columns to plot (Day vs Temp or Day vs Humidity)
3. Add custom styling in inline code

### 3. plot_from_csv.py
Example Python script showing CSV plotting

**How to use:**
1. In "Script" tab, select "Load from File"
2. Browse to this .py file
3. Still need to configure CSV import in Data Import tab
4. The script will use the loaded x_data and y_data

---

## Complete Workflow Examples

### Example 1: Simple Line Plot from CSV

**Goal:** Plot sales over months

**Steps:**
1. Create CSV:
   ```csv
   Month,Sales
   1,15000
   2,18000
   3,22000
   4,19000
   5,25000
   ```

2. In Extension:
   - Tab: **Data Import**
     - ☑ Use Data File
     - File Path: Browse to CSV
     - X Column: 0
     - Y Column: 1
     - ☑ Skip Header
   
   - Tab: **Script**
     - Source: Inline Code
     - Code:
       ```python
       plt.plot(x_data, y_data, marker='o', color='blue', linewidth=2)
       plt.title('Monthly Sales')
       plt.xlabel('Month')
       plt.ylabel('Sales ($)')
       plt.grid(True, alpha=0.3)
       ```
   
   - Tab: **Format**
     - Format: SVG
     - Width: 8.0, Height: 6.0
     - DPI: 300
   
   - Click **Apply**

### Example 2: Bar Chart with Template

**Goal:** Compare categories using template

**Steps:**
1. Tab: **Script**
   - Source: Template
   
2. Tab: **Templates**
   - Type: Bar Chart
   - Title: "Sales by Region"
   - X-label: "Region"
   - Y-label: "Sales"

3. Tab: **Style**
   - Color Map: plasma
   - ☑ Show Grid

4. Click **Apply**

### Example 3: Custom Multi-line Plot

**Goal:** Plot both Sales and Expenses on same chart

**Steps:**
1. Create CSV:
   ```csv
   Month,Sales,Expenses,Profit
   1,15000,12000,3000
   2,18000,13500,4500
   3,22000,15000,7000
   ```

2. In Extension:
   - Tab: **Data Import**
     - ☑ Use Data File
     - Browse to CSV
     - ☑ Skip Header
     - X Column: 0
     - Y Column: 1 (won't use Y column, will load manually)
   
   - Tab: **Script**
     - Source: Inline Code
     - Code:
       ```python
       # Load all data manually
       import csv
       data = []
       with open(r'C:/path/to/file.csv', 'r') as f:
           reader = csv.reader(f)
           next(reader)  # Skip header
           for row in reader:
               data.append([float(x) for x in row])
       
       data = np.array(data)
       months = data[:, 0]
       sales = data[:, 1]
       expenses = data[:, 2]
       profit = data[:, 3]
       
       # Create plots
       plt.plot(months, sales, marker='o', label='Sales', linewidth=2)
       plt.plot(months, expenses, marker='s', label='Expenses', linewidth=2)
       plt.plot(months, profit, marker='^', label='Profit', linewidth=2)
       
       plt.title('Financial Overview')
       plt.xlabel('Month')
       plt.ylabel('Amount ($)')
       plt.legend()
       plt.grid(True, alpha=0.3)
       ```

3. Click **Apply**

---

## Troubleshooting

### CSV Issues

**Problem:** "Failed to read CSV file"
- **Solution**: Check file path, ensure file exists, use forward slashes: `C:/path/file.csv`

**Problem:** "ValueError: could not convert string to float"
- **Solution**: 
  - Remove currency symbols: `$15,000` → `15000`
  - Remove commas from numbers: `1,000` → `1000`
  - Check for text in numeric columns
  - Ensure decimal point, not comma: `12.5` not `12,5`

**Problem:** Empty plot
- **Solution**: 
  - Check X and Y column numbers (start from 0)
  - Ensure "Skip Header" is checked if CSV has headers
  - Verify delimiter matches your CSV (`,` vs `;`)

**Problem:** All points on one line
- **Solution**: Data might be in wrong format, check column selection

### General Issues

**Problem:** Python not found
- **Solution**: Install Python, or set correct path in Advanced tab

**Problem:** Matplotlib not installed
- **Solution**: Run `pip install matplotlib` in terminal

**Problem:** Plot not appearing in Inkscape
- **Solution**: 
  - Check Placement tab settings
  - Try different position mode
  - Ensure figure size is reasonable (not too small/large)

**Problem:** "Script execution failed"
- **Solution**:
  - Check inline code for syntax errors
  - Enable "Keep Temp Files" and "Save Script" to debug
  - Review saved script for issues

---

## Tips and Best Practices

1. **Test Your CSV First**: Open in Excel/LibreOffice to verify format
2. **Use Absolute Paths**: Full paths work better than relative: `C:/Users/.../file.csv`
3. **Start Simple**: Test with template first, then customize
4. **Save Your Scripts**: Use "Save Script" option to keep working code
5. **SVG vs PNG**: Use SVG for scalability, PNG for compatibility
6. **Column Indexing**: Remember columns start at 0: first=0, second=1, third=2
7. **Preview Data**: Print first few rows in code to verify loading:
   ```python
   print(f"First X value: {x_data[0]}")
   print(f"First Y value: {y_data[0]}")
   ```

---

## Quick Reference Card

### CSV Column Numbers
```
Column A = 0
Column B = 1
Column C = 2
Column D = 3
```

### Common Delimiters
```
Comma:     ,
Semicolon: ;
Tab:       \t
Space:     (space)
```

### Available Variables After CSV Import
```python
x_data  # Values from X Column
y_data  # Values from Y Column
```

### Basic Plot Commands
```python
plt.plot(x, y)              # Line plot
plt.scatter(x, y)           # Scatter plot
plt.bar(x, y)               # Bar chart
plt.hist(data)              # Histogram
plt.xlabel('label')         # X-axis label
plt.ylabel('label')         # Y-axis label
plt.title('title')          # Plot title
plt.legend()                # Show legend
plt.grid(True)              # Show grid
```

---

## Support

For more help:
- Matplotlib documentation: https://matplotlib.org/stable/gallery/index.html
- NumPy documentation: https://numpy.org/doc/
- CSV format: https://en.wikipedia.org/wiki/Comma-separated_values





---



I'll refactor the extension to remove the template option and add a proper script bank system. Here are the updated files:

````xml
<?xml version="1.0" encoding="UTF-8"?>
<inkscape-extension xmlns="http://www.inkscape.org/namespace/inkscape/extension">
    <name>Matplotlib Figure Generator</name>
    <id>org.inkscape.matplotlib.generator</id>
    
    <param name="tab" type="notebook">
        <page name="script" gui-text="Script">
            <param name="python_path" type="string" gui-text="Python executable path:">python</param>
            <label>Path to Python with matplotlib installed (e.g., python, python3, or full path)</label>
            <spacer/>
            
            <param name="script_source" type="optiongroup" appearance="combo" gui-text="Script source:">
                <option value="inline">Inline code</option>
                <option value="file">External file</option>
                <option value="bank">Script Bank</option>
            </param>
            <spacer/>
            
            <param name="script_code" type="string" appearance="multiline" max_length="1000" gui-text="Python code:">import matplotlib.pyplot as plt
import numpy as np
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)</param>
            <label>Multi-line code supported. Don't include plt.show() or plt.savefig()</label>
            <spacer/>
            
            <param name="script_file" type="string" gui-text="Script file path:"></param>
            <label>Only used when 'External file' is selected</label>
        </page>
        
        <page name="bank" gui-text="Script Bank">
            <label appearance="header">Research Figure Templates</label>
            <label>Pre-built scripts for common research visualizations</label>
            <spacer/>
            
            <param name="bank_category" type="optiongroup" appearance="combo" gui-text="Category:">
                <option value="line_plots">Line Plots</option>
                <option value="scatter_plots">Scatter Plots</option>
                <option value="bar_charts">Bar Charts</option>
                <option value="statistical">Statistical Plots</option>
                <option value="heatmaps">Heatmaps &amp; Matrices</option>
                <option value="time_series">Time Series</option>
                <option value="distributions">Distributions</option>
                <option value="multi_panel">Multi-Panel Figures</option>
            </param>
            <spacer/>
            
            <param name="bank_script" type="optiongroup" appearance="combo" gui-text="Script:">
                <!-- Line Plots -->
                <option value="basic_line">Basic Line Plot</option>
                <option value="multi_line">Multiple Lines with Legend</option>
                <option value="error_bars">Line with Error Bars</option>
                <option value="fill_between">Filled Area Plot</option>
                <!-- Scatter Plots -->
                <option value="basic_scatter">Basic Scatter Plot</option>
                <option value="scatter_regression">Scatter with Regression</option>
                <option value="bubble_chart">Bubble Chart</option>
                <!-- Bar Charts -->
                <option value="basic_bar">Basic Bar Chart</option>
                <option value="grouped_bar">Grouped Bar Chart</option>
                <option value="stacked_bar">Stacked Bar Chart</option>
                <option value="horizontal_bar">Horizontal Bar Chart</option>
                <!-- Statistical -->
                <option value="box_plot">Box Plot</option>
                <option value="violin_plot">Violin Plot</option>
                <option value="error_bar_plot">Error Bar Comparison</option>
                <!-- Heatmaps -->
                <option value="correlation_matrix">Correlation Matrix</option>
                <option value="basic_heatmap">Basic Heatmap</option>
                <!-- Time Series -->
                <option value="time_series_basic">Basic Time Series</option>
                <option value="time_series_dual_axis">Dual Y-Axis Time Series</option>
                <!-- Distributions -->
                <option value="histogram">Histogram</option>
                <option value="kde_plot">KDE Density Plot</option>
                <option value="histogram_kde">Histogram with KDE</option>
                <!-- Multi-Panel -->
                <option value="subplot_2x2">2x2 Subplot Grid</option>
                <option value="subplot_comparison">Side-by-side Comparison</option>
            </param>
            <spacer/>
            
            <label>Note: Select category then choose a script. Scripts use extension settings for styling.</label>
            <label>Data can be loaded from the Data Import tab or use sample data.</label>
        </page>
        
        <page name="format" gui-text="Format">
            <param name="output_format" type="optiongroup" appearance="combo" gui-text="Output format:">
                <option value="svg">SVG (Vector, best for Inkscape)</option>
                <option value="png">PNG (Raster)</option>
                <option value="pdf">PDF (Vector)</option>
            </param>
            <spacer/>
            
            <param name="figure_width" type="float" min="1.0" max="50.0" precision="1" gui-text="Figure width (inches):">8.0</param>
            <param name="figure_height" type="float" min="1.0" max="50.0" precision="1" gui-text="Figure height (inches):">6.0</param>
            <label>Matplotlib uses inches as unit (1 inch = 96 pixels at default DPI)</label>
            <spacer/>
            
            <param name="dpi" type="int" min="50" max="600" gui-text="DPI (resolution):">96</param>
            <label>96 DPI = standard screen resolution (matches Inkscape default)</label>
            <label>Higher DPI = better quality but larger file size</label>
            <spacer/>
            
            <param name="transparent" type="bool" gui-text="Transparent background">false</param>
            <param name="tight_layout" type="bool" gui-text="Use tight layout">true</param>
        </page>
        
        <page name="style" gui-text="Style">
            <param name="plot_style" type="optiongroup" appearance="combo" gui-text="Plot style:">
                <option value="default">Default</option>
                <option value="seaborn-v0_8">Seaborn</option>
                <option value="ggplot">ggplot</option>
                <option value="bmh">Bayesian Methods</option>
                <option value="dark_background">Dark Background</option>
                <option value="grayscale">Grayscale</option>
                <option value="fivethirtyeight">FiveThirtyEight</option>
                <option value="tableau-colorblind10">Tableau Colorblind</option>
            </param>
            <spacer/>
            
            <param name="color_map" type="optiongroup" appearance="combo" gui-text="Color map:">
                <option value="viridis">Viridis</option>
                <option value="plasma">Plasma</option>
                <option value="inferno">Inferno</option>
                <option value="magma">Magma</option>
                <option value="coolwarm">Cool Warm</option>
                <option value="rainbow">Rainbow</option>
                <option value="jet">Jet</option>
                <option value="hsv">HSV</option>
            </param>
            <spacer/>
            
            <param name="grid" type="bool" gui-text="Show grid">true</param>
            <param name="legend" type="bool" gui-text="Show legend">true</param>
            <param name="legend_position" type="optiongroup" appearance="combo" gui-text="Legend position:">
                <option value="best">Best</option>
                <option value="upper right">Upper Right</option>
                <option value="upper left">Upper Left</option>
                <option value="lower right">Lower Right</option>
                <option value="lower left">Lower Left</option>
                <option value="center">Center</option>
            </param>
        </page>
        
        <page name="placement" gui-text="Placement">
            <param name="position_mode" type="optiongroup" appearance="combo" gui-text="Position:">
                <option value="center">Center of canvas</option>
                <option value="cursor">At cursor/selected object</option>
                <option value="top_left">Top left</option>
                <option value="top_center">Top center</option>
                <option value="top_right">Top right</option>
                <option value="bottom_left">Bottom left</option>
                <option value="bottom_center">Bottom center</option>
                <option value="bottom_right">Bottom right</option>
            </param>
            <label>Figure will be inserted at original size (width × height × DPI)</label>
            <spacer/>
            
            <param name="embed_image" type="bool" gui-text="Embed image in SVG">true</param>
            <label>If unchecked, links to external file (not recommended)</label>
        </page>
        
        <page name="advanced" gui-text="Advanced">
            <param name="font_family" type="string" gui-text="Font family:">sans-serif</param>
            <param name="font_size" type="int" min="6" max="72" gui-text="Base font size:">10</param>
            <spacer/>
            
            <param name="line_width" type="float" min="0.5" max="10.0" precision="1" gui-text="Line width:">1.5</param>
            <param name="marker_size" type="float" min="1.0" max="20.0" precision="1" gui-text="Marker size:">6.0</param>
            <spacer/>
            
            <param name="use_latex" type="bool" gui-text="Use LaTeX rendering">false</param>
            <label>Requires LaTeX installation on system</label>
            <spacer/>
            
            <param name="save_script" type="bool" gui-text="Save generated script to file">false</param>
            <param name="script_save_path" type="string" gui-text="Script save path:"></param>
            <spacer/>
            
            <param name="keep_temp_files" type="bool" gui-text="Keep temporary files for debugging">false</param>
        </page>
        
        <page name="data" gui-text="Data Import">
            <param name="use_data_file" type="bool" gui-text="Import data from file">false</param>
            <param name="data_file_path" type="string" gui-text="Data file path:"></param>
            <param name="data_format" type="optiongroup" appearance="combo" gui-text="Data format:">
                <option value="csv">CSV</option>
                <option value="txt">Text (space/tab separated)</option>
                <option value="excel">Excel (.xlsx)</option>
                <option value="json">JSON</option>
            </param>
            <spacer/>
            
            <param name="csv_delimiter" type="string" gui-text="CSV delimiter:">,</param>
            <param name="skip_header" type="bool" gui-text="Skip header row">true</param>
            <spacer/>
            
            <param name="x_column" type="int" min="0" max="100" gui-text="X column index (0-based):">0</param>
            <param name="y_column" type="int" min="0" max="100" gui-text="Y column index (0-based):">1</param>
            <spacer/>
            
            <label>When using Script Bank with data import:</label>
            <label>- x_data and y_data arrays will be available</label>
            <label>- df (DataFrame) available for CSV/Excel</label>
        </page>
        
        <page name="help" gui-text="Help">
            <label appearance="header">Matplotlib Figure Generator</label>
            <spacer/>
            <label>How to use:</label>
            <label>1. Ensure matplotlib is installed (pip install matplotlib)</label>
            <label>2. Select script source: inline, file, or Script Bank</label>
            <label>3. For Script Bank: choose category and script</label>
            <label>4. Configure format, style, and placement</label>
            <label>5. Optionally import data from CSV/Excel</label>
            <label>6. Click Apply to generate and insert figure</label>
            <spacer/>
            <label appearance="header">Script Bank Categories:</label>
            <label>• Line Plots: Basic, multi-line, error bars, filled</label>
            <label>• Scatter: Basic, regression, bubble charts</label>
            <label>• Bar Charts: Basic, grouped, stacked, horizontal</label>
            <label>• Statistical: Box plots, violin, error bars</label>
            <label>• Heatmaps: Correlation matrices, basic heatmaps</label>
            <label>• Time Series: Single/dual axis temporal data</label>
            <label>• Distributions: Histograms, KDE plots</label>
            <label>• Multi-Panel: 2x2 grids, comparisons</label>
            <spacer/>
            <label appearance="header">Figure Sizing:</label>
            <label>- Width/height in inches (matplotlib standard)</label>
            <label>- DPI: 96 (screen), 150 (draft), 300 (print)</label>
            <label>- Example: 8" × 6" at 96 DPI = 768 × 576 px</label>
            <spacer/>
            <label>Required: matplotlib, numpy</label>
            <label>Optional: pandas (for data import)</label>
        </page>
    </param>
    
    <effect>
        <object-type>all</object-type>
        <effects-menu>
            <submenu name="Generate"/>
        </effects-menu>
    </effect>
    
    <script>
        <command location="inx" interpreter="python">plt_ink.py</command>
    </script>
</inkscape-extension>
````

Now let's create the script bank directory structure and scripts:

````python
# Basic Line Plot
# Plots x_data vs y_data with customizable styling

if 'x_data' not in dir() or 'y_data' not in dir():
    # Generate sample data if no data file loaded
    x_data = np.linspace(0, 10, 50)
    y_data = np.sin(x_data) + np.random.normal(0, 0.1, len(x_data))

plt.plot(x_data, y_data, marker='o', linestyle='-', linewidth=_fig_width/4, 
         markersize=_fig_width/2, color='#2563eb', label='Data')

plt.title('Line Plot', fontsize=_fig_height * 2)
plt.xlabel('X Values', fontsize=_fig_height * 1.5)
plt.ylabel('Y Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Multiple Lines with Legend
# Plots multiple data series for comparison

if 'x_data' not in dir():
    x_data = np.linspace(0, 10, 50)

# If only x_data and y_data exist, create additional series
if 'y_data' in dir():
    y1 = y_data
    y2 = y_data * 0.8 + np.random.normal(0, 0.1, len(x_data))
    y3 = y_data * 1.2 + np.random.normal(0, 0.1, len(x_data))
else:
    y1 = np.sin(x_data)
    y2 = np.cos(x_data)
    y3 = np.sin(x_data + np.pi/4)

colors = ['#2563eb', '#dc2626', '#16a34a']
labels = ['Series A', 'Series B', 'Series C']
markers = ['o', 's', '^']

for i, (y, color, label, marker) in enumerate(zip([y1, y2, y3], colors, labels, markers)):
    plt.plot(x_data, y, marker=marker, linestyle='-', linewidth=1.5,
             markersize=5, color=color, label=label, markevery=5)

plt.title('Multi-Line Comparison', fontsize=_fig_height * 2)
plt.xlabel('X Values', fontsize=_fig_height * 1.5)
plt.ylabel('Y Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position, framealpha=0.9)
````

````python
# Line Plot with Error Bars
# Shows data with uncertainty/standard deviation

if 'x_data' not in dir() or 'y_data' not in dir():
    x_data = np.arange(1, 11)
    y_data = np.array([2.3, 3.1, 4.5, 5.2, 6.8, 7.1, 8.3, 9.0, 9.8, 10.5])

# Calculate or use provided errors
if 'y_error' not in dir():
    y_error = np.abs(y_data) * 0.1 + 0.2  # 10% + baseline error

plt.errorbar(x_data, y_data, yerr=y_error, fmt='o-', capsize=4, capthick=1.5,
             color='#2563eb', ecolor='#64748b', markersize=6, linewidth=1.5,
             label='Measured Data')

plt.title('Measurements with Error Bars', fontsize=_fig_height * 2)
plt.xlabel('Sample Number', fontsize=_fig_height * 1.5)
plt.ylabel('Measured Value', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Filled Area Plot
# Shows data with shaded confidence interval or range

if 'x_data' not in dir() or 'y_data' not in dir():
    x_data = np.linspace(0, 10, 100)
    y_data = np.sin(x_data) * np.exp(-x_data/10)

# Calculate bounds (mean ± std or custom)
if 'y_lower' not in dir() or 'y_upper' not in dir():
    uncertainty = np.abs(y_data) * 0.2 + 0.1
    y_lower = y_data - uncertainty
    y_upper = y_data + uncertainty

plt.fill_between(x_data, y_lower, y_upper, alpha=0.3, color='#2563eb', label='95% CI')
plt.plot(x_data, y_data, color='#1d4ed8', linewidth=2, label='Mean')

plt.title('Data with Confidence Interval', fontsize=_fig_height * 2)
plt.xlabel('X Values', fontsize=_fig_height * 1.5)
plt.ylabel('Y Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Basic Scatter Plot
# Simple x vs y scatter visualization

if 'x_data' not in dir() or 'y_data' not in dir():
    np.random.seed(42)
    x_data = np.random.randn(50) * 2 + 5
    y_data = x_data * 0.8 + np.random.randn(50) * 1.5 + 2

plt.scatter(x_data, y_data, s=60, c='#2563eb', alpha=0.7, 
            edgecolors='white', linewidths=0.5, label='Data Points')

plt.title('Scatter Plot', fontsize=_fig_height * 2)
plt.xlabel('X Variable', fontsize=_fig_height * 1.5)
plt.ylabel('Y Variable', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Scatter Plot with Linear Regression
# Shows data points with fitted trend line and R² value

if 'x_data' not in dir() or 'y_data' not in dir():
    np.random.seed(42)
    x_data = np.linspace(0, 10, 30)
    y_data = 2.5 * x_data + 3 + np.random.randn(30) * 2

# Calculate linear regression
coeffs = np.polyfit(x_data, y_data, 1)
poly = np.poly1d(coeffs)
y_fit = poly(x_data)

# Calculate R²
ss_res = np.sum((y_data - y_fit) ** 2)
ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
r_squared = 1 - (ss_res / ss_tot)

# Plot
plt.scatter(x_data, y_data, s=60, c='#2563eb', alpha=0.7, 
            edgecolors='white', linewidths=0.5, label='Data')
plt.plot(x_data, y_fit, 'r-', linewidth=2, 
         label=f'Fit: y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}\n$R^2$ = {r_squared:.3f}')

plt.title('Linear Regression Analysis', fontsize=_fig_height * 2)
plt.xlabel('Independent Variable (X)', fontsize=_fig_height * 1.5)
plt.ylabel('Dependent Variable (Y)', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Bubble Chart
# Scatter plot with variable point sizes representing a third dimension

if 'x_data' not in dir() or 'y_data' not in dir():
    np.random.seed(42)
    x_data = np.random.rand(20) * 10
    y_data = np.random.rand(20) * 10

# Size data (third dimension)
if 'size_data' not in dir():
    size_data = np.random.rand(len(x_data)) * 500 + 50

# Color data (optional fourth dimension)
if 'color_data' not in dir():
    color_data = np.random.rand(len(x_data))

scatter = plt.scatter(x_data, y_data, s=size_data, c=color_data, 
                      cmap=_colormap, alpha=0.6, edgecolors='white', linewidths=1)

plt.colorbar(scatter, label='Color Scale')

plt.title('Bubble Chart (Size = Third Variable)', fontsize=_fig_height * 2)
plt.xlabel('X Variable', fontsize=_fig_height * 1.5)
plt.ylabel('Y Variable', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')
````

````python
# Basic Bar Chart
# Vertical bar chart for categorical data

if 'x_data' not in dir() or 'y_data' not in dir():
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    x_data = np.arange(len(categories))
    y_data = np.array([23, 45, 56, 78, 32])
else:
    categories = [f'Cat {i+1}' for i in range(len(x_data))]

colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(x_data)))

bars = plt.bar(x_data, y_data, color=colors, edgecolor='white', linewidth=1)

# Add value labels on bars
for bar, val in zip(bars, y_data):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(y_data)*0.02,
             f'{val:.1f}', ha='center', va='bottom', fontsize=9)

plt.xticks(x_data, categories, rotation=45, ha='right')
plt.title('Bar Chart', fontsize=_fig_height * 2)
plt.xlabel('Categories', fontsize=_fig_height * 1.5)
plt.ylabel('Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
````

````python
# Grouped Bar Chart
# Compare multiple series across categories

categories = ['Group 1', 'Group 2', 'Group 3', 'Group 4']
n_categories = len(categories)

if 'y_data' in dir() and len(y_data) >= n_categories * 2:
    series1 = y_data[:n_categories]
    series2 = y_data[n_categories:n_categories*2]
    series3 = y_data[n_categories*2:n_categories*3] if len(y_data) >= n_categories*3 else None
else:
    series1 = np.array([20, 35, 30, 35])
    series2 = np.array([25, 32, 34, 20])
    series3 = np.array([15, 25, 28, 30])

x = np.arange(n_categories)
width = 0.25

plt.bar(x - width, series1, width, label='Series A', color='#2563eb', edgecolor='white')
plt.bar(x, series2, width, label='Series B', color='#dc2626', edgecolor='white')
if series3 is not None:
    plt.bar(x + width, series3, width, label='Series C', color='#16a34a', edgecolor='white')

plt.xticks(x, categories)
plt.title('Grouped Bar Chart Comparison', fontsize=_fig_height * 2)
plt.xlabel('Categories', fontsize=_fig_height * 1.5)
plt.ylabel('Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Stacked Bar Chart
# Show composition of totals across categories

categories = ['Q1', 'Q2', 'Q3', 'Q4']
n_categories = len(categories)

if 'y_data' in dir() and len(y_data) >= n_categories * 2:
    component1 = y_data[:n_categories]
    component2 = y_data[n_categories:n_categories*2]
    component3 = y_data[n_categories*2:n_categories*3] if len(y_data) >= n_categories*3 else np.zeros(n_categories)
else:
    component1 = np.array([20, 25, 30, 35])
    component2 = np.array([15, 20, 25, 20])
    component3 = np.array([10, 15, 10, 15])

x = np.arange(n_categories)

plt.bar(x, component1, label='Component A', color='#2563eb', edgecolor='white')
plt.bar(x, component2, bottom=component1, label='Component B', color='#dc2626', edgecolor='white')
plt.bar(x, component3, bottom=component1+component2, label='Component C', color='#16a34a', edgecolor='white')

plt.xticks(x, categories)
plt.title('Stacked Bar Chart', fontsize=_fig_height * 2)
plt.xlabel('Time Period', fontsize=_fig_height * 1.5)
plt.ylabel('Total Value', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Horizontal Bar Chart
# Good for long category names or ranking data

if 'x_data' not in dir() or 'y_data' not in dir():
    categories = ['Long Category Name A', 'Category B', 'Another Long Name C', 
                  'Category D', 'Extended Category E', 'Category F']
    y_data = np.array([85, 72, 68, 54, 48, 35])
else:
    categories = [f'Item {i+1}' for i in range(len(y_data))]

# Sort by value
sorted_idx = np.argsort(y_data)
y_sorted = y_data[sorted_idx]
categories_sorted = [categories[i] for i in sorted_idx]

colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(y_data)))

y_pos = np.arange(len(categories))
bars = plt.barh(y_pos, y_sorted, color=colors[sorted_idx], edgecolor='white', height=0.6)

# Add value labels
for bar, val in zip(bars, y_sorted):
    plt.text(val + max(y_sorted)*0.02, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}', va='center', fontsize=9)

plt.yticks(y_pos, categories_sorted)
plt.title('Horizontal Bar Chart (Ranked)', fontsize=_fig_height * 2)
plt.xlabel('Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='x')
````

````python
# Box Plot
# Statistical distribution visualization showing median, quartiles, and outliers

if 'data' in dir() and hasattr(data, 'values'):
    # Use loaded DataFrame columns
    plot_data = [data.iloc[:, i].dropna().values for i in range(min(5, data.shape[1]))]
    labels = list(data.columns[:5])
else:
    # Generate sample data
    np.random.seed(42)
    plot_data = [np.random.normal(loc, 1.5, 50) for loc in [3, 4, 5, 4.5, 3.5]]
    labels = ['Group A', 'Group B', 'Group C', 'Group D', 'Group E']

bp = plt.boxplot(plot_data, labels=labels, patch_artist=True, 
                 notch=True, showmeans=True,
                 meanprops=dict(marker='D', markerfacecolor='red', markersize=6))

# Color the boxes
colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(plot_data)))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

plt.title('Box Plot Distribution Analysis', fontsize=_fig_height * 2)
plt.xlabel('Groups', fontsize=_fig_height * 1.5)
plt.ylabel('Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
````

````python
# Violin Plot
# Shows probability density of data at different values

if 'data' in dir() and hasattr(data, 'values'):
    plot_data = [data.iloc[:, i].dropna().values for i in range(min(5, data.shape[1]))]
    labels = list(data.columns[:5])
else:
    np.random.seed(42)
    plot_data = [
        np.concatenate([np.random.normal(3, 0.5, 30), np.random.normal(5, 0.3, 20)]),
        np.random.normal(4, 1, 50),
        np.random.exponential(2, 50) + 1,
        np.random.normal(4.5, 0.8, 50),
        np.random.uniform(2, 6, 50)
    ]
    labels = ['Bimodal', 'Normal', 'Skewed', 'Narrow', 'Uniform']

parts = plt.violinplot(plot_data, showmeans=True, showmedians=True, showextrema=True)

# Color the violins
colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(plot_data)))
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(colors[i])
    pc.set_alpha(0.7)

plt.xticks(range(1, len(labels) + 1), labels)
plt.title('Violin Plot - Distribution Comparison', fontsize=_fig_height * 2)
plt.xlabel('Groups', fontsize=_fig_height * 1.5)
plt.ylabel('Values', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
````

````python
# Error Bar Comparison Plot
# Compare means with error bars (standard deviation/error)

if 'y_data' in dir():
    means = y_data[:5] if len(y_data) >= 5 else y_data
    errors = means * 0.15
    labels = [f'Condition {i+1}' for i in range(len(means))]
else:
    means = np.array([4.2, 5.8, 3.9, 6.1, 4.7])
    errors = np.array([0.5, 0.7, 0.4, 0.8, 0.6])
    labels = ['Control', 'Treatment A', 'Treatment B', 'Treatment C', 'Treatment D']

x = np.arange(len(means))
colors = plt.cm.get_cmap(_colormap)(np.linspace(0.2, 0.8, len(means)))

bars = plt.bar(x, means, yerr=errors, capsize=5, color=colors, 
               edgecolor='white', linewidth=1, error_kw={'linewidth': 1.5})

# Add significance markers (example)
max_val = max(means + errors)
plt.plot([0, 1], [max_val * 1.1, max_val * 1.1], 'k-', linewidth=1)
plt.text(0.5, max_val * 1.12, '*', ha='center', fontsize=14)

plt.xticks(x, labels, rotation=45, ha='right')
plt.title('Mean Comparison with Error Bars', fontsize=_fig_height * 2)
plt.xlabel('Conditions', fontsize=_fig_height * 1.5)
plt.ylabel('Mean Value ± SE', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')
````

````python
# Correlation Matrix Heatmap
# Visualize correlations between variables

if 'data' in dir() and hasattr(data, 'corr'):
    corr_matrix = data.corr()
    labels = list(data.columns)
else:
    # Generate sample correlation matrix
    np.random.seed(42)
    n_vars = 6
    labels = ['Var A', 'Var B', 'Var C', 'Var D', 'Var E', 'Var F']
    # Create a valid correlation matrix
    random_data = np.random.randn(100, n_vars)
    random_data[:, 1] = random_data[:, 0] * 0.8 + np.random.randn(100) * 0.3
    random_data[:, 2] = -random_data[:, 0] * 0.6 + np.random.randn(100) * 0.5
    corr_matrix = np.corrcoef(random_data.T)

im = plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
plt.colorbar(im, label='Correlation Coefficient')

# Add text annotations
for i in range(len(labels)):
    for j in range(len(labels)):
        val = corr_matrix[i, j] if isinstance(corr_matrix, np.ndarray) else corr_matrix.iloc[i, j]
        color = 'white' if abs(val) > 0.5 else 'black'
        plt.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=9)

plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
plt.yticks(range(len(labels)), labels)
plt.title('Correlation Matrix', fontsize=_fig_height * 2)
````

````python
# Basic Heatmap
# 2D data visualization with color mapping

if 'data' in dir() and hasattr(data, 'values'):
    heatmap_data = data.values[:20, :20]  # Limit size
    x_labels = list(data.columns[:20])
    y_labels = list(data.index[:20])
else:
    # Generate sample data
    np.random.seed(42)
    heatmap_data = np.random.rand(8, 10) * 100
    x_labels = [f'Col {i+1}' for i in range(10)]
    y_labels = [f'Row {i+1}' for i in range(8)]

im = plt.imshow(heatmap_data, cmap=_colormap, aspect='auto')
plt.colorbar(im, label='Value')

# Add text annotations if data is small enough
if heatmap_data.shape[0] <= 10 and heatmap_data.shape[1] <= 12:
    for i in range(heatmap_data.shape[0]):
        for j in range(heatmap_data.shape[1]):
            val = heatmap_data[i, j]
            color = 'white' if val > (heatmap_data.max() + heatmap_data.min())/2 else 'black'
            plt.text(j, i, f'{val:.1f}', ha='center', va='center', color=color, fontsize=8)

plt.xticks(range(len(x_labels)), x_labels, rotation=45, ha='right')
plt.yticks(range(len(y_labels)), y_labels)
plt.title('Heatmap Visualization', fontsize=_fig_height * 2)
````

````python
# Basic Time Series Plot
# Temporal data visualization

if 'x_data' in dir() and 'y_data' in dir():
    time_data = x_data
    values = y_data
else:
    # Generate sample time series
    np.random.seed(42)
    n_points = 100
    time_data = np.arange(n_points)
    trend = np.linspace(0, 5, n_points)
    seasonal = 2 * np.sin(2 * np.pi * time_data / 12)
    noise = np.random.randn(n_points) * 0.5
    values = trend + seasonal + noise

plt.plot(time_data, values, color='#2563eb', linewidth=1.5, label='Time Series')

# Add trend line
z = np.polyfit(time_data, values, 1)
p = np.poly1d(z)
plt.plot(time_data, p(time_data), '--', color='#dc2626', linewidth=2, 
         label=f'Trend (slope={z[0]:.3f})')

plt.title('Time Series Analysis', fontsize=_fig_height * 2)
plt.xlabel('Time', fontsize=_fig_height * 1.5)
plt.ylabel('Value', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Dual Y-Axis Time Series
# Compare two metrics with different scales

fig, ax1 = plt.subplots(figsize=(_fig_width, _fig_height))

if 'x_data' in dir() and 'y_data' in dir():
    time_data = x_data
    series1 = y_data
    series2 = y_data * 10 + np.random.randn(len(y_data)) * 5
else:
    np.random.seed(42)
    n_points = 50
    time_data = np.arange(n_points)
    series1 = np.cumsum(np.random.randn(n_points)) + 50
    series2 = (np.sin(time_data / 5) + 1) * 500 + np.random.randn(n_points) * 50

# First axis
color1 = '#2563eb'
ax1.set_xlabel('Time', fontsize=_fig_height * 1.5)
ax1.set_ylabel('Metric A', color=color1, fontsize=_fig_height * 1.5)
line1 = ax1.plot(time_data, series1, color=color1, linewidth=2, label='Metric A')
ax1.tick_params(axis='y', labelcolor=color1)

# Second axis
ax2 = ax1.twinx()
color2 = '#dc2626'
ax2.set_ylabel('Metric B', color=color2, fontsize=_fig_height * 1.5)
line2 = ax2.plot(time_data, series2, color=color2, linewidth=2, linestyle='--', label='Metric B')
ax2.tick_params(axis='y', labelcolor=color2)

# Combined legend
lines = line1 + line2
labels = [l.get_label() for l in lines]
if _show_legend:
    ax1.legend(lines, labels, loc=_legend_position)

plt.title('Dual-Axis Time Series', fontsize=_fig_height * 2)

if _show_grid:
    ax1.grid(True, alpha=0.3, linestyle='--')
````

````python
# Histogram
# Frequency distribution of data

if 'y_data' in dir():
    data_vals = y_data
else:
    np.random.seed(42)
    data_vals = np.concatenate([
        np.random.normal(25, 5, 200),
        np.random.normal(45, 8, 150)
    ])

n, bins, patches = plt.hist(data_vals, bins='auto', color='#2563eb', 
                             edgecolor='white', alpha=0.7, density=False)

# Color gradient based on height
cm = plt.cm.get_cmap(_colormap)
bin_centers = 0.5 * (bins[:-1] + bins[1:])
col = (bin_centers - bin_centers.min()) / (bin_centers.max() - bin_centers.min())
for c, p in zip(col, patches):
    plt.setp(p, 'facecolor', cm(c))

plt.axvline(np.mean(data_vals), color='red', linestyle='--', linewidth=2, 
            label=f'Mean: {np.mean(data_vals):.2f}')
plt.axvline(np.median(data_vals), color='orange', linestyle=':', linewidth=2, 
            label=f'Median: {np.median(data_vals):.2f}')

plt.title('Histogram - Data Distribution', fontsize=_fig_height * 2)
plt.xlabel('Value', fontsize=_fig_height * 1.5)
plt.ylabel('Frequency', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--', axis='y')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Kernel Density Estimation Plot
# Smooth probability density function

from scipy import stats

if 'y_data' in dir():
    data_vals = y_data
else:
    np.random.seed(42)
    data_vals = np.concatenate([
        np.random.normal(30, 5, 150),
        np.random.normal(50, 3, 100)
    ])

# Calculate KDE
kde = stats.gaussian_kde(data_vals)
x_range = np.linspace(data_vals.min() - 5, data_vals.max() + 5, 200)
density = kde(x_range)

plt.fill_between(x_range, density, alpha=0.5, color='#2563eb', label='KDE')
plt.plot(x_range, density, color='#1d4ed8', linewidth=2)

# Add rug plot
plt.plot(data_vals, np.zeros_like(data_vals) - 0.002, '|', color='#64748b', 
         markersize=10, alpha=0.5, label='Data points')

plt.title('Kernel Density Estimation', fontsize=_fig_height * 2)
plt.xlabel('Value', fontsize=_fig_height * 1.5)
plt.ylabel('Density', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# Histogram with KDE Overlay
# Combined frequency and density visualization

from scipy import stats

if 'y_data' in dir():
    data_vals = y_data
else:
    np.random.seed(42)
    data_vals = np.random.gamma(5, 2, 300)

# Histogram (normalized)
n, bins, patches = plt.hist(data_vals, bins='auto', color='#2563eb', 
                             edgecolor='white', alpha=0.5, density=True, label='Histogram')

# KDE overlay
kde = stats.gaussian_kde(data_vals)
x_range = np.linspace(data_vals.min(), data_vals.max(), 200)
plt.plot(x_range, kde(x_range), color='#dc2626', linewidth=2.5, label='KDE')

# Statistics
mean_val = np.mean(data_vals)
std_val = np.std(data_vals)
plt.axvline(mean_val, color='#16a34a', linestyle='--', linewidth=2, 
            label=f'Mean: {mean_val:.2f}')

# Normal distribution for comparison
from scipy.stats import norm
x_norm = np.linspace(data_vals.min(), data_vals.max(), 100)
plt.plot(x_norm, norm.pdf(x_norm, mean_val, std_val), 'k:', linewidth=1.5, 
         alpha=0.7, label='Normal fit')

plt.title('Distribution Analysis', fontsize=_fig_height * 2)
plt.xlabel('Value', fontsize=_fig_height * 1.5)
plt.ylabel('Density', fontsize=_fig_height * 1.5)

if _show_grid:
    plt.grid(True, alpha=0.3, linestyle='--')

if _show_legend:
    plt.legend(loc=_legend_position)
````

````python
# 2x2 Subplot Grid
# Four related visualizations in one figure

fig, axes = plt.subplots(2, 2, figsize=(_fig_width, _fig_height))

if 'x_data' in dir() and 'y_data' in dir():
    x = x_data
    y = y_data
else:
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    y = np.sin(x) + np.random.randn(50) * 0.2

# Top-left: Line plot
axes[0, 0].plot(x, y, 'o-', color='#2563eb', markersize=4, linewidth=1.5)
axes[0, 0].set_title('(a) Line Plot')
axes[0, 0].set_xlabel('X')
axes[0, 0].set_ylabel('Y')
if _show_grid:
    axes[0, 0].grid(True, alpha=0.3)

# Top-right: Scatter plot
axes[0, 1].scatter(x, y, c=y, cmap=_colormap, s=30, alpha=0.7)
axes[0, 1].set_title('(b) Scatter Plot')
axes[0, 1].set_xlabel('X')
axes[0, 1].set_ylabel('Y')
if _show_grid:
    axes[0, 1].grid(True, alpha=0.3)

# Bottom-left: Histogram
axes[1, 0].hist(y, bins=15, color='#2563eb', edgecolor='white', alpha=0.7)
axes[1, 0].axvline(np.mean(y), color='red', linestyle='--', label=f'Mean: {np.mean(y):.2f}')
axes[1, 0].set_title('(c) Distribution')
axes[1, 0].set_xlabel('Value')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].legend(fontsize=8)
if _show_grid:
    axes[1, 0].grid(True, alpha=0.3, axis='y')

# Bottom-right: Box plot
axes[1, 1].boxplot([y[:len(y)//2], y[len(y)//2:]], labels=['First Half', 'Second Half'])
axes[1, 1].set_title('(d) Comparison')
axes[1, 1].set_ylabel('Value')
if _show_grid:
    axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.suptitle('Multi-Panel Analysis', fontsize=_fig_height * 2, y=1.02)
````

````python
# Side-by-side Comparison
# Two panel figure for before/after or method comparison

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(_fig_width, _fig_height))

if 'x_data' in dir() and 'y_data' in dir():
    x = x_data
    y1 = y_data
    y2 = y_data * 1.2 + np.random.randn(len(y_data)) * 0.3
else:
    np.random.seed(42)
    x = np.linspace(0, 10, 30)
    y1 = 2 * x + 1 + np.random.randn(30) * 2
    y2 = 2.2 * x + 0.5 + np.random.randn(30) * 1.5

# Left panel: Method A / Before
ax1.scatter(x, y1, color='#2563eb', s=50, alpha=0.7, label='Data')
z1 = np.polyfit(x, y1, 1)
ax1.plot(x, np.poly1d(z1)(x), '--', color='#dc2626', linewidth=2, label=f'Fit (R²={np.corrcoef(x, y1)[0,1]**2:.3f})')
ax1.set_title('(a) Method A / Before', fontsize=12)
ax1.set_xlabel('X Variable')
ax1.set_ylabel('Y Variable')
if _show_legend:
    ax1.legend(loc='upper left', fontsize=9)
if _show_grid:
    ax1.grid(True, alpha=0.3)

# Right panel: Method B / After
ax2.scatter(x, y2, color='#16a34a', s=50, alpha=0.7, label='Data')
z2 = np.polyfit(x, y2, 1)
ax2.plot(x, np.poly1d(z2)(x), '--', color='#dc2626', linewidth=2, label=f'Fit (R²={np.corrcoef(x, y2)[0,1]**2:.3f})')
ax2.set_title('(b) Method B / After', fontsize=12)
ax2.set_xlabel('X Variable')
ax2.set_ylabel('Y Variable')
if _show_legend:
    ax2.legend(loc='upper left', fontsize=9)
if _show_grid:
    ax2.grid(True, alpha=0.3)

# Match y-axis limits
y_min = min(ax1.get_ylim()[0], ax2.get_ylim()[0])
y_max = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
ax1.set_ylim(y_min, y_max)
ax2.set_ylim(y_min, y_max)

plt.suptitle('Comparison Analysis', fontsize=_fig_height * 2)
````

Now create sample CSV files for testing:

````csv
Sample,Measurement,Error,Treatment
1,23.5,1.2,Control
2,25.1,0.9,Control
3,22.8,1.5,Control
4,24.2,1.1,Control
5,23.9,1.0,Control
6,31.2,1.4,Drug A
7,29.8,1.6,Drug A
8,32.5,1.2,Drug A
9,30.1,1.3,Drug A
10,31.8,1.1,Drug A
11,28.4,1.5,Drug B
12,27.9,1.2,Drug B
13,29.1,1.4,Drug B
14,28.2,1.1,Drug B
15,28.7,1.3,Drug B
````

````csv
Time,Temperature,Humidity,Pressure
0,22.5,45.2,1013.2
1,22.8,44.8,1013.1
2,23.1,44.5,1013.0
3,23.5,44.1,1012.9
4,24.2,43.5,1012.8
5,24.8,42.8,1012.6
6,25.5,42.0,1012.5
7,26.1,41.2,1012.4
8,26.5,40.5,1012.3
9,26.8,40.0,1012.2
10,27.0,39.5,1012.1
11,26.9,39.8,1012.2
12,26.5,40.2,1012.3
13,26.0,41.0,1012.5
14,25.4,42.0,1012.7
15,24.8,43.0,1012.9
16,24.2,44.0,1013.1
17,23.5,45.0,1013.3
18,23.0,45.8,1013.5
19,22.5,46.5,1013.6
20,22.2,47.0,1013.7
21,22.0,47.5,1013.8
22,22.0,47.8,1013.8
23,22.2,47.5,1013.7
````

````csv
Wavelength,Absorbance,Reference
200,0.05,0.02
220,0.08,0.03
240,0.15,0.05
260,0.85,0.08
280,0.92,0.10
300,0.45,0.12
320,0.22,0.11
340,0.15,0.09
360,0.12,0.07
380,0.10,0.06
400,0.08,0.05
420,0.07,0.04
440,0.06,0.04
460,0.06,0.03
480,0.05,0.03
500,0.05,0.02
520,0.04,0.02
540,0.04,0.02
560,0.04,0.02
580,0.03,0.01
600,0.03,0.01
````

````csv
Category,Score_2023,Score_2024,Sample_Size
Customer Satisfaction,7.2,7.8,450
Product Quality,8.1,8.4,450
Delivery// filepath: c:\Users\youve\AppData\Roaming\inkscape\extensions\dev\plt_ink_scripts\sample_data\survey_results.csv
Category,Score_2023,Score_2024,Sample_Size
Customer Satisfaction,7.2,7.8,450
Product Quality,8.1,8.4,450
Delivery