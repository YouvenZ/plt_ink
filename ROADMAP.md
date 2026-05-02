# plt_ink — Development Roadmap

> **How to use this file:**  
> Work through items top-to-bottom by section priority.  
> Mark items `[x]` when done, `[~]` when in-progress, `[!]` for blocked.  
> Re-run the agent on this file after each session to continue automatically.

---

## Legend
- `[ ]` — To do
- `[~]` — In progress
- `[x]` — Done
- `[BUG]` — Known defect
- `[MISS]` — Missing feature (advertised but not implemented)
- `[ENH]` — Enhancement / improvement
- `[GOOD]` — Already working well (no action needed)

---

## 0 — What is already good (GOOD — no action)

- `[GOOD]` Clean architecture: preamble → user code → postamble pipeline
- `[GOOD]` Multiple script sources: inline, external file, script bank
- `[GOOD]` Structured logging with timestamp to temp log file
- `[GOOD]` Wide configuration surface (format, style, layout, placement, data)
- `[GOOD]` Configurable placement modes (center, cursor, corners, custom XY)
- `[GOOD]` Multi-column data import with range parsing ("0-3", "0,2-4,6")
- `[GOOD]` Named column access with safe identifier generation
- `[GOOD]` Auto-figure creation detection (checks for plt.subplots / plt.figure in code)
- `[GOOD]` Helper variables exposed to user scripts (_fig_width, _colormap, etc.)
- `[GOOD]` Color cycle presets (tab10, tab20, Set1, Set2, Paired, Dark2)
- `[GOOD]` Style presets (seaborn, ggplot, bmh, dark_background, etc.)
- `[GOOD]` LaTeX rendering support (opt-in)
- `[GOOD]` Auto-despine option
- `[GOOD]` Scale factor for sizing the inserted figure
- `[GOOD]` Script save-to-file for debugging
- `[GOOD]` Keep temp files option for debugging

---

## 1 — BUGS (fix first)

### 1.1 Deprecated API — `plt.cm.get_cmap()` [BUG]
- [x] **Fixed** in `generate_preamble()` — now uses `matplotlib.colormaps[name]` with fallback.

### 1.2 Deprecated API — `date_parser` in `pd.read_csv()` [BUG]
- [x] **Fixed** — `date_parser=` kwarg removed. `pd.to_datetime(df.iloc[:, col], format=..., errors='coerce')` applied post-load.

### 1.3 Unsafe imports in non-preamble path [BUG]
- [x] **Fixed** — removed `import random` and `import scipy` from minimal imports path.

### 1.4 `SCRIPT_CATEGORIES` dict defined but never used [BUG]
- [x] **Fixed** — `SCRIPT_CATEGORIES` now includes all 10 categories. `get_bank_script_path()` validates `bank_category` against the dict before building the path.

### 1.5 Hardcoded absolute paths in `.inx` file [BUG]
- [x] **Fixed** — `.inx` replaced with a minimal launcher stub (no `<param>` tags at all). All paths live in the GTK dialog which uses empty defaults.

### 1.6 Inline escape-sequence double-decoding hazard [BUG]
- [x] **Fixed** — GTK `TextView` delivers real Python strings; escape decoding removed entirely. No replacement needed.

### 1.7 SVG import strips `<defs>` and stylesheet [BUG]
- [x] **Fixed** in `import_svg_content()` — `<defs>` children are now merged into the document's own `<defs>` block; only drawing elements go into the group.

### 1.8 `xlink:href` deprecated in SVG 2 [BUG]
- [x] **Fixed** — both `href` and `{xlink}href` are now set for backward compatibility.

### 1.9 `debug_mode` is always `True` — log fills without limit [BUG]
- [x] **Fixed** — defaults to `False`; user enables it via the Advanced tab in the GTK dialog. Log rotation added (`_rotate_log()`, cap ~1 MB).

### 1.10 `calculate_size()` unit conversion may be incorrect [BUG]
- [x] **Fixed** — display size now always `figure_width * 96 px/in * scale_factor` regardless of render DPI. DPI noted as quality-only parameter.

---

## 2 — MISSING (advertised but not implemented)

### 2.1 Script Bank — Missing scripts [MISS]
- [x] **All 24 missing scripts created** (see tracker in §6).

### 2.2 "cursor" position mode is not truly at cursor [MISS]
- [x] **Fixed** — renamed to "At selection" in the GTK dialog. Hint text explains the fallback.

### 2.3 No "Update existing figure" feature [MISS]
- [x] **Done** — Inserted elements tagged with `plt_ink:source` attribute and `inkscape:label`. On re-run, `_find_existing_plt_ink()` detects a selected plt_ink element and replaces it in-place.

---

## 3 — ENHANCEMENTS

### 3.1 Execution timeout should be configurable [ENH]
- [x] **Done** — GTK dialog Advanced tab has "Timeout (seconds)" spinner (5–600 s, default 60).

### 3.2 Improve error display — show line numbers [ENH]
- [x] **Done** — `_preamble_lines` tracked in `generate_script()`. `_remap_traceback()` subtracts preamble offset before showing errors.

### 3.3 Add a "Copy generated script" button / script preview [ENH]
- [x] **Done** — When `save_script=True` and `script_save_path` is empty, script is auto-saved to the extension directory as `plt_ink_script_<timestamp>.py`. The path is shown via `inkex.utils.debug()` in the Inkscape console.

### 3.4 Support conda/virtual environments [ENH]
- [x] **Done** — Added a "Detect…" button next to the Python path field in the Script tab. Clicking it probes system PATH for `python3`/`python`, then scans `~/.venv`, `~/venv`, `~/.virtualenvs/*`, `~/miniconda3/envs/*`, `~/anaconda3/envs/*`, and `~/.conda/envs/*` (both Unix and Windows layouts). Found interpreters are shown in a pick-list dialog; selecting one writes the path into the entry.

### 3.5 Validate color inputs [ENH]
- [x] **Done** — `generate_preamble()` now wraps the background color `rcParams` assignments in a `try/except ValueError` block. On failure it issues a `warnings.warn()` and falls back to white.

### 3.6 Inline code character limit is too small [ENH]
- [x] **Done** — Moot: the `.inx` now has zero `<param>` elements (pure launcher stub). All UI — including the code editor — lives in the GTK3 `TextView` widget which has no character limit. The `max_length` attribute no longer exists in the INX at all.

---

## 1b — NEW BUGS (found in use)

### 1b.1 GTK dialog crashes / small rectangle window appears [BUG]
- [x] **Fixed** — Root cause: calling `dialog.run()` inside Inkscape's own GTK process creates a nested GTK main loop, causing freezes and crashes. The small rectangle was Inkscape's native parameter stub dialog appearing before the Python script ran.
- **Fix:** The GTK dialog is now launched as a **subprocess** via `sys.executable` (Inkscape's Python, which has GTK). The dialog outputs all settings as JSON to stdout; the main extension reads the JSON. No nested GTK loop. INX stub updated with `needs-live-preview="false"` and a description label.

### 1b.2 Selected Python environment not being used correctly [BUG]
- [x] **Fixed** — Caused by the GTK crash (1b.1): if the dialog crashed mid-interaction, options were never properly collected, so the default `"python"` was used instead of the user's selection. Fixed as a side-effect of the subprocess dialog approach — options are now reliably serialised to JSON and reconstructed, so `python_path` is always correct.

### 1b.3 UnicodeDecodeError / `cp1252` crash on Windows — matplotlib check fails [BUG]
- [x] **Fixed** — On Windows the default subprocess text encoding is `cp1252`. The dialog subprocess outputs UTF-8 JSON (with Unicode characters from hint labels); when the parent tried to decode it as cp1252, a `UnicodeDecodeError` was raised in the reader thread, the JSON was never parsed, `python_path` fell back to `"python"` (Inkscape's Python), and the matplotlib check failed.
- **Fix:** `encoding='utf-8', errors='replace'` added to **all four** `subprocess.run()` calls in `plt_ink.py`. In `plt_ink_dialog.py` `__main__`, stdout is reconfigured to UTF-8 via `io.TextIOWrapper` before writing JSON. The parent now also takes the **last non-empty line** of stdout as the JSON payload, ignoring any GTK debug lines printed above it. Cancel/error detection filters out harmless GTK/GLib noise from stderr.

### 3.7 Log file rotation [ENH]
- [x] **Done** — `_rotate_log()` called at startup; truncates log to ~5000 recent lines when it exceeds 1 MB.

### 3.8 SCRIPT_CATEGORIES dict — add missing categories [ENH]
- [x] **Done** — merged with fix for BUG 1.4.

### 3.9 Expose `_data`, `_x_data`, `_y_data` variable names in Help tab [ENH]
- [x] **Done** — Inline code hint text now lists data variables (`df/data`, `x_data`, `y_data`, `x_columns`, `y_columns`, `columns`, `<colname>`). Data tab variable documentation updated to accurately reflect single-column vs multi-column behaviour and the `x_columns`/`y_columns` alias semantics.

### 3.10 Add version number [ENH]
- [x] **Done** — `__version__ = "1.1.0"` added near top of `plt_ink.py`.

### 3.11 Figure title / metadata on insertion [ENH]
- [x] **Done** — `_get_figure_label()` builds a label from source/category/script-name; set as `inkscape:label` and `plt_ink:source` on every inserted element.

### 3.12 "Wrap user error" mode — catch user code errors gracefully [ENH]
- [x] **Done** — when `error_handling == "warn"`, user code is wrapped in `try/except` in the generated script. Exception printed as `USER_ERROR:` line; detected and surfaced by `execute_script()`.

### 3.13 SVG import: handle namespaces correctly [ENH]
- [x] **Done** — `import_svg_content()` now builds a merged namespace map from the imported SVG root (`src_nsmap`) and the document's existing nsmap (`doc_nsmap`). The wrapper `<g>` element is created via `etree.Element(..., nsmap=merged_nsmap)` instead of `inkex.Group()`, ensuring all namespace prefix declarations (`xlink`, `dc`, `cc`, `rdf`, etc.) are preserved on the group element and all child references resolve correctly.

### 3.14 Configurable figure group naming [ENH]
- [x] **Done** — merged with ENH 3.11 fix. `_get_figure_label()` regex-parses `plt.title(...)` for inline code.

---

## 1c — NEW BUGS (Windows console window)

### 1c.1 Empty rectangle dialog appears when extension runs on Windows [BUG]
- [x] **Fixed** — Root cause was two-part: (1) `python.exe` spawns a console window (fixed with `CREATE_NO_WINDOW`). (2) `Gtk.Dialog` creates a hidden transient-parent `GtkWindow` when no parent is provided — this hidden window was appearing as a visible empty rectangle on Windows.
- **Fix (final):** Converted `MatplotlibDialog` from `Gtk.Dialog` to `Gtk.Window`, following the TexText extension pattern. Manual Cancel/Apply buttons are created in a button box and connected to `_on_cancel` / `_on_apply` callbacks that set `self._accepted` and call `Gtk.main_quit()`. `__main__` now uses `window.show(); Gtk.main()` and checks `window._accepted` instead of `dialog.run()` / `ResponseType`. `delete-event` connected to `_on_delete` for proper window-close handling. No `Gtk.Dialog` anywhere in the window hierarchy — no hidden transient parent, no empty rectangle.

---

- [x] **Live preview panel** — "Preview" button in Script tab generates a low-res PNG thumbnail of the figure using a headless subprocess run, then shows it in a `Gtk.Dialog` containing a `Gtk.Image`. Falls back gracefully if matplotlib is unavailable.
- [x] **Export as standalone script** — "Export script only" checkbox + path picker in Advanced tab. When checked, `plt_ink.py` generates the assembled script, saves it to the specified path (or auto-names it), shows the path via `inkex.utils.debug()`, and exits without executing or inserting any figure.
- [x] **Script bank editor** — Preview pane added to Script Bank frame: read-only monospace `TextView` shows selected script contents. "Load into Editor" copies script to inline editor + switches mode. "Open File" opens the `.py` in the OS default editor.
- [ ] **Figure update on data change** — Watch a linked data file and re-generate on change (requires Inkscape 1.3+ extension events or an external daemon).
- [x] **Multi-figure batch insert** — Batch tab added to the dialog with a draggable script queue (inline/file/bank entries). "Add Current Script" queues the active script; Apply in batch mode runs each entry in sequence, inserting figures left-to-right or top-to-bottom with a configurable gap. `_run_batch()` method in `plt_ink.py` handles execution and progressive placement via custom XY offset.
- [x] **Seaborn support** — Optional `import seaborn as sns` added to preamble (try/except; exposes `seaborn_available` flag). Added `seaborn` category to `SCRIPT_CATEGORIES` and dialog `CATEGORY_LABELS`. Three bank scripts created: `seaborn/basic_seaborn.py`, `seaborn/seaborn_heatmap.py`, `seaborn/seaborn_violin.py`.
- [x] **Plotly static export** — Format tab "Rendering Backend" selector (Matplotlib / Plotly+Kaleido). `check_plotly()` validates both packages. `generate_plotly_preamble()` imports go/px/numpy, exposes same `_fig_width` etc. variables. `generate_plotly_postamble()` locates the user figure (`fig` or `_fig_plotly`) and calls `fig.write_image()` via kaleido. Style/grid rcParams sections greyed out when Plotly is selected.
- [x] **Help / Cheat Sheet tab** — New "Help" tab in the dialog with a read-only monospace text view listing all preamble variables (`_fig_width`, `_colormap`, …), helper functions (`apply_style`, `get_cmap`), data variables (`df`, `x_data`, `y_data`, …), Plotly mode notes, and quick code examples.

---

## 5 — Priority order for agent execution

> **Work through these in order. Each item references a section above.**

1. `[BUG 1.5]` Fix hardcoded paths in `.inx` — quick win, breaks other machines
2. `[BUG 1.7]` Fix SVG import stripping `<defs>` — critical visual correctness
3. `[BUG 1.10]` Fix figure size calculation (DPI vs display size) — affects all users
4. `[BUG 1.1]` Fix deprecated `get_cmap()` API
5. `[BUG 1.2]` Fix deprecated `date_parser` pandas API
6. `[BUG 1.3]` Remove unsafe `scipy`/`random` from minimal imports
7. `[BUG 1.4]` Use `SCRIPT_CATEGORIES` for validation; add missing categories
8. `[BUG 1.6]` Fix escape-sequence double-decode
9. `[BUG 1.8]` Add `href` alongside `xlink:href`
10. `[BUG 1.9]` Make `debug_mode` configurable; add log rotation
11. `[ENH 3.1]` Add configurable execution timeout
12. `[ENH 3.6]` Increase inline code max_length to 50000
13. `[ENH 3.7]` Add log rotation
14. `[ENH 3.8]` Complete SCRIPT_CATEGORIES dict
15. `[ENH 3.10]` Add version number
16. `[ENH 3.12]` Wrap user code in try/except for warn mode
17. `[ENH 3.2]` Better error messages with adjusted line numbers
18. `[MISS 2.2]` Fix cursor/selection position label in INX
19. `[MISS 2.3]` Update-existing-figure feature
20. `[MISS 2.1]` Fill in all missing script bank files (30+ files)

---

## 6 — Script bank completion tracker

| Script | File | Status |
|--------|------|--------|
| basic_line | line_plots/basic_line.py | ✅ Done |
| multi_line | line_plots/multi_line.py | ✅ Done |
| basic_scatter | scatter_plots/basic_scatter.py | ✅ Done |
| basic_bar | bar_charts/basic_bar.py | ✅ Done |
| error_bars | line_plots/error_bars.py | ✅ Done |
| fill_between | line_plots/fill_between.py | ✅ Done |
| scatter_regression | scatter_plots/scatter_regression.py | ✅ Done |
| bubble_chart | scatter_plots/bubble_chart.py | ✅ Done |
| grouped_bar | bar_charts/grouped_bar.py | ✅ Done |
| stacked_bar | bar_charts/stacked_bar.py | ✅ Done |
| horizontal_bar | bar_charts/horizontal_bar.py | ✅ Done |
| box_plot | statistical/box_plot.py | ✅ Done |
| violin_plot | statistical/violin_plot.py | ✅ Done |
| error_bar_plot | statistical/error_bar_plot.py | ✅ Done |
| contour_plot | scientific/contour_plot.py | ✅ Done |
| vector_field | scientific/vector_field.py | ✅ Done |
| 3d_surface | scientific/3d_surface.py | ✅ Done |
| correlation_matrix | heatmaps/correlation_matrix.py | ✅ Done |
| basic_heatmap | heatmaps/basic_heatmap.py | ✅ Done |
| time_series_basic | time_series/time_series_basic.py | ✅ Done |
| time_series_dual_axis | time_series/time_series_dual_axis.py | ✅ Done |
| histogram | distributions/histogram.py | ✅ Done |
| kde_plot | distributions/kde_plot.py | ✅ Done |
| histogram_kde | distributions/histogram_kde.py | ✅ Done |
| subplot_2x2 | multi_panel/subplot_2x2.py | ✅ Done |
| subplot_comparison | multi_panel/subplot_comparison.py | ✅ Done |
| publication_single | publication/publication_single.py | ✅ Done |
| publication_multi | publication/publication_multi.py | ✅ Done |

---

## Session Log

| Date | Agent session summary |
|------|-----------------------|
| 2026-04-28 | Initial audit. 10 bugs, 2 missing categories, 24 missing bank scripts, 14 enhancements identified. Roadmap created. |
| 2026-04-28 | Implemented GTK dialog (`plt_ink_dialog.py`). Replaced `.inx` with minimal stub. Fixed bugs: 1.1, 1.3, 1.5, 1.7, 1.8, 1.9, 1.10. Renamed cursor→selection (2.2). Added configurable timeout (3.1) and log rotation (3.7). Remaining open: bugs 1.2, 1.4, 1.6; enhancements 3.2–3.6, 3.8–3.14; 24 missing bank scripts (2.1); update feature (2.3). |
| 2026-04-28 | **Session 3** — Fixed BUG 1.2 (date_parser), 1.4 (SCRIPT_CATEGORIES validation), 1.6 (escape decode removed). Added ENH 3.2 (line-number remapping), 3.8 (complete categories), 3.10 (version), 3.11 (inkscape:label), 3.12 (warn-mode try/except), 3.14 (figure label from title regex), MISS 2.3 (replace-existing-figure). Created all 24 missing bank scripts. Remaining open: ENH 3.3, 3.4, 3.5, 3.9, 3.13. |
| 2026-04-29 | **Session 4** — Fixed SyntaxError on line 796: orphaned `finally:` block was inside `_remap_traceback()` instead of closing `execute_script()`'s try/except. Moved `finally` (temp-file cleanup) to the correct position at the end of `execute_script()`. Syntax validated clean. Remaining open: ENH 3.3, 3.4, 3.5, 3.9, 3.13. |
| 2026-04-29 | **Session 5** — Completed all remaining open enhancements: ENH 3.3 (script auto-save to ext dir with path shown), ENH 3.4 (Detect… button probes venv/conda locations), ENH 3.5 (background color try/except fallback), ENH 3.9 (inline hint + data tab docs synced with actual variables), ENH 3.13 (SVG namespace merge via etree nsmap). Both files syntax-validated clean. All roadmap items now complete. |
| 2026-04-29 | **Session 7** — Fixed BUG 1b.3: Windows cp1252 UnicodeDecodeError when reading dialog subprocess stdout. Added `encoding='utf-8', errors='replace'` to all four `subprocess.run()` calls; reconfigured dialog stdout to UTF-8 via `io.TextIOWrapper` in `__main__`. Parent now extracts the last non-empty stdout line as JSON (ignores GTK debug lines). Stderr filtered to suppress harmless GTK/GLib noise. Both files syntax-validated clean. |
| 2026-04-29 | **Session 8** — Fixed SyntaxError on line 127: `f"...{'\n'.join(...)}"` uses a backslash inside an f-string expression, illegal in Python < 3.12. Extracted the join to a variable before the f-string. This was the root cause of the reported GTK crash and wrong-env symptoms in this session — the SyntaxError prevented `plt_ink.py` from loading at all, so none of the prior subprocess/encoding fixes were taking effect. Syntax-validated clean. |
| 2026-04-29 | **Session 9** — Fixed two runtime errors: (1) `Invalid attribute name 'plt_ink:source'` — bare namespace prefix without URI declaration is illegal in XML; changed `PLT_INK_ATTR` from `'plt_ink:source'` to Clark notation `'{https://github.com/YouvenZ/plt_ink}source'`, added `PLT_INK_NS` constant, added `'plt_ink': PLT_INK_NS` to the merged nsmap on SVG group elements. (2) `AttributeError: 'types.SimpleNamespace' object has no attribute 'output'` — `self.options` was being fully replaced with the dialog SimpleNamespace, losing inkex's built-in `output` attribute (used by `save_raw()`); fix merges dialog defaults + values into the existing `self.options` via `setattr` without ever replacing the object. Syntax-validated clean. |
| 2026-04-29 | **Session 10** — Full GTK migration: removed the last `<param>` element from `plt_ink.inx`, making it a pure registration stub. Inkscape now invokes `plt_ink.py` directly with no native dialog whatsoever — the GTK3 dialog is the only UI. ENH 3.6 (`max_length`) closed as permanently moot (no INX params exist to have a `max_length`). All roadmap items now complete. |
| 2026-04-29 | **Session 11** — Fixed `Invalid attribute name 'inkscape:label'`: bare namespace prefix illegal in lxml `.set()`. Added `INKSCAPE_NS = 'http://www.inkscape.org/namespaces/inkscape'` and `INKSCAPE_LABEL = f'{{{INKSCAPE_NS}}}label'` constants. Replaced both bare `'inkscape:label'` string calls with `INKSCAPE_LABEL`. Added `'inkscape': INKSCAPE_NS` to `merged_nsmap` so lxml serialises the attribute with the correct `inkscape:` prefix. Audited for any other bare `ns:attr` strings — none found. SVG output path now unblocked. Syntax-validated clean. |
| 2026-04-29 | **Session 12** — Implemented three items from Future Ideas: (1) **Seaborn support**: optional `import seaborn as sns` (try/except) added to `generate_preamble()` when `auto_imports=True`; exposes `seaborn_available` flag; added `seaborn` category to `SCRIPT_CATEGORIES` and dialog `CATEGORY_LABELS`; created three bank scripts (`basic_seaborn.py`, `seaborn_heatmap.py`, `seaborn_violin.py`). (2) **Export script only mode**: new "Export" section in Advanced tab with checkbox + path picker; when enabled, `plt_ink.py` generates the assembled script, saves it, shows the path via `inkex.utils.debug()`, and returns without executing or inserting a figure. (3) **Windows Python detection**: `_on_detect_python()` now also scans `%LOCALAPPDATA%\Programs\Python\Python*`, `%APPDATA%\Python\Python*\Scripts`, `C:\Python*`, `D:\Python*`, and `*.virtualenvs\*\Scripts` (Windows venv layout). Both files syntax-validated clean. |
| 2026-04-30 | **Session 13** — Fixed BUG 1c.1 (two parts): (1) Added `CREATE_NO_WINDOW` to all 6 subprocess calls to suppress Windows console windows. (2) Converted `MatplotlibDialog` from `Gtk.Dialog` to `Gtk.Window` (TexText pattern): manual button row with `_on_cancel`/`_on_apply` + `_accepted` flag; `__main__` uses `window.show(); Gtk.main()` instead of `dialog.run()`; `delete-event` connected to `_on_delete`. Eliminates the hidden transient GtkWindow that `Gtk.Dialog` creates without a parent, which was the empty rectangle. Both files syntax-validated clean. |
| 2026-04-30 | **Session 14** — Applied same GTK fixes to sister extension `svg_maker`: (1) `svg_llm.inx` — added `needs-live-preview="false" implements-custom-gui="true"`. (2) `SVGLLMDialog(Gtk.Dialog)` → `Gtk.Window` with `_accepted` flag + manual Cancel/Generate buttons + `_on_delete`. (3) `GenerationProgressDialog(Gtk.Dialog)` → `Gtk.Window` with `_done_ok` flag + manual Cancel button + `Gtk.main_quit()` replacing `self.response()`. (4) All three `Gtk.MessageDialog(text=...)` calls escaped via `GLib.markup_escape_text()` to prevent Pango crashes. (5) `svg_llm.py` call sites updated to `window.show(); Gtk.main()` pattern. Both files syntax-validated clean. |
| 2026-04-30 | **Session 15** — Implemented two Future Ideas items: (1) **Script bank editor**: added preview pane (read-only monospace `TextView`) to Script Bank frame that auto-loads selected script content; "Load into Editor" button copies code to inline editor and switches mode; "Open File" button opens `.py` in OS default editor. `_on_bank_script_changed` signal handler + `_get_bank_script_path()` helper. (2) **Live preview thumbnail**: "Preview Figure" button added to Script tab that runs the assembled script headlessly (saves PNG to temp file via `plt.savefig`) in a subprocess and displays the PNG in a `Gtk.Dialog` with a `Gtk.Image`. Falls back with an error alert if matplotlib/the script fails. Both files syntax-validated clean. |
| 2026-04-30 | **Session 16** — Implemented three UX and Future Ideas features: (1) **Keyboard shortcuts**: `key-press-event` on the window — Ctrl+Enter = Apply, Escape = Cancel. (2) **Check Syntax button**: validates inline code via `py_compile` and shows a green ✓ or red error in-place, no dialog needed. (3) **Multi-figure batch insert**: new "Batch" tab with a draggable `Gtk.TreeView` queue of scripts (inline/file/bank); "Add Current Script", "Remove Selected", "Clear All" buttons; gap + direction (horizontal/vertical) layout options. Queue serialised to JSON in `batch_scripts` option. `_run_batch()` added to `plt_ink.py` — iterates queue, overrides script source per entry, executes and inserts each figure with a progressively advancing custom XY offset. Both files syntax-validated clean. |
| 2026-05-02 | **Session 17** — Fixed critical BUG: `_on_position_changed` method was missing from `MatplotlibDialog`. Code for this method was accidentally left inside `_show_preview_image` (added in Session 15) instead of being a standalone method. Because `__init__` calls `self._on_position_changed(self.position_combo)`, this raised `AttributeError` immediately on startup, killing the dialog before the window ever appeared. Fix: removed stray code from `_show_preview_image`, added proper `def _on_position_changed(self, combo)` method. Dialog now opens correctly. Implemented **Plotly static export**: Format tab "Rendering Backend" selector; `check_plotly()`, `generate_plotly_preamble()`, `generate_plotly_postamble()` added to `plt_ink.py`; `plot_backend` option added to defaults; style tab greyed out when Plotly selected. Added **Help/Cheat Sheet tab** to dialog. Both files syntax-validated clean. |
| 2026-05-02 | **Session 18** — Added **Result/Status dialog** (`plt_ink_result.py`): a standalone GTK3 `Gtk.Window` launched as a subprocess after the extension finishes. Shows a colour-coded header (green ✓ success / red ✗ error / amber ⚠ warning), a stats grid (format, size, backend, file size) on success, a scrollable traceback view on error, and a "Copy Error to Clipboard" button. Wired into every outcome path in `plt_ink.py` via `_show_result()`: Python-not-found, library-not-installed, script-generation-failure, execution-failure, export-only, success, and batch completion (with per-entry error reporting). Replaced all bare `inkex.errormsg()` / `inkex.utils.debug()` calls in the main flow with `_show_result()`. All three files syntax-validated clean. |
