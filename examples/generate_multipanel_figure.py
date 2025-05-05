#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-panel Figure Generation Template for SciTex

This script demonstrates how to programmatically create multi-panel figures
using matplotlib and save them in the correct SciTex format. It also
generates the corresponding caption file with proper formatting.

Usage:
  python generate_multipanel_figure.py [--id XX] [--name NAME] [--outdir DIR]

Options:
  --id XX     Figure ID number (default: next available)
  --name NAME Descriptive name for the figure (default: 'multipanel')
  --outdir DIR Output directory (default: manuscript/src/figures/src)
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a multi-panel figure for SciTex')
    parser.add_argument('--id', type=str, help='Figure ID number (e.g., 01, 02)')
    parser.add_argument('--name', type=str, default='multipanel', help='Descriptive name for the figure')
    parser.add_argument('--outdir', type=str, default='manuscript/src/figures/src', 
                      help='Output directory for the figure')
    return parser.parse_args()

def find_next_figure_id(outdir):
    """Find the next available figure ID."""
    existing_ids = []
    if os.path.exists(outdir):
        for filename in os.listdir(outdir):
            if filename.startswith('Figure_ID_') and (filename.endswith('.png') or filename.endswith('.jpg')):
                try:
                    fig_id = int(filename.split('_')[2])
                    existing_ids.append(fig_id)
                except (IndexError, ValueError):
                    continue
    
    if not existing_ids:
        return '01'
    
    next_id = max(existing_ids) + 1
    return f'{next_id:02d}'

def create_multipanel_figure(fig_id, name, outdir):
    """
    Create a multi-panel figure with four panels arranged in a 2x2 grid.
    
    Parameters:
        fig_id (str): The figure ID (e.g., '01', '02')
        name (str): Descriptive name for the figure
        outdir (str): Output directory
    
    Returns:
        tuple: Paths to the created image and caption files
    """
    # Create figure with a 2x2 grid layout
    fig = plt.figure(figsize=(10, 8))
    gs = GridSpec(2, 2, figure=fig, wspace=0.3, hspace=0.3)
    
    # Panel A: Line plot
    ax1 = fig.add_subplot(gs[0, 0])
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax1.plot(x, y, '-b', linewidth=2)
    ax1.set_xlabel('X Axis')
    ax1.set_ylabel('Y Axis')
    ax1.set_title('A', fontweight='bold', loc='left', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Panel B: Scatter plot
    ax2 = fig.add_subplot(gs[0, 1])
    n = 50
    x = np.random.rand(n)
    y = np.random.rand(n)
    colors = np.random.rand(n)
    sizes = 1000 * np.random.rand(n)
    ax2.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
    ax2.set_xlabel('X Axis')
    ax2.set_ylabel('Y Axis')
    ax2.set_title('B', fontweight='bold', loc='left', fontsize=14)
    
    # Panel C: Bar chart
    ax3 = fig.add_subplot(gs[1, 0])
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    values = [25, 40, 30, 55]
    bars = ax3.bar(categories, values, color='skyblue', edgecolor='navy')
    ax3.set_xlabel('Categories')
    ax3.set_ylabel('Values')
    ax3.set_title('C', fontweight='bold', loc='left', fontsize=14)
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}', ha='center', va='bottom')
    
    # Panel D: Heatmap
    ax4 = fig.add_subplot(gs[1, 1])
    data = np.random.rand(10, 10)
    im = ax4.imshow(data, cmap='coolwarm')
    plt.colorbar(im, ax=ax4, shrink=0.7)
    ax4.set_title('D', fontweight='bold', loc='left', fontsize=14)
    ax4.set_xticks(np.arange(10))
    ax4.set_yticks(np.arange(10))
    
    # Set overall figure title (optional)
    # fig.suptitle(f'Multi-panel Figure Example', fontsize=16, fontweight='bold')
    
    # Create filename following SciTex naming convention
    filename = f'Figure_ID_{fig_id}_{name}'
    img_path = os.path.join(outdir, f'{filename}.png')
    caption_path = os.path.join(outdir, f'{filename}.tex')
    
    # Ensure output directory exists
    os.makedirs(outdir, exist_ok=True)
    
    # Save the figure as a high-resolution PNG
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {img_path}")
    
    # Create caption file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(caption_path, 'w') as f:
        f.write(f"%% -*- coding: utf-8 -*-\n")
        f.write(f"%% Timestamp: \"{timestamp} (auto-generated)\"\n")
        f.write(f"%% File: {os.path.basename(caption_path)}\n\n")
        f.write("\\caption{\\textbf{\n")
        f.write("Programmatically Generated Multi-panel Figure\n")
        f.write("}\n")
        f.write("\\smallskip\n")
        f.write("\\\\\n")
        f.write("This multi-panel figure was generated programmatically using matplotlib. ")
        f.write("\\textbf{\\textit{A.}} Sine wave plotted as a function of x. ")
        f.write("\\textbf{\\textit{B.}} Scatter plot with points colored by value and sized by magnitude. ")
        f.write("\\textbf{\\textit{C.}} Bar chart showing values across four categories with labels. ")
        f.write("\\textbf{\\textit{D.}} Heatmap visualization of a 10×10 random matrix with colorbar.\n")
        f.write("}\n")
        f.write("% width=1\\textwidth\n\n")
        f.write("%%%% EOF\n")
    
    print(f"Caption file saved to: {caption_path}")
    
    plt.close(fig)
    return img_path, caption_path

def main():
    """Main function."""
    args = parse_arguments()
    
    # Determine the output directory
    outdir = os.path.abspath(args.outdir)
    
    # Determine the figure ID (either from command line or next available)
    fig_id = args.id if args.id else find_next_figure_id(outdir)
    
    # Create the figure
    img_path, caption_path = create_multipanel_figure(fig_id, args.name, outdir)
    
    print("\nFigure generation complete!")
    print(f"You can reference this figure in your LaTeX document using: Figure~\\ref{{fig:{fig_id}}}")
    print("\nTo compile the manuscript with this figure:")
    print("./compile -m --figs")

if __name__ == "__main__":
    main()