
<div align="center">

# Matplotlib Figure Generator for Inkscape

[![Inkscape](https://img.shields.io/badge/Inkscape-1.0+-blue.svg)](https://inkscape.org/)
[![Python](https://img.shields.io/badge/Python-3.6+-green.svg)](https://www.python.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.0+-orange.svg)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Generate and embed matplotlib figures directly in Inkscape**

A powerful Inkscape extension that allows you to create matplotlib visualizations and insert them seamlessly into your SVG documents. Perfect for scientific illustrations, data visualization in design projects, and publication-ready graphics.

</div>

## 📺 Demo

<div align="center">

<!-- Replace VIDEO_ID with your actual YouTube video ID -->
[![Watch the Demo](https://img.youtube.com/vi/lmj0Jzv106A/maxresdefault.jpg)](https://www.youtube.com/watch?v=lmj0Jzv106A)

*Click to watch the full tutorial on YouTube*

</div>



---

## 📋 Table of Contents

- Features
- Installation
- Quick Start
- Usage Guide
- Dependencies
- Examples
- Troubleshooting
- Script Bank
- Contributing

---

## ✨ Features

- **📊 Multiple Script Sources**
  - **Inline Code**: Write matplotlib code directly in the extension dialog
  - **External File**: Load scripts from `.py` files
  - **Script Bank**: Pre-built templates for common plot types

- **🎨 Flexible Output Formats**
  - **SVG**: Native vector graphics, fully editable in Inkscape
  - **PNG**: High-resolution raster images
  - **PDF**: Publication-quality vector output

- **📁 Data Import Support**
  - CSV, Excel, JSON, and text file formats
  - Automatic column extraction
  - Pandas DataFrame integration

- **🎯 Customizable Styling**
  - Built-in matplotlib styles (seaborn, ggplot, etc.)
  - Font family and size controls
  - Color map selection
  - Grid and legend customization

- **📐 Smart Positioning**
  - Center, corners, or cursor-based placement
  - Automatic size calculation based on DPI
  - Preserve aspect ratio

---

## 📦 Installation

### Step 1: Locate Your Inkscape Extensions Directory

**Windows:**
```
C:\Users\[YourUsername]\AppData\Roaming\inkscape\extensions\
```

**macOS:**
```
~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/
```

**Linux:**
```
~/.config/inkscape/extensions/
```

### Step 2: Install the Extension

1. **Download/Clone the extension:**
   ```bash
   git clone https://github.com/YouvenZ/plt_ink.git
   ```

2. **Copy to extensions directory:**
   ```bash
   # Windows (PowerShell)
   Copy-Item -Recurse plt_ink [extensions-directory]\plt_ink
   
   # macOS/Linux
   cp -r plt_ink [extensions-directory]/plt_ink
   ```

3. **Verify file structure:**
   ```
   plt_ink/
   ├── plt_ink.py
   ├── plt_ink.inx
   ├── sample_data/          # example CSVs + imaging assets
   └── plt_ink_scripts/
       ├── evaluation/
       ├── analysis/
       ├── clinical/
       ├── stats/
       ├── imaging/
       └── basics/
   ```

4. **Restart Inkscape**

### Step 3: Verify Installation

Open Inkscape and check: **Extensions → Render → Matplotlib Figure Generator**

---

## 🚀 Quick Start

### Basic Example (Inline Code)

1. Open your document in Inkscape
2. Go to **Extensions → Render → Matplotlib Figure Generator**
3. In the Script tab, select **Inline Code** as source
4. Enter your matplotlib code:
   ```python
   import numpy as np
   x = np.linspace(0, 10, 100)
   y = np.sin(x)
   plt.plot(x, y, label='sin(x)')
   plt.xlabel('X axis')
   plt.ylabel('Y axis')
   plt.title('Simple Sine Wave')
   if _show_legend:
       plt.legend(loc=_legend_position)
   if _show_grid:
       plt.grid(True)
   ```
5. Click **Apply**

**Result:** A matplotlib figure appears in your Inkscape document!

---

## 📖 Usage Guide

### Script Tab

#### Inline Code Mode

<details>
<summary><b>Click to expand</b></summary>

Write matplotlib code directly in the text area. The extension provides:

**Pre-defined Variables:**
- `_fig_width` - Figure width from settings
- `_fig_height` - Figure height from settings
- `_dpi` - DPI setting
- `_show_grid` - Grid toggle
- `_show_legend` - Legend toggle
- `_legend_position` - Legend location
- `_colormap` - Selected colormap

**Auto-imported Modules:**
- `matplotlib.pyplot as plt`
- `numpy as np`

**Example:**
```python
# Data
x = np.linspace(0, 2*np.pi, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Plot
plt.plot(x, y1, label='sin(x)', color='blue')
plt.plot(x, y2, label='cos(x)', color='red')

plt.title('Trigonometric Functions')
plt.xlabel('Radians')
plt.ylabel('Value')

if _show_legend:
    plt.legend(loc=_legend_position)
if _show_grid:
    plt.grid(True, alpha=0.3)
```

</details>

#### External File Mode

<details>
<summary><b>Click to expand</b></summary>

Load a Python script from your filesystem:

1. Select **External File** as source
2. Browse to your `.py` file
3. Click Apply

**File Requirements:**
- Must use `plt` for plotting
- Don't call `plt.show()` (handled automatically)
- Don't call `plt.savefig()` (handled automatically)

</details>

#### Script Bank Mode

<details>
<summary><b>Click to expand</b></summary>

Use pre-built templates from the script bank:

**Available Categories:**
| Category | Description |
|----------|-------------|
| `evaluation` | Training curves, ROC/PR, confusion matrix, calibration, model comparison |
| `analysis` | Hyperparameter sweeps, Pareto fronts, learning curves, SHAP, embeddings |
| `clinical` | Kaplan-Meier, forest plots, Bland-Altman, volcano, dose-response |
| `stats` | Rainclouds, paired slopes, joint scatter, parity/residuals, clustermaps |
| `imaging` | Segmentation panels and metrics, Grad-CAM, spectra, composite figures |
| `basics` | 3D surfaces, contours, vector fields, dual-axis series, a demo figure |

**How to use:**
1. Click **Templates…** on the Script tab
2. Search or filter by category; the description shows the columns the
   template expects and the example data it falls back to
3. Click Apply

Every template in the first five categories is data-driven: it reads the file
selected on the Data tab when the columns match, and otherwise falls back to a
bundled example in `sample_data/`, so it always renders.

</details>

### Format Tab

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Output Format | SVG | SVG/PNG/PDF | Output file format |
| Figure Width | 8.0 | 1-20 | Width in inches |
| Figure Height | 6.0 | 1-20 | Height in inches |
| DPI | 96 | 72-600 | Resolution |
| Transparent | No | Yes/No | Transparent background |
| Tight Layout | Yes | Yes/No | Remove extra whitespace |

### Style Tab

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| Plot Style | default | default, seaborn, ggplot, etc. | Matplotlib style |
| Color Map | viridis | viridis, plasma, etc. | Default colormap |
| Show Grid | Yes | Yes/No | Enable grid |
| Show Legend | Yes | Yes/No | Enable legend |
| Legend Position | best | best, upper right, etc. | Legend location |

### Placement Tab

| Parameter | Default | Description |
|-----------|---------|-------------|
| Position Mode | center | Where to place the figure |
| Embed Image | Yes | Embed as data URI vs. link |

**Position Options:**
- `center` - Center of document
- `top_left`, `top_center`, `top_right`
- `bottom_left`, `bottom_center`, `bottom_right`
- `cursor` - At selected object position

### Advanced Tab

| Parameter | Default | Description |
|-----------|---------|-------------|
| Font Family | sans-serif | Plot font family |
| Font Size | 10 | Base font size |
| Line Width | 1.5 | Default line width |
| Marker Size | 6.0 | Default marker size |
| Use LaTeX | No | LaTeX text rendering |
| Save Script | No | Save generated script |
| Keep Temp Files | No | Don't delete temp files |

### Data Import Tab

<details>
<summary><b>Click to expand</b></summary>

Import external data files for plotting:

**Supported Formats:**
| Format | Extension | Description |
|--------|-----------|-------------|
| CSV | .csv | Comma-separated values |
| Excel | .xlsx, .xls | Excel spreadsheets |
| JSON | .json | JSON arrays/objects |
| Text | .txt, .dat | Space/tab-delimited |

**Parameters:**
- **Data File Path**: Path to your data file
- **CSV Delimiter**: Separator character (default: `,`)
- **Skip Header**: Skip first row
- **X Column**: Column index for X data
- **Y Column**: Column index for Y data

**Available Variables (after import):**
- `x_data` - X column as numpy array
- `y_data` - Y column as numpy array
- `data` or `df` - Full DataFrame

**Example with CSV:**
```python
# x_data and y_data are automatically loaded
plt.scatter(x_data, y_data, c='blue', alpha=0.6)
plt.xlabel('X Values')
plt.ylabel('Y Values')
```

</details>

---

## 🔧 Dependencies

### Core Requirements (Required)

| Component | Version | Purpose |
|-----------|---------|---------|
| **Inkscape** | 1.0+ | Vector graphics editor |
| **Python** | 3.6+ | Extension runtime |
| **matplotlib** | 3.0+ | Plotting library |
| **numpy** | 1.15+ | Numerical computing |

**Installation:**
```bash
pip install matplotlib numpy
```

### Optional Dependencies

| Component | Purpose | Installation |
|-----------|---------|--------------|
| **pandas** | Data file import | `pip install pandas` |
| **openpyxl** | Excel file support | `pip install openpyxl` |
| **LaTeX** | LaTeX text rendering | Install TeX distribution |

**Check Installation:**
```bash
python -c "import matplotlib; print(matplotlib.__version__)"
python -c "import numpy; print(numpy.__version__)"
```

---

## 💡 Examples

### Example 1: Simple Line Plot

**Inline Code:**
```python
x = np.linspace(0, 10, 100)
y = np.sin(x) * np.exp(-x/10)

plt.plot(x, y, 'b-', linewidth=2, label='Damped sine')
plt.fill_between(x, y, alpha=0.3)
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title('Damped Oscillation')
plt.legend()
plt.grid(True, alpha=0.3)
```

### Example 2: Multi-Panel Figure

```python
fig, axes = plt.subplots(2, 2, figsize=(_fig_width, _fig_height))

x = np.linspace(0, 2*np.pi, 100)

axes[0,0].plot(x, np.sin(x))
axes[0,0].set_title('sin(x)')

axes[0,1].plot(x, np.cos(x))
axes[0,1].set_title('cos(x)')

axes[1,0].plot(x, np.tan(x))
axes[1,0].set_ylim(-5, 5)
axes[1,0].set_title('tan(x)')

axes[1,1].plot(x, np.sin(x)**2)
axes[1,1].set_title('sin²(x)')

for ax in axes.flat:
    ax.grid(True, alpha=0.3)
```

### Example 3: Scientific Visualization

```python
# Create meshgrid
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y)

# Contour plot
fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))
contour = ax.contourf(X, Y, Z, levels=20, cmap=_colormap)
plt.colorbar(contour, label='Value')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Contour Plot')
```

### Example 4: Using External Data

**CSV file (data.csv):**
```csv
time,temperature,humidity
0,20.5,65
1,21.2,63
2,22.1,60
3,23.5,58
4,24.0,55
```

**Script:**
```python
# x_data and y_data loaded from columns 0 and 1
# df contains full DataFrame

fig, ax1 = plt.subplots()

ax1.plot(df.iloc[:,0], df.iloc[:,1], 'b-', label='Temperature')
ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Temperature (°C)', color='b')

ax2 = ax1.twinx()
ax2.plot(df.iloc[:,0], df.iloc[:,2], 'r--', label='Humidity')
ax2.set_ylabel('Humidity (%)', color='r')

plt.title('Temperature and Humidity Over Time')
```

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Extension not appearing in menu</b></summary>

**Solutions:**
1. Check file locations match the expected structure
2. Verify file permissions:
   ```bash
   # Linux/macOS
   chmod +x plt_ink.py
   ```
3. Check Inkscape error console: **View → Messages**
4. Restart Inkscape completely
5. Verify Python path in extension settings

</details>

<details>
<summary><b>"Python not found" error</b></summary>

**Solutions:**
1. In the extension dialog, set **Python Path** to your Python executable:
   ```
   # Windows
   C:\Python39\python.exe
   
   # macOS/Linux
   /usr/bin/python3
   ```
2. Check Python installation:
   ```bash
   python --version
   python3 --version
   ```

</details>

<details>
<summary><b>"Matplotlib not installed" error</b></summary>

**Solutions:**
1. Install matplotlib for your Python version:
   ```bash
   pip install matplotlib
   # or
   pip3 install matplotlib
   ```
2. Verify installation:
   ```bash
   python -c "import matplotlib; print(matplotlib.__version__)"
   ```
3. Ensure you're using the same Python that Inkscape uses

</details>

<details>
<summary><b>Script execution fails</b></summary>

**Debug Steps:**
1. Enable **Keep Temp Files** in Advanced tab
2. Check the log file:
   ```
   # Windows
   %TEMP%\matplotlib_inkscape_debug.log
   
   # macOS/Linux
   /tmp/matplotlib_inkscape_debug.log
   ```
3. Check the generated script in temp directory
4. Run the script manually to see errors:
   ```bash
   python /tmp/matplotlib_output_*.py
   ```

</details>

<details>
<summary><b>Figure not appearing or wrong size</b></summary>

**Solutions:**
1. Check output format (SVG recommended for vector graphics)
2. Verify figure dimensions aren't too large
3. Check document units match expectations
4. Try enabling **Embed Image** option

</details>

### Debug Tips

**Check Log File:**
The extension writes detailed logs to:
```
[temp-directory]/matplotlib_inkscape_debug.log
```

**Test Inline Code:**
Start with a minimal example:
```python
plt.plot([1, 2, 3], [1, 4, 9])
plt.title('Test Plot')
```

**Verify Script Generation:**
1. Enable **Save Script** option
2. Set **Script Save Path** to a known location
3. Examine the generated script for issues

---

## 📚 Script Bank

Thirty templates: twenty-five data-driven research figures plus five basics.
Each research template declares the columns it needs and ships with an example
CSV, so it renders before you have configured anything. None of them require
scipy, seaborn or sklearn — numpy, pandas and matplotlib only.

#### Model Evaluation (`evaluation/`)
| Script | Figure | Needs |
|---|---|---|
| `training_curves.py` | Train/val curves, mean ± s.d. over seeds, LR schedule | `model, seed, epoch, split, loss, accuracy, lr` |
| `roc_pr_curves.py` | ROC + PR with bootstrap bands, AUC/AP, Youden point | `model, y_true, y_score` |
| `confusion_matrix.py` | Counts + row-normalised, per-class P/R/F1, κ | `y_true, y_pred` |
| `calibration_reliability.py` | Reliability diagram, ECE/MCE/Brier, score histogram | `model, y_true, y_score` |
| `model_comparison_stats.py` | Bars with per-seed dots and permutation-test brackets | `dataset, model, seed, score` |

#### Model Analysis (`analysis/`)
| Script | Figure | Needs |
|---|---|---|
| `hparam_sweep_heatmap.py` | 2-factor grid, best cell ringed, marginal best-of curves | `lr, batch_size, val_score` |
| `pareto_tradeoff.py` | Accuracy vs cost, Pareto front traced, size-coded markers | `model, accuracy, latency_ms, params_m` |
| `learning_curve_size.py` | Score vs training-set size with a fitted power law | `model, train_size, seed, score` |
| `feature_importance_shap.py` | SHAP beeswarm + ranked mean\|SHAP\| with bootstrap CI | `feature, sample_id, shap_value, feature_value` |
| `embedding_scatter.py` | t-SNE/UMAP with density contours and error rings | `x, y, label` |

#### Clinical & Biostatistics (`clinical/`)
| Script | Figure | Needs |
|---|---|---|
| `kaplan_meier.py` | Survival curves, censor ticks, at-risk table, log-rank, HR | `time, event, group` |
| `forest_plot.py` | Subgroup/meta estimates, weights, random-effects diamonds, I² | `study, subgroup, estimate, ci_low, ci_high, weight` |
| `bland_altman.py` | Bias, 95% LoA with CIs, proportional-bias test, Lin's CCC | `method_a, method_b` |
| `volcano_plot.py` | FDR + fold-change thresholds, labelled top hits | `gene, log2fc, pvalue, padj` |
| `dose_response.py` | 4PL fits, EC50 markers, bootstrap bands | `compound, dose, replicate, response` |

#### Distributions & Statistics (`stats/`)
| Script | Figure | Needs |
|---|---|---|
| `raincloud_groups.py` | Half-violin + box + points, permutation tests, Hedges' g | `group, value` |
| `paired_slope.py` | Per-subject before/after lines, sign-flip test, Cohen's dz | `subject, group, timepoint, value` |
| `joint_scatter_marginals.py` | Regression + CI band with marginal KDEs, r/R²/slope/p | `x, y, group` |
| `parity_residuals.py` | Predicted vs measured, residuals-vs-fitted, normal Q-Q | `y_true, y_pred, split` |
| `correlation_clustermap.py` | Hierarchically ordered correlations with dendrograms | any wide numeric table |

#### Imaging & Signals (`imaging/`)
| Script | Figure | Needs |
|---|---|---|
| `segmentation_panel.py` | Image / GT / prediction / FP-FN error map per case, with Dice | images + masks |
| `segmentation_metrics.py` | Per-structure Dice and HD95 boxplots, paired tests | `case_id, model, structure, dice, hd95` |
| `gradcam_grid.py` | Input / saliency / overlay grid, lesion enrichment and IoU | images + saliency maps |
| `signal_spectrum.py` | Time trace, Welch PSD with peak callouts, spectrogram | `channel, t, amplitude` |
| `composite_figure.py` | Four mixed panels, a/b/c/d labels, shared legend, caption | a CSV + an image |

#### Basics & Extras (`basics/`)
- `3d_surface.py`, `contour_plot.py`, `vector_field.py` — field and surface plots
- `time_series_dual_axis.py` — two series on twin y-axes
- `training_dynamics.py` — heavily annotated demo figure (needs scipy)

### Regenerating the example data

`sample_data/` is produced by a seeded generator, so it can be rebuilt or
resized at will:

```bash
python tools/make_sample_data.py
```

To check every template still renders after an edit:

```bash
python tools/render_bank.py            # with each template's example data injected
python tools/render_bank.py --no-data  # exercising the bundled-sample fallback
```

### Creating Custom Scripts

Add scripts to `plt_ink_scripts/[category]/`. The docstring is the metadata:
the first line is the title, the rest is the description, and any recognised
`key: value` line is parsed by `plt_ink_bank.py` and shown in the template
browser.

```python
"""
My Custom Plot Template
What this figure shows and when to use it.
requires_data: true                      # shows the "needs data" badge
data_columns: group, value               # validated against the chosen file
sample_data: group_measurements.csv      # fallback, relative to sample_data/
requires_image: true                     # optional
sample_image: images/case01_image.png    # optional
sample_mask: images/case01_mask_gt.png   # optional
tags: distribution, comparison           # searchable in the browser
note: requires scipy                     # caveat shown under the description
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Rename these to match your own file — nothing below uses raw column names.
COLS = dict(group='group', value='value')
SAMPLE = 'group_measurements.csv'


def _opt(name, default):
    """Read an extension setting, with a fallback when run standalone."""
    value = globals().get(name)
    return default if value is None else value


def _sample_dir():
    """Where the bundled example data lives. Looked up lazily: `__file__` is
    undefined when the code is exec'd inline."""
    root = globals().get('_sample_data_dir')
    if root:
        return root
    here = globals().get('__file__')
    if here:
        return os.path.join(os.path.dirname(os.path.abspath(here)),
                            '..', '..', 'sample_data')
    return 'sample_data'


def _load(sample, needed):
    """Use the extension's `data` when it carries the needed columns, else the
    bundled example — so the template always renders."""
    frame = globals().get('data')
    if frame is not None and not set(needed) - set(map(str, frame.columns)):
        return frame.copy()
    return pd.read_csv(os.path.join(_sample_dir(), sample))


df = _load(SAMPLE, COLS.values())

fig, ax = plt.subplots(figsize=(_opt('_fig_width', 8.0),
                                _opt('_fig_height', 5.0)),
                       layout='constrained')
ax.plot(df[COLS['value']].to_numpy())
ax.set_ylabel('Value')
```

**Variables the extension injects:** `_fig_width`, `_fig_height`, `_dpi`,
`_show_grid`, `_show_legend`, `_legend_position`, `_colormap`, `_transparent`,
`_subplot_rows`, `_subplot_cols`, `_sample_data_dir`, plus the helpers
`apply_style(ax)` and `get_cmap(name)`. Reading them through `_opt()` keeps the
template runnable outside the dialog.

**Layout note:** if you pass `layout='constrained'`, the extension skips its
own `tight_layout()` call, so your layout survives. Templates with
equal-aspect panels, colorbars or nested grids should use it.

---

## 📝 File Structure

```
plt_ink/
├── plt_ink.py              # Main extension code
├── plt_ink.inx             # Inkscape extension definition
├── README.md               # This file
├── LICENSE                 # MIT License
├── plt_ink_bank.py         # Category + template metadata (single source of truth)
├── tools/
│   ├── make_sample_data.py # Seeded generator for sample_data/
│   └── render_bank.py      # Headless render test for every template
├── sample_data/            # Example CSVs the templates fall back to
│   └── images/             # Example slices, masks and saliency maps
└── plt_ink_scripts/        # Template bank
    ├── evaluation/
    ├── analysis/
    ├── clinical/
    ├── stats/
    ├── imaging/
    └── basics/
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Adding Scripts to Bank:**
- Create your script in the appropriate category folder
- Include docstring with description
- Use pre-defined variables (`_fig_width`, `_show_grid`, etc.)
- Test with the extension before submitting

**Development Setup:**
```bash
git clone https://github.com/YouvenZ/plt_ink.git
cd plt_ink
# Symlink to extensions directory for testing
# Windows (PowerShell as Admin)
New-Item -ItemType Junction -Path "$env:APPDATA\inkscape\extensions\plt_ink" -Target "$(Get-Location)"
```

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

Copyright (c) 2026 Rachid, Youven ZEGHLACHE

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/YouvenZ/plt_ink/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YouvenZ/plt_ink/discussions)
- **Email**: youvenz.pro@gmail.com

---

## 🔄 Changelog

### v1.0.0 (2026-02-19)
- ✨ Initial release
- ✅ Inline code execution
- ✅ External file loading
- ✅ Script bank with templates
- ✅ SVG, PNG, PDF output formats
- ✅ Data import (CSV, Excel, JSON, Text)
- ✅ Multiple matplotlib styles
- ✅ Custom positioning options
- ✅ LaTeX support
- ✅ Comprehensive logging