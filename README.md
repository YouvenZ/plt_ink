Collecting workspace information# Poster Utilities for Inkscape

[![Inkscape](https://img.shields.io/badge/Inkscape-1.0+-blue.svg)](https://inkscape.org/)
[![Python](https://img.shields.io/badge/Python-3.6+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Automate poster header creation in Inkscape with professional formatting**

A powerful Inkscape extension that automatically adds formatted title, authors, affiliations, and conference information to academic posters. Supports both native Inkscape text rendering and LaTeX compilation for publication-quality output.

---

## 📋 Table of Contents

- Features
- Installation
- Quick Start
- Usage Guide
- Dependencies
- Examples
- Troubleshooting
- Advanced Features
- Contributing

---

## ✨ Features

- **🎨 Two Rendering Modes**
  - **Inkscape Native**: Fast, simple, no external dependencies
  - **LaTeX**: Publication-quality typography with full LaTeX support

- **👥 Smart Author-Affiliation Mapping**
  - Superscript, subscript, parenthesis, or symbol markers
  - Automatic or manual author-institution linking
  - Multiple affiliations per author

- **📁 Flexible Input**
  - Direct text input in the extension dialog
  - CSV file import for batch processing
  - Custom LaTeX templates

- **🎯 Customizable Formatting**
  - Font sizes for each element (title, authors, conference, institutions)
  - Text alignment (left, center, right)
  - Adjustable line spacing and positioning

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

1. **Download the extension files:**
   - poster_utilities.py
   - poster_utilities.inx

2. **Create the extension folder:**
   ```bash
   mkdir -p [extensions-directory]/poster_utils
   ```

3. **Copy files to the folder:**
   ```bash
   cp poster_utilities.py [extensions-directory]/poster_utils/
   cp poster_utilities.inx [extensions-directory]/poster_utils/
   ```

4. **Restart Inkscape**

### Step 3: Verify Installation

Open Inkscape and check: **Extensions → Text → Poster Utilities**

---

## 🚀 Quick Start

### Basic Example (Inkscape Mode)

1. Open your poster in Inkscape
2. Go to **Extensions → Text → Poster Utilities**
3. Fill in the fields:
   ```
   Title: Novel Approaches to Machine Learning
   Authors: Jane Smith; John Doe; Alice Johnson
   Conference: ICML 2024
   Institution: MIT; Stanford University; UC Berkeley
   ```
4. Set position (e.g., X: 100, Y: 100)
5. Click **Apply**

**Result:** Formatted text appears on your poster!

---

## 📖 Usage Guide

### Input Tab

#### Direct Input Mode

<details>
<summary><b>Click to expand</b></summary>

**Fields:**
- **Title**: Your poster title
- **Authors**: Semicolon-separated list (e.g., `Jane Smith; John Doe`)
- **Conference**: Conference name/details
- **Institution**: Semicolon-separated affiliations

**Example:**
```
Title: Deep Learning for Climate Modeling
Authors: Dr. Sarah Chen; Prof. Michael Rodriguez; Dr. Emily Zhang
Conference: NeurIPS 2024 - Vancouver, Canada
Institution: MIT CSAIL; Stanford AI Lab; Oxford Deep Learning Group
```

</details>

#### CSV Input Mode

<details>
<summary><b>Click to expand</b></summary>

**CSV Format:**
```csv
title,authors,conference,institutions,author_inst_map
"Your Title","Author1; Author2","Conference Name","Inst1; Inst2","1,2; 2"
```

**Example CSV (`poster_data.csv`):**
```csv
title,authors,conference,institutions,author_inst_map
"Quantum Computing for Drug Discovery","Dr. Alice Smith; Prof. Bob Johnson; Dr. Carol Williams","QCHEM 2024","Harvard University; MIT; Caltech","1; 1,2; 3"
```

**How to use:**
1. ☑ Check "Use CSV file"
2. Browse to your CSV file
3. Click Apply

</details>

### Author-Institution Mapping Tab

#### Mapping Formats

**1. Positional Format** (simplest)
```
Author-Inst Map: 1; 2; 1,2
```
- First author → Institution 1
- Second author → Institution 2  
- Third author → Institutions 1 and 2

**2. Explicit Format** (recommended)
```
Author-Inst Map: Jane Smith:1; John Doe:2; Alice Johnson:1,2
```

**3. Marker Styles:**
- **Superscript**: Jane Smith¹ ²  
- **Subscript**: Jane Smith₁ ₂
- **Parenthesis**: Jane Smith (1, 2)
- **Symbol**: Jane Smith* †

### Formatting Tab

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Title Size | 48 | 12-120 | Font size in pixels |
| Author Size | 32 | 12-96 | Font size in pixels |
| Conference Size | 28 | 12-96 | Font size in pixels |
| Institution Size | 24 | 12-72 | Font size in pixels |
| X Position | 100 | 0-10000 | Horizontal position |
| Y Position | 100 | 0-10000 | Vertical position |
| Line Spacing | 80 | 20-200 | Space between elements |
| Text Align | Left | Left/Center/Right | Text alignment |

### LaTeX Mode

<details>
<summary><b>Advanced LaTeX Features</b></summary>

**Custom Preamble:**
```latex
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{fontspec}
\setmainfont{Times New Roman}
```

**Custom Template:**
```latex
\documentclass{article}
\usepackage[utf8]{inputenc}
\begin{document}
\begin{center}
{\Huge\textbf{{title}}}\\[0.5cm]
{\Large {authors}}\\[0.3cm]
{\large\textit{{conference}}}\\[0.3cm]
{\normalsize {institution}}
\end{center}
\end{document}
```

**Placeholders:**
- `{title}` → Your title
- `{authors}` → Author list
- `{conference}` → Conference info
- `{institution}` → Affiliations
- `{author_inst_map}` → Mapping string

</details>

---

## 🔧 Dependencies

### Core Requirements (Required)

| Component | Version | Purpose |
|-----------|---------|---------|
| **Inkscape** | 1.0+ | Vector graphics editor |
| **Python** | 3.6+ | Extension runtime |
| **lxml** | Latest | XML parsing |

**Installation:**
```bash
# Usually pre-installed with Inkscape
pip install lxml
```

### LaTeX Mode (Optional)

Required only if using LaTeX backend:

| Tool | Purpose | Installation |
|------|---------|--------------|
| **pdflatex** | LaTeX compilation | Install TeX Live or MiKTeX |
| **Inkscape CLI** | PDF→SVG conversion | Included with Inkscape |

**Check Installation:**
```bash
# Test LaTeX
pdflatex --version

# Test Inkscape CLI
inkscape --version
```

**Install LaTeX:**

<details>
<summary><b>Windows</b></summary>

1. Download **MiKTeX**: https://miktex.org/download
2. Run installer
3. Add to PATH during installation

</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install --cask mactex
```

Or download MacTeX: https://tug.org/mactex/

</details>

<details>
<summary><b>Linux (Debian/Ubuntu)</b></summary>

```bash
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra
```

</details>

---

## 💡 Examples

### Example 1: Simple Conference Poster

**Input:**
```
Backend: Inkscape Native
Title: Advances in Neural Networks
Authors: Jane Smith; John Doe
Conference: ICML 2024
Institution: MIT; Stanford
Position: X=100, Y=100
```

**Output:**
```
Advances in Neural Networks
Jane Smith, John Doe
ICML 2024
MIT, Stanford
```

### Example 2: Multi-Affiliation Authors

**Input:**
```
Authors: Dr. Sarah Chen; Prof. Michael Brown; Dr. Emily White
Institution: Harvard Med; MIT CSAIL; Stanford AI Lab
Author-Inst Map: 1; 1,2; 2,3
Mapping Style: Superscript
```

**Output:**
```
Dr. Sarah Chen¹, Prof. Michael Brown¹ ², Dr. Emily White² ³
¹Harvard Med, ²MIT CSAIL, ³Stanford AI Lab
```

### Example 3: CSV Batch Processing

**CSV File (`posters.csv`):**
```csv
title,authors,conference,institutions,author_inst_map
"Poster A","A1; A2","Conf A","Inst1; Inst2","1; 2"
"Poster B","B1; B2; B3","Conf B","Inst1; Inst2; Inst3","1; 2; 3"
```

**Workflow:**
1. Create poster template in Inkscape
2. Use CSV input mode
3. Process each row
4. Export results

### Example 4: LaTeX Mode with Math

**Custom Template:**
```latex
\documentclass{article}
\usepackage{amsmath}
\begin{document}
\begin{center}
{\Huge\textbf{{title}}}\\[0.5cm]
{\Large {authors}}\\[0.3cm]
{\normalsize {institution}}
\end{center}
\end{document}
```

**Input Title:**
```
Neural Networks with $\mathcal{L}_2$ Regularization
```

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Extension not appearing in menu</b></summary>

**Solution:**
1. Check file locations:
   ```bash
   ls [extensions-directory]/poster_utils/
   # Should show: poster_utilities.py, poster_utilities.inx
   ```
2. Verify permissions:
   ```bash
   chmod +x poster_utilities.py
   ```
3. Check Inkscape error log:
   - **Edit → Preferences → System → View Error Log**
4. Restart Inkscape completely

</details>

<details>
<summary><b>LaTeX mode fails</b></summary>

**Error:** "LaTeX rendering failed"

**Solutions:**
1. Verify LaTeX installation:
   ```bash
   pdflatex --version
   ```
2. Check Inkscape CLI:
   ```bash
   inkscape --help
   ```
3. Review error message in Inkscape console
4. Try Inkscape mode as fallback

**Debug Mode:**
- Enable "Keep Temp Files" in extension
- Check temp directory for `.tex`, `.pdf`, `.log` files
- Review LaTeX error log

</details>

<details>
<summary><b>CSV not loading</b></summary>

**Common Causes:**
- Incorrect CSV format
- File encoding issues
- Missing headers

**Solution:**
```csv
title,authors,conference,institutions,author_inst_map
"Test Title","Author1","Conference","Institution",""
```

**Encoding:** Save as **UTF-8** encoding

</details>

<details>
<summary><b>Formatting issues</b></summary>

**Text overlapping:**
- Increase line spacing (default: 80)
- Reduce font sizes
- Adjust Y position

**Text cut off:**
- Check canvas size
- Adjust X/Y position
- Use text wrapping (automatic)

</details>

### Debug Tips

**Enable Debug Output:**
```python
# In poster_utilities.py
inkex.utils.debug(f"Data: {data}")
```

**Check Error Console:**
- **Extensions → Error Log** (Inkscape 1.2+)
- Terminal output (if launched from command line)

**Test with Minimal Example:**
```
Title: Test
Authors: A
Conference: C
Institution: I
```

---

## 🎓 Advanced Features

### Custom Marker Symbols

Edit in `poster_utilities.py` line 155:

```python
symbols = ['*', '†', '‡', '§', '¶', '‖', '**', '††']  # Add more symbols
```

### Text Wrapping Control

Adjust max characters per line (line 210):

```python
def wrap_text(self, text, max_chars=60):  # Change 60 to your preference
```

### Custom Fonts

Inkscape mode (line 323):

```python
style = {
    'font-family': 'Helvetica, Arial, sans-serif',  # Change font
    # ...
}
```

LaTeX mode (line 509):

```latex
\usepackage{fontspec}
\setmainfont{Times New Roman}
```

### Batch Processing Script

```python
import subprocess
import csv

with open('posters.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Export as PNG with author names
        subprocess.run([
            'inkscape', 'template.svg',
            '--export-filename', f"{row['authors']}.png"
        ])
```

---

## 📝 File Structure

```
poster_utils/
├── poster_utilities.py      # Main extension code
├── poster_utilities.inx     # Inkscape extension definition
├── README.md                # This file
└── examples/
    ├── sample_poster.svg
    ├── sample_data.csv
    └── latex_template.tex
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Development Setup:**
```bash
git clone https://github.com/yourusername/poster-utilities.git
cd poster-utilities
# Symlink to extensions directory for testing
ln -s $(pwd) ~/.config/inkscape/extensions/poster_utils
```

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/YouvenZ/poster-utilities/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YouvenZ/poster-utilities/discussions)
- **Email**: youvenz.pro@gmail.com

---

## 🔄 Changelog

### v1.0.0 (2024-01-15)
- ✨ Initial release
- ✅ Inkscape native text rendering
- ✅ LaTeX rendering support
- ✅ CSV input
- ✅ Author-institution mapping
- ✅ Multiple marker styles
