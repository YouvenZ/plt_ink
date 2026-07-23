"""
GTK3 dynamic dialog for plt_ink Matplotlib Figure Generator.

Replaces the static .inx parameter UI with a fully dynamic dialog:
  - One always-visible code editor; templates (script bank), opened files and
    recent files all load INTO it. An opened file can optionally be "linked"
    (re-read at Apply time; editor becomes read-only).
  - Fields show/hide based on selections (position mode, data format …)
  - Settings persist across sessions (see settings_path())
  - Debug mode and execution timeout are user-configurable
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Pango

import glob
import json
import os
import subprocess
import sys
import threading
from types import SimpleNamespace

import plt_ink_bank

# Suppress Windows console window for all subprocesses.
_WIN_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0


# ---------------------------------------------------------------------------
# Default options
# ---------------------------------------------------------------------------

def get_default_options():
    """Return all extension options with their defaults as a SimpleNamespace."""
    return SimpleNamespace(
        # Script
        python_path="python",
        script_source="inline",
        script_code=(
            "x = np.linspace(0, 10, 100)\n"
            "y = np.sin(x)\n"
            "plt.plot(x, y, label='sin(x)')\n"
            "plt.title('Sine Wave')\n"
            "plt.xlabel('X')\n"
            "plt.ylabel('Y')\n"
            "if _show_legend:\n"
            "    plt.legend(loc=_legend_position)"
        ),
        script_file="",
        bank_category="line_plots",
        bank_script="basic_line",
        # Preamble
        use_preamble=True,
        custom_preamble="",
        auto_imports=True,
        additional_imports="",
        # Format
        output_format="svg",
        figure_width=8.0,
        figure_height=6.0,
        dpi=96,
        transparent=False,
        tight_layout=True,
        constrained_layout=False,
        # Figure creation
        auto_create_figure=True,
        subplot_rows=1,
        subplot_cols=1,
        share_x=False,
        share_y=False,
        # Style
        plot_style="default",
        color_map="viridis",
        color_cycle="default",
        background_color="white",
        grid=True,
        grid_style="--",
        grid_alpha=0.3,
        legend=True,
        legend_position="best",
        auto_despine=False,
        # Placement
        position_mode="center",
        custom_x=0.0,
        custom_y=0.0,
        embed_image=True,
        scale_factor=1.0,
        # Typography
        font_family="sans-serif",
        font_size=10,
        title_size=14,
        label_size=12,
        line_width=1.5,
        marker_size=6.0,
        use_latex=False,
        # Error handling
        error_handling="stop",
        show_warnings=True,
        # Execution
        execution_timeout=60,
        # Debugging
        debug_mode=False,
        save_script=False,
        script_save_path="",
        keep_temp_files=False,
        export_script_only=False,
        export_script_path="",
        # Backend
        plot_backend="matplotlib",
        # Batch mode
        batch_mode=False,
        batch_scripts=None,   # list of [source_type, value, label] serialised as JSON string
        batch_gap=20,
        batch_direction="horizontal",
        # Data import
        use_data_file=False,
        data_file_path="",
        data_format="csv",
        csv_delimiter=",",
        skip_header=True,
        header_row=0,
        x_columns="0",
        y_columns="1",
        column_names="",
        load_all_columns=False,
        date_columns="",
        date_format="%Y-%m-%d",
    )


# ---------------------------------------------------------------------------
# Settings persistence
#
# All dialog options are saved to <user-config>/plt_ink/settings.json on Apply
# and restored at the next launch, so nothing has to be re-entered per session.
# Persistence is best-effort: any I/O error falls back to defaults silently.
# ---------------------------------------------------------------------------

SETTINGS_SCHEMA = 1

# Flags that must never survive a session — re-enabling them silently would
# change what Apply does in surprising ways.
_TRANSIENT_RESET = {
    "export_script_only": False,
    "batch_mode": False,
}


def settings_path():
    """Per-user settings file (e.g. %APPDATA%/plt_ink or ~/.config/plt_ink)."""
    return os.path.join(GLib.get_user_config_dir(), 'plt_ink', 'settings.json')


def load_saved_options():
    """Return (options, had_settings).

    Starts from defaults and overlays any saved values whose keys still exist,
    so renamed/removed options degrade gracefully across versions.
    """
    opts = get_default_options()
    try:
        with open(settings_path(), encoding='utf-8') as fh:
            saved = json.load(fh)
    except Exception:
        return opts, False
    if not isinstance(saved, dict):
        return opts, False
    for key, value in saved.items():
        if not key.startswith('_') and hasattr(opts, key):
            setattr(opts, key, value)
    for key, value in _TRANSIENT_RESET.items():
        setattr(opts, key, value)
    return opts, True


def save_options(opts):
    """Persist options atomically; also maintain the recent-files list."""
    path = settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Carry the recent-files list forward, promoting the current file.
        recent = []
        try:
            with open(path, encoding='utf-8') as fh:
                prev = json.load(fh)
            if isinstance(prev, dict):
                recent = [p for p in prev.get('_recent_script_files', [])
                          if isinstance(p, str)]
        except Exception:
            pass
        current = getattr(opts, 'script_file', '')
        if current:
            recent = [current] + [p for p in recent if p != current]

        payload = {'_schema': SETTINGS_SCHEMA,
                   '_recent_script_files': recent[:10]}
        payload.update(vars(opts))

        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2)
        os.replace(tmp, path)
    except Exception:
        pass  # never block figure generation on settings I/O


def load_recent_files():
    """Return the persisted recent-script-files list (may be empty)."""
    try:
        with open(settings_path(), encoding='utf-8') as fh:
            saved = json.load(fh)
        if isinstance(saved, dict):
            return [p for p in saved.get('_recent_script_files', [])
                    if isinstance(p, str)]
    except Exception:
        pass
    return []


def add_recent_file(path):
    """Promote a script path to the front of the recent list, on disk now."""
    try:
        sp = settings_path()
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        try:
            with open(sp, encoding='utf-8') as fh:
                saved = json.load(fh)
            if not isinstance(saved, dict):
                saved = {}
        except Exception:
            saved = {}
        recent = [p for p in saved.get('_recent_script_files', [])
                  if isinstance(p, str) and p != path]
        saved['_recent_script_files'] = [path] + recent[:9]
        saved.setdefault('_schema', SETTINGS_SCHEMA)
        tmp = sp + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(saved, fh, indent=2)
        os.replace(tmp, sp)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Python interpreter probing (shared by the Detect… button and first-run setup)
# ---------------------------------------------------------------------------

def probe_python_candidates():
    """Probe PATH + common venv/conda/installer locations.

    Returns a list of (path, version_string) tuples, PATH interpreters first.
    """
    candidates = []

    for name in ("python3", "python"):
        try:
            result = subprocess.run(
                [name, "--version"], capture_output=True, text=True, timeout=5,
                creationflags=_WIN_FLAGS,
            )
            if result.returncode == 0:
                ver = (result.stdout or result.stderr).strip()
                candidates.append((name, ver))
        except Exception:
            pass

    home = os.path.expanduser("~")
    search_patterns = [
        # Unix venv
        os.path.join(home, ".venv", "bin", "python"),
        os.path.join(home, "venv", "bin", "python"),
        os.path.join(home, ".virtualenvs", "*", "bin", "python"),
        # conda
        os.path.join(home, "miniconda3", "bin", "python"),
        os.path.join(home, "anaconda3", "bin", "python"),
        os.path.join(home, "miniconda3", "envs", "*", "bin", "python"),
        os.path.join(home, "anaconda3", "envs", "*", "bin", "python"),
        os.path.join(home, ".conda", "envs", "*", "bin", "python"),
        # Windows conda / venv (Scripts\ layout)
        os.path.join(home, "miniconda3", "python.exe"),
        os.path.join(home, "anaconda3", "python.exe"),
        os.path.join(home, "miniconda3", "envs", "*", "python.exe"),
        os.path.join(home, "anaconda3", "envs", "*", "python.exe"),
        os.path.join(home, ".conda", "envs", "*", "python.exe"),
        os.path.join(home, "venv", "Scripts", "python.exe"),
        os.path.join(home, ".venv", "Scripts", "python.exe"),
        os.path.join(home, ".virtualenvs", "*", "Scripts", "python.exe"),
    ]

    local_app = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    if local_app:
        search_patterns += [
            os.path.join(local_app, "Programs", "Python", "Python*", "python.exe"),
            os.path.join(local_app, "Programs", "Python", "Python*", "Scripts", "python.exe"),
        ]
    if app_data:
        search_patterns += [
            os.path.join(app_data, "Python", "Python*", "Scripts", "python.exe"),
        ]
    for drive in ("C:\\", "D:\\"):
        search_patterns.append(os.path.join(drive, "Python*", "python.exe"))

    for pattern in search_patterns:
        for exe in glob.glob(pattern):
            try:
                result = subprocess.run(
                    [exe, "--version"], capture_output=True, text=True, timeout=5,
                    creationflags=_WIN_FLAGS,
                )
                if result.returncode == 0:
                    ver = (result.stdout or result.stderr).strip()
                    if not any(c[0] == exe for c in candidates):
                        candidates.append((exe, ver))
            except Exception:
                pass

    return candidates


def autodetect_python(max_checks=5):
    """First-run helper: pick the best interpreter without user interaction.

    Prefers the first candidate that can import matplotlib; falls back to the
    first candidate found, then to plain "python".
    """
    candidates = probe_python_candidates()
    for exe, _ver in candidates[:max_checks]:
        try:
            result = subprocess.run(
                [exe, "-c", "import matplotlib"],
                capture_output=True, timeout=10, creationflags=_WIN_FLAGS,
            )
            if result.returncode == 0:
                return exe
        except Exception:
            pass
    return candidates[0][0] if candidates else "python"


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class MatplotlibDialog(Gtk.Window):
    """Dynamic GTK3 window — all UI state is self-contained."""

    SCRIPT_BANK_DIR = plt_ink_bank.BANK_DIR

    PLOT_STYLES = [
        ("default",                   "Default"),
        ("seaborn-v0_8",              "Seaborn"),
        ("seaborn-v0_8-whitegrid",    "Seaborn Whitegrid"),
        ("seaborn-v0_8-darkgrid",     "Seaborn Darkgrid"),
        ("ggplot",                    "ggplot"),
        ("bmh",                       "Bayesian Methods"),
        ("dark_background",           "Dark Background"),
        ("grayscale",                 "Grayscale"),
        ("fivethirtyeight",           "FiveThirtyEight"),
        ("tableau-colorblind10",      "Tableau Colorblind"),
        ("classic",                   "Classic Matplotlib"),
        # ── Academic / journal presets (plt_ink built-in) ──────────────────────
        ("ieee",                      "★ IEEE Journal (serif, 300 dpi)"),
        ("nature",                    "★ Nature / Science (colourblind-safe)"),
        ("apa",                       "★ APA / General Academic (sans-serif)"),
    ]

    COLORMAPS = [
        ("viridis",   "Viridis (perceptual)"),
        ("plasma",    "Plasma"),
        ("inferno",   "Inferno"),
        ("magma",     "Magma"),
        ("cividis",   "Cividis (colorblind)"),
        ("coolwarm",  "Cool Warm (diverging)"),
        ("RdBu",      "Red-Blue (diverging)"),
        ("rainbow",   "Rainbow"),
        ("jet",       "Jet"),
        ("turbo",     "Turbo"),
    ]

    COLOR_CYCLES = [
        ("default", "Default"),
        ("tab10",   "Tab10 (10 colors)"),
        ("tab20",   "Tab20 (20 colors)"),
        ("set1",    "Set1  (9 colors)"),
        ("set2",    "Set2  (8 colors)"),
        ("paired",  "Paired (12 colors)"),
        ("dark2",   "Dark2 (8 colors)"),
    ]

    LEGEND_POSITIONS = [
        ("best",          "Best (auto)"),
        ("upper right",   "Upper Right"),
        ("upper left",    "Upper Left"),
        ("lower right",   "Lower Right"),
        ("lower left",    "Lower Left"),
        ("center",        "Center"),
        ("center right",  "Center Right"),
        ("center left",   "Center Left"),
        ("upper center",  "Upper Center"),
        ("lower center",  "Lower Center"),
    ]

    POSITION_MODES = [
        ("center",        "Center of canvas"),
        ("selection",     "At selection"),
        ("custom",        "Custom coordinates"),
        ("top_left",      "Top left"),
        ("top_center",    "Top center"),
        ("top_right",     "Top right"),
        ("bottom_left",   "Bottom left"),
        ("bottom_center", "Bottom center"),
        ("bottom_right",  "Bottom right"),
    ]

    # Single source of truth — shared with plt_ink.py via plt_ink_bank.
    CATEGORY_LABELS = plt_ink_bank.CATEGORIES

    # ------------------------------------------------------------------ init

    def __init__(self, opts=None):
        super().__init__()
        self.set_title("Matplotlib Figure Generator")
        self.set_default_size(700, 760)
        self.set_resizable(True)
        self._accepted = False  # True when user clicks Apply
        self.opts = opts or get_default_options()

        # Unified-editor state
        self._script_file_path = ""    # last opened file ("" = none)
        self._loaded_template = None   # (category, name) of last loaded template
        self._editor_baseline = ""     # last programmatically loaded content

        self._build_ui()
        self._load_values()
        self.show_all()

        # Trigger visibility logic after show_all so widgets are realised
        self._update_link_row()
        self._on_position_changed(self.position_combo)
        self._on_data_toggle(self.use_data_check)
        self._on_data_format_changed(self.data_format_combo)
        self._on_auto_create_toggled(self.auto_create_check)
        self._on_save_script_toggled(self.save_script_check)
        self._on_export_script_toggled(self.export_script_only_check)

        self.connect("delete-event", self._on_delete)
        self.connect("key-press-event", self._on_key_press)

    def _on_delete(self, widget, event):
        """Window close button — treat as Cancel."""
        self._accepted = False
        Gtk.main_quit()
        return False

    def _on_cancel(self, *_):
        self._accepted = False
        Gtk.main_quit()

    def _on_apply(self, *_):
        self._accepted = True
        Gtk.main_quit()

    def _on_key_press(self, widget, event):
        """Ctrl+Enter = Apply; Escape = Cancel."""
        from gi.repository import Gdk
        keyval = event.keyval
        state   = event.state & Gtk.accelerator_get_default_mod_mask()
        ctrl    = Gdk.ModifierType.CONTROL_MASK
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and (state & ctrl):
            self._on_apply()
            return True
        if keyval == Gdk.KEY_Escape:
            self._on_cancel()
            return True
        return False

    # ------------------------------------------------------------------ helpers

    def _make_section(self, text):
        lbl = Gtk.Label()
        lbl.set_markup(f"<b>{GLib.markup_escape_text(text)}</b>")
        lbl.set_xalign(0.0)
        lbl.set_margin_top(10)
        lbl.set_margin_bottom(2)
        return lbl

    @staticmethod
    def _italic_label(text):
        lbl = Gtk.Label()
        lbl.set_markup(f"<i><small>{text}</small></i>")
        lbl.set_xalign(0.0)
        lbl.set_line_wrap(True)
        return lbl

    def _make_combo(self, items):
        """items: list of (id, label) tuples."""
        combo = Gtk.ComboBoxText()
        for val, label in items:
            combo.append(val, label)
        return combo

    def _set_combo(self, combo, value):
        model = combo.get_model()
        for i, row in enumerate(model):
            if row[0] == value:
                combo.set_active(i)
                return
        combo.set_active(0)

    def _get_combo_value(self, combo):
        return combo.get_active_id() or ""

    def _make_spin_float(self, lo, hi, step, digits=1):
        adj = Gtk.Adjustment(value=lo, lower=lo, upper=hi, step_increment=step)
        return Gtk.SpinButton(adjustment=adj, climb_rate=1, digits=digits)

    def _make_spin_int(self, lo, hi):
        adj = Gtk.Adjustment(value=lo, lower=lo, upper=hi, step_increment=1)
        return Gtk.SpinButton(adjustment=adj, climb_rate=1, digits=0)

    def _vbox(self, spacing=6, margin=12):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)
        box.set_margin_start(margin)
        box.set_margin_end(margin)
        box.set_margin_top(margin)
        box.set_margin_bottom(margin)
        return box

    def _hbox(self, spacing=6):
        return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing)

    def _scrolled(self, child, min_height=0):
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        if min_height:
            sw.set_min_content_height(min_height)
        sw.add(child)
        return sw

    def _get_tv(self, textview):
        buf = textview.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)

    def _set_tv(self, textview, text):
        textview.get_buffer().set_text(text or "")

    def _alert(self, message):
        from gi.repository import GLib as _GLib
        dlg = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
        )
        dlg.set_markup(_GLib.markup_escape_text(str(message)))
        dlg.run()
        dlg.destroy()

    # ------------------------------------------------------------------ build

    def _build_ui(self):
        # Root vertical box: notebook (expanding) + button row (fixed)
        root_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(root_vbox)

        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        root_vbox.pack_start(notebook, True, True, 0)
        self._notebook = notebook

        def tab(builder, label):
            sw = Gtk.ScrolledWindow()
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            sw.add(builder())
            notebook.append_page(sw, Gtk.Label(label=label))

        tab(self._build_script_tab,    "Script")
        tab(self._build_format_tab,    "Format")
        tab(self._build_style_tab,     "Style")
        tab(self._build_placement_tab, "Placement")
        tab(self._build_advanced_tab,  "Advanced")
        tab(self._build_data_tab,      "Data")
        tab(self._build_preamble_tab,  "Preamble")
        tab(self._build_batch_tab,     "Batch")
        tab(self._build_help_tab,      "Help")

        # --- Button row (like TexText's create_buttons approach) ---
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_start(8)
        button_box.set_margin_end(8)
        button_box.set_margin_top(4)
        button_box.set_margin_bottom(8)
        button_box.set_halign(Gtk.Align.END)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", self._on_cancel)
        button_box.pack_start(cancel_btn, False, False, 0)

        apply_btn = Gtk.Button(label="Apply")
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.connect("clicked", self._on_apply)
        button_box.pack_start(apply_btn, False, False, 0)

        root_vbox.pack_start(button_box, False, False, 0)

    # ── Script tab ─────────────────────────────────────────────────────────

    def _build_script_tab(self):
        box = self._vbox()

        box.pack_start(self._make_section("Python Interpreter"), False, False, 0)
        hb = self._hbox()
        hb.pack_start(Gtk.Label(label="Python path:"), False, False, 0)
        self.python_path_entry = Gtk.Entry()
        self.python_path_entry.set_hexpand(True)
        hb.pack_start(self.python_path_entry, True, True, 4)
        detect_btn = Gtk.Button(label="Detect…")
        detect_btn.connect("clicked", self._on_detect_python)
        hb.pack_start(detect_btn, False, False, 0)
        box.pack_start(hb, False, False, 0)
        box.pack_start(self._italic_label(
            "e.g. python, python3, /path/to/venv/bin/python  •  "
            "Use Detect… to find conda/venv environments"
        ), False, False, 0)

        box.pack_start(self._make_section("Script"), False, False, 0)

        # ── source toolbar — every source loads INTO the one editor below ──
        tb = self._hbox()
        templates_btn = Gtk.Button(label="Templates…")
        templates_btn.set_tooltip_text(
            "Browse the script bank and load a template into the editor")
        templates_btn.connect("clicked", self._on_open_template_browser)
        tb.pack_start(templates_btn, False, False, 0)

        open_file_btn = Gtk.Button(label="Open File…")
        open_file_btn.set_tooltip_text("Load a .py script from disk into the editor")
        open_file_btn.connect("clicked", self._on_open_script_file)
        tb.pack_start(open_file_btn, False, False, 0)

        self.recent_btn = Gtk.MenuButton(label="Recent")
        self.recent_btn.set_tooltip_text("Recently opened script files")
        self._rebuild_recent_menu()
        tb.pack_start(self.recent_btn, False, False, 0)

        self.script_origin_lbl = Gtk.Label(label="")
        self.script_origin_lbl.set_xalign(1.0)
        self.script_origin_lbl.set_ellipsize(Pango.EllipsizeMode.START)
        tb.pack_start(self.script_origin_lbl, True, True, 0)
        box.pack_start(tb, False, False, 0)

        # ── linked-file row (visible only after a file has been opened) ──
        self.link_row = self._hbox()
        self.link_check = Gtk.CheckButton(
            label="Link to file — re-read on Apply; editor is read-only")
        self.link_check.set_tooltip_text(
            "Keep editing the file in your own editor; plt_ink re-reads it "
            "every time you Apply")
        self.link_check.connect("toggled", self._on_link_toggled)
        self.link_row.pack_start(self.link_check, False, False, 0)
        reload_btn = Gtk.Button(label="Reload")
        reload_btn.set_tooltip_text("Re-read the file into the editor now")
        reload_btn.connect("clicked", self._on_reload_linked)
        self.link_row.pack_start(reload_btn, False, False, 0)
        self.linked_path_lbl = Gtk.Label(label="")
        self.linked_path_lbl.set_xalign(0.0)
        self.linked_path_lbl.set_ellipsize(Pango.EllipsizeMode.START)
        self.linked_path_lbl.get_style_context().add_class("dim-label")
        self.link_row.pack_start(self.linked_path_lbl, True, True, 4)
        box.pack_start(self.link_row, False, False, 0)

        # ── the editor ──
        self.editor_frame = Gtk.Frame(label="Python Code")
        ib = self._vbox(spacing=4, margin=8)
        self.code_view = Gtk.TextView()
        self.code_view.set_monospace(True)
        self.code_view.set_wrap_mode(Gtk.WrapMode.NONE)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.set_min_content_height(220)
        sw.add(self.code_view)
        ib.pack_start(sw, True, True, 0)
        ib.pack_start(self._italic_label(
            "Available: plt, np, fig, ax  •  _fig_width, _fig_height, _dpi  •  "
            "_colormap, _show_grid, _show_legend, _legend_position  •  apply_style(ax), get_cmap()\n"
            "Data (when enabled): df / data — DataFrame  •  "
            "x_data, y_data — arrays (list of arrays for multi-column)  •  "
            "x_columns, y_columns — aliases for multi-column  •  "
            "columns — dict  •  &lt;colname&gt; — named column"
        ), False, False, 0)

        # syntax check row
        syntax_row = self._hbox(spacing=6)
        check_syntax_btn = Gtk.Button(label="Check Syntax")
        check_syntax_btn.set_tooltip_text("Validate the code for Python syntax errors")
        check_syntax_btn.connect("clicked", self._on_check_syntax)
        syntax_row.pack_start(check_syntax_btn, False, False, 0)
        self.syntax_status_lbl = Gtk.Label(label="")
        self.syntax_status_lbl.set_xalign(0.0)
        syntax_row.pack_start(self.syntax_status_lbl, True, True, 0)
        ib.pack_start(syntax_row, False, False, 0)

        self.editor_frame.add(ib)
        box.pack_start(self.editor_frame, True, True, 0)

        # ── preview button ──
        preview_row = self._hbox(spacing=6)
        self.preview_btn = Gtk.Button(label="Preview Figure")
        self.preview_btn.set_tooltip_text(
            "Run the current script and show a thumbnail of the figure"
        )
        self.preview_btn.connect("clicked", self._on_preview_figure)
        preview_row.pack_start(self.preview_btn, False, False, 0)
        self.preview_status_lbl = Gtk.Label(label="")
        self.preview_status_lbl.set_xalign(0.0)
        preview_row.pack_start(self.preview_status_lbl, True, True, 0)
        box.pack_start(preview_row, False, False, 0)

        return box

    # ── Format tab ─────────────────────────────────────────────────────────

    def _build_format_tab(self):
        box = self._vbox()

        box.pack_start(self._make_section("Rendering Backend"), False, False, 0)
        self.backend_combo = self._make_combo([
            ("matplotlib", "Matplotlib (default)"),
            ("plotly",     "Plotly + Kaleido (interactive-style charts)"),
        ])
        self.backend_combo.connect("changed", self._on_backend_changed)
        box.pack_start(self.backend_combo, False, False, 0)
        box.pack_start(self._italic_label(
            "Plotly requires: pip install plotly kaleido  •  "
            "Style/Grid settings are ignored in Plotly mode"
        ), False, False, 0)

        box.pack_start(self._make_section("Output Format"), False, False, 0)
        self.output_format_combo = self._make_combo([
            ("svg", "SVG (Vector — best for Inkscape)"),
            ("png", "PNG (Raster)"),
            ("pdf", "PDF (Vector)"),
        ])
        box.pack_start(self.output_format_combo, False, False, 0)

        box.pack_start(self._make_section("Figure Size"), False, False, 0)
        g = Gtk.Grid(column_spacing=10, row_spacing=6)
        g.attach(Gtk.Label(label="Width (inches):"),  0, 0, 1, 1)
        self.fig_width_spin = self._make_spin_float(1.0, 50.0, 0.5, digits=1)
        g.attach(self.fig_width_spin, 1, 0, 1, 1)
        g.attach(Gtk.Label(label="Height (inches):"), 0, 1, 1, 1)
        self.fig_height_spin = self._make_spin_float(1.0, 50.0, 0.5, digits=1)
        g.attach(self.fig_height_spin, 1, 1, 1, 1)
        g.attach(Gtk.Label(label="Render DPI:"),      0, 2, 1, 1)
        self.dpi_spin = self._make_spin_int(50, 600)
        g.attach(self.dpi_spin, 1, 2, 1, 1)
        box.pack_start(g, False, False, 0)
        box.pack_start(self._italic_label(
            "96 = screen  •  150 = draft print  •  300 = publication  "
            "(DPI affects raster quality only, not display size in Inkscape)"
        ), False, False, 0)

        box.pack_start(self._make_section("Layout"), False, False, 0)
        self.transparent_check    = Gtk.CheckButton(label="Transparent background")
        self.tight_layout_check   = Gtk.CheckButton(label="Use tight layout")
        self.constrained_layout_check = Gtk.CheckButton(
            label="Use constrained layout (newer, recommended for complex figures)"
        )
        box.pack_start(self.transparent_check,         False, False, 0)
        box.pack_start(self.tight_layout_check,        False, False, 0)
        box.pack_start(self.constrained_layout_check,  False, False, 0)

        box.pack_start(self._make_section("Figure Creation"), False, False, 0)
        self.auto_create_check = Gtk.CheckButton(
            label="Auto-create figure / axes if not in code"
        )
        self.auto_create_check.connect("toggled", self._on_auto_create_toggled)
        box.pack_start(self.auto_create_check, False, False, 0)

        self.subplot_frame = Gtk.Frame(label="Subplot Grid")
        sp = self._vbox(spacing=4, margin=8)
        sg = Gtk.Grid(column_spacing=8, row_spacing=4)
        sg.attach(Gtk.Label(label="Rows:"), 0, 0, 1, 1)
        self.subplot_rows_spin = self._make_spin_int(1, 10)
        sg.attach(self.subplot_rows_spin, 1, 0, 1, 1)
        sg.attach(Gtk.Label(label="Cols:"), 2, 0, 1, 1)
        self.subplot_cols_spin = self._make_spin_int(1, 10)
        sg.attach(self.subplot_cols_spin, 3, 0, 1, 1)
        sp.pack_start(sg, False, False, 0)
        self.share_x_check = Gtk.CheckButton(label="Share X axis")
        self.share_y_check = Gtk.CheckButton(label="Share Y axis")
        sp.pack_start(self.share_x_check, False, False, 0)
        sp.pack_start(self.share_y_check, False, False, 0)
        self.subplot_frame.add(sp)
        box.pack_start(self.subplot_frame, False, False, 0)

        return box

    # ── Style tab ──────────────────────────────────────────────────────────

    def _build_style_tab(self):
        box = self._vbox()
        self._style_tab_box = box  # kept for backend sensitivity toggle

        box.pack_start(self._make_section("Plot Style"), False, False, 0)
        self.plot_style_combo = self._make_combo(self.PLOT_STYLES)
        box.pack_start(self.plot_style_combo, False, False, 0)

        box.pack_start(self._make_section("Colors"), False, False, 0)
        cg = Gtk.Grid(column_spacing=10, row_spacing=6)
        cg.attach(Gtk.Label(label="Colormap:"),    0, 0, 1, 1)
        self.colormap_combo = self._make_combo(self.COLORMAPS)
        cg.attach(self.colormap_combo,             1, 0, 1, 1)
        cg.attach(Gtk.Label(label="Color cycle:"), 0, 1, 1, 1)
        self.color_cycle_combo = self._make_combo(self.COLOR_CYCLES)
        cg.attach(self.color_cycle_combo,          1, 1, 1, 1)
        cg.attach(Gtk.Label(label="Background:"),  0, 2, 1, 1)
        self.bg_color_entry = Gtk.Entry()
        cg.attach(self.bg_color_entry,             1, 2, 1, 1)
        box.pack_start(cg, False, False, 0)
        box.pack_start(self._italic_label(
            "Color name (white, lightgray) or hex (#f0f0f0)"
        ), False, False, 0)

        box.pack_start(self._make_section("Grid"), False, False, 0)
        self.grid_check = Gtk.CheckButton(label="Show grid")
        box.pack_start(self.grid_check, False, False, 0)
        gg = Gtk.Grid(column_spacing=10, row_spacing=6)
        gg.attach(Gtk.Label(label="Style:"), 0, 0, 1, 1)
        self.grid_style_combo = self._make_combo([
            ("--", "Dashed (--)"),
            ("-",  "Solid (-)"),
            (":",  "Dotted (:)"),
            ("-.", "Dash-dot (-.)"),
        ])
        gg.attach(self.grid_style_combo,           1, 0, 1, 1)
        gg.attach(Gtk.Label(label="Alpha:"),       0, 1, 1, 1)
        self.grid_alpha_spin = self._make_spin_float(0.0, 1.0, 0.05, digits=2)
        gg.attach(self.grid_alpha_spin,            1, 1, 1, 1)
        box.pack_start(gg, False, False, 0)

        box.pack_start(self._make_section("Legend"), False, False, 0)
        self.legend_check = Gtk.CheckButton(label="Show legend")
        box.pack_start(self.legend_check, False, False, 0)
        lh = self._hbox()
        lh.pack_start(Gtk.Label(label="Position:"), False, False, 0)
        self.legend_pos_combo = self._make_combo(self.LEGEND_POSITIONS)
        lh.pack_start(self.legend_pos_combo, True, True, 4)
        box.pack_start(lh, False, False, 0)

        box.pack_start(self._make_section("Spines"), False, False, 0)
        self.despine_check = Gtk.CheckButton(
            label="Remove top/right spines (cleaner publication look)"
        )
        box.pack_start(self.despine_check, False, False, 0)

        return box

    # ── Placement tab ──────────────────────────────────────────────────────

    def _build_placement_tab(self):
        box = self._vbox()

        box.pack_start(self._make_section("Insert Position"), False, False, 0)
        self.position_combo = self._make_combo(self.POSITION_MODES)
        self.position_combo.connect("changed", self._on_position_changed)
        box.pack_start(self.position_combo, False, False, 0)
        box.pack_start(self._italic_label(
            '"At selection" uses the bounding box center of the selected object.'
        ), False, False, 0)

        self.custom_pos_frame = Gtk.Frame(label="Custom Coordinates")
        cp = self._vbox(spacing=4, margin=8)
        cpg = Gtk.Grid(column_spacing=8, row_spacing=4)
        cpg.attach(Gtk.Label(label="X:"), 0, 0, 1, 1)
        self.custom_x_spin = self._make_spin_float(-10000, 10000, 1.0, digits=1)
        cpg.attach(self.custom_x_spin, 1, 0, 1, 1)
        cpg.attach(Gtk.Label(label="Y:"), 2, 0, 1, 1)
        self.custom_y_spin = self._make_spin_float(-10000, 10000, 1.0, digits=1)
        cpg.attach(self.custom_y_spin, 3, 0, 1, 1)
        cp.pack_start(cpg, False, False, 0)
        self.custom_pos_frame.add(cp)
        box.pack_start(self.custom_pos_frame, False, False, 0)

        box.pack_start(self._make_section("Scale"), False, False, 0)
        sh = self._hbox()
        sh.pack_start(Gtk.Label(label="Scale factor:"), False, False, 0)
        self.scale_factor_spin = self._make_spin_float(0.1, 10.0, 0.1, digits=2)
        sh.pack_start(self.scale_factor_spin, False, False, 4)
        box.pack_start(sh, False, False, 0)
        box.pack_start(self._italic_label("1.0 = original size"), False, False, 0)

        box.pack_start(self._make_section("Embedding"), False, False, 0)
        self.embed_check = Gtk.CheckButton(
            label="Embed image in SVG document (recommended — no external file needed)"
        )
        box.pack_start(self.embed_check, False, False, 0)

        return box

    # ── Advanced tab ───────────────────────────────────────────────────────

    def _build_advanced_tab(self):
        box = self._vbox()

        box.pack_start(self._make_section("Typography"), False, False, 0)
        tg = Gtk.Grid(column_spacing=10, row_spacing=6)
        tg.attach(Gtk.Label(label="Font family:"), 0, 0, 1, 1)
        self.font_family_combo = self._make_combo([
            ("sans-serif",      "Sans-serif"),
            ("serif",           "Serif"),
            ("monospace",       "Monospace"),
            ("DejaVu Sans",     "DejaVu Sans"),
            ("Arial",           "Arial"),
            ("Helvetica",       "Helvetica"),
            ("Times New Roman", "Times New Roman"),
        ])
        tg.attach(self.font_family_combo, 1, 0, 1, 1)
        tg.attach(Gtk.Label(label="Base size:"),   0, 1, 1, 1)
        self.font_size_spin  = self._make_spin_int(6, 72)
        tg.attach(self.font_size_spin,  1, 1, 1, 1)
        tg.attach(Gtk.Label(label="Title size:"),  0, 2, 1, 1)
        self.title_size_spin = self._make_spin_int(6, 72)
        tg.attach(self.title_size_spin, 1, 2, 1, 1)
        tg.attach(Gtk.Label(label="Label size:"),  0, 3, 1, 1)
        self.label_size_spin = self._make_spin_int(6, 72)
        tg.attach(self.label_size_spin, 1, 3, 1, 1)
        box.pack_start(tg, False, False, 0)

        box.pack_start(self._make_section("Line & Marker"), False, False, 0)
        lmg = Gtk.Grid(column_spacing=10, row_spacing=6)
        lmg.attach(Gtk.Label(label="Line width:"),  0, 0, 1, 1)
        self.line_width_spin   = self._make_spin_float(0.5, 10.0, 0.5, digits=1)
        lmg.attach(self.line_width_spin,   1, 0, 1, 1)
        lmg.attach(Gtk.Label(label="Marker size:"), 0, 1, 1, 1)
        self.marker_size_spin  = self._make_spin_float(1.0, 20.0, 0.5, digits=1)
        lmg.attach(self.marker_size_spin,  1, 1, 1, 1)
        box.pack_start(lmg, False, False, 0)

        box.pack_start(self._make_section("LaTeX"), False, False, 0)
        self.latex_check = Gtk.CheckButton(
            label="Use LaTeX rendering (requires texlive / miktex installed)"
        )
        box.pack_start(self.latex_check, False, False, 0)

        box.pack_start(self._make_section("Error Handling"), False, False, 0)
        self.error_handling_combo = self._make_combo([
            ("stop", "Stop and show error"),
            ("warn", "Show warning and continue"),
        ])
        box.pack_start(self.error_handling_combo, False, False, 0)
        self.show_warnings_check = Gtk.CheckButton(label="Show Python warnings")
        box.pack_start(self.show_warnings_check, False, False, 0)

        box.pack_start(self._make_section("Execution"), False, False, 0)
        eh = self._hbox()
        eh.pack_start(Gtk.Label(label="Timeout (seconds):"), False, False, 0)
        self.timeout_spin = self._make_spin_int(5, 600)
        eh.pack_start(self.timeout_spin, False, False, 4)
        box.pack_start(eh, False, False, 0)

        box.pack_start(self._make_section("Debugging"), False, False, 0)
        self.debug_mode_check = Gtk.CheckButton(
            label="Enable debug logging to temp file"
        )
        box.pack_start(self.debug_mode_check, False, False, 0)
        self.save_script_check = Gtk.CheckButton(
            label="Save generated script to file"
        )
        self.save_script_check.connect("toggled", self._on_save_script_toggled)
        box.pack_start(self.save_script_check, False, False, 0)

        self.script_save_frame = Gtk.Frame()
        ss = self._vbox(spacing=4, margin=8)
        ssh = self._hbox()
        ssh.pack_start(Gtk.Label(label="Path:"), False, False, 0)
        self.script_save_entry = Gtk.Entry()
        self.script_save_entry.set_hexpand(True)
        ssh.pack_start(self.script_save_entry, True, True, 4)
        browse_save = Gtk.Button(label="Browse…")
        browse_save.connect("clicked", self._on_browse_save)
        ssh.pack_start(browse_save, False, False, 0)
        ss.pack_start(ssh, False, False, 0)
        self.script_save_frame.add(ss)
        box.pack_start(self.script_save_frame, False, False, 0)

        self.keep_temp_check = Gtk.CheckButton(
            label="Keep temporary files (useful for manual debugging)"
        )
        box.pack_start(self.keep_temp_check, False, False, 0)

        box.pack_start(self._make_section("Export"), False, False, 0)
        self.export_script_only_check = Gtk.CheckButton(
            label="Export script only — generate .py file, skip figure insertion"
        )
        self.export_script_only_check.connect("toggled", self._on_export_script_toggled)
        box.pack_start(self.export_script_only_check, False, False, 0)

        self.export_script_frame = Gtk.Frame()
        es = self._vbox(spacing=4, margin=8)
        esh = self._hbox()
        esh.pack_start(Gtk.Label(label="Save to:"), False, False, 0)
        self.export_script_entry = Gtk.Entry()
        self.export_script_entry.set_placeholder_text("Leave blank for auto-named file in extension folder")
        self.export_script_entry.set_hexpand(True)
        esh.pack_start(self.export_script_entry, True, True, 4)
        browse_export = Gtk.Button(label="Browse\u2026")
        browse_export.connect("clicked", self._on_browse_export)
        esh.pack_start(browse_export, False, False, 0)
        es.pack_start(esh, False, False, 0)
        self.export_script_frame.add(es)
        box.pack_start(self.export_script_frame, False, False, 0)

        return box

    # ── Data Import tab ────────────────────────────────────────────────────

    def _build_data_tab(self):
        box = self._vbox()

        self.use_data_check = Gtk.CheckButton(label="Import data from file")
        self.use_data_check.connect("toggled", self._on_data_toggle)
        box.pack_start(self.use_data_check, False, False, 0)

        self.data_frame = Gtk.Frame()
        db = self._vbox(spacing=6, margin=8)

        fh = self._hbox()
        fh.pack_start(Gtk.Label(label="File:"), False, False, 0)
        self.data_file_entry = Gtk.Entry()
        self.data_file_entry.set_hexpand(True)
        fh.pack_start(self.data_file_entry, True, True, 4)
        browse_data = Gtk.Button(label="Browse…")
        browse_data.connect("clicked", self._on_browse_data)
        fh.pack_start(browse_data, False, False, 0)
        db.pack_start(fh, False, False, 0)

        dh = self._hbox()
        dh.pack_start(Gtk.Label(label="Format:"), False, False, 0)
        self.data_format_combo = self._make_combo([
            ("csv",   "CSV"),
            ("txt",   "Text (space/tab separated)"),
            ("excel", "Excel (.xlsx)"),
            ("json",  "JSON"),
        ])
        self.data_format_combo.connect("changed", self._on_data_format_changed)
        dh.pack_start(self.data_format_combo, True, True, 4)
        db.pack_start(dh, False, False, 0)

        # CSV-specific options (hidden for other formats)
        self.csv_options_frame = Gtk.Frame(label="CSV / Text Options")
        cv = self._vbox(spacing=4, margin=8)
        cvg = Gtk.Grid(column_spacing=8, row_spacing=4)
        cvg.attach(Gtk.Label(label="Delimiter:"), 0, 0, 1, 1)
        self.delimiter_entry = Gtk.Entry()
        self.delimiter_entry.set_max_length(4)
        self.delimiter_entry.set_width_chars(4)
        cvg.attach(self.delimiter_entry, 1, 0, 1, 1)
        self.skip_header_check = Gtk.CheckButton(label="File has header row")
        cvg.attach(self.skip_header_check, 0, 1, 2, 1)
        cvg.attach(Gtk.Label(label="Header row (0-indexed):"), 0, 2, 1, 1)
        self.header_row_spin = self._make_spin_int(0, 100)
        cvg.attach(self.header_row_spin, 1, 2, 1, 1)
        cv.pack_start(cvg, False, False, 0)
        self.csv_options_frame.add(cv)
        db.pack_start(self.csv_options_frame, False, False, 0)

        # Column selection
        db.pack_start(self._make_section("Column Selection"), False, False, 0)
        cg = Gtk.Grid(column_spacing=10, row_spacing=6)
        cg.attach(Gtk.Label(label="X column(s):"),    0, 0, 1, 1)
        self.x_columns_entry = Gtk.Entry()
        cg.attach(self.x_columns_entry, 1, 0, 1, 1)
        cg.attach(Gtk.Label(label="Y column(s):"),    0, 1, 1, 1)
        self.y_columns_entry = Gtk.Entry()
        cg.attach(self.y_columns_entry, 1, 1, 1, 1)
        cg.attach(Gtk.Label(label="Column names:"),   0, 2, 1, 1)
        self.col_names_entry = Gtk.Entry()
        cg.attach(self.col_names_entry, 1, 2, 1, 1)
        db.pack_start(cg, False, False, 0)
        db.pack_start(self._italic_label(
            'Single index "0", list "0,1,2", or range "0-3"'
        ), False, False, 0)
        self.load_all_check = Gtk.CheckButton(label="Load all columns into dict")
        db.pack_start(self.load_all_check, False, False, 0)

        # Date parsing
        db.pack_start(self._make_section("Date / Time Parsing"), False, False, 0)
        dtg = Gtk.Grid(column_spacing=10, row_spacing=4)
        dtg.attach(Gtk.Label(label="Date column(s):"), 0, 0, 1, 1)
        self.date_columns_entry = Gtk.Entry()
        dtg.attach(self.date_columns_entry, 1, 0, 1, 1)
        dtg.attach(Gtk.Label(label="Date format:"),    0, 1, 1, 1)
        self.date_format_entry = Gtk.Entry()
        dtg.attach(self.date_format_entry, 1, 1, 1, 1)
        db.pack_start(dtg, False, False, 0)
        db.pack_start(self._italic_label(
            "%Y-%m-%d   %H:%M:%S   %d/%m/%Y   %Y-%m-%dT%H:%M:%S"
        ), False, False, 0)

        db.pack_start(self._make_section("Available Variables in Scripts"), False, False, 0)
        db.pack_start(self._italic_label(
            "df / data — full DataFrame\n"
            "x_data — X array (single col) or list of arrays (multi-col)\n"
            "y_data — Y array (single col) or list of arrays (multi-col)\n"
            "x_columns / y_columns — aliases for multi-column x_data / y_data\n"
            "columns — dict keyed by 'x0','x1',... and 'y0','y1',...\n"
            "&lt;colname&gt; — direct variable for each name in Column names field"
        ), False, False, 0)

        self.data_frame.add(db)
        box.pack_start(self.data_frame, False, False, 0)
        return box

    # ── Preamble tab ───────────────────────────────────────────────────────

    def _build_preamble_tab(self):
        box = self._vbox()

        self.use_preamble_check = Gtk.CheckButton(
            label="Include full preamble (imports, style config, helpers)"
        )
        box.pack_start(self.use_preamble_check, False, False, 0)
        self.auto_imports_check = Gtk.CheckButton(
            label="Auto-import numpy as np, matplotlib.pyplot as plt"
        )
        box.pack_start(self.auto_imports_check, False, False, 0)

        box.pack_start(self._make_section("Additional Imports"), False, False, 0)
        box.pack_start(self._italic_label(
            'e.g.  from scipy import stats\nimport seaborn as sns'
        ), False, False, 0)
        ai_sw = Gtk.ScrolledWindow()
        ai_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        ai_sw.set_min_content_height(80)
        self.additional_imports_view = Gtk.TextView()
        self.additional_imports_view.set_monospace(True)
        ai_sw.add(self.additional_imports_view)
        box.pack_start(ai_sw, False, False, 0)

        box.pack_start(self._make_section("Custom Preamble Code"), False, False, 0)
        box.pack_start(self._italic_label(
            "Runs after imports and rcParams, before your script code."
        ), False, False, 0)
        cp_sw = Gtk.ScrolledWindow()
        cp_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        cp_sw.set_min_content_height(160)
        self.custom_preamble_view = Gtk.TextView()
        self.custom_preamble_view.set_monospace(True)
        cp_sw.add(self.custom_preamble_view)
        box.pack_start(cp_sw, True, True, 0)

        return box

    def _build_help_tab(self):
        """Cheat sheet of all variables and helpers available to user scripts."""
        box = self._vbox()

        HELP_TEXT = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  plt_ink — Script Cheat Sheet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MATPLOTLIB MODE — always available when preamble is enabled
──────────────────────────────────────────────────────────────
  import matplotlib.pyplot as plt   (alias: plt)
  import numpy as np                (alias: np)
  import seaborn as sns             (if installed; seaborn_available = True/False)

Configuration variables (reflect dialog settings)
  _fig_width        figure width in inches
  _fig_height       figure height in inches
  _dpi              render DPI
  _show_grid        True / False
  _show_legend      True / False
  _legend_position  e.g. 'best', 'upper right'
  _colormap         colormap name e.g. 'viridis'
  _transparent      True / False
  _subplot_rows     number of subplot rows
  _subplot_cols     number of subplot columns

Helper functions
  apply_style(ax=None)  — applies grid/despine to an axis
  get_cmap(name=None)   — returns a Colormap (matplotlib 3.7+ safe)

Figure creation (when Auto-create is ON and no plt.figure/subplots in code)
  fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))  ← auto-added

──────────────────────────────────────────────────────────────
DATA VARIABLES  (Data tab → Use data file)
──────────────────────────────────────────────────────────────
  df / data         the full pandas DataFrame
  x_data            first X column as numpy array (single-column mode)
  y_data            first Y column as numpy array (single-column mode)
  x_columns         list of X arrays (multi-column mode)
  y_columns         list of Y arrays (multi-column mode)
  columns           dict: 'x0','x1',…,'y0','y1',… → numpy arrays
  <colname>         named columns (safe Python identifier, e.g. temperature)

──────────────────────────────────────────────────────────────
PLOTLY MODE  (Format tab → Backend: Plotly)
──────────────────────────────────────────────────────────────
  import plotly.graph_objects as go  (alias: go)
  import plotly.express as px        (alias: px)
  import numpy as np

  Same _fig_width, _fig_height, _dpi, _colormap variables available.
  Your script must assign the figure to a variable named  fig  or  _fig_plotly.

  Example:
    fig = px.scatter(x=[1,2,3], y=[4,5,6], title="My Chart")

──────────────────────────────────────────────────────────────
QUICK EXAMPLES
──────────────────────────────────────────────────────────────
  # Simple line plot
  x = np.linspace(0, 2*np.pi, 200)
  plt.plot(x, np.sin(x))
  plt.title("Sine Wave")

  # Using data file variables
  plt.plot(x_data, y_data, marker='o')

  # Multi-panel (subplot_rows=2, subplot_cols=1 in Format tab)
  axes[0].plot(x_data, y_data)
  axes[1].hist(y_data, bins=20)

  # Plotly example
  fig = go.Figure(go.Scatter(x=[1,2,3], y=[4,5,6], mode='lines+markers'))
  fig.update_layout(title="Plotly Figure")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        tv = Gtk.TextView()
        tv.set_editable(False)
        tv.set_monospace(True)
        tv.set_wrap_mode(Gtk.WrapMode.NONE)
        tv.get_buffer().set_text(HELP_TEXT)
        tv.set_margin_start(8)
        tv.set_margin_end(8)
        tv.set_margin_top(8)
        tv.set_margin_bottom(8)
        box.pack_start(tv, True, True, 0)
        return box

    def _build_batch_tab(self):
        """Batch insert tab — queue multiple scripts, insert them in a row/grid."""
        box = self._vbox()

        box.pack_start(self._make_section("Batch Mode"), False, False, 0)
        box.pack_start(self._italic_label(
            "Add scripts to the queue below. Click Apply — each script runs in sequence "
            "and figures are placed left-to-right with the configured spacing. "
            "Individual script settings (format, style, size) follow the Format/Style tabs."
        ), False, False, 0)

        # Enable batch toggle
        self.batch_mode_check = Gtk.CheckButton(label="Enable Batch Mode")
        self.batch_mode_check.set_tooltip_text(
            "When checked, Apply runs all queued scripts instead of the single script on the Script tab"
        )
        self.batch_mode_check.connect("toggled", self._on_batch_mode_toggled)
        box.pack_start(self.batch_mode_check, False, False, 0)

        # Batch controls frame
        self.batch_controls_frame = Gtk.Frame(label="Script Queue")
        bc = self._vbox(spacing=6, margin=8)

        # Queue list: columns = (source_type, value, label)
        self._batch_store = Gtk.ListStore(str, str, str)
        self._batch_tv = Gtk.TreeView(model=self._batch_store)
        self._batch_tv.set_reorderable(True)
        self._batch_tv.append_column(
            Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=0)
        )
        val_col = Gtk.TreeViewColumn("Script / Path", Gtk.CellRendererText(), text=2)
        val_col.set_expand(True)
        self._batch_tv.append_column(val_col)
        queue_sw = Gtk.ScrolledWindow()
        queue_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        queue_sw.set_min_content_height(140)
        queue_sw.add(self._batch_tv)
        bc.pack_start(queue_sw, True, True, 0)

        # Queue action buttons
        qbtn_row = self._hbox(spacing=6)
        add_inline_btn = Gtk.Button(label="Add Current Script")
        add_inline_btn.set_tooltip_text(
            "Add the script currently selected on the Script tab to the queue"
        )
        add_inline_btn.connect("clicked", self._on_batch_add_current)
        remove_btn = Gtk.Button(label="Remove Selected")
        remove_btn.connect("clicked", self._on_batch_remove)
        clear_btn = Gtk.Button(label="Clear All")
        clear_btn.connect("clicked", self._on_batch_clear)
        qbtn_row.pack_start(add_inline_btn, False, False, 0)
        qbtn_row.pack_start(remove_btn, False, False, 0)
        qbtn_row.pack_start(clear_btn, False, False, 0)
        bc.pack_start(qbtn_row, False, False, 0)

        self.batch_controls_frame.add(bc)
        box.pack_start(self.batch_controls_frame, True, True, 0)

        # Layout options
        layout_frame = Gtk.Frame(label="Placement Layout")
        lf = self._vbox(spacing=6, margin=8)

        gap_row = self._hbox()
        gap_row.pack_start(Gtk.Label(label="Gap between figures (px):"), False, False, 0)
        self.batch_gap_spin = self._make_spin_int(0, 500)
        self.batch_gap_spin.set_value(20)
        gap_row.pack_start(self.batch_gap_spin, False, False, 4)
        lf.pack_start(gap_row, False, False, 0)

        dir_row = self._hbox()
        dir_row.pack_start(Gtk.Label(label="Direction:"), False, False, 0)
        self.batch_direction_combo = self._make_combo([
            ("horizontal", "Left → Right"),
            ("vertical",   "Top → Bottom"),
        ])
        dir_row.pack_start(self.batch_direction_combo, False, False, 4)
        lf.pack_start(dir_row, False, False, 0)

        layout_frame.add(lf)
        box.pack_start(layout_frame, False, False, 0)

        box.pack_start(self._italic_label(
            "Tip: drag rows in the queue to reorder. "
            "Ctrl+Enter or Apply generates all figures in sequence."
        ), False, False, 0)

        return box

    # ------------------------------------------------------------------ signals

    # ── unified script editor: templates / files / recent all load here ──

    def _on_open_template_browser(self, _btn):
        """Searchable template browser; loads the chosen script into the editor."""
        dlg = Gtk.Dialog(title="Script Templates", transient_for=self, modal=True)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        "Load into Editor", Gtk.ResponseType.OK)
        dlg.set_default_size(780, 540)
        content = dlg.get_content_area()
        content.set_spacing(6)
        content.set_margin_start(10)
        content.set_margin_end(10)
        content.set_margin_top(10)

        # filter row: search + category
        frow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search = Gtk.SearchEntry()
        search.set_placeholder_text("Search templates…")
        frow.pack_start(search, True, True, 0)
        cat_combo = Gtk.ComboBoxText()
        cat_combo.append("", "All Categories")
        for cid, label in plt_ink_bank.CATEGORIES.items():
            cat_combo.append(cid, label)
        cat_combo.set_active(0)
        frow.pack_start(cat_combo, False, False, 0)
        content.pack_start(frow, False, False, 0)

        # collect all metadata once
        metas = []
        for cid in plt_ink_bank.CATEGORIES:
            for m in plt_ink_bank.list_scripts(cid):
                m['category'] = cid
                metas.append(m)

        # list + code preview side by side
        store = Gtk.ListStore(str, str, str, int)   # title, category, data?, meta idx
        tv = Gtk.TreeView(model=store)
        tv.append_column(Gtk.TreeViewColumn("Template", Gtk.CellRendererText(), text=0))
        tv.append_column(Gtk.TreeViewColumn("Category", Gtk.CellRendererText(), text=1))
        tv.append_column(Gtk.TreeViewColumn("Data",     Gtk.CellRendererText(), text=2))
        list_sw = Gtk.ScrolledWindow()
        list_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        list_sw.add(tv)

        preview_buf = Gtk.TextBuffer()
        preview_view = Gtk.TextView(buffer=preview_buf)
        preview_view.set_monospace(True)
        preview_view.set_editable(False)
        prev_sw = Gtk.ScrolledWindow()
        prev_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        prev_sw.add(preview_view)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.pack1(list_sw, resize=True, shrink=False)
        paned.pack2(prev_sw, resize=True, shrink=False)
        paned.set_position(340)
        content.pack_start(paned, True, True, 0)

        desc_lbl = Gtk.Label(label="")
        desc_lbl.set_xalign(0.0)
        desc_lbl.set_line_wrap(True)
        content.pack_start(desc_lbl, False, False, 0)

        def repopulate(*_a):
            store.clear()
            q = search.get_text().lower().strip()
            cat = cat_combo.get_active_id()
            for i, m in enumerate(metas):
                if cat and m['category'] != cat:
                    continue
                if q:
                    haystack = ' '.join(
                        [m['title'], m['name'], m['description']] + m['tags']
                    ).lower()
                    if q not in haystack:
                        continue
                store.append([
                    m['title'],
                    plt_ink_bank.CATEGORIES[m['category']],
                    "needs data" if m['requires_data'] else "",
                    i,
                ])
            if len(store):
                tv.get_selection().select_path(Gtk.TreePath.new_first())

        def on_select(sel):
            model, it = sel.get_selected()
            if not it:
                return
            m = metas[model[it][3]]
            desc_lbl.set_markup(
                f"<i>{GLib.markup_escape_text(m['description'])}</i>")
            try:
                with open(m['path'], encoding='utf-8', errors='replace') as fh:
                    preview_buf.set_text(fh.read())
            except Exception as exc:
                preview_buf.set_text(f"# Could not read file:\n# {exc}")

        search.connect("search-changed", repopulate)
        cat_combo.connect("changed", repopulate)
        tv.get_selection().connect("changed", on_select)
        tv.connect("row-activated",
                   lambda *_a: dlg.response(Gtk.ResponseType.OK))
        repopulate()

        dlg.show_all()
        chosen = None
        if dlg.run() == Gtk.ResponseType.OK:
            model, it = tv.get_selection().get_selected()
            if it:
                chosen = metas[model[it][3]]
        dlg.destroy()

        if chosen:
            try:
                with open(chosen['path'], encoding='utf-8', errors='replace') as fh:
                    code = fh.read()
            except Exception as exc:
                self._alert(f"Could not read template:\n{exc}")
                return
            self._load_script_into_editor(code, template=chosen)

    def _load_script_into_editor(self, code, template=None, file_path=None):
        """Put code into the editor, tracking its origin.

        Asks before overwriting edits the user has made since the last load.
        Returns True when the editor content was replaced.
        """
        current = self._get_tv(self.code_view)
        if current.strip() and current != self._editor_baseline:
            if not self._confirm("Replace the current code in the editor?"):
                return False
        if template is not None:
            self._loaded_template = (template['category'], template['name'])
            self._script_file_path = ""
            self.link_check.set_active(False)
            self.script_origin_lbl.set_markup(
                f"<i>Template: {GLib.markup_escape_text(template['title'])}</i>")
        elif file_path:
            self._loaded_template = None
            self._script_file_path = file_path
            add_recent_file(file_path)
            self._rebuild_recent_menu()
            self.script_origin_lbl.set_markup(
                f"<i>{GLib.markup_escape_text(os.path.basename(file_path))}</i>")
        self._set_tv(self.code_view, code)
        self._editor_baseline = code
        self._update_link_row()
        return True

    def _confirm(self, text):
        dlg = Gtk.MessageDialog(
            parent=self, modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=text,
        )
        response = dlg.run()
        dlg.destroy()
        return response == Gtk.ResponseType.YES

    def _update_link_row(self):
        has_file = bool(self._script_file_path)
        self.link_row.set_visible(has_file)
        if has_file:
            self.linked_path_lbl.set_text(self._script_file_path)

    def _on_open_script_file(self, _btn):
        path = self._open_dialog("Open Python Script",
                                 [("Python files", "*.py"), ("All files", "*")])
        if path:
            self._open_script_path(path)

    def _open_script_path(self, path):
        try:
            with open(path, encoding='utf-8', errors='replace') as fh:
                code = fh.read()
        except Exception as exc:
            self._alert(f"Could not read script:\n{exc}")
            return
        self._load_script_into_editor(code, file_path=path)

    def _rebuild_recent_menu(self):
        menu = Gtk.Menu()
        recents = [p for p in load_recent_files() if os.path.isfile(p)]
        if not recents:
            item = Gtk.MenuItem(label="(no recent files)")
            item.set_sensitive(False)
            menu.append(item)
        for p in recents:
            item = Gtk.MenuItem(label=p)
            item.connect("activate",
                         lambda _i, pp=p: self._open_script_path(pp))
            menu.append(item)
        menu.show_all()
        self.recent_btn.set_popup(menu)

    def _on_link_toggled(self, check):
        linked = check.get_active() and bool(self._script_file_path)
        self.code_view.set_editable(not linked)
        self.code_view.set_cursor_visible(not linked)
        if linked:
            self._on_reload_linked(None)

    def _on_reload_linked(self, _btn):
        if not self._script_file_path:
            return
        try:
            with open(self._script_file_path,
                      encoding='utf-8', errors='replace') as fh:
                code = fh.read()
        except Exception as exc:
            self._alert(f"Could not read file:\n{exc}")
            return
        self._set_tv(self.code_view, code)
        self._editor_baseline = code

    def _on_check_syntax(self, _btn):
        """Validate the inline code buffer for Python syntax errors."""
        import py_compile, tempfile
        code = self._get_tv(self.code_view)
        if not code.strip():
            self.syntax_status_lbl.set_markup("<i>Nothing to check.</i>")
            return
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
        try:
            tmp.write(code)
            tmp.close()
            py_compile.compile(tmp.name, doraise=True)
            self.syntax_status_lbl.set_markup(
                "<span foreground='green'>✓ Syntax OK</span>"
            )
        except py_compile.PyCompileError as exc:
            msg = str(exc).replace(tmp.name, "&lt;inline&gt;")
            from gi.repository import GLib as _GLib
            self.syntax_status_lbl.set_markup(
                f"<span foreground='red'>⚠ {_GLib.markup_escape_text(msg)}</span>"
            )
        finally:
            try:
                os.remove(tmp.name)
            except OSError:
                pass

    def _on_preview_figure(self, _btn):
        """Run current script headlessly, save PNG to temp, show in a popup.

        The subprocess runs on a worker thread so the dialog stays responsive
        (the run can take up to 30 s); the result is marshalled back to the
        GTK main thread with GLib.idle_add.
        """
        import tempfile
        self.preview_status_lbl.set_markup("<i>Generating preview…</i>")
        self.preview_btn.set_sensitive(False)

        # Resolve the code to preview: linked file, else editor content
        if self.link_check.get_active() and self._script_file_path:
            fp = self._script_file_path
            if not os.path.isfile(fp):
                self._preview_done(None, "Linked script file not found.")
                return
            try:
                with open(fp, encoding='utf-8', errors='replace') as fh:
                    code = fh.read()
            except Exception as exc:
                self._preview_done(None, str(exc))
                return
        else:
            code = self._get_tv(self.code_view)
            if not code.strip():
                self._preview_done(None, "The editor is empty.")
                return

        # Wrap code in a headless runner that saves a PNG. Inject the same
        # helper variables the real preamble provides so templates preview
        # correctly (values taken live from the dialog widgets).
        tmp_png = tempfile.mktemp(suffix=".png")
        preamble = (
            "import matplotlib\nmatplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "import numpy as np\n"
            f"_fig_width = {self.fig_width_spin.get_value()!r}\n"
            f"_fig_height = {self.fig_height_spin.get_value()!r}\n"
            "_dpi = 96\n"
            f"_show_grid = {self.grid_check.get_active()!r}\n"
            f"_show_legend = {self.legend_check.get_active()!r}\n"
            f"_legend_position = {self._get_combo_value(self.legend_pos_combo) or 'best'!r}\n"
            f"_colormap = {self._get_combo_value(self.colormap_combo) or 'viridis'!r}\n"
            "def get_cmap(name=None):\n"
            "    return matplotlib.colormaps[name or _colormap]\n"
            "def apply_style(ax=None):\n"
            "    pass\n"
            "try:\n"
            "    import seaborn as sns\n"
            "    seaborn_available = True\n"
            "except Exception:\n"
            "    seaborn_available = False\n"
        )
        if 'plt.subplots' not in code and 'plt.figure' not in code:
            preamble += "fig, ax = plt.subplots(figsize=(_fig_width, _fig_height))\n"
        runner = (
            preamble
            + f"{code}\n"
            + "fig = plt.gcf()\n"
            + f"fig.savefig({tmp_png!r}, dpi=72, bbox_inches='tight')\n"
            + "plt.close('all')\n"
        )

        python = self.python_path_entry.get_text().strip() or "python"
        tmp_script = tempfile.mktemp(suffix=".py")
        threading.Thread(
            target=self._preview_worker,
            args=(python, runner, tmp_script, tmp_png),
            daemon=True,
        ).start()

    def _preview_worker(self, python, runner, tmp_script, tmp_png):
        """Background thread: run the preview subprocess. No GTK calls here."""
        error = None
        try:
            with open(tmp_script, "w", encoding='utf-8') as fh:
                fh.write(runner)
            result = subprocess.run(
                [python, tmp_script],
                capture_output=True, text=True, timeout=30,
                creationflags=_WIN_FLAGS,
            )
            if result.returncode != 0 or not os.path.isfile(tmp_png):
                error = (result.stderr or result.stdout or "Unknown error").strip()[:400]
        except Exception as exc:
            error = str(exc)
        finally:
            try:
                os.remove(tmp_script)
            except OSError:
                pass
        GLib.idle_add(self._preview_done, tmp_png if error is None else None, error)

    def _preview_done(self, tmp_png, error):
        """Main thread: show the result and re-enable the button."""
        self.preview_btn.set_sensitive(True)
        if error is not None:
            self._show_preview_error(error)
            return False
        try:
            self._show_preview_image(tmp_png)
            self.preview_status_lbl.set_markup(
                "<span foreground='green'>✓ Preview ready</span>"
            )
        finally:
            try:
                os.remove(tmp_png)
            except OSError:
                pass
        return False

    def _show_preview_error(self, message):
        self.preview_status_lbl.set_markup(
            "<span foreground='red'>⚠ Preview failed</span>"
        )
        dlg = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
        )
        from gi.repository import GLib as _GLib
        dlg.set_markup(_GLib.markup_escape_text(message))
        dlg.run()
        dlg.destroy()

    def _show_preview_image(self, png_path):
        """Open a small dialog showing the preview PNG."""
        dlg = Gtk.Dialog(title="Figure Preview", transient_for=self, modal=True)
        dlg.set_default_size(520, 420)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                png_path, width=500, height=400, preserve_aspect_ratio=True
            )
            img = Gtk.Image.new_from_pixbuf(pixbuf)
        except Exception:
            img = Gtk.Label(label="(Could not load image)")
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(img)
        dlg.get_content_area().pack_start(sw, True, True, 8)
        dlg.add_button("Close", Gtk.ResponseType.OK)
        dlg.show_all()
        dlg.run()
        dlg.destroy()

    def _on_position_changed(self, combo):
        self.custom_pos_frame.set_visible(
            self._get_combo_value(combo) == "custom"
        )

    def _on_data_toggle(self, check):
        self.data_frame.set_sensitive(check.get_active())

    def _on_data_format_changed(self, combo):
        fmt = self._get_combo_value(combo)
        self.csv_options_frame.set_visible(fmt in ("csv", "txt"))

    def _on_auto_create_toggled(self, check):
        self.subplot_frame.set_sensitive(check.get_active())

    def _on_export_script_toggled(self, check):
        self.export_script_frame.set_visible(check.get_active())

    def _on_browse_export(self, _btn):
        path = self._save_dialog("Export Script As", [("Python files", "*.py"), ("All files", "*")])
        if path:
            if not path.endswith(".py"):
                path += ".py"
            self.export_script_entry.set_text(path)

    def _on_save_script_toggled(self, check):
        self.script_save_frame.set_visible(check.get_active())

    # ── Batch tab signals ─────────────────────────────────────────────────

    def _on_backend_changed(self, combo):
        """Show/hide style-related sections that don't apply to Plotly."""
        backend = self._get_combo_value(combo)
        is_mpl = (backend == "matplotlib")
        # Style tab sections rely on matplotlib rcParams — grey them out for plotly
        if hasattr(self, '_style_tab_box'):
            self._style_tab_box.set_sensitive(is_mpl)

    def _on_batch_mode_toggled(self, check):
        self.batch_controls_frame.set_sensitive(check.get_active())

    def _on_batch_add_current(self, _btn):
        """Add the current editor script (or linked file) to the batch queue."""
        if self.link_check.get_active() and self._script_file_path:
            self._batch_store.append(
                ["file", self._script_file_path,
                 os.path.basename(self._script_file_path)])
            return
        code = self._get_tv(self.code_view).strip()
        if not code:
            self._alert("The editor is empty.")
            return
        if self._loaded_template:
            label = "/".join(self._loaded_template)
        else:
            label = code.splitlines()[0][:60] or "<inline>"
        self._batch_store.append(["inline", code, label])

    def _on_batch_remove(self, _btn):
        sel = self._batch_tv.get_selection()
        model, it = sel.get_selected()
        if it:
            model.remove(it)

    def _on_batch_clear(self, _btn):
        self._batch_store.clear()

    def _on_detect_python(self, btn):
        """Probe common locations for Python interpreters and offer a pick list.

        Probing runs several ``python --version`` subprocesses (5 s timeout
        each), so it happens on a worker thread; the picker dialog is shown
        back on the GTK main thread.
        """
        btn.set_sensitive(False)
        old_label = btn.get_label()
        btn.set_label("Detecting…")

        def worker():
            try:
                candidates = probe_python_candidates()
            except Exception:
                candidates = []
            GLib.idle_add(self._detect_python_done, btn, old_label, candidates)

        threading.Thread(target=worker, daemon=True).start()

    def _detect_python_done(self, btn, old_label, candidates):
        """Main thread: restore the button and show the interpreter picker."""
        btn.set_label(old_label)
        btn.set_sensitive(True)

        if not candidates:
            dlg = Gtk.MessageDialog(
                parent=self, modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="No Python interpreters detected automatically."
            )
            dlg.format_secondary_text(
                "Enter the path manually, e.g.:\n"
                "  python3\n  /path/to/venv/bin/python"
            )
            dlg.run()
            dlg.destroy()
            return

        # Show picker dialog
        dlg = Gtk.Dialog(title="Select Python Interpreter", parent=self, modal=True)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK,     Gtk.ResponseType.OK)
        dlg.set_default_size(520, 300)

        store = Gtk.ListStore(str, str)
        for exe, ver in candidates:
            store.append([exe, ver])
        tv = Gtk.TreeView(model=store)
        tv.append_column(Gtk.TreeViewColumn("Path",    Gtk.CellRendererText(), text=0))
        tv.append_column(Gtk.TreeViewColumn("Version", Gtk.CellRendererText(), text=1))
        tv.get_selection().select_path(Gtk.TreePath.new_first())
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(tv)
        dlg.get_content_area().pack_start(sw, True, True, 8)
        dlg.show_all()

        if dlg.run() == Gtk.ResponseType.OK:
            model, it = tv.get_selection().get_selected()
            if it:
                self.python_path_entry.set_text(model[it][0])
        dlg.destroy()

    def _on_browse_data(self, _btn):
        # Start in the bundled sample_data folder when nothing is set yet.
        folder = None
        if not self.data_file_entry.get_text().strip() \
                and os.path.isdir(plt_ink_bank.SAMPLE_DATA_DIR):
            folder = plt_ink_bank.SAMPLE_DATA_DIR
        path = self._open_dialog("Select Data File",
                                 [("Data files", "*.csv *.txt *.xlsx *.json"),
                                  ("All files", "*")],
                                 folder=folder)
        if path:
            self.data_file_entry.set_text(path)

    def _on_browse_save(self, _btn):
        path = self._save_dialog("Save Script As", [("Python files", "*.py")])
        if path:
            self.script_save_entry.set_text(path)

    # ------------------------------------------------------------------ file dialogs

    def _open_dialog(self, title, filters=None, folder=None):
        dlg = Gtk.FileChooserDialog(
            title=title, parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OPEN,   Gtk.ResponseType.OK)
        if folder:
            dlg.set_current_folder(folder)
        self._add_filters(dlg, filters)
        result = dlg.get_filename() if dlg.run() == Gtk.ResponseType.OK else None
        dlg.destroy()
        return result

    def _save_dialog(self, title, filters=None):
        dlg = Gtk.FileChooserDialog(
            title=title, parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_SAVE,   Gtk.ResponseType.OK)
        dlg.set_do_overwrite_confirmation(True)
        self._add_filters(dlg, filters)
        result = dlg.get_filename() if dlg.run() == Gtk.ResponseType.OK else None
        dlg.destroy()
        return result

    @staticmethod
    def _add_filters(dlg, filters):
        if not filters:
            return
        for name, pattern in filters:
            f = Gtk.FileFilter()
            f.set_name(name)
            f.add_pattern(pattern)
            dlg.add_filter(f)

    # ------------------------------------------------------------------ load / save

    def _load_values(self):
        o = self.opts

        self.python_path_entry.set_text(o.python_path)

        # Unified editor: restore content + origin from the legacy three-source
        # options (inline / file / bank all map onto the one editor).
        src = getattr(o, 'script_source', 'inline')
        code = o.script_code
        self._script_file_path = o.script_file or ""
        if src == 'bank':
            # migrate old bank mode: load the template into the editor
            path = plt_ink_bank.script_path(o.bank_category, o.bank_script)
            if path:
                try:
                    with open(path, encoding='utf-8', errors='replace') as fh:
                        code = fh.read()
                    self._loaded_template = (o.bank_category, o.bank_script)
                    self.script_origin_lbl.set_markup(
                        f"<i>Template: {GLib.markup_escape_text(o.bank_script)}</i>")
                except Exception:
                    pass
        self._set_tv(self.code_view, code)
        self._editor_baseline = code
        if src == 'file' and self._script_file_path:
            self.script_origin_lbl.set_markup(
                f"<i>{GLib.markup_escape_text(os.path.basename(self._script_file_path))}</i>")
            # triggers read-only mode + reload of the file into the editor
            self.link_check.set_active(True)

        self._set_combo(self.backend_combo, getattr(o, 'plot_backend', 'matplotlib'))
        self._set_combo(self.output_format_combo, o.output_format)
        self.fig_width_spin.set_value(o.figure_width)
        self.fig_height_spin.set_value(o.figure_height)
        self.dpi_spin.set_value(o.dpi)
        self.transparent_check.set_active(o.transparent)
        self.tight_layout_check.set_active(o.tight_layout)
        self.constrained_layout_check.set_active(o.constrained_layout)
        self.auto_create_check.set_active(o.auto_create_figure)
        self.subplot_rows_spin.set_value(o.subplot_rows)
        self.subplot_cols_spin.set_value(o.subplot_cols)
        self.share_x_check.set_active(o.share_x)
        self.share_y_check.set_active(o.share_y)

        self._set_combo(self.plot_style_combo,   o.plot_style)
        self._set_combo(self.colormap_combo,     o.color_map)
        self._set_combo(self.color_cycle_combo,  o.color_cycle)
        self.bg_color_entry.set_text(o.background_color)
        self.grid_check.set_active(o.grid)
        self._set_combo(self.grid_style_combo,   o.grid_style)
        self.grid_alpha_spin.set_value(o.grid_alpha)
        self.legend_check.set_active(o.legend)
        self._set_combo(self.legend_pos_combo,   o.legend_position)
        self.despine_check.set_active(o.auto_despine)

        self._set_combo(self.position_combo, o.position_mode)
        self.custom_x_spin.set_value(o.custom_x)
        self.custom_y_spin.set_value(o.custom_y)
        self.scale_factor_spin.set_value(o.scale_factor)
        self.embed_check.set_active(o.embed_image)

        self._set_combo(self.font_family_combo,      o.font_family)
        self.font_size_spin.set_value(o.font_size)
        self.title_size_spin.set_value(o.title_size)
        self.label_size_spin.set_value(o.label_size)
        self.line_width_spin.set_value(o.line_width)
        self.marker_size_spin.set_value(o.marker_size)
        self.latex_check.set_active(o.use_latex)
        self._set_combo(self.error_handling_combo, o.error_handling)
        self.show_warnings_check.set_active(o.show_warnings)
        self.timeout_spin.set_value(o.execution_timeout)
        self.debug_mode_check.set_active(o.debug_mode)
        self.save_script_check.set_active(o.save_script)
        self.script_save_entry.set_text(o.script_save_path)
        self.keep_temp_check.set_active(o.keep_temp_files)
        self.export_script_only_check.set_active(o.export_script_only)
        self.export_script_entry.set_text(o.export_script_path)

        self.use_data_check.set_active(o.use_data_file)
        self.data_file_entry.set_text(o.data_file_path)
        self._set_combo(self.data_format_combo, o.data_format)
        self.delimiter_entry.set_text(o.csv_delimiter)
        self.skip_header_check.set_active(o.skip_header)
        self.header_row_spin.set_value(o.header_row)
        self.x_columns_entry.set_text(o.x_columns)
        self.y_columns_entry.set_text(o.y_columns)
        self.col_names_entry.set_text(o.column_names)
        self.load_all_check.set_active(o.load_all_columns)
        self.date_columns_entry.set_text(o.date_columns)
        self.date_format_entry.set_text(o.date_format)

        self.use_preamble_check.set_active(o.use_preamble)
        self.auto_imports_check.set_active(o.auto_imports)
        self._set_tv(self.additional_imports_view, o.additional_imports)
        self._set_tv(self.custom_preamble_view,    o.custom_preamble)

        # Batch mode
        self.batch_mode_check.set_active(getattr(o, 'batch_mode', False))
        self.batch_gap_spin.set_value(getattr(o, 'batch_gap', 20))
        self._set_combo(self.batch_direction_combo, getattr(o, 'batch_direction', 'horizontal'))
        raw = getattr(o, 'batch_scripts', None)
        if raw:
            import json as _json
            try:
                for row in _json.loads(raw):
                    self._batch_store.append(row[:3])
            except Exception:
                pass
        self._on_batch_mode_toggled(self.batch_mode_check)

    def get_options(self):
        """Collect all widget values and return them as a SimpleNamespace."""
        o = SimpleNamespace()

        o.python_path   = self.python_path_entry.get_text().strip() or "python"
        o.plot_backend  = self._get_combo_value(self.backend_combo)
        # Unified editor: "file" only when linked (re-read at Apply), else the
        # editor content is the script. Bank identity kept for figure labels.
        linked = self.link_check.get_active() and bool(self._script_file_path)
        o.script_source = "file" if linked else "inline"
        o.script_code   = self._get_tv(self.code_view)
        o.script_file   = self._script_file_path
        tpl = self._loaded_template or ("line_plots", "basic_line")
        o.bank_category, o.bank_script = tpl

        o.output_format       = self._get_combo_value(self.output_format_combo)
        o.figure_width        = self.fig_width_spin.get_value()
        o.figure_height       = self.fig_height_spin.get_value()
        o.dpi                 = int(self.dpi_spin.get_value())
        o.transparent         = self.transparent_check.get_active()
        o.tight_layout        = self.tight_layout_check.get_active()
        o.constrained_layout  = self.constrained_layout_check.get_active()
        o.auto_create_figure  = self.auto_create_check.get_active()
        o.subplot_rows        = int(self.subplot_rows_spin.get_value())
        o.subplot_cols        = int(self.subplot_cols_spin.get_value())
        o.share_x             = self.share_x_check.get_active()
        o.share_y             = self.share_y_check.get_active()

        o.plot_style      = self._get_combo_value(self.plot_style_combo)
        o.color_map       = self._get_combo_value(self.colormap_combo)
        o.color_cycle     = self._get_combo_value(self.color_cycle_combo)
        o.background_color = self.bg_color_entry.get_text().strip() or "white"
        o.grid            = self.grid_check.get_active()
        o.grid_style      = self._get_combo_value(self.grid_style_combo)
        o.grid_alpha      = self.grid_alpha_spin.get_value()
        o.legend          = self.legend_check.get_active()
        o.legend_position = self._get_combo_value(self.legend_pos_combo)
        o.auto_despine    = self.despine_check.get_active()

        o.position_mode = self._get_combo_value(self.position_combo)
        o.custom_x      = self.custom_x_spin.get_value()
        o.custom_y      = self.custom_y_spin.get_value()
        o.scale_factor  = self.scale_factor_spin.get_value()
        o.embed_image   = self.embed_check.get_active()

        o.font_family      = self._get_combo_value(self.font_family_combo)
        o.font_size        = int(self.font_size_spin.get_value())
        o.title_size       = int(self.title_size_spin.get_value())
        o.label_size       = int(self.label_size_spin.get_value())
        o.line_width       = self.line_width_spin.get_value()
        o.marker_size      = self.marker_size_spin.get_value()
        o.use_latex        = self.latex_check.get_active()
        o.error_handling   = self._get_combo_value(self.error_handling_combo)
        o.show_warnings    = self.show_warnings_check.get_active()
        o.execution_timeout = int(self.timeout_spin.get_value())
        o.debug_mode       = self.debug_mode_check.get_active()
        o.save_script      = self.save_script_check.get_active()
        o.script_save_path = self.script_save_entry.get_text().strip()
        o.keep_temp_files  = self.keep_temp_check.get_active()
        o.export_script_only = self.export_script_only_check.get_active()
        o.export_script_path = self.export_script_entry.get_text().strip()

        o.use_data_file    = self.use_data_check.get_active()
        o.data_file_path   = self.data_file_entry.get_text().strip()
        o.data_format      = self._get_combo_value(self.data_format_combo)
        o.csv_delimiter    = self.delimiter_entry.get_text() or ","
        o.skip_header      = self.skip_header_check.get_active()
        o.header_row       = int(self.header_row_spin.get_value())
        o.x_columns        = self.x_columns_entry.get_text().strip() or "0"
        o.y_columns        = self.y_columns_entry.get_text().strip() or "1"
        o.column_names     = self.col_names_entry.get_text().strip()
        o.load_all_columns = self.load_all_check.get_active()
        o.date_columns     = self.date_columns_entry.get_text().strip()
        o.date_format      = self.date_format_entry.get_text().strip() or "%Y-%m-%d"

        o.use_preamble        = self.use_preamble_check.get_active()
        o.auto_imports        = self.auto_imports_check.get_active()
        o.additional_imports  = self._get_tv(self.additional_imports_view)
        o.custom_preamble     = self._get_tv(self.custom_preamble_view)

        # Batch mode
        o.batch_mode      = self.batch_mode_check.get_active()
        batch_rows = []
        for row in self._batch_store:
            batch_rows.append([row[0], row[1], row[2]])
        import json as _json
        o.batch_scripts   = _json.dumps(batch_rows)
        o.batch_gap       = int(self.batch_gap_spin.get_value())
        o.batch_direction = self._get_combo_value(self.batch_direction_combo)

        return o


# ---------------------------------------------------------------------------
# Standalone entry point — used by plt_ink.py via subprocess to avoid running
# a nested GTK event loop inside Inkscape's own GTK context.
#
# Outputs all options as a single JSON line on stdout; exits 0 on OK, 1 on cancel.
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import io

    # Force UTF-8 on stdout so the JSON payload is never re-encoded by the
    # Windows console's default cp1252 codec, which would cause a
    # UnicodeDecodeError in the parent process.
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    opts, had_settings = load_saved_options()

    # Use Gtk.Window + Gtk.main() / Gtk.main_quit() (TexText pattern).
    # Gtk.Dialog.run() creates a hidden transient parent window on GTK when no
    # parent is given, which appears as a visible empty rectangle on Windows.
    window = MatplotlibDialog(opts)
    window.show()

    # On true first run, auto-detect a Python interpreter (preferring one with
    # matplotlib) so the extension works without manual setup. Detection runs
    # many subprocesses and can take tens of seconds, so it happens on a
    # background thread AFTER the window is visible; the result is applied
    # only if the user hasn't already typed a path themselves.
    if not had_settings and opts.python_path in ("", "python"):
        def _first_run_detect():
            try:
                found = autodetect_python()
            except Exception:
                found = ""

            def _apply():
                if found and found != "python":
                    current = window.python_path_entry.get_text().strip()
                    if current in ("", "python"):
                        window.python_path_entry.set_text(found)
                return False

            GLib.idle_add(_apply)

        threading.Thread(target=_first_run_detect, daemon=True).start()

    Gtk.main()

    if window._accepted:
        opts = window.get_options()
        save_options(opts)  # persist for the next session
        # Print options as JSON to stdout for the parent process to read.
        print(json.dumps(vars(opts)), flush=True)
        window.destroy()
        sys.exit(0)
    else:
        window.destroy()
        sys.exit(1)
