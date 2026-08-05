#!/usr/bin/env python3
"""Render every bank template headlessly and report failures.

Reproduces what ``plt_ink.py`` does around a template — the injected preamble
variables, the auto-created figure, and the postamble's grid/despine/
tight_layout/savefig — so a template that renders here renders in Inkscape.

    python tools/render_bank.py [--out DIR] [--filter SUBSTR] [--no-data]

``--no-data`` leaves ``data`` undefined, exercising the bundled-sample
fallback every template is required to have. Without it, a template's declared
``sample_data:`` CSV is loaded and injected as ``data``, exercising the path
the user takes when they pick a file on the Data tab.
"""

import argparse
import os
import sys
import traceback
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import plt_ink_bank  # noqa: E402

# Mirrors the dialog defaults so the harness sees what a fresh install sees.
DEFAULTS = dict(
    _fig_width=10.0, _fig_height=6.5, _dpi=96, _show_grid=True,
    _show_legend=True, _legend_position='best', _colormap='viridis',
    _transparent=False, _subplot_rows=1, _subplot_cols=1,
)


def make_globals(meta, inject_data):
    """Build the namespace plt_ink.py hands to a script."""
    g = {
        '__name__': '__main__',
        'plt': plt, 'np': np, 'pd': pd, 'matplotlib': matplotlib,
        '_sample_data_dir': plt_ink_bank.SAMPLE_DATA_DIR,
    }
    g.update(DEFAULTS)

    def get_cmap(name=None):
        return matplotlib.colormaps[name or g['_colormap']]

    def apply_style(ax=None):
        (ax or plt.gca()).grid(g['_show_grid'], alpha=0.3, linestyle='--')

    g['get_cmap'] = get_cmap
    g['apply_style'] = apply_style
    try:
        import seaborn as sns
        g['sns'] = sns
        g['seaborn_available'] = True
    except Exception:
        g['seaborn_available'] = False

    if inject_data and meta['sample_data']:
        path = plt_ink_bank.sample_asset(meta['sample_data'])
        if path:
            g['data'] = pd.read_csv(path)
    return g


def postamble(fig, out_path, show_grid):
    """What plt_ink.py appends after the user script."""
    for ax in fig.get_axes():
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')
    try:
        if getattr(fig, 'get_layout_engine', lambda: None)() is None:
            plt.tight_layout()
    except Exception:
        pass
    fig.savefig(out_path, format='png', dpi=110, bbox_inches='tight')


def render(meta, out_dir, inject_data):
    """Run one template. Returns (ok, message, size_bytes)."""
    out_path = os.path.join(out_dir, f"{meta['category']}__{meta['name']}.png")
    with open(meta['path'], encoding='utf-8') as fh:
        source = fh.read()
    g = make_globals(meta, inject_data)
    # plt_ink.py only auto-creates a figure when the script makes none.
    if 'plt.subplots' not in source and 'plt.figure' not in source:
        fig, ax = plt.subplots(figsize=(g['_fig_width'], g['_fig_height']))
        g['fig'], g['ax'] = fig, ax
    caught = []
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            exec(compile(source, meta['path'], 'exec'), g)
            caught = [str(x.message).split('\n')[0] for x in w
                      if issubclass(x.category, UserWarning)]
        fig = plt.gcf()
        if not fig.get_axes():
            return False, 'script produced no axes', 0
        postamble(fig, out_path, g['_show_grid'])
    except Exception:
        return False, traceback.format_exc(limit=3).strip().split('\n')[-1], 0
    finally:
        plt.close('all')
    size = os.path.getsize(out_path)
    note = f'  [{len(caught)} warning(s): {caught[0][:60]}]' if caught else ''
    return True, note, size


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', default=os.path.join(HERE, '_render'))
    ap.add_argument('--filter', default='')
    ap.add_argument('--no-data', action='store_true',
                    help='leave `data` undefined to test the sample fallback')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    metas = []
    for cid in plt_ink_bank.CATEGORIES:
        for m in plt_ink_bank.list_scripts(cid):
            m['category'] = cid
            if args.filter and args.filter not in m['name']:
                continue
            metas.append(m)

    failures, small = [], []
    for m in metas:
        ok, msg, size = render(m, args.out, inject_data=not args.no_data)
        status = 'ok  ' if ok else 'FAIL'
        print(f"[{status}] {m['category']:<11} {m['name']:<28} "
              f"{size // 1024:>4} KB {msg}")
        if not ok:
            failures.append((m['name'], msg))
        elif size < 12000:
            small.append((m['name'], size))

    print(f'\n{len(metas) - len(failures)}/{len(metas)} rendered '
          f"({'sample fallback' if args.no_data else 'injected data'})")
    for name, msg in failures:
        print(f'  FAIL {name}: {msg}')
    for name, size in small:
        print(f'  THIN {name}: only {size} bytes — probably near-empty')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
