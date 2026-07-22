#!/usr/bin/env python3
"""
Inkscape extension to generate and insert matplotlib figures.
"""
# MIT License
# Copyright (c) 2026 Rachid, Youven ZEGHLACHE

__version__ = "1.1.0"

import inkex
from inkex import Image, Group
import subprocess
import os
import tempfile
import base64
import shutil
from datetime import datetime
from lxml import etree
import sys
import re

# Suppress Windows console window for all subprocesses (python.exe is a console
# application and spawns a visible CMD-style window even with capture_output=True).
_WIN_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0


# Categories live in plt_ink_bank.py — single source of truth shared with the
# dialog. Fallback keeps the extension alive if the module is missing.
try:
    from plt_ink_bank import CATEGORIES as SCRIPT_CATEGORIES
except ImportError:
    SCRIPT_CATEGORIES = {'line_plots': 'Line Plots'}

# Namespace and attribute used to tag plt_ink-inserted elements for later update detection.
# Must use Clark notation {uri}local so lxml accepts it as a valid attribute name.
PLT_INK_NS = 'https://github.com/YouvenZ/plt_ink'
PLT_INK_ATTR = f'{{{PLT_INK_NS}}}source'

# Inkscape namespace — used for inkscape:label (must be Clark notation for lxml).
INKSCAPE_NS = 'http://www.inkscape.org/namespaces/inkscape'
INKSCAPE_LABEL = f'{{{INKSCAPE_NS}}}label'



class MatplotlibGenerator(inkex.EffectExtension):
    """Extension to generate matplotlib figures."""
    
    def __init__(self):
        super().__init__()
        self.debug_mode = False  # controlled by dialog; default off
        self.log_file = os.path.join(tempfile.gettempdir(), 'matplotlib_inkscape_debug.log')
        # Script bank directory
        self.script_bank_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plt_ink_scripts')
        self._rotate_log()
        
    def log(self, message, level="INFO"):
        """Log messages to file and optionally to stderr."""
        if not self.debug_mode:
            return
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message)
        except:
            pass
        
        if level in ["ERROR", "WARNING"]:
            sys.stderr.write(log_message)
    
    def debug_var(self, var_name, var_value):
        """Log a variable's value for debugging."""
        self.log(f"VAR: {var_name} = {repr(var_value)}", "DEBUG")

    def _rotate_log(self):
        """Keep the log file under ~1 MB by discarding old lines."""
        max_bytes = 1_000_000
        try:
            if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > max_bytes:
                with open(self.log_file, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                keep = lines[-(max_bytes // 200):]  # keep ~5000 recent lines
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"[log rotated]\n")
                    f.writelines(keep)
        except Exception:
            pass

    def add_arguments(self, pars):
        # No params — the GTK dialog in plt_ink_dialog.py handles all settings.
        pass

    # ── Result dialog ─────────────────────────────────────────────────────

    def _show_result(self, status: str, message: str,
                     detail: str = "", stats: dict = None):
        """Launch plt_ink_result.py as a subprocess to show a status dialog.

        Args:
            status:  "success" | "error" | "warning"
            message: one-line summary shown in the header
            detail:  optional traceback / extra text shown in a scrolled view
            stats:   optional dict of key/value pairs (format, size, etc.)
        """
        import json as _json
        result_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'plt_ink_result.py'
        )
        if not os.path.isfile(result_script):
            # Fallback — no result script available
            if status == "success":
                inkex.utils.debug(f"plt_ink: {message}")
            else:
                inkex.errormsg(f"plt_ink {status.upper()}:\n{message}\n{detail}")
            return

        title_map = {
            "success": "plt_ink — Success",
            "error":   "plt_ink — Error",
            "warning": "plt_ink — Warning",
        }
        payload = {
            "status":  status,
            "title":   title_map.get(status, "plt_ink"),
            "message": message,
            "detail":  detail,
            "stats":   stats or {},
        }
        try:
            subprocess.run(
                [sys.executable, result_script],
                input=_json.dumps(payload),
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=_WIN_FLAGS,
            )
        except Exception as exc:
            self.log(f"Result dialog failed to launch: {exc}", "WARNING")

    def effect(self):
        """Main effect function — opens GTK dialog (subprocess) then runs generation."""
        import json
        from types import SimpleNamespace

        # Launch the GTK dialog as a SEPARATE subprocess using the same Python
        # interpreter that Inkscape uses (sys.executable has GTK available).
        # This avoids running a nested GTK main loop inside Inkscape's own GTK
        # context, which causes crashes and freezes.
        dialog_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plt_ink_dialog.py')

        try:
            result = subprocess.run(
                [sys.executable, dialog_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=_WIN_FLAGS,
            )
        except Exception as e:
            inkex.errormsg(
                f"Cannot open dialog: {e}\n\n"
                "Ensure GTK3 / PyGObject is available in Inkscape's Python."
            )
            return

        if result.returncode != 0:
            # User cancelled (exit 1) or dialog errored — stderr may have details.
            # Filter out harmless GTK/GLib debug noise from stderr before showing it.
            stderr_lines = [
                l for l in result.stderr.splitlines()
                if l.strip() and not any(
                    tok in l for tok in ('GLib', 'Gtk', 'GDK', 'Pango', 'fontconfig', 'WARNING **')
                )
            ]
            if stderr_lines:
                stderr_text = '\n'.join(stderr_lines)
                self._show_result("error", "Dialog error", detail=stderr_text)
                inkex.errormsg(f"Dialog error:\n{stderr_text}")
            return

        # The dialog may print GTK debug lines before the JSON; take the last
        # non-empty line which is always the JSON payload.
        json_lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        opts_json = json_lines[-1] if json_lines else ''
        if not opts_json:
            self._show_result("error", "Dialog produced no output.",
                              detail="The settings dialog closed without returning any data. Please try again.")
            inkex.errormsg("Dialog produced no output. Please try again.")
            return

        try:
            opts_dict = json.loads(opts_json)
        except json.JSONDecodeError as e:
            self._show_result("error", "Failed to parse dialog output.",
                              detail=f"JSON error: {e}\n\nRaw output:\n{opts_json[:500]}")
            inkex.errormsg(f"Failed to parse dialog output: {e}\n\nRaw output:\n{opts_json[:300]}")
            return

        # Merge dialog options into the existing self.options so inkex's built-in
        # attributes (e.g. 'output') are preserved.  First apply defaults for any
        # keys not already present, then apply actual dialog values on top.
        try:
            from plt_ink_dialog import get_default_options
            for k, v in vars(get_default_options()).items():
                if not hasattr(self.options, k):
                    setattr(self.options, k, v)
        except Exception:
            pass
        for k, v in opts_dict.items():
            setattr(self.options, k, v)

        # Sync debug mode from dialog choice
        self.debug_mode = self.options.debug_mode

        self.log("="*80)
        self.log("Starting Matplotlib Figure Generator")
        self.log(f"Log file: {self.log_file}")

        try:
            # Log all options
            self.log("Options:")
            for key, value in vars(self.options).items():
                self.debug_var(f"options.{key}", value)
            
            # Check if Python is available
            self.log("Checking Python availability...")
            if not self.check_python():
                error_msg = f"Python not found at '{self.options.python_path}'."
                detail_msg = (
                    f"Could not find a Python interpreter at:\n  {self.options.python_path}\n\n"
                    "Please install Python or set the correct path in the Script tab → Python path field."
                )
                self.log(error_msg, "ERROR")
                self._show_result("error", error_msg, detail=detail_msg)
                return
            self.log("Python check passed")
            
            # Check if the required plotting library is installed
            self.log("Checking plotting library installation...")
            _backend = getattr(self.options, 'plot_backend', 'matplotlib')
            if _backend == 'plotly':
                if not self.check_plotly():
                    self._show_result(
                        "error",
                        "Plotly or Kaleido not installed.",
                        detail=(
                            "The Plotly backend requires two packages:\n"
                            "  pip install plotly kaleido\n\n"
                            "Run this command in the same Python environment "
                            f"configured in the dialog:\n  {self.options.python_path}"
                        ),
                    )
                    return
            else:
                if not self.check_matplotlib():
                    self._show_result(
                        "error",
                        "Matplotlib not installed.",
                        detail=(
                            "Please install Matplotlib in the configured Python environment:\n"
                            f"  {self.options.python_path} -m pip install matplotlib"
                        ),
                    )
                    return
            self.log("Plotting library check passed")
            
            # Generate the script
            self.log("Generating script...")
            script_content = self.generate_script()
            
            if not script_content:
                self.log("Script generation failed", "ERROR")
                self._show_result("error", "Failed to generate script.",
                                  detail="No script content was produced. Check that code is provided in the Script tab.")
                return
            
            self.log(f"Script generated ({len(script_content)} characters)")
            self.debug_var("script_content", script_content[:500] + "..." if len(script_content) > 500 else script_content)
            
            # Save script if requested
            if self.options.save_script:
                save_path = (self.options.script_save_path or "").strip()
                if not save_path:
                    # Fall back to extension directory with a timestamped name
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ext_dir = os.path.dirname(os.path.abspath(__file__))
                    save_path = os.path.join(ext_dir, f"plt_ink_script_{ts}.py")
                self.log(f"Saving script to: {save_path}")
                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(script_content)
                    self.log("Script saved successfully")
                except Exception as e:
                    self.log(f"Failed to save script: {str(e)}", "ERROR")
                    self._show_result("warning", "Could not save script file.",
                                      detail=str(e))
                    return
            
            # Export-only mode: save the generated script and exit without
            # executing it or inserting any figure into the document.
            if getattr(self.options, 'export_script_only', False):
                export_path = (getattr(self.options, 'export_script_path', '') or '').strip()
                if not export_path:
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ext_dir = os.path.dirname(os.path.abspath(__file__))
                    export_path = os.path.join(ext_dir, f"plt_ink_export_{ts}.py")
                try:
                    with open(export_path, 'w', encoding='utf-8') as f:
                        f.write(script_content)
                    self.log(f"Script exported to: {export_path}")
                    self._show_result(
                        "success",
                        "Script exported successfully.",
                        stats={"Saved to": export_path},
                    )
                except Exception as e:
                    self.log(f"Failed to export script: {str(e)}", "ERROR")
                    self._show_result("error", "Failed to export script.", detail=str(e))
                return

            # Batch mode: run each queued script and place figures in a row/column.
            if getattr(self.options, 'batch_mode', False):
                self._run_batch()
                return

            # Execute the script and get output file
            self.log("Executing script...")
            output_file = self.execute_script(script_content)
            
            if output_file and os.path.exists(output_file):
                self.log(f"Output file generated: {output_file}")
                file_size = os.path.getsize(output_file)
                self.debug_var("output_file_size", file_size)
                
                # Insert the figure into the document
                self.log("Inserting figure into document...")
                self.insert_figure(output_file)
                self.log("Figure inserted successfully")

                # Show success result dialog
                _fmt = getattr(self.options, 'output_format', 'svg').upper()
                _w   = getattr(self.options, 'figure_width',  8.0)
                _h   = getattr(self.options, 'figure_height', 6.0)
                _dpi = getattr(self.options, 'dpi', 96)
                _src = getattr(self.options, 'script_source', 'inline')
                self._show_result(
                    "success",
                    "Figure inserted successfully.",
                    stats={
                        "Format":  _fmt,
                        "Size":    f"{_w} × {_h} in  ({_dpi} DPI)",
                        "Source":  _src,
                        "Backend": getattr(self.options, 'plot_backend', 'matplotlib'),
                        "File size": f"{file_size / 1024:.1f} KB",
                    },
                )

                # Clean up temporary file
                if not self.options.keep_temp_files:
                    try:
                        os.remove(output_file)
                        self.log("Temporary file removed")
                    except Exception as e:
                        self.log(f"Failed to remove temp file: {str(e)}", "WARNING")
            else:
                self.log("Failed to generate figure - no output file", "ERROR")
                self._show_result("error", "Figure generation failed.",
                                  detail="The script ran but produced no output file. "
                                         "Check your code for errors — enable Debug mode for more detail.")
        
        except Exception as e:
            import traceback as _tb
            tb = _tb.format_exc()
            self.log(f"Exception occurred: {str(e)}", "ERROR")
            self.log(f"Traceback:\n{tb}", "ERROR")
            self._show_result("error", f"Unexpected error: {type(e).__name__}",
                              detail=tb)
        
        self.log("Extension execution completed")
        self.log("="*80 + "\n")
    
    def check_python(self):
        """Check if Python is available."""
        try:
            self.log(f"Checking Python at: {self.options.python_path}")
            result = subprocess.run(
                [self.options.python_path, '--version'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=5,
                creationflags=_WIN_FLAGS,
            )
            self.debug_var("python_check_returncode", result.returncode)
            self.debug_var("python_version", result.stdout.strip())
            return result.returncode == 0
        except Exception as e:
            self.log(f"Python check failed: {str(e)}", "ERROR")
            return False
    
    def check_matplotlib(self):
        """Check if matplotlib is installed."""
        try:
            result = subprocess.run(
                [self.options.python_path, '-c', 'import matplotlib; print(matplotlib.__version__)'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=5,
                creationflags=_WIN_FLAGS,
            )
            self.debug_var("matplotlib_check_returncode", result.returncode)
            if result.returncode == 0:
                self.debug_var("matplotlib_version", result.stdout.strip())
            else:
                self.debug_var("matplotlib_error", result.stderr)
            return result.returncode == 0
        except Exception as e:
            self.log(f"Matplotlib check failed: {str(e)}", "ERROR")
            return False

    def check_plotly(self):
        """Check if plotly and kaleido are installed (required for Plotly backend)."""
        try:
            result = subprocess.run(
                [self.options.python_path, '-c',
                 'import plotly; import kaleido; print(plotly.__version__)'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=5,
                creationflags=_WIN_FLAGS,
            )
            self.debug_var("plotly_check_returncode", result.returncode)
            if result.returncode == 0:
                self.debug_var("plotly_version", result.stdout.strip())
            else:
                self.debug_var("plotly_error", result.stderr)
            return result.returncode == 0
        except Exception as e:
            self.log(f"Plotly check failed: {str(e)}", "ERROR")
            return False
    
    def get_bank_script_path(self):
        """Get the path to the selected script from the bank.

        Validates category against SCRIPT_CATEGORIES before building path.
        """
        category = self.options.bank_category
        if category not in SCRIPT_CATEGORIES:
            self.log(f"Unknown bank category: {category!r}", "WARNING")
        script_name = f"{self.options.bank_script}.py"
        return os.path.join(self.script_bank_dir, category, script_name)
    
    def parse_column_indices(self, column_str):
        """Parse comma-separated column indices or ranges.
        
        Supports formats like:
        - "0,1,2" -> [0, 1, 2]
        - "0-3" -> [0, 1, 2, 3]
        - "0,2-4,6" -> [0, 2, 3, 4, 6]
        """
        if not column_str or column_str.strip() == "":
            return []
        
        indices = []
        parts = column_str.replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part and not part.startswith('-'):
                # Handle range like "2-5"
                try:
                    start, end = part.split('-')
                    indices.extend(range(int(start), int(end) + 1))
                except ValueError:
                    self.log(f"Invalid range format: {part}", "WARNING")
            else:
                # Handle single index
                try:
                    indices.append(int(part))
                except ValueError:
                    self.log(f"Invalid column index: {part}", "WARNING")
        
        return indices
    
    def generate_script(self):
        """Generate the matplotlib script based on settings."""
        self.log(f"Script source: {self.options.script_source}")
        
        if self.options.script_source == "file":
            # Load from external file
            self.log(f"Loading script from file: {self.options.script_file}")
            if not os.path.exists(self.options.script_file):
                self.log(f"Script file not found: {self.options.script_file}", "ERROR")
                inkex.errormsg(f"Script file not found: {self.options.script_file}")
                return None
            
            try:
                with open(self.options.script_file, 'r', encoding='utf-8') as f:
                    user_code = f.read()
                self.log(f"Loaded {len(user_code)} characters from file")
            except Exception as e:
                self.log(f"Failed to read script file: {str(e)}", "ERROR")
                inkex.errormsg(f"Failed to read script file: {str(e)}")
                return None
        
        elif self.options.script_source == "bank":
            # Load from script bank
            script_path = self.get_bank_script_path()
            self.log(f"Loading script from bank: {script_path}")
            
            if not os.path.exists(script_path):
                self.log(f"Bank script not found: {script_path}", "ERROR")
                inkex.errormsg(f"Bank script not found: {script_path}\n\nPlease ensure the script bank is installed correctly.")
                return None
            
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    user_code = f.read()
                self.log(f"Loaded {len(user_code)} characters from bank script")
            except Exception as e:
                self.log(f"Failed to read bank script: {str(e)}", "ERROR")
                inkex.errormsg(f"Failed to read bank script: {str(e)}")
                return None
        
        else:
            # Use inline code from GTK TextView — already a real Python string,
            # no escape-sequence decoding needed.
            self.log("Using inline code")
            user_code = self.options.script_code
            
            self.log(f"Inline code length: {len(user_code)}")
            self.debug_var("inline_code_preview", user_code[:200])
        
        if not user_code or user_code.strip() == "":
            self.log("No code provided", "ERROR")
            inkex.errormsg("No code provided.")
            return None

        _backend = getattr(self.options, 'plot_backend', 'matplotlib')

        # Record preamble line count so errors can be mapped back to user code
        self._preamble_lines = 0

        # Build complete script
        script_parts = []

        # Only add preamble if requested
        if self.options.use_preamble:
            if _backend == 'plotly':
                script_parts.extend(self.generate_plotly_preamble())
            else:
                script_parts.extend(self.generate_preamble(user_code))
        else:
            # Minimal setup without preamble
            if self.options.auto_imports:
                if _backend == 'plotly':
                    script_parts.append("import plotly.graph_objects as go")
                    script_parts.append("import plotly.express as px")
                    script_parts.append("import numpy as np")
                else:
                    script_parts.append("import matplotlib")
                    script_parts.append("matplotlib.use('Agg')")
                    script_parts.append("import matplotlib.pyplot as plt")
                    script_parts.append("import numpy as np")
            script_parts.append("")

        # Load data if requested (before user code)
        if self.options.use_data_file and self.options.data_file_path and os.path.exists(self.options.data_file_path):
            self.log(f"Loading data from: {self.options.data_file_path}")
            script_parts.append("# Load data")
            script_parts.append(self.generate_data_loading_code())
            script_parts.append("")

        # Track how many lines precede user code for error reporting
        self._preamble_lines = sum(p.count('\n') + 1 for p in script_parts)

        # User code — wrap in try/except when error_handling == "warn"
        if getattr(self.options, 'error_handling', 'stop') == 'warn':
            script_parts.append("# User code (wrapped for graceful error handling)")
            script_parts.append("try:")
            for line in user_code.splitlines():
                script_parts.append("    " + line)
            script_parts.append("except Exception as _plt_ink_err:")
            script_parts.append("    import traceback as _tb")
            script_parts.append("    print(f'USER_ERROR:{_tb.format_exc()}')")
        else:
            script_parts.append("# User code")
            script_parts.append(user_code)
        script_parts.append("")

        # Post-processing
        if _backend == 'plotly':
            script_parts.extend(self.generate_plotly_postamble())
        else:
            script_parts.extend(self.generate_postamble())

        return '\n'.join(script_parts)
    
    def generate_plotly_preamble(self):
        """Generate preamble lines for the Plotly backend."""
        p = []
        p.append("import plotly.graph_objects as go")
        p.append("import plotly.express as px")
        p.append("import numpy as np")
        p.append("import os")

        # Additional imports
        if self.options.additional_imports:
            p.append("")
            p.append("# Additional imports")
            for line in self.options.additional_imports.split('\n'):
                if line.strip():
                    p.append(line.strip())

        # Optional data imports
        if self.options.use_data_file:
            p.append("import pandas as pd")
            if self.options.data_format == "json":
                p.append("import json")

        # Custom preamble
        if self.options.custom_preamble:
            p.append("")
            p.append("# Custom preamble")
            for line in self.options.custom_preamble.split('\n'):
                p.append(line)

        p.append("")
        p.append("# Extension configuration (available to user scripts)")
        p.append(f"_fig_width = {self.options.figure_width}")
        p.append(f"_fig_height = {self.options.figure_height}")
        p.append(f"_dpi = {self.options.dpi}")
        p.append(f"_colormap = '{self.options.color_map}'")
        p.append(f"_show_legend = {self.options.legend}")
        p.append(f"_subplot_rows = {self.options.subplot_rows}")
        p.append(f"_subplot_cols = {self.options.subplot_cols}")
        p.append("")
        return p

    def generate_plotly_postamble(self):
        """Generate postamble for Plotly backend: find fig, export via kaleido."""
        output_path = self.get_temp_output_path()
        fmt = self.options.output_format
        # kaleido supports svg, png, pdf, webp, jpeg
        if fmt not in ('svg', 'png', 'pdf', 'jpeg', 'webp'):
            fmt = 'svg'
        width_px  = int(self.options.figure_width  * 96)
        height_px = int(self.options.figure_height * 96)

        post = []
        post.append("")
        post.append("# Save Plotly figure")
        post.append("# The user script must assign the figure to 'fig' or '_fig_plotly'.")
        post.append("_plt_ink_fig = None")
        post.append("for _name in ('fig', '_fig_plotly'):")
        post.append("    try:")
        post.append("        import plotly.basedatatypes as _pbt")
        post.append("        _candidate = locals().get(_name) or globals().get(_name)")
        post.append("        if isinstance(_candidate, _pbt.BaseFigure):")
        post.append("            _plt_ink_fig = _candidate")
        post.append("            break")
        post.append("    except Exception:")
        post.append("        pass")
        post.append("if _plt_ink_fig is None:")
        post.append("    raise RuntimeError(")
        post.append("        'plt_ink Plotly backend: no figure found. '")
        post.append("        'Assign your figure to a variable named `fig` or `_fig_plotly`.'")
        post.append("    )")
        post.append(f"output_file = r'{output_path}'")
        post.append(
            f"_plt_ink_fig.write_image(output_file, format='{fmt}', "
            f"width={width_px}, height={height_px})"
        )
        post.append("print(f'SUCCESS:{output_file}')")
        return post

    def generate_preamble(self, user_code):
        """Generate the preamble (imports, configuration, etc.)."""
        preamble = []
        
        # Error handling setup
        if self.options.error_handling == "warn":
            preamble.append("import warnings")
            if not self.options.show_warnings:
                preamble.append("warnings.filterwarnings('ignore')")
            preamble.append("")
        
        # Auto imports
        if self.options.auto_imports:
            preamble.append("import matplotlib")
            preamble.append("matplotlib.use('Agg')  # Non-interactive backend")
            preamble.append("import matplotlib.pyplot as plt")
            preamble.append("import numpy as np")
            preamble.append("import os")
            preamble.append("from matplotlib import cm")
            preamble.append("from matplotlib.colors import Normalize")
            preamble.append("try:")
            preamble.append("    import seaborn as sns")
            preamble.append("    seaborn_available = True")
            preamble.append("except ImportError:")
            preamble.append("    seaborn_available = False")
        
        # Additional imports
        if self.options.additional_imports:
            preamble.append("")
            preamble.append("# Additional imports")
            additional = self.options.additional_imports.replace('\\n', '\n')
            for line in additional.split('\n'):
                if line.strip():
                    preamble.append(line.strip())
        
        # Optional imports for data
        if self.options.use_data_file:
            self.log("Adding data import libraries")
            preamble.append("import pandas as pd")
            if self.options.data_format == "json":
                preamble.append("import json")
            if self.options.date_columns:
                preamble.append("from datetime import datetime")
        
        preamble.append("")
        
        # Custom preamble
        if self.options.custom_preamble:
            preamble.append("# Custom preamble")
            custom = self.options.custom_preamble.replace('\\n', '\n')
            for line in custom.split('\n'):
                preamble.append(line)
            preamble.append("")
        
        # Apply style
        if self.options.plot_style != "default":
            self.log(f"Applying plot style: {self.options.plot_style}")
            # Academic presets (ieee / nature / apa) are stored as .mplstyle files
            # in the plt_ink_styles/ sub-directory alongside this extension.
            _ACADEMIC_STYLES = ('ieee', 'nature', 'apa')
            if self.options.plot_style in _ACADEMIC_STYLES:
                _styles_dir = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 'plt_ink_styles'
                )
                _style_file = os.path.join(_styles_dir, f'{self.options.plot_style}.mplstyle')
                preamble.append("import os as _os_pltink")
                preamble.append(f"_plt_ink_style = r'{_style_file}'")
                preamble.append("if _os_pltink.path.isfile(_plt_ink_style):")
                preamble.append("    plt.style.use(_plt_ink_style)")
                preamble.append("del _os_pltink, _plt_ink_style")
            else:
                preamble.append(f"plt.style.use('{self.options.plot_style}')")

        
        # Configure matplotlib
        preamble.append("# Configure matplotlib")
        preamble.append(f"plt.rcParams['font.family'] = '{self.options.font_family}'")
        preamble.append(f"plt.rcParams['font.size'] = {self.options.font_size}")
        preamble.append(f"plt.rcParams['axes.titlesize'] = {self.options.title_size}")
        preamble.append(f"plt.rcParams['axes.labelsize'] = {self.options.label_size}")
        preamble.append(f"plt.rcParams['lines.linewidth'] = {self.options.line_width}")
        preamble.append(f"plt.rcParams['lines.markersize'] = {self.options.marker_size}")
        
        # Background color (validated at runtime to catch invalid color names)
        if self.options.background_color != "white":
            preamble.append("try:")
            preamble.append(f"    plt.rcParams['axes.facecolor'] = '{self.options.background_color}'")
            preamble.append(f"    plt.rcParams['figure.facecolor'] = '{self.options.background_color}'")
            preamble.append("except ValueError:")
            preamble.append("    import warnings")
            preamble.append(f"    warnings.warn(\"Invalid background color '{self.options.background_color}', falling back to white.\")")
            preamble.append("    plt.rcParams['axes.facecolor'] = 'white'")
            preamble.append("    plt.rcParams['figure.facecolor'] = 'white'")
        
        # Grid styling
        preamble.append(f"plt.rcParams['grid.linestyle'] = '{self.options.grid_style}'")
        preamble.append(f"plt.rcParams['grid.alpha'] = {self.options.grid_alpha}")
        
        # Color cycle
        if self.options.color_cycle != "default":
            color_cycles = {
                "tab10": "plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.tab10.colors)",
                "tab20": "plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.tab20.colors)",
                "set1": "plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Set1.colors)",
                "set2": "plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Set2.colors)",
                "paired": "plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Paired.colors)",
                "dark2": "plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Dark2.colors)",
            }
            if self.options.color_cycle in color_cycles:
                preamble.append(color_cycles[self.options.color_cycle])
        
        if self.options.use_latex:
            preamble.append("plt.rcParams['text.usetex'] = True")
        
        preamble.append("")
        
        # Provide configuration variables to user scripts
        preamble.append("# Extension configuration (available to user scripts)")
        preamble.append(f"_fig_width = {self.options.figure_width}")
        preamble.append(f"_fig_height = {self.options.figure_height}")
        preamble.append(f"_dpi = {self.options.dpi}")
        preamble.append(f"_show_grid = {self.options.grid}")
        preamble.append(f"_show_legend = {self.options.legend}")
        preamble.append(f"_legend_position = '{self.options.legend_position}'")
        preamble.append(f"_colormap = '{self.options.color_map}'")
        preamble.append(f"_transparent = {self.options.transparent}")
        preamble.append(f"_subplot_rows = {self.options.subplot_rows}")
        preamble.append(f"_subplot_cols = {self.options.subplot_cols}")
        preamble.append("")
        
        # Helper functions
        preamble.append("# Helper functions")
        preamble.append("def apply_style(ax=None):")
        preamble.append("    '''Apply common styling to axis.'''")
        preamble.append("    if ax is None:")
        preamble.append("        ax = plt.gca()")
        preamble.append(f"    if {self.options.grid}:")
        preamble.append(f"        ax.grid(True, alpha={self.options.grid_alpha}, linestyle='{self.options.grid_style}')")
        if self.options.auto_despine:
            preamble.append("    ax.spines['top'].set_visible(False)")
            preamble.append("    ax.spines['right'].set_visible(False)")
        preamble.append("")
        
        preamble.append("def get_cmap(name=None):")
        preamble.append("    '''Get colormap by name or default (matplotlib 3.7+ compatible).'''")
        preamble.append(f"    _cname = name or '{self.options.color_map}'")
        preamble.append("    try:")
        preamble.append("        import matplotlib as _mpl")
        preamble.append("        return _mpl.colormaps[_cname]")
        preamble.append("    except (KeyError, AttributeError):")
        preamble.append("        return plt.cm.get_cmap(_cname)  # fallback for older matplotlib")
        preamble.append("")
        
        # Create figure if user code doesn't and auto_create_figure is enabled
        if self.options.auto_create_figure:
            if 'plt.figure' not in user_code and 'plt.subplots' not in user_code:
                self.log("Creating figure (user code doesn't create figure)")
                preamble.append("# Create figure")
                if self.options.subplot_rows > 1 or self.options.subplot_cols > 1:
                    share_x = "True" if self.options.share_x else "False"
                    share_y = "True" if self.options.share_y else "False"
                    layout = "'constrained'" if self.options.constrained_layout else "None"
                    preamble.append(
                        f"fig, axes = plt.subplots({self.options.subplot_rows}, {self.options.subplot_cols}, "
                        f"figsize=({self.options.figure_width}, {self.options.figure_height}), "
                        f"sharex={share_x}, sharey={share_y}, layout={layout})"
                    )
                    preamble.append("# Make 'ax' point to first axis for convenience")
                    preamble.append("ax = axes.flat[0] if hasattr(axes, 'flat') else axes")
                else:
                    layout_arg = ", layout='constrained'" if self.options.constrained_layout else ""
                    preamble.append(f"fig, ax = plt.subplots(figsize=({self.options.figure_width}, {self.options.figure_height}){layout_arg})")
                preamble.append("")
        
        return preamble
    
    def generate_postamble(self):
        """Generate the postamble (tight layout, save, etc.)."""
        postamble = []
        
        # Auto despine if enabled (apply to all axes)
        if self.options.auto_despine:
            postamble.append("# Apply despine to all axes")
            postamble.append("for ax in plt.gcf().get_axes():")
            postamble.append("    ax.spines['top'].set_visible(False)")
            postamble.append("    ax.spines['right'].set_visible(False)")
            postamble.append("")
        
        # Apply grid to all axes if enabled
        if self.options.grid:
            postamble.append("# Apply grid to all axes")
            postamble.append("for ax in plt.gcf().get_axes():")
            postamble.append(f"    ax.grid(True, alpha={self.options.grid_alpha}, linestyle='{self.options.grid_style}')")
            postamble.append("")
        
        # Layout adjustment
        if self.options.tight_layout and not self.options.constrained_layout:
            postamble.append("try:")
            postamble.append("    plt.tight_layout()")
            postamble.append("except Exception:")
            postamble.append("    pass  # tight_layout may fail with some configurations")
        
        # Save figure
        postamble.append("")
        postamble.append("# Save figure")
        output_path = self.get_temp_output_path()
        self.log(f"Output path: {output_path}")
        
        save_params = []
        save_params.append(f"format='{self.options.output_format}'")
        save_params.append(f"dpi={self.options.dpi}")
        save_params.append(f"transparent={self.options.transparent}")
        if self.options.tight_layout and not self.options.constrained_layout:
            save_params.append("bbox_inches='tight'")
        
        save_params_str = ', '.join(save_params)
        self.debug_var("save_params", save_params_str)
        
        postamble.append(f"output_file = r'{output_path}'")
        postamble.append(f"plt.savefig(output_file, {save_params_str})")
        postamble.append("plt.close()")
        postamble.append("print(f'SUCCESS:{output_file}')")
        
        return postamble

    def generate_data_loading_code(self):
        """Generate code to load data from file with multi-column support."""
        data_path = self.options.data_file_path.replace('\\', '/')
        self.debug_var("data_file_path", data_path)
        self.debug_var("data_format", self.options.data_format)
        
        code_lines = []
        
        # Parse column indices
        x_indices = self.parse_column_indices(self.options.x_columns)
        y_indices = self.parse_column_indices(self.options.y_columns)
        date_indices = self.parse_column_indices(self.options.date_columns)
        column_names = [n.strip() for n in self.options.column_names.split(',') if n.strip()]
        
        self.debug_var("x_indices", x_indices)
        self.debug_var("y_indices", y_indices)
        self.debug_var("date_indices", date_indices)
        self.debug_var("column_names", column_names)
        
        if self.options.data_format == "csv":
            # Build read_csv parameters
            csv_params = [f"r'{data_path}'"]
            csv_params.append(f"delimiter='{self.options.csv_delimiter}'")
            
            if self.options.skip_header:
                csv_params.append(f"header={self.options.header_row}")
            else:
                csv_params.append("header=None")
            
            # Parse dates if specified
            if date_indices:
                # pandas >= 2.0: parse_dates still works; apply to_datetime after load
                csv_params.append(f"parse_dates={date_indices}")
            
            # Load specific columns by name if provided
            if column_names and not self.options.load_all_columns:
                csv_params.append(f"usecols={column_names}")
            
            code_lines.append(f"df = pd.read_csv({', '.join(csv_params)})")
            # Apply date format conversion after loading (avoids deprecated date_parser kwarg)
            if date_indices and self.options.date_format:
                for col_idx in date_indices:
                    code_lines.append(
                        f"df.iloc[:, {col_idx}] = pd.to_datetime(df.iloc[:, {col_idx}], "
                        f"format='{self.options.date_format}', errors='coerce')"
                    )
        
        elif self.options.data_format == "excel":
            excel_params = [f"r'{data_path}'"]
            if self.options.skip_header:
                excel_params.append(f"header={self.options.header_row}")
            else:
                excel_params.append("header=None")
            
            if date_indices:
                excel_params.append(f"parse_dates={date_indices}")
            
            code_lines.append(f"df = pd.read_excel({', '.join(excel_params)})")
        
        elif self.options.data_format == "json":
            code_lines.append(f"with open(r'{data_path}', 'r') as f:")
            code_lines.append("    _json_data = json.load(f)")
            code_lines.append("if isinstance(_json_data, list):")
            code_lines.append("    df = pd.DataFrame(_json_data)")
            code_lines.append("elif isinstance(_json_data, dict):")
            code_lines.append("    df = pd.DataFrame(_json_data)")
            code_lines.append("else:")
            code_lines.append("    df = pd.DataFrame([_json_data])")
        
        else:
            # Text format (space/tab separated)
            skip_rows = self.options.header_row + 1 if self.options.skip_header else 0
            code_lines.append(f"_raw_data = np.loadtxt(r'{data_path}', skiprows={skip_rows})")
            code_lines.append("df = pd.DataFrame(_raw_data)")
        
        code_lines.append("")
        code_lines.append("# Make dataframe available as 'data'")
        code_lines.append("data = df")
        code_lines.append("")
        
        # Extract columns
        code_lines.append("# Column data extraction")
        code_lines.append("columns = {}")
        
        if self.options.load_all_columns:
            code_lines.append("# All columns loaded into dictionary")
            code_lines.append("for i, col in enumerate(df.columns):")
            code_lines.append("    columns[f'col_{i}'] = df.iloc[:, i].values")
            code_lines.append("    columns[str(col)] = df.iloc[:, i].values")
        else:
            # Extract X columns
            if x_indices:
                if len(x_indices) == 1:
                    code_lines.append(f"x_data = df.iloc[:, {x_indices[0]}].values")
                else:
                    code_lines.append(f"x_data = [df.iloc[:, i].values for i in {x_indices}]")
                    code_lines.append("x_columns = x_data  # List of X column arrays")
            
            # Extract Y columns
            if y_indices:
                if len(y_indices) == 1:
                    code_lines.append(f"y_data = df.iloc[:, {y_indices[0]}].values")
                else:
                    code_lines.append(f"y_data = [df.iloc[:, i].values for i in {y_indices}]")
                    code_lines.append("y_columns = y_data  # List of Y column arrays")
            
            # Store in columns dict
            for i, idx in enumerate(x_indices):
                code_lines.append(f"columns['x{i}'] = df.iloc[:, {idx}].values")
            for i, idx in enumerate(y_indices):
                code_lines.append(f"columns['y{i}'] = df.iloc[:, {idx}].values")
        
        # Named column access
        if column_names:
            code_lines.append("")
            code_lines.append("# Named column access")
            for name in column_names:
                safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
                code_lines.append(f"try:")
                code_lines.append(f"    {safe_name} = df['{name}'].values")
                code_lines.append(f"except KeyError:")
                code_lines.append(f"    pass  # Column '{name}' not found")
        
        code_lines.append("")
        code_lines.append("# Data info for debugging")
        code_lines.append("print(f'Loaded data shape: {df.shape}')")
        code_lines.append("print(f'Columns: {list(df.columns)}')")
        
        return '\n'.join(code_lines)
        
    def get_temp_output_path(self):
        """Get temporary output file path."""
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"matplotlib_output_{timestamp}.{self.options.output_format}"
        return os.path.join(temp_dir, filename)
    
    def execute_script(self, script_content):
        """Execute the matplotlib script and return output file path."""
        temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
        
        try:
            self.log(f"Writing script to temp file: {temp_script.name}")
            temp_script.write(script_content)
            temp_script.close()
            
            self.log(f"Executing: {self.options.python_path} {temp_script.name}")
            timeout = getattr(self.options, 'execution_timeout', 60)
            result = subprocess.run(
                [self.options.python_path, temp_script.name],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                creationflags=_WIN_FLAGS,
            )
            
            self.debug_var("execution_returncode", result.returncode)
            self.debug_var("execution_stdout", result.stdout)
            self.debug_var("execution_stderr", result.stderr)
            
            if result.returncode == 0:
                # Check for USER_ERROR message from wrapped warn-mode execution
                for line in result.stdout.split('\n'):
                    if line.startswith('USER_ERROR:'):
                        tb_raw = line.replace('USER_ERROR:', '', 1)
                        friendly = self._remap_traceback(tb_raw)
                        inkex.errormsg(f"Script warning (continuing):\n{friendly}")
                for line in result.stdout.split('\n'):
                    if line.startswith('SUCCESS:'):
                        output_path = line.replace('SUCCESS:', '').strip()
                        self.log(f"Found output path: {output_path}")
                        return output_path

                self.log("Script executed but no SUCCESS message found", "WARNING")
                inkex.errormsg("Script executed but no output file generated.")
                if result.stdout:
                    inkex.errormsg(f"Output: {result.stdout}")
                return None
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                self.log(f"Script execution failed with code {result.returncode}", "ERROR")
                self.log(f"Error message: {error_msg}", "ERROR")
                friendly = self._remap_traceback(error_msg)
                if self.options.error_handling == "warn":
                    inkex.errormsg(f"Warning: Script had errors:\n{friendly}")
                else:
                    inkex.errormsg(f"Script execution failed:\n{friendly}")
                return None
        
        except subprocess.TimeoutExpired:
            timeout = getattr(self.options, 'execution_timeout', 60)
            self.log(f"Script execution timed out after {timeout}s", "ERROR")
            inkex.errormsg(f"Script execution timed out ({timeout} seconds).")
            return None

        except Exception as e:
            self.log(f"Exception during script execution: {str(e)}", "ERROR")
            inkex.errormsg(f"Failed to execute script: {str(e)}")
            return None

        finally:
            if not self.options.keep_temp_files:
                try:
                    os.remove(temp_script.name)
                    self.log("Temp script file removed")
                except Exception as e:
                    self.log(f"Failed to remove temp script: {str(e)}", "WARNING")

    def _remap_traceback(self, tb_text):
        """Rewrite temp-file line numbers to user-code line numbers in tracebacks."""
        preamble = getattr(self, '_preamble_lines', 0)
        if preamble == 0:
            return tb_text
        lines_out = []
        for line in tb_text.splitlines():
            m = re.search(r'line (\d+)', line)
            if m:
                abs_line = int(m.group(1))
                user_line = abs_line - preamble
                if user_line > 0:
                    line = line[:m.start(1)] + str(user_line) + line[m.end(1):]
                    line = line.replace('.py', ' (your script)')
            lines_out.append(line)
        return '\n'.join(lines_out)
    
    def _get_figure_label(self):
        """Build a human-readable label for the inserted figure element."""
        src = getattr(self.options, 'script_source', 'inline')
        if src == 'bank':
            cat  = getattr(self.options, 'bank_category', '')
            name = getattr(self.options, 'bank_script', '')
            return f"plt_ink: {cat}/{name}"
        elif src == 'file':
            base = os.path.basename(getattr(self.options, 'script_file', '') or 'script.py')
            return f"plt_ink: {base}"
        else:
            # Try to extract the first plt.title() call from inline code
            code = getattr(self.options, 'script_code', '')
            m = re.search(r"plt\.title\(['\"]([^'\"]+)['\"]", code)
            return f"plt_ink: {m.group(1)}" if m else 'plt_ink: inline'

    def _find_existing_plt_ink(self):
        """Return the first plt_ink element in the current selection, or None."""
        for elem in self.svg.selection:
            if elem.get(PLT_INK_ATTR):
                return elem
            # Also check direct children of a group
            for child in elem:
                if child.get(PLT_INK_ATTR):
                    return child
        return None

    def _run_batch(self):
        """Execute all queued batch scripts and insert figures in a row or column."""
        import json as _json

        raw = getattr(self.options, 'batch_scripts', None)
        if not raw:
            inkex.errormsg("Batch mode is enabled but the script queue is empty.")
            return

        try:
            batch_rows = _json.loads(raw)
        except Exception as exc:
            inkex.errormsg(f"Could not parse batch queue: {exc}")
            return

        if not batch_rows:
            inkex.errormsg("Batch queue is empty.")
            return

        gap       = float(getattr(self.options, 'batch_gap', 20))
        direction = getattr(self.options, 'batch_direction', 'horizontal')

        # Starting offset — append to the right/below the current canvas origin
        offset_x = 0.0
        offset_y = 0.0

        successes = 0
        errors    = []

        for idx, row in enumerate(batch_rows):
            source_type, value, label = row[0], row[1], row[2] if len(row) > 2 else ""
            self.log(f"Batch [{idx+1}/{len(batch_rows)}]: {label}")

            # Override script source temporarily
            orig_source  = self.options.script_source
            orig_code    = self.options.script_code
            orig_file    = self.options.script_file
            orig_bank_cat  = getattr(self.options, 'bank_category', '')
            orig_bank_scr  = getattr(self.options, 'bank_script', '')

            try:
                if source_type == "inline":
                    self.options.script_source = "inline"
                    self.options.script_code   = value
                elif source_type == "file":
                    self.options.script_source = "file"
                    self.options.script_file   = value
                elif source_type == "bank":
                    # value is absolute path; derive category/script from it
                    self.options.script_source = "file"
                    self.options.script_file   = value
                else:
                    errors.append(f"[{idx+1}] Unknown source type: {source_type}")
                    continue

                script_content = self.generate_script()
                if not script_content:
                    errors.append(f"[{idx+1}] Script generation failed for: {label}")
                    continue

                output_file = self.execute_script(script_content)
                if not output_file or not os.path.exists(output_file):
                    errors.append(f"[{idx+1}] Execution produced no output for: {label}")
                    continue

                # Temporarily patch position so insert_figure places at offset
                orig_pos = self.options.position_mode
                orig_cx  = getattr(self.options, 'custom_x', 0)
                orig_cy  = getattr(self.options, 'custom_y', 0)
                self.options.position_mode = 'custom'
                self.options.custom_x = offset_x
                self.options.custom_y = offset_y

                self.insert_figure(output_file)
                successes += 1

                self.options.position_mode = orig_pos
                self.options.custom_x      = orig_cx
                self.options.custom_y      = orig_cy

                # Advance offset by figure size + gap
                fig_w_px = self.options.figure_width  * 96 * self.options.scale_factor
                fig_h_px = self.options.figure_height * 96 * self.options.scale_factor
                if direction == 'horizontal':
                    offset_x += fig_w_px + gap
                else:
                    offset_y += fig_h_px + gap

                if not self.options.keep_temp_files:
                    try:
                        os.remove(output_file)
                    except OSError:
                        pass

            finally:
                self.options.script_source   = orig_source
                self.options.script_code     = orig_code
                self.options.script_file     = orig_file
                self.options.bank_category   = orig_bank_cat
                self.options.bank_script     = orig_bank_scr

        msg = f"Batch complete: {successes}/{len(batch_rows)} figure(s) inserted."
        if errors:
            self._show_result(
                "warning",
                f"Batch completed with {len(errors)} error(s).",
                detail="\n".join(errors),
                stats={
                    "Inserted": f"{successes} / {len(batch_rows)}",
                    "Errors":   str(len(errors)),
                    "Direction": direction,
                },
            )
        else:
            self._show_result(
                "success",
                msg,
                stats={
                    "Figures inserted": str(successes),
                    "Direction":        direction,
                    "Gap":              f"{gap} px",
                },
            )
        self.log(msg)

    # Maximum raster image size to embed without warning (50 MB of raw image data).
    _RASTER_WARN_BYTES = 50 * 1_000_000
    # Above this threshold (100 MB) we refuse to embed to prevent Inkscape OOM crash.
    _RASTER_LIMIT_BYTES = 100 * 1_000_000

    def insert_figure(self, figure_path):
        """Insert the generated figure — replaces an existing plt_ink element if selected."""
        self.log(f"Inserting figure from: {figure_path}")

        # ── File-size guard ───────────────────────────────────────────────────────
        try:
            file_size = os.path.getsize(figure_path)
        except OSError:
            file_size = 0

        if file_size > self._RASTER_LIMIT_BYTES:
            msg = (
                f"The generated figure is very large ({file_size / 1e6:.1f} MB) and "
                "cannot be safely embedded — Inkscape may crash.\n\n"
                "Suggestions:\n"
                "  • Reduce figure size or data point count\n"
                "  • Lower DPI (current: {self.options.dpi}) to something like 96\n"
                "  • Use SVG format for vector output (usually much smaller)\n"
                "  • Disable 'Embed image' and use a linked file instead"
            )
            self.log(msg, "ERROR")
            self._show_result("error", "Figure too large to embed safely", detail=msg)
            return
        elif file_size > self._RASTER_WARN_BYTES:
            self.log(
                f"Figure file is large ({file_size / 1e6:.1f} MB). "
                "Embedding may be slow — consider reducing size or using SVG format.",
                "WARNING"
            )

        try:
            with open(figure_path, 'rb') as f:
                image_data = f.read()
            self.log(f"Read {len(image_data)} bytes from figure file")
        except Exception as e:
            self.log(f"Failed to read figure file: {str(e)}", "ERROR")
            inkex.errormsg(f"Failed to read figure file: {str(e)}")
            return

        label = self._get_figure_label()
        existing = self._find_existing_plt_ink()

        if self.options.output_format == 'svg':
            try:
                svg_content = image_data.decode('utf-8')
                self.log("Importing SVG content directly")
                self.import_svg_content(svg_content, label=label, replace=existing)
                return
            except MemoryError:
                msg = (
                    f"Not enough memory to parse the SVG figure ({file_size / 1e6:.1f} MB).  "
                    "Try reducing figure complexity or switching to PNG format."
                )
                self.log(msg, "ERROR")
                self._show_result("error", "Out of memory parsing SVG", detail=msg)
                return
            except Exception as e:
                self.log(f"Failed to import SVG directly: {str(e)}", "WARNING")

        image_elem = Image()
        image_elem.set('id', self.svg.get_unique_id('matplotlib-figure'))
        
        if self.options.embed_image:
            self.log("Embedding image as data URI")
            encoded = base64.b64encode(image_data).decode('utf-8')
            mime_types = {
                'png': 'image/png',
                'svg': 'image/svg+xml',
                'pdf': 'application/pdf'
            }
            mime_type = mime_types.get(self.options.output_format, 'image/png')
            data_uri = f'data:{mime_type};base64,{encoded}'
            # Set both modern href and legacy xlink:href for compatibility
            image_elem.set('href', data_uri)
            image_elem.set('{http://www.w3.org/1999/xlink}href', data_uri)
            self.log(f"Embedded as {mime_type}")
        else:
            self.log(f"Linking to external file: {figure_path}")
            image_elem.set('href', figure_path)
            image_elem.set('{http://www.w3.org/1999/xlink}href', figure_path)
        
        position = self.calculate_position()
        size = self.calculate_size()
        
        self.debug_var("position", position)
        self.debug_var("size", size)
        
        image_elem.set('x', str(position['x']))
        image_elem.set('y', str(position['y']))
        image_elem.set('width', str(size['width']))
        image_elem.set('height', str(size['height']))
        image_elem.set('preserveAspectRatio', 'xMidYMid meet')
        image_elem.set(PLT_INK_ATTR, label)
        image_elem.set(INKSCAPE_LABEL, label)

        if existing is not None:
            self.log(f"Replacing existing plt_ink element: {existing.get('id')}")
            parent = existing.getparent()
            idx = list(parent).index(existing)
            parent.remove(existing)
            parent.insert(idx, image_elem)
        else:
            self.svg.get_current_layer().append(image_elem)
        self.log("Image element added to document")
    
    def _parse_svg_viewport(self, root):
        """Return (vb_x, vb_y, vb_w, vb_h) from the SVG root's viewBox, or None if absent.

        Falls back to parsing the width/height attributes (handling pt/in/px/mm units)
        so we can compute the correct coordinate-space-to-display-size scale factor.
        """
        SVG_NS = 'http://www.w3.org/2000/svg'

        # Try viewBox first
        vb = root.get('viewBox') or root.get(f'{{{SVG_NS}}}viewBox')
        if vb:
            try:
                parts = [float(v) for v in vb.replace(',', ' ').split()]
                if len(parts) == 4:
                    return tuple(parts)  # (x, y, w, h)
            except ValueError:
                pass

        # Fall back to width/height attributes
        def _to_px(val_str):
            """Convert a CSS-unit dimension string to pixels (96 dpi)."""
            if not val_str:
                return None
            val_str = val_str.strip()
            units_map = {
                'pt': 96 / 72,
                'in': 96.0,
                'mm': 96 / 25.4,
                'cm': 96 / 2.54,
                'px': 1.0,
                'em': 16.0,  # assume 16px default
            }
            for unit, factor in units_map.items():
                if val_str.endswith(unit):
                    try:
                        return float(val_str[:-len(unit)]) * factor
                    except ValueError:
                        return None
            try:
                return float(val_str)  # bare number → pixels
            except ValueError:
                return None

        w = _to_px(root.get('width'))
        h = _to_px(root.get('height'))
        if w and h:
            return (0.0, 0.0, w, h)
        return None

    def import_svg_content(self, svg_content, label='plt_ink', replace=None):
        """Import SVG content directly into the document, optionally replacing an existing element.

        Position fix: matplotlib's SVG uses an internal coordinate space derived from
        72 pt/in (e.g. a 8×6 in figure has a viewBox of 0 0 576 432).  When we strip
        the SVG root and embed the children in a <g>, those coordinates are interpreted
        in the document's user-unit space (96 px/in).  We therefore compute a scale
        factor  sx = display_width / vb_w  (and sy = display_height / vb_h) so that
        the imported content is rendered at exactly the size Inkscape expects.
        """
        try:
            self.log("Parsing SVG content")

            # ── Size guard: very large SVG files can exhaust lxml's memory ─────────
            svg_bytes = len(svg_content.encode('utf-8'))
            SVG_SIZE_WARN_MB = 25
            if svg_bytes > SVG_SIZE_WARN_MB * 1_000_000:
                self.log(
                    f"SVG content is large ({svg_bytes / 1e6:.1f} MB). "
                    "Consider using PNG format for complex figures to avoid performance issues.",
                    "WARNING"
                )

            try:
                root = etree.fromstring(svg_content.encode('utf-8'))
            except MemoryError:
                raise RuntimeError(
                    f"Not enough memory to parse the SVG figure "
                    f"({svg_bytes / 1e6:.1f} MB).  "
                    "Try reducing figure complexity, lowering the figure dimensions, "
                    "or switching to PNG output format."
                )

            SVG_NS = 'http://www.w3.org/2000/svg'
            defs_tag = f'{{{SVG_NS}}}defs'
            meta_tag = f'{{{SVG_NS}}}metadata'

            # Build a merged namespace map: document namespaces + imported SVG namespaces.
            # This ensures namespace prefixes used by matplotlib (xlink, dc, cc, rdf …)
            # are declared on the wrapper <g> element so all child references resolve.
            doc_nsmap = dict(self.svg.nsmap)
            src_nsmap = {k: v for k, v in root.nsmap.items() if k is not None}
            merged_nsmap = {**src_nsmap, **doc_nsmap}  # doc wins on conflict

            # Create the group element using the merged nsmap so lxml serialises all
            # required xmlns: declarations onto it.  Include plt_ink namespace so
            # the PLT_INK_ATTR Clark-notation attribute is serialised with a prefix.
            merged_nsmap['plt_ink'] = PLT_INK_NS
            merged_nsmap['inkscape'] = INKSCAPE_NS
            group = etree.Element(f'{{{SVG_NS}}}g', nsmap=merged_nsmap)
            group.set('id', self.svg.get_unique_id('matplotlib-svg'))
            group.set(PLT_INK_ATTR, label)
            group.set(INKSCAPE_LABEL, label)

            position = self.calculate_position()
            user_scale = self.options.scale_factor
            self.debug_var("svg_import_position", position)
            self.debug_var("scale_factor", user_scale)

            # ── Coordinate-system scale fix ───────────────────────────────────────
            # Determine scale factors that map from the SVG's internal coordinate
            # space (viewBox) to the desired display size in Inkscape's user units.
            viewport = self._parse_svg_viewport(root)
            self.debug_var("svg_viewport", viewport)

            if viewport and viewport[2] > 0 and viewport[3] > 0:
                vb_x, vb_y, vb_w, vb_h = viewport
                display = self.calculate_size()
                # display['width'] / display['height'] are in Inkscape user units (px).
                sx = display['width']  / vb_w * user_scale
                sy = display['height'] / vb_h * user_scale
                tx = position['x'] - vb_x * sx
                ty = position['y'] - vb_y * sy
                self.log(
                    f"SVG viewport {vb_w:.1f}×{vb_h:.1f} → "
                    f"display {display['width']:.1f}×{display['height']:.1f} px  "
                    f"(scale {sx:.4f}, {sy:.4f})"
                )
                if abs(sx - sy) < 1e-6:
                    # Uniform scale: simpler transform
                    transform = f'translate({tx:.4f}, {ty:.4f}) scale({sx:.6f})'
                else:
                    transform = f'translate({tx:.4f}, {ty:.4f}) scale({sx:.6f}, {sy:.6f})'
            else:
                # No viewBox — fall back to translate + user scale only
                tx, ty = position['x'], position['y']
                if user_scale != 1.0:
                    transform = f'translate({tx}, {ty}) scale({user_scale})'
                else:
                    transform = f'translate({tx}, {ty})'

            group.set('transform', transform)

            # Merge <defs> into document defs; skip <metadata>; append drawing elements.
            doc_defs = self.svg.find(defs_tag)
            if doc_defs is None:
                doc_defs = etree.SubElement(self.svg, defs_tag)

            elem_count = 0
            for elem in list(root):
                tag = elem.tag
                if tag == defs_tag or tag == 'defs':
                    # Merge matplotlib defs children into document defs
                    for child in list(elem):
                        doc_defs.append(child)
                elif tag in (meta_tag, 'metadata'):
                    pass  # skip metadata
                else:
                    group.append(elem)
                    elem_count += 1

            self.log(f"Imported {elem_count} elements from SVG")

            if replace is not None:
                self.log(f"Replacing existing plt_ink group: {replace.get('id')}")
                parent = replace.getparent()
                idx = list(parent).index(replace)
                parent.remove(replace)
                parent.insert(idx, group)
            else:
                self.svg.get_current_layer().append(group)
            self.log("SVG group added to document")

        except MemoryError as e:
            msg = (
                "Not enough memory to import the SVG figure.  "
                "Try reducing figure size/complexity or using PNG format."
            )
            self.log(msg, "ERROR")
            inkex.errormsg(msg)
            raise RuntimeError(msg) from e
        except Exception as e:
            self.log(f"Failed to import SVG content: {str(e)}", "ERROR")
            inkex.errormsg(f"Failed to import SVG content: {str(e)}")
            raise
    
    def calculate_position(self):
        """Calculate position based on position mode."""
        doc_width = self.svg.viewport_width
        doc_height = self.svg.viewport_height
        
        self.debug_var("doc_width", doc_width)
        self.debug_var("doc_height", doc_height)
        
        size = self.calculate_size()
        
        # Handle custom position
        if self.options.position_mode == 'custom':
            return {
                'x': self.options.custom_x,
                'y': self.options.custom_y
            }
        
        positions = {
            'center': {
                'x': (doc_width - size['width']) / 2,
                'y': (doc_height - size['height']) / 2
            },
            'top_left': {'x': 0, 'y': 0},
            'top_center': {
                'x': (doc_width - size['width']) / 2,
                'y': 0
            },
            'top_right': {
                'x': doc_width - size['width'],
                'y': 0
            },
            'bottom_left': {
                'x': 0,
                'y': doc_height - size['height']
            },
            'bottom_center': {
                'x': (doc_width - size['width']) / 2,
                'y': doc_height - size['height']
            },
            'bottom_right': {
                'x': doc_width - size['width'],
                'y': doc_height - size['height']
            },
            'cursor': {
                'x': (doc_width - size['width']) / 2,
                'y': (doc_height - size['height']) / 2
            }
        }
        
        if self.options.position_mode == 'selection' and self.svg.selection:
            for elem in self.svg.selection:
                bbox = elem.bounding_box()
                if bbox:
                    self.log(f"Using selected object position")
                    self.debug_var("bbox_center", (bbox.center_x, bbox.center_y))
                    return {
                        'x': bbox.center_x - size['width']/2, 
                        'y': bbox.center_y - size['height']/2
                    }
        
        position = positions.get(self.options.position_mode, positions['center'])
        self.log(f"Position mode: {self.options.position_mode}")
        return position
    
    def calculate_size(self):
        """Calculate image display size in document units.

        DPI only affects render quality, not the visual size Inkscape displays.
        Display size is always figure_width * 96 px/in (Inkscape's base resolution).
        """
        DISPLAY_PPI = 96.0
        width_px  = self.options.figure_width  * DISPLAY_PPI * self.options.scale_factor
        height_px = self.options.figure_height * DISPLAY_PPI * self.options.scale_factor

        width  = self.svg.unittouu(f'{width_px}px')
        height = self.svg.unittouu(f'{height_px}px')

        self.log(
            f"Figure size: {self.options.figure_width}\" x {self.options.figure_height}\" "
            f"(render DPI={self.options.dpi}, display at 96 ppi, scale={self.options.scale_factor})"
        )
        self.log(f"Display pixels: {width_px} x {height_px}")
        self.log(f"Document units: {width} x {height}")

        return {'width': width, 'height': height}


if __name__ == '__main__':
    MatplotlibGenerator().run()