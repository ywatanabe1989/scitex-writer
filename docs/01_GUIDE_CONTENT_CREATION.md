# Content Creation Guide

Comprehensive guide for creating figures, tables, and managing manuscript content in SciTeX.

## Quick Start

### Adding a Figure
1. Create figure in PNG format (300 DPI)
2. Name: `.XX_description.png`
3. Place in: `manuscript/contents/figures/contents/`
4. Create caption: `.XX_description.tex`
5. Reference: `Figure~\ref{fig:XX}`

### Adding a Table
1. Create table in CSV format
2. Name: `.XX_description.csv`
3. Place in: `manuscript/contents/tables/contents/`
4. Create caption: `.XX_description.tex`
5. Reference: `Table~\ref{tab:XX}`

## Figure Management

### Directory Structure
```
manuscript/contents/figures/
├── compiled/           # Auto-generated (DO NOT EDIT)
├── contents/          # Place your files here
│   ├── .XX.png        # Image files
│   └── .XX.tex        # Caption files
└── templates/         # Templates for new figures
```

### Naming Conventions
All figures follow pattern: `.XX_descriptive_name.ext`
- `XX`: Two-digit number (01, 02, etc.)
- `descriptive_name`: Short description
- `.ext`: `.png` for images, `.tex` for captions

### Creating Figures

#### Method 1: Direct Image
1. Create PNG/JPG (300 DPI recommended)
2. Name according to convention
3. Place in contents directory

#### Method 2: PowerPoint
```bash
./compile -m --pptx2png
```

#### Method 3: SVG Vector Graphics
1. Create in Inkscape, Illustrator, etc.
2. Export as SVG
3. Name with convention (`.03_flowchart.svg`)
4. Place in contents directory
5. Create caption file

#### Method 4: TikZ (LaTeX Drawing)
```latex
\begin{tikzpicture}[
    block/.style={rectangle, draw, fill=blue!20,
                 text width=2.5cm, text centered, rounded corners},
    line/.style={draw, -latex'}
]
\node [block] (A) {Component A};
\node [block, right=of A] (B) {Component B};
\path [line] (A) -- (B);
\end{tikzpicture}

\caption{\textbf{Workflow diagram.} Description here.}
```

### Figure Captions

Create `.tex` file with same name as image:
```latex
\caption{\textbf{
FIGURE TITLE HERE
}
\smallskip
\\
FIGURE LEGEND HERE.
}
% width=0.9\textwidth
```

Width options: `0.75\textwidth` to `1\textwidth`

### Referencing Figures

In manuscript text:
```latex
Figure~\ref{fig:XX}
```

For multi-panel figures:
```latex
Figure~\ref{fig:01}A
Figure~\ref{fig:01}(i)
Figure~\ref{fig:01}B--D
```

### Multi-Panel Figures

#### Approach 1: Pre-assembled Image (Recommended)
1. Create figure with all panels in graphics software
2. Add panel labels (A, B, C, etc.) in image
3. Export as high-resolution PNG (300 DPI)
4. Create single caption file explaining each panel

Advantages:
- Full control over placement
- Consistent styling
- Simple LaTeX implementation

#### Approach 2: LaTeX Subfigures (Grid Layouts)
```latex
\begin{figure*}[htbp]
  \centering
  \begin{subfigure}[b]{0.48\textwidth}
    \includegraphics[width=\textwidth]{panel_a.png}
    \caption{}
    \label{fig:02A}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \includegraphics[width=\textwidth]{panel_b.png}
    \caption{}
    \label{fig:02B}
  \end{subfigure}

  \caption{\textbf{Title.}
  \textbf{\textit{A.}} Description of panel A.
  \textbf{\textit{B.}} Description of panel B.}
  \label{fig:02}
\end{figure*}
```

Advantages:
- Individual panels easily updated
- Automatic labeling
- Perfect for grid layouts

#### Approach 3: TikZ Diagrams
For diagrams, flowcharts, and conceptual figures created directly in LaTeX with full vector graphics control.

### Multi-Panel Captions

Structure:
```latex
\caption{\textbf{
Overall figure title describing content
}
\smallskip
\\
\textbf{\textit{A.}} Description of first panel.
\textbf{\textit{B.}} Description of second panel.
\textbf{\textit{C.}} Description of third panel.
}
% width=1\textwidth
```

Panel labeling conventions:
- Uppercase letters: A, B, C, ...
- Lowercase roman numerals: (i), (ii), (iii), ... for sub-panels
- Lowercase letters: a, b, c, ... for another level

### Figure Troubleshooting

**Figure Not Appearing**
- Check PNG and TEX files have matching names
- Verify PNG format (8-bit, RGB, or grayscale)
- Examine debug files in `compiled/debug/`

**Figure Too Large/Small**
- Adjust width parameter in caption: `% width=0.8\textwidth`

**Resolution Issues**
- Ensure 300 DPI minimum
- Check for compression artifacts

**Caption Problems**
- Verify LaTeX syntax
- Check proper formatting of title and legend

**Format Issues**
- Check for special characters
- Verify TikZ code correctness
- Look for mismatched braces

## Table Management

### Directory Structure
```
manuscript/contents/tables/
├── compiled/     # Auto-generated (DO NOT EDIT)
└── contents/     # Place your files here
    ├── .XX.csv   # Data files
    └── .XX.tex   # Caption files
```

### Naming Conventions
Pattern: `.XX_descriptive_name.ext`
- `XX`: Two-digit number (01, 02, etc.)
- `descriptive_name`: Short description
- `.ext`: `.csv` for data, `.tex` for captions

### Creating Tables

1. Create CSV file with data:
```csv
Column1,Column2,Column3
Value1,Value2,Value3
Value4,Value5,Value6
```

2. Name according to convention (`.01_results.csv`)
3. Place in contents directory
4. Create caption file (`.01_results.tex`)

### Table Captions

Template:
```latex
\caption{\textbf{
TABLE TITLE HERE
}
\smallskip
\\
TABLE LEGEND HERE.
}
% width=1\textwidth
```

### Table Formatting Options

Specify as comments in caption file:

```latex
% fontsize=small
% alignment=auto
% orientation=landscape
% style=fancy
\caption{...}
```

#### Basic Formatting
| Option | Values | Default |
|--------|--------|---------|
| `fontsize` | tiny, scriptsize, footnotesize, small, normalsize | small |
| `tabcolsep` | Dimension (4pt, 6pt) | 4pt |
| `width` | Dimension (0.9\textwidth) | 1\textwidth |

#### Alignment Options
| Option | Values | Default |
|--------|--------|---------|
| `alignment` | l, c, r, auto, mixed, smart | r |
| `column-spec` | LaTeX column specifiers | — |
| `first-col-bold` | Flag | — |

Alignment values:
- `l`: All columns left-aligned
- `c`: All columns centered
- `r`: All columns right-aligned
- `auto`: First left, others centered
- `mixed`: First left, others right
- `smart`: Text left, numeric right

#### Layout Options
| Option | Values |
|--------|--------|
| `orientation` | landscape |
| `float-pos` | h, t, b, p, ! (LaTeX positions) |
| `caption-pos` | top, bottom |
| `scale-to-width` | Flag to scale to specified width |

#### Style Options
| Option | Values | Default |
|--------|--------|---------|
| `style` | booktabs, basic, fancy | booktabs |
| `header-style` | bold, plain, colored | bold |
| `no-color` | Flag | — |
| `no-math` | Flag (disables math formatting) | — |

#### Advanced Options
| Option | Values |
|--------|--------|
| `wrap-text` | Flag for text wrapping |
| `auto-width` | Flag for auto column widths |
| `multirow` | Flag for multi-row cells |

### Table Examples

**Basic Right-aligned:**
```latex
% fontsize=small
% alignment=r
\caption{\textbf{Performance Comparison} ...}
% width=0.9\textwidth
```

**Fancy with Mixed Alignment:**
```latex
% fontsize=footnotesize
% alignment=mixed
% style=fancy
% wrap-text
\caption{\textbf{Feature Comparison} ...}
% width=0.95\textwidth
```

**Landscape with Custom Columns:**
```latex
% orientation=landscape
% column-spec=l>{\centering}p{2cm}r
% tabcolsep=6pt
\caption{\textbf{Wide Dataset} ...}
% width=0.9\textwidth
```

**Smart Alignment, No Colors:**
```latex
% alignment=smart
% no-color
% header-style=plain
\caption{\textbf{Mixed Data} ...}
% width=0.85\textwidth
```

### Referencing Tables

In manuscript text:
```latex
Table~\ref{tab:XX}
```

Example:
```latex
Table~\ref{tab:01} shows the performance comparison.
```

## Compilation

### Processing Figures
```bash
./compile --figs
./compile -f
```

Steps:
1. Initialization
2. PowerPoint conversion (if requested)
3. Filename normalization
4. Caption generation
5. Image cropping
6. Format conversion (TIF/JPG to PNG)
7. Legend compilation
8. Figure visibility control
9. File aggregation

### Processing Tables
```bash
./compile
```

Steps:
1. Initialization
2. CSV processing
3. Caption integration
4. File aggregation

## Cross-Referencing

Reference supplementary materials from manuscript:
```latex
See Supplementary Figure~\ref{supple-fig:01_extra} for additional data.
Supplementary Table~\ref{supple-tab:01_all} provides full dataset.
```

Add to supplementary to reference manuscript:
```latex
\link[main-]{../01_manuscript/manuscript}
```

Compilation order:
1. `./compile_supplementary`
2. `./compile_manuscript`
3. `./compile_manuscript` (again to resolve references)

## Best Practices

### Figures
- Consistency: Use same labeling style throughout
- Visual hierarchy: Make labels distinct
- Logical ordering: Left-to-right, top-to-bottom
- Clear references: Include figure number
- Detail: Concise but informative captions
- Test resolution at 100% zoom and print size

### Tables
- Data accuracy: Verify all values
- Consistent formatting: Use same styles
- Clear headers: Use descriptive column names
- Appropriate width: Avoid overly cramped layouts
- Logical columns: Order by importance/sequence

## Additional Resources

- See the `to_claude/guidelines/` directory for language-specific guides
- Check `structure/` directory for overall repository structure
- Review examples in manuscript template files
