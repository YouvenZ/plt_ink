<div align="center">

# 📊 plt_ink — Matplotlib Figure Generator for Inkscape

[![Inkscape](https://img.shields.io/badge/Inkscape-1.0+-blue.svg)](https://inkscape.org/)
[![Python](https://img.shields.io/badge/Python-3.6+-green.svg)](https://www.python.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.0+-orange.svg)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0-success.svg)](#changelog)

**Generate publication-ready scientific figures directly inside Inkscape**

Create matplotlib visualizations, load from your scripts, or use 30+ pre-built templates. Export as SVG (editable), PNG (raster), or PDF (print-ready). Perfect for academic papers, research posters, technical reports, and design projects.

> **Your figures. Your data. Your design. All in one place.**

</div>

---

## 🎯 What You Can Do

<table align="center">
  <tr>
    <td align="center"><strong>📈 Plot in Code</strong><br/>Write matplotlib in the dialog or load from files</td>
    <td align="center"><strong>🎨 Use Templates</strong><br/>30+ ready-to-use templates for common figures</td>
    <td align="center"><strong>📊 Import Data</strong><br/>CSV, Excel, JSON — auto-load and visualize</td>
  </tr>
  <tr>
    <td align="center"><strong>🖼️ Multiple Formats</strong><br/>SVG (editable), PNG (raster), PDF (print)</td>
    <td align="center"><strong>🎯 Smart Placement</strong><br/>Center, corners, cursor — you choose</td>
    <td align="center"><strong>✨ Live Preview</strong><br/>See changes instantly in your document</td>
  </tr>
</table>

---

## 📺 Demo & Quick Links

<div align="center">

[![Watch the Demo](https://img.youtube.com/vi/lmj0Jzv106A/maxresdefault.jpg)](https://www.youtube.com/watch?v=lmj0Jzv106A)

[🎬 Full Tutorial](https://www.youtube.com/watch?v=lmj0Jzv106A) • [📖 Script Bank](https://github.com/YouvenZ/plt_ink#-script-bank) • [🐛 Troubleshooting](#-troubleshooting) • [💬 Discussions](https://github.com/YouvenZ/plt_ink/discussions)

</div>

---

## 📋 Quick Links

- [⚡ Installation](#-installation)
- [🚀 Quick Start (2 min)](#-quick-start)
- [📖 Usage Guide](#-usage-guide)
- [📚 Script Bank Templates](#-script-bank) (30+ templates)
- [💡 Examples](#-examples)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)

---

## ✨ Key Features

| Feature | What It Does | Benefit |
|---------|-------------|---------|
| **3 Script Modes** | Inline code • External files • Pre-built templates | Work your way—code, files, or templates |
| **30+ Templates** | Research-ready figures for analysis, clinical, evaluation, imaging, stats | No setup needed; renders with example data immediately |
| **3 Export Formats** | SVG (editable) • PNG (raster) • PDF (print-ready) | Seamless publishing pipeline |
| **Data Import** | CSV, Excel, JSON, Text • Auto-column detection | Your data, your figures, instantly |
| **Smart Placement** | Center • corners • cursor tracking • size preview | Precise positioning every time |
| **Style Control** | 10+ matplotlib styles • custom fonts • colormaps • grid/legend toggles | Publication-ready styling in seconds |

---

## 📦 Full Installation

### Prerequisites

- **Inkscape** 1.0 or higher
- **Python** 3.6+ (with `matplotlib` and `numpy`)
- **pip** (to install Python packages)

**Install Python dependencies:**
```bash
pip install matplotlib numpy
# Optional: for data import features
pip install pandas openpyxl
```

### Installation Steps

<details>
<summary><b>📍 Step 1: Find Your Extensions Folder</b></summary>

| OS | Path |
|----|------|
| **Windows** | `C:\Users\[YourName]\AppData\Roaming\inkscape\extensions\` |
| **macOS** | `~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/` |
| **Linux** | `~/.config/inkscape/extensions/` |

</details>

<details>
<summary><b>📥 Step 2: Clone & Copy</b></summary>

```bash
# Clone the repository
git clone https://github.com/YouvenZ/plt_ink.git

# Copy to extensions folder
# Windows (PowerShell):
Copy-Item -Recurse plt_ink $env:APPDATA\inkscape\extensions\

# macOS/Linux:
cp -r plt_ink ~/.config/inkscape/extensions/
```

</details>

<details>
<summary><b>✅ Step 3: Verify & Restart</b></summary>

1. Restart Inkscape
2. Go to **Extensions → Render → Matplotlib Figure Generator**
3. You should see the dialog! 🎉

If it doesn't appear, see [Troubleshooting](#-troubleshooting).

</details>

---

## 🚀 Quick Start (2 minutes)

### Step 1️⃣ Install (One-time)

```bash
# Clone the repository
git clone https://github.com/YouvenZ/plt_ink.git

# Copy to your Inkscape extensions folder
# Windows:
Copy-Item -Recurse plt_ink $env:APPDATA\inkscape\extensions\

# macOS/Linux:
cp -r plt_ink ~/.config/inkscape/extensions/
```

**Then restart Inkscape.** ✅

### Step 2️⃣ Create Your First Plot

1. Open Inkscape → **Extensions → Render → Matplotlib Figure Generator**
2. Paste this code in the **Script** tab:

```python
import numpy as np
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y, linewidth=2, label='sin(x)')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('My First Figure')
if _show_legend:
    plt.legend()
```

3. Click **Apply** ✨

**Boom!** Your figure appears in the document.

### 💡 Next: Try Templates

Want a pre-built figure? 

1. Click **Templates…** on the Script tab
2. Pick any template (they work instantly with example data)
3. Click **Apply**

Each template shows what columns it needs. Once you have data, it'll use yours instead. No setup required.

---

## 📖 Complete Usage Guide

The extension dialog has 7 tabs. Here's what each does:

### 🔤 Script Tab — Write or Load Your Code

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

## 🔧 Requirements

### Must Have

| Package | Version | Why |
|---------|---------|-----|
| Inkscape | 1.0+ | The host application |
| Python | 3.6+ | Runs the extension |
| matplotlib | 3.0+ | Creates plots |
| numpy | 1.15+ | Numerical math |

**Install Python packages:**
```bash
pip install matplotlib numpy
```

### Optional (For More Features)

| Package | What It Enables |
|---------|-----------------|
| `pandas` | CSV/Excel import |
| `openpyxl` | `.xlsx` file support |
| `LaTeX` | Fancy math text (install TeX separately) |

**Verify your setup:**
```bash
python --version                              # Should be 3.6+
python -c "import matplotlib; print(matplotlib.__version__)"  # Should be 3.0+
python -c "import numpy; print(numpy.__version__)"            # Should be 1.15+
```

---

## 💡 Code Examples

Start with these. Copy → paste → click Apply.

### 📈 Example 1: Simple Line Plot

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

### 🎯 Example 2: Multi-Panel Figure (2×2 Grid)

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

### 🔬 Example 3: Scientific Visualization (Contour Plot)

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

### 📊 Example 4: Using External Data (Twin Y-Axes)

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

### Problem Solver

| Problem | Solution |
|---------|----------|
| **Extension doesn't appear in menu** | Restart Inkscape; check file locations match structure above |
| **"Python not found"** | Set Python Path in dialog (e.g., `C:\Python39\python.exe`) |
| **"Matplotlib not installed"** | Run `pip install matplotlib` then restart Inkscape |
| **Script execution fails** | Enable **Keep Temp Files** (Advanced tab); check log file |
| **Figure won't show** | Try SVG format; check figure size isn't huge; enable **Embed Image** |

### Debugging Checklist

<details>
<summary><b>🔍 How to Debug Issues</b></summary>

**Step 1: Enable logging**
- Go to **Advanced** tab → enable **Keep Temp Files**
- Go to **Advanced** tab → enable **Save Script**

**Step 2: Find the log**
```
# Windows
%TEMP%\matplotlib_inkscape_debug.log

# macOS/Linux
/tmp/matplotlib_inkscape_debug.log
```

**Step 3: Check the generated script**
- Generated scripts are saved to temp folder
- Try running it manually to see actual error:
```bash
python /tmp/matplotlib_output_*.py
```

**Step 4: Test a minimal example**
```python
# Paste this to test if plt works
plt.plot([1, 2, 3], [1, 4, 9])
plt.title('Test')
```

**Step 5: Verify Python**
```bash
python --version
python -c "import matplotlib; print(matplotlib.__version__)"
```

</details>

### Common Fixes

<details>
<summary><b>Extension not appearing after restart</b></summary>

Check **View → Messages** in Inkscape for error details. If you see Python errors:

1. Verify Python path: **Edit → Preferences → System → Python Executable**
2. Ensure permissions: `chmod +x plt_ink.py` (macOS/Linux)
3. Check file structure is exactly as shown above
4. Try full Inkscape restart (not just window close)

</details>

<details>
<summary><b>Figure appears blank or wrong size</b></summary>

Try these in order:

1. **Switch output format**: Use **Format tab** → change to SVG
2. **Reduce figure size**: Format tab → set Width/Height to 5-6 inches
3. **Enable embedding**: Placement tab → check **Embed Image**
4. **Check margins**: Disable **Tight Layout** in Format tab

</details>

<details>
<summary><b>Data not loading from CSV</b></summary>

1. Ensure CSV file exists at the path you specified
2. Check delimiter matches your file (usually `,`)
3. Verify column numbers are correct (0-indexed)
4. Try with a simple test CSV first

</details>

---

## 📚 Script Bank — 30 Ready-to-Use Templates

**Every template works immediately** with bundled example data. Once you import your data matching the required columns, it uses yours instead. No setup, no code.

**Available across 6 domains:**

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

## 📁 Project Structure

```
plt_ink/                          # Main extension folder
├── plt_ink.py                    # 🔧 Main extension logic
├── plt_ink.inx                   # Inkscape metadata
├── plt_ink_bank.py               # 📚 Template registry
├── plt_ink_dialog.py             # 🖼️ UI dialog
│
├── plt_ink_scripts/              # 📊 Template library (30 templates)
│   ├── evaluation/      (5)      # Training, ROC/PR, confusion matrix, calibration, comparison
│   ├── analysis/        (5)      # Hyperparameter, Pareto, learning curves, SHAP, embeddings
│   ├── clinical/        (5)      # Kaplan-Meier, forest plots, Bland-Altman, volcano, dose-response
│   ├── stats/           (5)      # Rainclouds, slopes, scatter, residuals, correlation
│   ├── imaging/         (5)      # Segmentation, Grad-CAM, spectra, composite figures
│   └── basics/          (5)      # 3D, contours, vector fields, dual-axis, demo
│
├── sample_data/                  # 📈 Example datasets (always available)
│   ├── *.csv            (15)     # CSV files for templates
│   └── images/                   # Sample images for imaging templates
│
├── tools/                        # 🛠️ Utilities
│   ├── make_sample_data.py       # Generate sample datasets
│   └── render_bank.py            # Test all templates
│
├── README.md                     # Documentation (you're reading it!)
└── LICENSE                       # MIT License
```

---

## 🤝 Contributing

Found a bug? Have a great idea? **Contributions are very welcome!**

### Report Issues

- [GitHub Issues](https://github.com/YouvenZ/plt_ink/issues) — bugs & feature requests
- [GitHub Discussions](https://github.com/YouvenZ/plt_ink/discussions) — questions & ideas

### Submit a Pull Request

1. **Fork** the repo
2. **Create a branch**: `git checkout -b feature/your-amazing-thing`
3. **Make changes** (see "Contributing Templates" below)
4. **Commit**: `git commit -m 'feat: add your feature'`
5. **Push**: `git push origin feature/your-amazing-thing`
6. **Open a PR** with a clear description

### Adding Templates to the Script Bank

Want to add a visualization template? Follow this template:

```python
"""
Your Figure Title
One-line description of what this shows and when to use it.

requires_data: true                    # Does it need user data?
data_columns: col1, col2, col3         # Expected column names
sample_data: your_example.csv          # Bundled fallback data file
tags: keyword, searchable              # Help users find it
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Your plotting code here
# Use _fig_width, _fig_height, _dpi, _show_legend, etc.
```

**Guidelines:**
- One template = one clear purpose
- Use only `numpy`, `pandas`, `matplotlib` (no scipy/seaborn/sklearn)
- Include sample data in `sample_data/` folder
- Test with and without user data
- Put in appropriate category folder

### Development Workflow

```bash
# Clone and setup
git clone https://github.com/YouvenZ/plt_ink.git
cd plt_ink

# Create symlink for testing (Windows PowerShell as Admin):
New-Item -ItemType Junction -Path "$env:APPDATA\inkscape\extensions\plt_ink" -Target "$(Get-Location)"

# Or Linux/macOS:
ln -s "$(pwd)" ~/.config/inkscape/extensions/plt_ink

# Test templates render:
python tools/render_bank.py
```

---

## 🆘 Need Help?

| What | Where |
|------|-------|
| **Bug report or feature idea** | [GitHub Issues](https://github.com/YouvenZ/plt_ink/issues) |
| **How do I...?** | [GitHub Discussions](https://github.com/YouvenZ/plt_ink/discussions) |
| **Direct question** | [Email: youven.z@gmail.com](mailto:youven.z@gmail.com) |

---

## 📄 License & Credits

**MIT License** — You're free to use, modify, and distribute this software.  
**Copyright © 2026** Youven & Rachid ZEGHLACHE

See [LICENSE](LICENSE) file for full details.

---

## 🔄 Changelog

### v2.0 (2026-08-05) — UX Overhaul
- ✨ **Unified Script Editor** — single tab for inline, external, and template scripts
- 📊 **Reorganized Script Library** — 30 templates across 6 focused categories
- 📈 **Sample Datasets** — 15 CSV files + imaging assets for instant testing
- ⚙️ **Settings Persistence** — your preferences survive restarts
- 🐍 **First-run Python Detection** — auto-finds Python if available
- 🛠️ **Build Tools** — utilities for developers

### v1.0.0 (2026-02-19)
- Initial release with inline code, external file loading, and script bank
- SVG/PNG/PDF output formats, data import, matplotlib styles, LaTeX support

---

## 🚀 What's Next?

- **Learn more**: [Full Documentation](https://github.com/YouvenZ/plt_ink)
- **See examples**: [Script Bank Templates](#-script-bank)
- **Get help**: [Troubleshooting](#-troubleshooting)
- **Contribute**: [Contributing Guide](#-contributing)

---

<div align="center">

**Made with ❤️ for scientists, researchers, and designers.**

[⭐ Star on GitHub](https://github.com/YouvenZ/plt_ink) • [🐛 Report a Bug](https://github.com/YouvenZ/plt_ink/issues) • [💬 Join Discussion](https://github.com/YouvenZ/plt_ink/discussions)

</div>