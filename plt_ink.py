#!/usr/bin/env python3
"""
Inkscape extension to generate and insert matplotlib figures.
"""


# MIT License

# Copyright (c) 2026 Rachid, Youven ZEGHLACHE
#!/usr/bin/env python3


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


SCRIPT_CATEGORIES = {
    'line_plots': 'Line Plots',
    'scatter_plots': 'Scatter Plots', 
    'bar_charts': 'Bar Charts',
    'statistical': 'Statistical Plots',
    'scientific': 'Scientific Plots',
    'time_series': 'Time Series',
    'publication': 'Publication Ready',
}



class MatplotlibGenerator(inkex.EffectExtension):
    """Extension to generate matplotlib figures."""
    
    def __init__(self):
        super().__init__()
        self.debug_mode = True
        self.log_file = os.path.join(tempfile.gettempdir(), 'matplotlib_inkscape_debug.log')
        # Script bank directory
        self.script_bank_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plt_ink_scripts')
        
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
    
    def add_arguments(self, pars):
        pars.add_argument("--tab", type=str, default="script", help="Active tab")
        
        # Script parameters
        pars.add_argument("--python_path", type=str, default="python", help="Python executable path")
        pars.add_argument("--script_source", type=str, default="inline", help="Script source: inline, file, or bank")
        pars.add_argument("--script_code", type=str, default="", help="Python code")
        pars.add_argument("--script_file", type=str, default="", help="Script file path")
        
        # Script bank parameters
        pars.add_argument("--bank_category", type=str, default="line_plots", help="Script bank category")
        pars.add_argument("--bank_script", type=str, default="basic_line", help="Script from bank")
        
        # Preamble parameters (NEW)
        pars.add_argument("--use_preamble", type=inkex.Boolean, default=True, help="Include preamble")
        pars.add_argument("--custom_preamble", type=str, default="", help="Custom preamble code")
        pars.add_argument("--auto_imports", type=inkex.Boolean, default=True, help="Auto import numpy/matplotlib")
        pars.add_argument("--additional_imports", type=str, default="", help="Additional import statements")
        
        # Format parameters
        pars.add_argument("--output_format", type=str, default="svg", help="Output format")
        pars.add_argument("--figure_width", type=float, default=8.0, help="Figure width in inches")
        pars.add_argument("--figure_height", type=float, default=6.0, help="Figure height in inches")
        pars.add_argument("--dpi", type=int, default=96, help="DPI (dots per inch)")
        pars.add_argument("--transparent", type=inkex.Boolean, default=False, help="Transparent background")
        pars.add_argument("--tight_layout", type=inkex.Boolean, default=True, help="Tight layout")
        
        # Style parameters
        pars.add_argument("--plot_style", type=str, default="default", help="Plot style")
        pars.add_argument("--color_map", type=str, default="viridis", help="Color map")
        pars.add_argument("--grid", type=inkex.Boolean, default=True, help="Show grid")
        pars.add_argument("--legend", type=inkex.Boolean, default=True, help="Show legend")
        pars.add_argument("--legend_position", type=str, default="best", help="Legend position")
        
        # Placement parameters
        pars.add_argument("--position_mode", type=str, default="center", help="Position mode")
        pars.add_argument("--custom_x", type=float, default=0.0, help="Custom X position")
        pars.add_argument("--custom_y", type=float, default=0.0, help="Custom Y position")
        pars.add_argument("--embed_image", type=inkex.Boolean, default=True, help="Embed image")
        pars.add_argument("--scale_factor", type=float, default=1.0, help="Scale factor for output")
        
        # Advanced parameters
        pars.add_argument("--font_family", type=str, default="sans-serif", help="Font family")
        pars.add_argument("--font_size", type=int, default=10, help="Font size")
        pars.add_argument("--title_size", type=int, default=14, help="Title font size")
        pars.add_argument("--label_size", type=int, default=12, help="Axis label font size")
        pars.add_argument("--line_width", type=float, default=1.5, help="Line width")
        pars.add_argument("--marker_size", type=float, default=6.0, help="Marker size")
        pars.add_argument("--use_latex", type=inkex.Boolean, default=False, help="Use LaTeX")
        pars.add_argument("--save_script", type=inkex.Boolean, default=False, help="Save script")
        pars.add_argument("--script_save_path", type=str, default="", help="Script save path")
        pars.add_argument("--keep_temp_files", type=inkex.Boolean, default=False, help="Keep temp files")
        
        # Figure creation options (NEW)
        pars.add_argument("--auto_create_figure", type=inkex.Boolean, default=True, help="Auto create figure")
        pars.add_argument("--subplot_rows", type=int, default=1, help="Subplot rows")
        pars.add_argument("--subplot_cols", type=int, default=1, help="Subplot columns")
        pars.add_argument("--share_x", type=inkex.Boolean, default=False, help="Share X axis")
        pars.add_argument("--share_y", type=inkex.Boolean, default=False, help="Share Y axis")
        
        # Data import parameters
        pars.add_argument("--use_data_file", type=inkex.Boolean, default=False, help="Use data file")
        pars.add_argument("--data_file_path", type=str, default="", help="Data file path")
        pars.add_argument("--data_format", type=str, default="csv", help="Data format")
        pars.add_argument("--csv_delimiter", type=str, default=",", help="CSV delimiter")
        pars.add_argument("--skip_header", type=inkex.Boolean, default=True, help="Skip header")
        pars.add_argument("--header_row", type=int, default=0, help="Header row number (0-indexed)")
        
        # Multi-column selection (NEW - replaces single x_column/y_column)
        pars.add_argument("--x_columns", type=str, default="0", help="X column indices (comma-separated)")
        pars.add_argument("--y_columns", type=str, default="1", help="Y column indices (comma-separated)")
        pars.add_argument("--column_names", type=str, default="", help="Column names to load (comma-separated)")
        pars.add_argument("--load_all_columns", type=inkex.Boolean, default=False, help="Load all columns")
        pars.add_argument("--date_columns", type=str, default="", help="Date column indices (comma-separated)")
        pars.add_argument("--date_format", type=str, default="%Y-%m-%d", help="Date format string")
        
        # Color/Style presets (NEW)
        pars.add_argument("--color_cycle", type=str, default="default", help="Color cycle preset")
        pars.add_argument("--background_color", type=str, default="white", help="Background color")
        pars.add_argument("--grid_style", type=str, default="--", help="Grid line style")
        pars.add_argument("--grid_alpha", type=float, default=0.3, help="Grid transparency")
        
        # Error handling (NEW)
        pars.add_argument("--error_handling", type=str, default="stop", help="Error handling mode")
        pars.add_argument("--show_warnings", type=inkex.Boolean, default=True, help="Show warnings")
        
        # Post-processing (NEW)
        pars.add_argument("--auto_despine", type=inkex.Boolean, default=False, help="Remove top/right spines")
        pars.add_argument("--constrained_layout", type=inkex.Boolean, default=False, help="Use constrained layout")
    
    def effect(self):
        """Main effect function."""
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
                error_msg = f"Python not found at '{self.options.python_path}'.\nPlease install Python or provide correct path."
                self.log(error_msg, "ERROR")
                inkex.errormsg(error_msg)
                return
            self.log("Python check passed")
            
            # Check if matplotlib is installed
            self.log("Checking matplotlib installation...")
            if not self.check_matplotlib():
                error_msg = "Matplotlib not installed.\nPlease install it using: pip install matplotlib"
                self.log(error_msg, "ERROR")
                inkex.errormsg(error_msg)
                return
            self.log("Matplotlib check passed")
            
            # Generate the script
            self.log("Generating script...")
            script_content = self.generate_script()
            
            if not script_content:
                self.log("Script generation failed", "ERROR")
                inkex.errormsg("Failed to generate script.")
                return
            
            self.log(f"Script generated ({len(script_content)} characters)")
            self.debug_var("script_content", script_content[:500] + "..." if len(script_content) > 500 else script_content)
            
            # Save script if requested
            if self.options.save_script and self.options.script_save_path:
                self.log(f"Saving script to: {self.options.script_save_path}")
                try:
                    with open(self.options.script_save_path, 'w', encoding='utf-8') as f:
                        f.write(script_content)
                    self.log("Script saved successfully")
                except Exception as e:
                    self.log(f"Failed to save script: {str(e)}", "ERROR")
                    inkex.errormsg(f"Failed to save script: {str(e)}")
            
            # Execute the script and get output file
            self.log("Executing script...")
            output_file = self.execute_script(script_content)
            
            if output_file and os.path.exists(output_file):
                self.log(f"Output file generated: {output_file}")
                self.debug_var("output_file_size", os.path.getsize(output_file))
                
                # Insert the figure into the document
                self.log("Inserting figure into document...")
                self.insert_figure(output_file)
                self.log("Figure inserted successfully")
                
                # Clean up temporary file
                if not self.options.keep_temp_files:
                    try:
                        os.remove(output_file)
                        self.log("Temporary file removed")
                    except Exception as e:
                        self.log(f"Failed to remove temp file: {str(e)}", "WARNING")
            else:
                self.log("Failed to generate figure - no output file", "ERROR")
                inkex.errormsg("Failed to generate figure.")
        
        except Exception as e:
            self.log(f"Exception occurred: {str(e)}", "ERROR")
            self.log(f"Exception type: {type(e).__name__}", "ERROR")
            import traceback
            self.log(f"Traceback:\n{traceback.format_exc()}", "ERROR")
            inkex.errormsg(f"Error: {str(e)}\n\nCheck log file: {self.log_file}")
        
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
                timeout=5
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
                timeout=5
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
    
    def get_bank_script_path(self):
        """Get the path to the selected script from the bank."""
        script_name = f"{self.options.bank_script}.py"
        script_path = os.path.join(self.script_bank_dir, self.options.bank_category, script_name)
        return script_path
    
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
            # Use inline code - decode escape sequences
            self.log("Using inline code")
            user_code = self.options.script_code
            
            # Decode literal escape sequences
            try:
                if r'\n' in user_code or '\\n' in user_code:
                    self.log("Decoding escape sequences in inline code")
                    user_code = user_code.replace('\\n', '\n')
                    user_code = user_code.replace('\\t', '\t')
                    user_code = user_code.replace('\\r', '\r')
                    user_code = user_code.replace("\\'", "'")
                    user_code = user_code.replace('\\"', '"')
                    self.log("Escape sequences decoded")
            except Exception as e:
                self.log(f"Warning: Failed to decode inline code: {str(e)}", "WARNING")
            
            self.log(f"Inline code length: {len(user_code)}")
            self.debug_var("inline_code_preview", user_code[:200])
        
        if not user_code or user_code.strip() == "":
            self.log("No code provided", "ERROR")
            inkex.errormsg("No code provided.")
            return None
        
        # Build complete script
        script_parts = []
        
        # Only add preamble if requested
        if self.options.use_preamble:
            script_parts.extend(self.generate_preamble(user_code))
        else:
            # Minimal setup without preamble
            if self.options.auto_imports:
                script_parts.append("import matplotlib")
                script_parts.append("matplotlib.use('Agg')")
                script_parts.append("import matplotlib.pyplot as plt")
                script_parts.append("import numpy as np")
                script_parts.append("import random")
                script_parts.append("import scipy")
                
            script_parts.append("")
        
        # Load data if requested (before user code)
        if self.options.use_data_file and self.options.data_file_path and os.path.exists(self.options.data_file_path):
            self.log(f"Loading data from: {self.options.data_file_path}")
            script_parts.append("# Load data")
            script_parts.append(self.generate_data_loading_code())
            script_parts.append("")
        
        # User code
        script_parts.append("# User code")
        script_parts.append(user_code)
        script_parts.append("")
        
        # Post-processing
        script_parts.extend(self.generate_postamble())
        
        return '\n'.join(script_parts)
    
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
            preamble.append(f"plt.style.use('{self.options.plot_style}')")
        
        # Configure matplotlib
        preamble.append("# Configure matplotlib")
        preamble.append(f"plt.rcParams['font.family'] = '{self.options.font_family}'")
        preamble.append(f"plt.rcParams['font.size'] = {self.options.font_size}")
        preamble.append(f"plt.rcParams['axes.titlesize'] = {self.options.title_size}")
        preamble.append(f"plt.rcParams['axes.labelsize'] = {self.options.label_size}")
        preamble.append(f"plt.rcParams['lines.linewidth'] = {self.options.line_width}")
        preamble.append(f"plt.rcParams['lines.markersize'] = {self.options.marker_size}")
        
        # Background color
        if self.options.background_color != "white":
            preamble.append(f"plt.rcParams['axes.facecolor'] = '{self.options.background_color}'")
            preamble.append(f"plt.rcParams['figure.facecolor'] = '{self.options.background_color}'")
        
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
        preamble.append("    '''Get colormap by name or default.'''")
        preamble.append(f"    return plt.cm.get_cmap(name or '{self.options.color_map}')")
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
                csv_params.append(f"parse_dates={date_indices}")
                if self.options.date_format:
                    code_lines.append(f"_date_parser = lambda x: pd.to_datetime(x, format='{self.options.date_format}')")
                    csv_params.append("date_parser=_date_parser")
            
            # Load specific columns by name if provided
            if column_names and not self.options.load_all_columns:
                csv_params.append(f"usecols={column_names}")
            
            code_lines.append(f"df = pd.read_csv({', '.join(csv_params)})")
        
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
            result = subprocess.run(
                [self.options.python_path, temp_script.name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self.debug_var("execution_returncode", result.returncode)
            self.debug_var("execution_stdout", result.stdout)
            self.debug_var("execution_stderr", result.stderr)
            
            if result.returncode == 0:
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
                
                if self.options.error_handling == "warn":
                    inkex.errormsg(f"Warning: Script had errors:\n{error_msg}")
                else:
                    inkex.errormsg(f"Script execution failed:\n{error_msg}")
                return None
        
        except subprocess.TimeoutExpired:
            self.log("Script execution timed out", "ERROR")
            inkex.errormsg("Script execution timed out (60 seconds).")
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
    
    def insert_figure(self, figure_path):
        """Insert the generated figure into the document."""
        self.log(f"Inserting figure from: {figure_path}")
        
        try:
            with open(figure_path, 'rb') as f:
                image_data = f.read()
            self.log(f"Read {len(image_data)} bytes from figure file")
        except Exception as e:
            self.log(f"Failed to read figure file: {str(e)}", "ERROR")
            inkex.errormsg(f"Failed to read figure file: {str(e)}")
            return
        
        if self.options.output_format == 'svg':
            try:
                svg_content = image_data.decode('utf-8')
                self.log("Importing SVG content directly")
                self.import_svg_content(svg_content)
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
            image_elem.set('xlink:href', f'data:{mime_type};base64,{encoded}')
            self.log(f"Embedded as {mime_type}")
        else:
            self.log(f"Linking to external file: {figure_path}")
            image_elem.set('xlink:href', figure_path)
        
        position = self.calculate_position()
        size = self.calculate_size()
        
        self.debug_var("position", position)
        self.debug_var("size", size)
        
        image_elem.set('x', str(position['x']))
        image_elem.set('y', str(position['y']))
        image_elem.set('width', str(size['width']))
        image_elem.set('height', str(size['height']))
        image_elem.set('preserveAspectRatio', 'xMidYMid meet')
        
        self.svg.get_current_layer().append(image_elem)
        self.log("Image element added to current layer")
    
    def import_svg_content(self, svg_content):
        """Import SVG content directly into the document."""
        try:
            self.log("Parsing SVG content")
            root = etree.fromstring(svg_content.encode('utf-8'))
            
            group = Group()
            group.set('id', self.svg.get_unique_id('matplotlib-svg'))
            
            position = self.calculate_position()
            scale = self.options.scale_factor
            self.debug_var("svg_import_position", position)
            self.debug_var("scale_factor", scale)
            
            if scale != 1.0:
                group.set('transform', f'translate({position["x"]}, {position["y"]}) scale({scale})')
            else:
                group.set('transform', f'translate({position["x"]}, {position["y"]})')
            
            elem_count = 0
            for elem in root:
                group.append(elem)
                elem_count += 1
            
            self.log(f"Imported {elem_count} elements from SVG")
            
            self.svg.get_current_layer().append(group)
            self.log("SVG group added to current layer")
        
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
        
        if self.options.position_mode == 'cursor' and self.svg.selection:
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
        """Calculate image size in document units."""
        width_px = self.options.figure_width * self.options.dpi * self.options.scale_factor
        height_px = self.options.figure_height * self.options.dpi * self.options.scale_factor
        
        width = self.svg.unittouu(f'{width_px}px')
        height = self.svg.unittouu(f'{height_px}px')
        
        self.log(f"Figure size: {self.options.figure_width}\" x {self.options.figure_height}\" @ {self.options.dpi} DPI (scale: {self.options.scale_factor})")
        self.log(f"Pixel size: {width_px} x {height_px} px")
        self.log(f"Document units: {width} x {height}")
        
        return {'width': width, 'height': height}


if __name__ == '__main__':
    MatplotlibGenerator().run()