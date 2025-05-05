#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Multi-panel Figure Generation for SciTex

This script demonstrates more sophisticated techniques for creating
multi-panel figures with custom layouts, shared axes, and annotations.
It shows how to create complex scientific figures programmatically
and integrate them into the SciTex workflow.

Usage:
  python advanced_multipanel_figure.py [--id XX] [--name NAME] [--outdir DIR]

Examples:
  python advanced_multipanel_figure.py --id 05 --name complex_analysis
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate an advanced multi-panel figure for SciTex')
    parser.add_argument('--id', type=str, help='Figure ID number (e.g., 01, 02)')
    parser.add_argument('--name', type=str, default='advanced_multipanel', help='Descriptive name for the figure')
    parser.add_argument('--outdir', type=str, default='manuscript/src/figures/src', 
                      help='Output directory for the figure')
    parser.add_argument('--style', type=str, default='science', choices=['default', 'science', 'nature', 'ieee'],
                      help='Plot style to use')
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

def set_plot_style(style_name):
    """Set the plot style based on the selected style name."""
    if style_name == 'science':
        plt.style.use(['science', 'ieee'])
    elif style_name == 'nature':
        plt.style.use(['science', 'nature'])
    elif style_name == 'ieee':
        plt.style.use(['science', 'ieee'])
    else:
        plt.style.use('default')

def create_sample_data():
    """Create sample datasets for the figure panels."""
    # Time series data (Panel A)
    np.random.seed(42)
    days = np.arange(0, 60)
    temp = 20 + 5 * np.sin(2 * np.pi * days / 30) + np.random.normal(0, 1, size=len(days))
    
    # Correlation data (Panel B)
    x = np.random.normal(0, 1, 100)
    y = 0.8 * x + np.random.normal(0, 0.5, 100)
    
    # Comparison data (Panel C)
    categories = ['Method A', 'Method B', 'Method C', 'Method D']
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    results = np.random.rand(len(categories), len(metrics)) * 30 + 60  # Values between 60-90
    
    # Distribution data (Panel D and E)
    group1 = np.random.normal(0, 1, 1000)
    group2 = np.random.normal(0.5, 1.2, 1000)
    group3 = np.random.normal(-0.5, 0.8, 1000)
    
    # 2D data for heatmap (Panel F)
    x_grid, y_grid = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
    z = np.exp(-(x_grid**2 + y_grid**2) / 2) * np.cos(x_grid * 3)
    
    return {
        'time_series': (days, temp),
        'correlation': (x, y),
        'comparison': (categories, metrics, results),
        'distributions': (group1, group2, group3),
        'heatmap': (x_grid, y_grid, z)
    }

def create_advanced_multipanel_figure(fig_id, name, outdir, style='default'):
    """
    Create an advanced multi-panel figure with custom layout and shared axes.
    
    Parameters:
        fig_id (str): The figure ID (e.g., '01', '02')
        name (str): Descriptive name for the figure
        outdir (str): Output directory
        style (str): Plot style to use
    
    Returns:
        tuple: Paths to the created image and caption files
    """
    # Set the selected plot style
    set_plot_style(style)
    
    # Create sample data for all panels
    data = create_sample_data()
    
    # Create figure with custom grid layout
    fig = plt.figure(figsize=(12, 10))
    
    # Create complex grid layout
    gs = gridspec.GridSpec(3, 3, figure=fig, width_ratios=[1, 1, 1], height_ratios=[1, 1, 1],
                          hspace=0.3, wspace=0.3)
    
    # Panel A: Time series plot (spanning 2 columns)
    ax_a = fig.add_subplot(gs[0, :2])
    days, temp = data['time_series']
    ax_a.plot(days, temp, 'o-', color='royalblue', alpha=0.7, markersize=4)
    ax_a.set_xlabel('Day')
    ax_a.set_ylabel('Temperature (°C)')
    ax_a.grid(True, linestyle='--', alpha=0.3)
    ax_a.set_title('A', fontweight='bold', loc='left', fontsize=14)
    
    # Add a highlighted region
    ax_a.axvspan(10, 20, alpha=0.2, color='red')
    ax_a.annotate('Anomaly', xy=(15, temp[15]), xytext=(15, temp[15]+3),
                 arrowprops=dict(arrowstyle='->', lw=1.5, color='red'),
                 ha='center', va='bottom', fontsize=10)
    
    # Panel B: Scatter plot with regression
    ax_b = fig.add_subplot(gs[0, 2])
    x, y = data['correlation']
    ax_b.scatter(x, y, color='forestgreen', alpha=0.7)
    
    # Add regression line
    coef = np.polyfit(x, y, 1)
    poly1d_fn = np.poly1d(coef)
    x_range = np.linspace(min(x), max(x), 100)
    ax_b.plot(x_range, poly1d_fn(x_range), 'r--', lw=2)
    
    # Add correlation coefficient annotation
    r = np.corrcoef(x, y)[0, 1]
    ax_b.annotate(f'r = {r:.2f}', xy=(0.05, 0.95), xycoords='axes fraction',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
                 ha='left', va='top', fontsize=10)
    
    ax_b.set_xlabel('Variable X')
    ax_b.set_ylabel('Variable Y')
    ax_b.set_title('B', fontweight='bold', loc='left', fontsize=14)
    
    # Panel C: Heatmap (comparison)
    ax_c = fig.add_subplot(gs[1, :2])
    categories, metrics, results = data['comparison']
    im = ax_c.imshow(results, cmap='YlGnBu', aspect='auto')
    
    # Add text annotations to heatmap
    for i in range(len(categories)):
        for j in range(len(metrics)):
            ax_c.text(j, i, f'{results[i, j]:.1f}', ha="center", va="center", color="black")
    
    # Set tick labels
    ax_c.set_xticks(np.arange(len(metrics)))
    ax_c.set_yticks(np.arange(len(categories)))
    ax_c.set_xticklabels(metrics)
    ax_c.set_yticklabels(categories)
    plt.setp(ax_c.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax_c, shrink=0.7)
    cbar.set_label('Value (%)')
    
    ax_c.set_title('C', fontweight='bold', loc='left', fontsize=14)
    
    # Panel D: Histogram (spanning 1 column)
    ax_d = fig.add_subplot(gs[1, 2])
    group1, group2, group3 = data['distributions']
    
    # Create histogram with KDE curve
    bins = np.linspace(-3, 3, 30)
    ax_d.hist(group1, bins=bins, alpha=0.3, color='blue', label='Group 1', density=True)
    ax_d.hist(group2, bins=bins, alpha=0.3, color='red', label='Group 2', density=True)
    
    # Add KDE curves
    from scipy.stats import gaussian_kde
    x_range = np.linspace(-4, 4, 1000)
    
    kde1 = gaussian_kde(group1)
    ax_d.plot(x_range, kde1(x_range), 'b-', lw=2)
    
    kde2 = gaussian_kde(group2)
    ax_d.plot(x_range, kde2(x_range), 'r-', lw=2)
    
    ax_d.set_xlabel('Value')
    ax_d.set_ylabel('Density')
    ax_d.legend(frameon=True, loc='upper left')
    ax_d.set_title('D', fontweight='bold', loc='left', fontsize=14)
    
    # Panel E: Box plots with individual points
    ax_e = fig.add_subplot(gs[2, 0])
    data_to_plot = [group1, group2, group3]
    labels = ['Group 1', 'Group 2', 'Group 3']
    
    # Create boxplots
    box = ax_e.boxplot(data_to_plot, patch_artist=True, labels=labels)
    
    # Customize boxplot colors
    colors = ['lightblue', 'lightgreen', 'lightsalmon']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    
    # Add individual points with jitter
    for i, data_group in enumerate(data_to_plot):
        # Add jitter to x position
        x = np.random.normal(i+1, 0.04, size=len(data_group))
        ax_e.scatter(x, data_group, s=10, alpha=0.3, color='darkblue')
    
    ax_e.set_ylabel('Value')
    ax_e.set_title('E', fontweight='bold', loc='left', fontsize=14)
    
    # Panel F: Contour plot with custom colormap
    ax_f = fig.add_subplot(gs[2, 1:])
    x_grid, y_grid, z = data['heatmap']
    
    # Create custom colormap
    colors = [(0, 'darkblue'), (0.5, 'white'), (1, 'darkred')]
    cmap_name = 'BlueWhiteRed'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=100)
    
    # Create filled contour plot
    levels = np.linspace(-1, 1, 20)
    cf = ax_f.contourf(x_grid, y_grid, z, levels=levels, cmap=cm)
    
    # Add contour lines
    cont = ax_f.contour(x_grid, y_grid, z, levels=np.linspace(-0.8, 0.8, 9), colors='black', alpha=0.5, linewidths=0.5)
    ax_f.clabel(cont, inline=True, fontsize=8, fmt='%.1f')
    
    # Add colorbar
    cbar = plt.colorbar(cf, ax=ax_f, shrink=0.7)
    cbar.set_label('Value')
    
    ax_f.set_xlabel('X coordinate')
    ax_f.set_ylabel('Y coordinate')
    ax_f.set_title('F', fontweight='bold', loc='left', fontsize=14)
    
    # Add overall figure title
    # fig.suptitle('Advanced Multi-panel Figure Example', fontsize=16, fontweight='bold')
    
    # Ensure output directory exists
    os.makedirs(outdir, exist_ok=True)
    
    # Create filename following SciTex naming convention
    filename = f'Figure_ID_{fig_id}_{name}'
    img_path = os.path.join(outdir, f'{filename}.png')
    caption_path = os.path.join(outdir, f'{filename}.tex')
    
    # Save the figure as a high-resolution PNG
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {img_path}")
    
    # Create caption file with a structured format for multi-panel figures
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(caption_path, 'w') as f:
        f.write(f"%% -*- coding: utf-8 -*-\n")
        f.write(f"%% Timestamp: \"{timestamp} (auto-generated)\"\n")
        f.write(f"%% File: {os.path.basename(caption_path)}\n\n")
        f.write("\\caption{\\textbf{\n")
        f.write("Advanced Programmatically Generated Multi-panel Scientific Figure\n")
        f.write("}\n")
        f.write("\\smallskip\n")
        f.write("\\\\\n")
        f.write("This figure demonstrates advanced multi-panel visualization techniques for scientific data analysis. ")
        f.write("\\textbf{\\textit{A.}} Time series of temperature measurements over 60 days showing seasonal variation with a highlighted anomaly region (red). ")
        f.write("\\textbf{\\textit{B.}} Correlation analysis between variables X and Y with regression line (r = 0.80). ")
        f.write("\\textbf{\\textit{C.}} Performance comparison heatmap showing multiple metrics across different methodologies. ")
        f.write("\\textbf{\\textit{D.}} Distribution analysis of two experimental groups with kernel density estimation curves. ")
        f.write("\\textbf{\\textit{E.}} Box plots with individual data points showing the distribution of three groups with different statistical properties. ")
        f.write("\\textbf{\\textit{F.}} Contour visualization of a 2D function with labeled isolines demonstrating spatial patterns in the data.\n")
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
    img_path, caption_path = create_advanced_multipanel_figure(fig_id, args.name, outdir, args.style)
    
    print("\nAdvanced multi-panel figure generation complete!")
    print(f"You can reference this figure in your LaTeX document using: Figure~\\ref{{fig:{fig_id}}}")
    print("\nTo compile the manuscript with this figure:")
    print("./compile -m --figs")

if __name__ == "__main__":
    main()