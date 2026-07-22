"""
plt_ink_bank — single source of truth for the script bank.

Both plt_ink.py (validation) and plt_ink_dialog.py (UI) import from here, so
categories and script metadata are defined exactly once.

Script metadata convention (module docstring of each bank script):

    \"\"\"
    Title On The First Line
    Free-text description on the following lines (may span several lines).
    requires_data: true          <- optional, default false
    tags: bars, comparison       <- optional, comma-separated
    \"\"\"

Lines matching a known ``key: value`` pair are treated as metadata; everything
else after the title is the description. Unknown keys are ignored so the
format can grow without breaking older versions.
"""

import ast
import os

# Directory layout ----------------------------------------------------------

BANK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'plt_ink_scripts')

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'sample_data')

# Category id -> human label. Order here is the display order in the dialog.
CATEGORIES = {
    'line_plots':    'Line Plots',
    'scatter_plots': 'Scatter Plots',
    'bar_charts':    'Bar Charts',
    'statistical':   'Statistical Plots',
    'scientific':    'Scientific Plots',
    'heatmaps':      'Heatmaps & Matrices',
    'time_series':   'Time Series',
    'distributions': 'Distributions',
    'multi_panel':   'Multi-Panel Figures',
    'publication':   'Publication Ready',
    'seaborn':       'Seaborn Plots',
    'plotly':        'Plotly Charts',
}

# Metadata keys recognised inside script docstrings.
_META_KEYS = ('requires_data', 'tags', 'note')

_TRUE_VALUES = ('true', 'yes', '1')


def parse_script_meta(path):
    """Parse a bank script's docstring into a metadata dict.

    Returns a dict with keys: name, path, title, description, requires_data,
    tags. Never raises — unreadable/unparsable files yield defaults derived
    from the filename.
    """
    name = os.path.splitext(os.path.basename(path))[0]
    meta = {
        'name':          name,
        'path':          path,
        'title':         name.replace('_', ' ').title(),
        'description':   '',
        'requires_data': False,
        'tags':          [],
    }
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            source = fh.read()
        doc = ast.get_docstring(ast.parse(source)) or ''
    except Exception:
        return meta

    desc_lines = []
    lines = [l.strip() for l in doc.strip().splitlines() if l.strip()]
    for i, line in enumerate(lines):
        key, sep, value = line.partition(':')
        key = key.strip().lower().replace(' ', '_')
        if sep and key in _META_KEYS:
            value = value.strip()
            if key == 'requires_data':
                meta['requires_data'] = value.lower() in _TRUE_VALUES
            elif key == 'tags':
                meta['tags'] = [t.strip() for t in value.split(',') if t.strip()]
            continue
        if i == 0:
            meta['title'] = line
        else:
            desc_lines.append(line)
    meta['description'] = ' '.join(desc_lines)
    return meta


def list_scripts(category):
    """Return sorted list of metadata dicts for all scripts in a category.

    Returns an empty list for unknown/missing categories.
    """
    category_dir = os.path.join(BANK_DIR, category)
    if not os.path.isdir(category_dir):
        return []
    scripts = []
    for fname in sorted(os.listdir(category_dir)):
        if fname.endswith('.py') and not fname.startswith('_'):
            scripts.append(parse_script_meta(os.path.join(category_dir, fname)))
    return scripts


def script_path(category, name):
    """Absolute path for a bank script, or None if it does not exist."""
    if category not in CATEGORIES or not name:
        return None
    path = os.path.join(BANK_DIR, category, name + '.py')
    return path if os.path.isfile(path) else None
