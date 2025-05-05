# Multi-panel Figure Generation for SciTex

This directory contains example scripts for programmatically generating multi-panel figures compatible with the SciTex system. These scripts demonstrate how to create complex scientific figures with proper formatting and integration into the SciTex workflow.

## Available Scripts

1. **generate_multipanel_figure.py**: Basic multi-panel figure creation with a 2×2 grid layout
2. **advanced_multipanel_figure.py**: Advanced multi-panel figure with custom layout, shared axes, and annotations

## Requirements

- Python 3.6 or higher
- NumPy
- Matplotlib
- SciPy (for the advanced example)

Install the required packages:

```bash
pip install numpy matplotlib scipy
```

For publication-quality plots, consider installing the SciencePlots package:

```bash
pip install SciencePlots
```

## Basic Usage

### Generate a Simple Multi-panel Figure

```bash
python generate_multipanel_figure.py --id 01 --name multipanel_example
```

This will create:
- `manuscript/src/figures/src/Figure_ID_01_multipanel_example.png`
- `manuscript/src/figures/src/Figure_ID_01_multipanel_example.tex`

### Generate an Advanced Multi-panel Figure

```bash
python advanced_multipanel_figure.py --id 02 --name advanced_analysis --style science
```

Options for the `--style` parameter:
- `default`: Standard matplotlib style
- `science`: Scientific publication style
- `nature`: Nature journal style
- `ieee`: IEEE publication style

## Command Line Arguments

Both scripts support the following arguments:

- `--id XX`: Figure ID number (e.g., 01, 02). If not provided, the next available ID will be used.
- `--name NAME`: Descriptive name for the figure (e.g., 'data_analysis')
- `--outdir DIR`: Output directory (default: manuscript/src/figures/src)

## Integration with SciTex

After generating the figure, compile your manuscript with:

```bash
./compile -m --figs
```

The figure can be referenced in your LaTeX document using:

```latex
Figure~\ref{fig:XX}
```

where `XX` is the figure ID you specified.

## Creating Your Own Multi-panel Figures

To create your own multi-panel figures, you can:

1. Modify the existing scripts with your own data and plot types
2. Create a new script using the provided templates as a starting point
3. Adapt the figure layout, styling, and panel organization to suit your needs

Always follow these guidelines:
- Use the SciTex naming convention: `Figure_ID_XX_descriptive_name`
- Generate a properly formatted caption file with the same base name
- Include panel labels (A, B, C, etc.) in the figure and reference them in the caption
- Save at appropriate resolution (300 DPI recommended)

## Best Practices

- Use consistent formatting across all panels
- Choose appropriate visualizations for your data
- Add clear labels and annotations
- Follow scientific visualization principles
- Use color effectively and consistently
- Consider accessibility (e.g., colorblind-friendly palettes)

For more details on figure requirements, see the main [FIGURE_TABLE_GUIDE.md](../docs/FIGURE_TABLE_GUIDE.md) and [MULTIPANEL_FIGURE_GUIDE.md](../docs/MULTIPANEL_FIGURE_GUIDE.md) documentation.