#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 20:55:00 (ywatanabe)"
# File: figure_workflow.py

__file__ = "figure_workflow.py"

"""This script demonstrates a complete workflow for figure management in SciTex.

Dependencies:
  - scripts:
    - None

  - packages:
    - pillow (PIL)
    - matplotlib

  - input:
    - None

  - output:
    - /manuscript/src/figures/src/Figure_ID_XX_generated.png
    - /manuscript/src/figures/src/Figure_ID_XX_generated.tex
"""

"""Imports"""
import os
import sys
import argparse
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

"""Functions & Classes"""
def create_sample_figure(figure_number, save_dir):
    """Create a sample matplotlib figure and save it.
    
    Parameters
    ----------
    figure_number : str
        Two-digit figure number
    save_dir : str
        Directory to save the figure
        
    Returns
    -------
    tuple
        (png_path, tex_path) - Paths to the created files
    """
    # Create a matplotlib figure
    plt.figure(figsize=(10, 6))
    
    # Create some sample data
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    values1 = [15, 30, 45, 10]
    values2 = [30, 25, 15, 20]
    
    # Plot data
    x = np.arange(len(categories))
    width = 0.35
    
    plt.bar(x - width/2, values1, width, label='Method 1')
    plt.bar(x + width/2, values2, width, label='Method 2')
    
    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.title('Sample SciTex Figure')
    plt.xticks(x, categories)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Save the figure
    basename = f"Figure_ID_{figure_number}_generated"
    png_path = os.path.join(save_dir, f"{basename}.png")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create caption tex file
    tex_path = os.path.join(save_dir, f"{basename}.tex")
    caption = f"""
\\caption{{\\textbf{{
Sample figure generated with matplotlib
}}
\\smallskip
\\\\
This figure demonstrates how to programmatically generate figures for SciTex using
matplotlib. The chart shows a comparison between Method 1 and Method 2 across four
categories, highlighting the effectiveness of Method 1 in Category C and Method 2
in Category A. This automated approach ensures consistent figure formatting and style.
}}
% width=0.9\\textwidth
"""
    
    with open(tex_path, 'w') as f:
        f.write(f"%% -*- coding: utf-8 -*-\n")
        f.write(f"%% Timestamp: \"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\" (ywatanabe)\n")
        f.write(f"%% File: \"{basename}.tex\"\n\n")
        f.write(caption)
        f.write("\n%%%% EOF")
    
    return png_path, tex_path


def create_multipanel_figure(figure_number, save_dir):
    """Create a multi-panel figure demonstration.
    
    Parameters
    ----------
    figure_number : str
        Two-digit figure number
    save_dir : str
        Directory to save the figure
        
    Returns
    -------
    tuple
        (png_path, tex_path) - Paths to the created files
    """
    # Create a blank image
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Load a default font
    try:
        font = ImageFont.truetype("Arial", 20)
        title_font = ImageFont.truetype("Arial", 24)
    except:
        # Fall back to default font if Arial not available
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw panel borders and labels
    panels = {
        'A': (50, 50, 550, 350),
        'B': (650, 50, 1150, 350),
        'C': (50, 450, 550, 750),
        'D': (650, 450, 1150, 750),
    }
    
    # Draw each panel
    for label, (x1, y1, x2, y2) in panels.items():
        # Draw rectangle
        draw.rectangle((x1, y1, x2, y2), outline=(0, 0, 0), width=2)
        
        # Draw panel label
        draw.text((x1 + 10, y1 + 10), f"Panel {label}", fill=(0, 0, 0), font=title_font)
        
        # Add sample content based on panel
        if label == 'A':
            draw.text((x1 + 50, y1 + 100), "Workflow Diagram", fill=(0, 0, 0), font=font)
            # Draw simple workflow arrows
            draw.line((x1 + 100, y1 + 200, x1 + 400, y1 + 200), fill=(0, 0, 255), width=3)
            draw.polygon([(x1 + 400, y1 + 190), (x1 + 400, y1 + 210), (x1 + 420, y1 + 200)], fill=(0, 0, 255))
            
        elif label == 'B':
            draw.text((x1 + 50, y1 + 100), "Performance Comparison", fill=(0, 0, 0), font=font)
            # Draw simple bar chart
            bars = [(x1 + 100, y1 + 250, x1 + 150, y1 + 150), 
                   (x1 + 200, y1 + 250, x1 + 250, y1 + 100),
                   (x1 + 300, y1 + 250, x1 + 350, y1 + 200)]
            for bar in bars:
                draw.rectangle(bar, fill=(255, 0, 0), outline=(0, 0, 0))
            
        elif label == 'C':
            draw.text((x1 + 50, y1 + 100), "User Satisfaction Ratings", fill=(0, 0, 0), font=font)
            # Draw simple pie chart
            draw.ellipse((x1 + 150, y1 + 150, x1 + 350, y1 + 350), fill=(0, 255, 0), outline=(0, 0, 0))
            draw.pieslice((x1 + 150, y1 + 150, x1 + 350, y1 + 350), start=0, end=90, fill=(255, 0, 0), outline=(0, 0, 0))
            
        else:  # Panel D
            draw.text((x1 + 50, y1 + 100), "Figure Visibility Control", fill=(0, 0, 0), font=font)
            # Draw toggle switches
            for i in range(3):
                y_pos = y1 + 180 + i*50
                draw.rectangle((x1 + 100, y_pos, x1 + 200, y_pos + 30), fill=(200, 200, 200), outline=(0, 0, 0))
                if i % 2 == 0:
                    draw.ellipse((x1 + 170, y_pos - 5, x1 + 210, y_pos + 35), fill=(0, 255, 0), outline=(0, 0, 0))
                else:
                    draw.ellipse((x1 + 90, y_pos - 5, x1 + 130, y_pos + 35), fill=(255, 0, 0), outline=(0, 0, 0))
    
    # Add main title
    draw.text((width//2 - 200, 10), "SciTex Multi-panel Figure Example", fill=(0, 0, 0), font=title_font)
    
    # Save the figure
    basename = f"Figure_ID_{figure_number}_multipanel_demo"
    png_path = os.path.join(save_dir, f"{basename}.png")
    img.save(png_path, "PNG", dpi=(300, 300))
    
    # Create caption tex file
    tex_path = os.path.join(save_dir, f"{basename}.tex")
    caption = f"""
\\caption{{\\textbf{{
Multi-panel demonstration of SciTex figure capabilities
}}
\\smallskip
\\\\
\\textbf{{\\textit{{A.}}}} Workflow diagram showing the process of figure compilation in SciTex.
\\textbf{{\\textit{{B.}}}} Performance comparison between traditional LaTeX workflows and SciTex for figure handling.
\\textbf{{\\textit{{C.}}}} User satisfaction ratings from a survey of scientists using SciTex, showing high approval ratings.
\\textbf{{\\textit{{D.}}}} Example of figure visibility control settings in SciTex, showing how figures can be enabled or disabled for compilation.
}}
% width=1\\textwidth
"""
    
    with open(tex_path, 'w') as f:
        f.write(f"%% -*- coding: utf-8 -*-\n")
        f.write(f"%% Timestamp: \"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\" (ywatanabe)\n")
        f.write(f"%% File: \"{basename}.tex\"\n\n")
        f.write(caption)
        f.write("\n%%%% EOF")
    
    return png_path, tex_path


def main(args):
    """
    Generate examples figures for SciTex.
    """
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    # Define output directories
    manuscript_figures_dir = os.path.join(repo_root, "manuscript", "src", "figures", "src")
    example_figures_dir = os.path.join(repo_root, "examples", "manuscript_template", "src", "figures", "src")
    
    # Create directories if they don't exist
    for dir_path in [manuscript_figures_dir, example_figures_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # Create sample figures
    # Use separate figure numbers for each type
    print(f"Generating matplotlib figure example...")
    png_path, tex_path = create_sample_figure(args.figure_number, manuscript_figures_dir)
    print(f"Created: {png_path}")
    print(f"Created: {tex_path}")
    
    # Create a copy in examples directory
    if args.example_copy:
        print(f"\nCreating example copies...")
        example_png = os.path.join(example_figures_dir, os.path.basename(png_path))
        example_tex = os.path.join(example_figures_dir, os.path.basename(tex_path))
        import shutil
        shutil.copy(png_path, example_png)
        shutil.copy(tex_path, example_tex)
        print(f"Created: {example_png}")
        print(f"Created: {example_tex}")
    
    # Create multi-panel figure
    print(f"\nGenerating multi-panel figure example...")
    multipanel_num = f"{int(args.figure_number) + 1:02d}"
    mpng_path, mtex_path = create_multipanel_figure(multipanel_num, manuscript_figures_dir)
    print(f"Created: {mpng_path}")
    print(f"Created: {mtex_path}")
    
    # Create a copy in examples directory
    if args.example_copy:
        example_mpng = os.path.join(example_figures_dir, os.path.basename(mpng_path))
        example_mtex = os.path.join(example_figures_dir, os.path.basename(mtex_path))
        import shutil
        shutil.copy(mpng_path, example_mpng)
        shutil.copy(mtex_path, example_mtex)
        print(f"Created: {example_mpng}")
        print(f"Created: {example_mtex}")
    
    print("\nGenerated figures for SciTex demonstration.")
    print("\nTo compile the manuscript with these figures, run:")
    print("./compile -m --figs")
    print("\nIn your LaTeX files, reference these figures with:")
    print(f"Figure~\\ref{{fig:{args.figure_number}}} and Figure~\\ref{{fig:{multipanel_num}}}")
    
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate example figures for SciTex')
    parser.add_argument(
        "--figure-number",
        type=str,
        default="07",
        help="Base two-digit figure number (default: %(default)s)",
    )
    parser.add_argument(
        "--example-copy",
        action="store_true",
        default=True,
        help="Create copies in example directory (default: %(default)s)",
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