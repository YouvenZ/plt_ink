"""
plt_ink — Result / Status Dialog
Launched as a subprocess by plt_ink.py after the extension finishes.

Receives a JSON payload on stdin with the structure:
  {
    "status":  "success" | "error" | "warning",
    "title":   "<dialog title>",
    "message": "<main message>",
    "detail":  "<optional detail / traceback>",
    "stats":   {"Format": "svg", "Size": "8×6 in", ...}   (success only)
  }
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import sys
import json
import io

# Force UTF-8 stdin so JSON with unicode survives Windows cp1252 default
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

# ── colour / icon constants ────────────────────────────────────────────────

_STATUS_COLOURS = {
    "success": "#1a9850",   # green
    "error":   "#d73027",   # red
    "warning": "#f59a00",   # amber
}

_STATUS_ICONS = {
    "success": "✓",
    "error":   "✗",
    "warning": "⚠",
}


# ── dialog class ──────────────────────────────────────────────────────────

class ResultDialog(Gtk.Window):
    """Compact status window shown after the extension finishes."""

    def __init__(self, payload: dict):
        super().__init__()
        status  = payload.get("status",  "success")
        title   = payload.get("title",   "plt_ink")
        message = payload.get("message", "")
        detail  = payload.get("detail",  "")
        stats   = payload.get("stats",   {})

        self.set_title(title)
        self.set_default_size(480, -1)
        self.set_resizable(True)
        self.set_border_width(0)
        self.connect("delete-event", self._quit)
        self.connect("key-press-event", self._on_key)

        colour = _STATUS_COLOURS.get(status, "#444")
        icon   = _STATUS_ICONS.get(status, "•")

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(root)

        # ── coloured header bar ──────────────────────────────────────────
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(14)
        header.set_margin_bottom(14)

        icon_lbl = Gtk.Label()
        icon_lbl.set_markup(
            f'<span foreground="{colour}" font="18" weight="bold">{icon}</span>'
        )
        header.pack_start(icon_lbl, False, False, 0)

        msg_lbl = Gtk.Label()
        msg_lbl.set_markup(
            f'<span foreground="{colour}" font="13" weight="bold">'
            f'{GLib.markup_escape_text(message)}</span>'
        )
        msg_lbl.set_xalign(0.0)
        msg_lbl.set_line_wrap(True)
        header.pack_start(msg_lbl, True, True, 0)

        root.pack_start(header, False, False, 0)

        # ── separator ───────────────────────────────────────────────────
        root.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
                        False, False, 0)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        body.set_margin_start(16)
        body.set_margin_end(16)
        body.set_margin_top(12)
        body.set_margin_bottom(12)
        root.pack_start(body, True, True, 0)

        # ── stats grid (success) ────────────────────────────────────────
        if stats:
            grid = Gtk.Grid(column_spacing=16, row_spacing=4)
            for row_i, (k, v) in enumerate(stats.items()):
                key_lbl = Gtk.Label(label=k + ":")
                key_lbl.set_xalign(1.0)
                key_lbl.get_style_context().add_class("dim-label")
                val_lbl = Gtk.Label(label=str(v))
                val_lbl.set_xalign(0.0)
                val_lbl.set_selectable(True)
                grid.attach(key_lbl, 0, row_i, 1, 1)
                grid.attach(val_lbl, 1, row_i, 1, 1)
            body.pack_start(grid, False, False, 0)

        # ── detail / traceback (error / warning) ────────────────────────
        if detail:
            detail_lbl = Gtk.Label(label="Details:")
            detail_lbl.set_xalign(0.0)
            detail_lbl.get_style_context().add_class("dim-label")
            body.pack_start(detail_lbl, False, False, 0)

            tv = Gtk.TextView()
            tv.set_editable(False)
            tv.set_monospace(True)
            tv.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            tv.get_buffer().set_text(detail)
            tv.set_margin_start(4)
            tv.set_margin_end(4)
            sw = Gtk.ScrolledWindow()
            sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            sw.set_min_content_height(120)
            sw.set_max_content_height(300)
            sw.add(tv)
            body.pack_start(sw, True, True, 0)

            # Copy button for errors
            if status == "error":
                copy_btn = Gtk.Button(label="Copy Error to Clipboard")
                copy_btn.connect("clicked", lambda *_: self._copy_text(detail))
                body.pack_start(copy_btn, False, False, 0)

        # ── button row ──────────────────────────────────────────────────
        root.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
                        False, False, 0)
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_row.set_halign(Gtk.Align.END)
        btn_row.set_margin_start(16)
        btn_row.set_margin_end(16)
        btn_row.set_margin_top(8)
        btn_row.set_margin_bottom(10)

        ok_btn = Gtk.Button(label="OK")
        ok_btn.get_style_context().add_class("suggested-action")
        ok_btn.connect("clicked", self._quit)
        btn_row.pack_start(ok_btn, False, False, 0)
        root.pack_start(btn_row, False, False, 0)

        self.show_all()

    def _quit(self, *_):
        Gtk.main_quit()
        return False

    def _on_key(self, _widget, event):
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter,
                            Gdk.KEY_Escape, Gdk.KEY_space):
            self._quit()
            return True
        return False

    def _copy_text(self, text):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()


# ── entry point ───────────────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
    except Exception:
        payload = {
            "status":  "error",
            "title":   "plt_ink",
            "message": "Could not read result payload.",
            "detail":  raw if 'raw' in dir() else "",
        }

    window = ResultDialog(payload)
    Gtk.main()
    sys.exit(0)
