#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 20:45:00 (ywatanabe)"
# File: using_tikz_figures.py

__file__ = "using_tikz_figures.py"

"""This script demonstrates how to create and use TikZ-based vector figures in SciTex.

Dependencies:
  - scripts:
    - ../manuscript/compile

  - packages:
    - None (uses standard libraries only)

  - input:
    - None

  - output:
    - /manuscript/src/figures/src/Figure_ID_XX_tikz_example.tex
"""

"""Imports"""
import os
import sys
from pathlib import Path
import argparse
import shutil

"""Functions & Classes"""
def create_tikz_figure(target_path, figure_number="06", figure_name="tikz_example"):
    """Create a TikZ figure file for demonstration.
    
    Parameters
    ----------
    target_path : str
        Path to save the figure file
    figure_number : str
        Two-digit figure number
    figure_name : str
        Descriptive name for the figure
    
    Returns
    -------
    str
        Path to the created file
    """
    filename = f"Figure_ID_{figure_number}_{figure_name}.tex"
    filepath = os.path.join(target_path, filename)
    
    # Create the figure content with TikZ code
    tikz_content = r'''%% -*- coding: utf-8 -*-
%% Timestamp: "2025-05-05 20:45:00 (ywatanabe)"
%% File: "Figure_ID_''' + figure_number + '_' + figure_name + r'''.tex"

% This is a TikZ-based figure that doesn't require an external image file
% It demonstrates how to create vector graphics directly in LaTeX

\begin{tikzpicture}[
    block/.style={rectangle, draw, fill=blue!20, 
                 text width=2.5cm, text centered, rounded corners, minimum height=1.5cm},
    line/.style={draw, -latex', thick},
    cloud/.style={draw, ellipse, fill=red!20, minimum height=1cm, text width=2.5cm, text centered}
]

% Place blocks in diagram
\node [block] (src) {Source Files};
\node [block, right=of src] (process) {Processing};
\node [block, right=of process] (compile) {Compilation};
\node [cloud, below=of process] (output) {Output PDF};

% Define shapes for figure types
\node [draw, rectangle, below left=of process, fill=green!10] (figures) {Figures};
\node [draw, rectangle, below right=of process, fill=yellow!10] (tables) {Tables};

% Connect blocks with arrows
\path [line] (src) -- (process);
\path [line] (process) -- (compile);
\path [line] (compile) -- (output);
\path [line] (figures) -- (process);
\path [line] (tables) -- (process);

\end{tikzpicture}

\caption{\textbf{
SciTex TikZ Diagram Example
}
\smallskip
\\
This figure demonstrates a vector-based diagram created directly with TikZ in LaTeX without requiring an external image file. It shows the workflow of SciTex, including how source files are processed and compiled into the final PDF output. The figure also illustrates how figures and tables feed into the processing pipeline.
}
% width=0.9\textwidth

%%%% EOF'''
    
    # Write the file
    with open(filepath, 'w') as f:
        f.write(tikz_content)
    
    return filepath


def main(args):
    """
    Create an example TikZ figure and place it in the manuscript template.
    """
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    figures_dir = os.path.join(repo_root, "manuscript", "src", "figures", "src")
    
    # Create template directory if it doesn't exist
    if not os.path.exists(figures_dir):
        print(f"Warning: Directory not found: {figures_dir}")
        print("Please ensure you're running this from the SciTex repository root.")
        return 1
    
    # Create the TikZ figure
    tikz_file = create_tikz_figure(figures_dir, 
                                  figure_number=args.figure_number, 
                                  figure_name=args.figure_name)
    
    print(f"Created TikZ figure: {tikz_file}")
    print("\nTo compile the manuscript with this figure, run:")
    print("./compile -m --figs")
    print("\nIn your LaTeX file, you can reference this figure with:")
    print(f"Figure~\\ref{{fig:{args.figure_number}}}")
    
    # Also create a copy in the examples directory for reference
    example_dir = os.path.join(repo_root, "examples", "manuscript_template", "src", "figures", "src")
    if os.path.exists(example_dir):
        example_file = os.path.join(example_dir, os.path.basename(tikz_file))
        shutil.copy(tikz_file, example_file)
        print(f"\nAlso created example file: {example_file}")
    
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create an example TikZ figure for SciTex')
    parser.add_argument(
        "--figure-number",
        type=str,
        default="06",
        help="Two-digit figure number (default: %(default)s)",
    )
    parser.add_argument(
        "--figure-name",
        type=str,
        default="tikz_example",
        help="Descriptive name for the figure (default: %(default)s)",
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Run the main function with parsed arguments."""
    args = parse_args()
    exit_status = main(args)
    sys.exit(exit_status)


if __name__ == '__main__':
    run_main()

# EOF