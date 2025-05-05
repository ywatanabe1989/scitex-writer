#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multipanel_helper.py - Helper functions for creating multi-panel figures in SciTex

This module provides utility functions for working with multi-panel figures, including:
- Creating panel labels with consistent formatting
- Generating caption files with proper structure
- Arranging panels in various layouts

Usage:
    import multipanel_helper as mph
    
    # Create panel labels
    fig, ax = plt.subplots()
    mph.add_panel_label(ax, 'A', position='northwest')
    
    # Generate a caption template
    mph.generate_caption_template('Figure_ID_05_analysis.tex', 
                                  title='Analysis of experimental results',
                                  panels=['A', 'B', 'C', 'D'],
                                  descriptions=['Panel A shows...', 'Panel B illustrates...'])
"""

import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime
import numpy as np

def add_panel_label(ax, label, position='northwest', format_style='bold', 
                   fontsize=14, padding=0.05, box=False, color='black'):
    """
    Add a panel label (A, B, C, etc.) to a matplotlib axis.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis to add the label to
    label : str
        The label text (e.g. 'A', 'B', 'C')
    position : str
        Position of the label: 'northwest' (default), 'northeast', 
        'southwest', 'southeast', or 'center'
    format_style : str
        Style of the label: 'bold' (default), 'italic', 'bold-italic', 
        'parentheses', 'bold-parentheses'
    fontsize : int
        Font size for the label (default: 14)
    padding : float
        Padding from the axis edge as fraction of axis size (default: 0.05)
    box : bool
        Whether to add a background box to the label (default: False)
    color : str
        Color of the label text (default: 'black')
        
    Returns
    -------
    text : matplotlib.text.Text
        The created text object
    """
    # Format the label based on style
    if format_style == 'bold':
        formatted_label = label
        weight = 'bold'
        style = 'normal'
    elif format_style == 'italic':
        formatted_label = label
        weight = 'normal'
        style = 'italic'
    elif format_style == 'bold-italic':
        formatted_label = label
        weight = 'bold'
        style = 'italic'
    elif format_style == 'parentheses':
        formatted_label = f'({label})'
        weight = 'normal'
        style = 'normal'
    elif format_style == 'bold-parentheses':
        formatted_label = f'({label})'
        weight = 'bold'
        style = 'normal'
    else:
        formatted_label = label
        weight = 'bold'
        style = 'normal'
    
    # Set position coordinates
    if position == 'northwest':
        x, y = padding, 1 - padding
        ha, va = 'left', 'top'
    elif position == 'northeast':
        x, y = 1 - padding, 1 - padding
        ha, va = 'right', 'top'
    elif position == 'southwest':
        x, y = padding, padding
        ha, va = 'left', 'bottom'
    elif position == 'southeast':
        x, y = 1 - padding, padding
        ha, va = 'right', 'bottom'
    elif position == 'center':
        x, y = 0.5, 0.5
        ha, va = 'center', 'center'
    else:
        x, y = padding, 1 - padding
        ha, va = 'left', 'top'
    
    # Create the text with properties
    text = ax.text(
        x, y, formatted_label,
        transform=ax.transAxes,
        ha=ha, va=va,
        fontsize=fontsize,
        fontweight=weight,
        fontstyle=style,
        color=color,
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2) if box else None
    )
    
    return text

def create_multi_panel_layout(nrows, ncols, figsize=None, width_ratios=None, 
                             height_ratios=None, panel_labels=None, label_position='northwest',
                             wspace=0.3, hspace=0.3):
    """
    Create a multi-panel figure with a grid layout.
    
    Parameters
    ----------
    nrows : int
        Number of rows in the grid
    ncols : int
        Number of columns in the grid
    figsize : tuple
        Figure size (width, height) in inches (default: auto calculated)
    width_ratios : list
        Relative widths of columns (default: equal widths)
    height_ratios : list
        Relative heights of rows (default: equal heights)
    panel_labels : list
        List of panel labels (e.g., ['A', 'B', 'C', 'D']) (default: None)
    label_position : str
        Position of panel labels (default: 'northwest')
    wspace : float
        Width spacing between panels (default: 0.3)
    hspace : float
        Height spacing between panels (default: 0.3)
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    axes : list
        List of axis objects for each panel
    """
    # Auto-calculate figure size if not provided
    if figsize is None:
        width = 4 * ncols
        height = 4 * nrows
        figsize = (width, height)
    
    # Create figure and grid
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(
        nrows, ncols, 
        width_ratios=width_ratios if width_ratios else [1] * ncols,
        height_ratios=height_ratios if height_ratios else [1] * nrows,
        wspace=wspace, hspace=hspace
    )
    
    # Create axes for each panel
    axes = []
    for i in range(nrows):
        for j in range(ncols):
            ax = fig.add_subplot(gs[i, j])
            axes.append(ax)
            
            # Add panel label if provided
            if panel_labels and i*ncols + j < len(panel_labels):
                add_panel_label(ax, panel_labels[i*ncols + j], position=label_position)
    
    return fig, axes

def create_irregular_layout(panel_specs, figsize=(10, 8), panel_labels=None, label_position='northwest'):
    """
    Create a figure with an irregular layout of panels.
    
    Parameters
    ----------
    panel_specs : list of dicts
        List of dictionaries defining panel positions and spans:
        [{'position': (row, col), 'span': (rowspan, colspan)}, ...]
    figsize : tuple
        Figure size (width, height) in inches (default: (10, 8))
    panel_labels : list
        List of panel labels (e.g., ['A', 'B', 'C']) (default: None)
    label_position : str
        Position of panel labels (default: 'northwest')
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    axes : list
        List of axis objects for each panel
    """
    # Calculate grid dimensions
    max_row = max(spec['position'][0] + spec['span'][0] for spec in panel_specs)
    max_col = max(spec['position'][1] + spec['span'][1] for spec in panel_specs)
    
    # Create figure and grid
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(max_row, max_col, figure=fig)
    
    # Create axes for each panel
    axes = []
    for i, spec in enumerate(panel_specs):
        row, col = spec['position']
        rowspan, colspan = spec['span']
        
        if rowspan == 1 and colspan == 1:
            ax = fig.add_subplot(gs[row, col])
        else:
            ax = fig.add_subplot(gs[row:row+rowspan, col:col+colspan])
        
        axes.append(ax)
        
        # Add panel label if provided
        if panel_labels and i < len(panel_labels):
            add_panel_label(ax, panel_labels[i], position=label_position)
    
    return fig, axes

def generate_caption_template(output_file, title=None, panels=None, descriptions=None, width='1\\textwidth'):
    """
    Generate a caption template file for a multi-panel figure.
    
    Parameters
    ----------
    output_file : str
        Path to the output caption file
    title : str
        Title of the figure (default: "Multi-panel figure")
    panels : list
        List of panel labels (e.g., ['A', 'B', 'C']) (default: ['A', 'B', 'C', 'D'])
    descriptions : list
        List of panel descriptions (default: placeholders)
    width : str
        Width specification for the figure (default: '1\\textwidth')
        
    Returns
    -------
    None
    """
    # Set defaults
    if title is None:
        title = "Multi-panel figure"
    
    if panels is None:
        panels = ['A', 'B', 'C', 'D']
    
    if descriptions is None:
        descriptions = [f"Description of panel {p}." for p in panels]
    
    # Ensure same number of descriptions as panels
    if len(descriptions) < len(panels):
        descriptions.extend([f"Description of panel {p}." for p in panels[len(descriptions):]])
    
    # Create panel description strings
    panel_descriptions = ""
    for i, (panel, desc) in enumerate(zip(panels, descriptions)):
        panel_descriptions += f"\\textbf{{\\textit{{{panel}.}}}} {desc} "
        if i < len(panels) - 1:
            panel_descriptions += ""
    
    # Panel layout info
    nrows = int(np.ceil(len(panels) / 2))
    ncols = min(2, len(panels))
    panel_layout = f"{nrows}x{ncols}"
    
    # Create caption content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption_content = f"%% -*- coding: utf-8 -*-\n"
    caption_content += f"%% Timestamp: \"{timestamp}\" (auto-generated)\n"
    caption_content += f"%% File: {os.path.basename(output_file)}\n\n"
    caption_content += "%% MULTI-PANEL FIGURE CAPTION\n"
    caption_content += "%% =========================\n"
    caption_content += f"%% width={width}\n"
    caption_content += f"%% panel_labels={','.join(panels)}\n"
    caption_content += f"%% panel_layout={panel_layout}\n"
    caption_content += "%% panel_spacing=0.3em\n\n"
    caption_content += "\\caption{\\textbf{\n"
    caption_content += f"{title}\n"
    caption_content += "}\n"
    caption_content += "\\smallskip\n"
    caption_content += "\\\\\n"
    caption_content += f"{panel_descriptions}\n"
    caption_content += "}\n\n"
    caption_content += "%%%% EOF"
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(caption_content)
    
    print(f"Caption template saved to: {output_file}")

def share_axes(axes, share_x=False, share_y=False):
    """
    Configure shared axes for multiple panels.
    
    Parameters
    ----------
    axes : list
        List of matplotlib axes objects
    share_x : bool
        Whether to share x-axes (default: False)
    share_y : bool
        Whether to share y-axes (default: False)
        
    Returns
    -------
    None
    """
    if not axes:
        return
    
    if share_x:
        for ax in axes[1:]:
            ax.sharex(axes[0])
        # Remove x tick labels except for bottom row
        for ax in axes[:-1]:
            plt.setp(ax.get_xticklabels(), visible=False)
    
    if share_y:
        for ax in axes[1:]:
            ax.sharey(axes[0])
        # Remove y tick labels except for leftmost column
        for i, ax in enumerate(axes):
            if i % 2 != 0:  # Assuming 2 columns
                plt.setp(ax.get_yticklabels(), visible=False)

def demo():
    """
    Demonstrate the functionality of the multipanel_helper module.
    """
    # Create a 2x2 grid layout with default options
    fig, axes = create_multi_panel_layout(2, 2, panel_labels=['A', 'B', 'C', 'D'])
    
    # Create some sample plots
    x = np.linspace(0, 10, 100)
    
    # Panel A: Line plot
    axes[0].plot(x, np.sin(x), 'b-', linewidth=2)
    axes[0].set_xlabel('X')
    axes[0].set_ylabel('sin(x)')
    axes[0].grid(True, alpha=0.3)
    
    # Panel B: Scatter plot
    axes[1].scatter(np.random.rand(30), np.random.rand(30), 
                    s=100*np.random.rand(30), c=np.random.rand(30), 
                    alpha=0.7, cmap='viridis')
    axes[1].set_xlabel('X')
    axes[1].set_ylabel('Y')
    
    # Panel C: Bar chart
    categories = ['A', 'B', 'C', 'D']
    values = [3, 7, 2, 5]
    axes[2].bar(categories, values, color='skyblue', edgecolor='navy')
    axes[2].set_xlabel('Category')
    axes[2].set_ylabel('Value')
    
    # Panel D: Histogram
    data = np.random.normal(0, 1, 1000)
    axes[3].hist(data, bins=30, alpha=0.7, color='green')
    axes[3].set_xlabel('Value')
    axes[3].set_ylabel('Frequency')
    
    # Add a title (optional)
    fig.suptitle('Multi-panel Figure Example', fontsize=16)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, 'multipanel_demo.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    # Generate caption template
    caption_file = os.path.splitext(output_file)[0] + '.tex'
    generate_caption_template(
        caption_file,
        title="Demonstration of multipanel_helper module capabilities",
        panels=['A', 'B', 'C', 'D'],
        descriptions=[
            "Line plot showing a sine wave.",
            "Scatter plot with points sized and colored by value.",
            "Bar chart comparing values across categories.",
            "Histogram showing the distribution of normally distributed data."
        ]
    )
    
    print(f"Demonstration figure saved to: {output_file}")
    return fig, axes

if __name__ == "__main__":
    demo()