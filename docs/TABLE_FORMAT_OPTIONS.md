# SciTex Table Formatting Options

This document outlines the available formatting options for tables in the SciTex system. These options can be specified in the table caption file as comments.

## Basic Usage

Table formatting options are specified as comments in the table caption file. For example:

```latex
% fontsize=small
% alignment=auto
% orientation=landscape
% style=fancy
\caption{\textbf{
Table title here
}
\smallskip
\\
Table description here.
}
% width=0.9\textwidth
```

## Available Formatting Options

### Basic Formatting

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `fontsize` | `tiny`, `scriptsize`, `footnotesize`, `small`, `normalsize` | `small` | Font size for the table content |
| `tabcolsep` | Dimension (e.g., `4pt`, `6pt`) | `4pt` | Spacing between columns |
| `width` | Dimension (e.g., `0.9\textwidth`) | `1\textwidth` | Width of the table caption |
| `max-width` | Dimension (e.g., `0.95\textwidth`) | — | Maximum width for the table |

### Alignment Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `alignment` | `l`, `c`, `r`, `auto`, `mixed`, `smart` | `r` | Column alignment (left, center, right, auto, mixed, smart) |
| `column-spec` | LaTeX column specifiers (e.g., `lccr`) | — | Custom column specification |
| `first-col-bold` | Flag (no value needed) | — | Makes the first column text bold |

#### Alignment Values Explained
- `l`: All columns left-aligned
- `c`: All columns centered
- `r`: All columns right-aligned
- `auto`: First column left-aligned, others centered
- `mixed`: First column left-aligned, others right-aligned
- `smart`: Text columns left-aligned, numeric columns right-aligned

### Layout Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `orientation` | `landscape` | — | Displays the table in landscape mode |
| `float-pos` | LaTeX float position (e.g., `h`, `t`, `b`, `p`, `!`) | `htbp` | Controls table positioning |
| `caption-pos` | `top`, `bottom` | `top` | Position of the caption |
| `scale-to-width` | Flag (no value needed) | — | Scales table to fit the specified width |

### Style Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `style` | `booktabs`, `basic`, `fancy` | `booktabs` | Overall table style |
| `header-style` | `bold`, `plain`, `colored` | `bold` | Style for the header row |
| `no-color` | Flag (no value needed) | — | Disables alternating row colors |
| `no-math` | Flag (no value needed) | — | Disables math formatting for numeric data |

### Advanced Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `wrap-text` | Flag (no value needed) | — | Enables text wrapping in cells |
| `auto-width` | Flag (no value needed) | — | Automatically determines column widths |
| `multirow` | Flag (no value needed) | — | Enables support for multi-row cells |

## Examples

### Basic Table with Right-aligned Columns

```latex
% fontsize=small
% alignment=r
\caption{\textbf{
Performance Comparison
}
\smallskip
\\
Comparison of execution times across different algorithms.
}
% width=0.9\textwidth
```

### Fancy Table with Mixed Alignment and Text Wrapping

```latex
% fontsize=footnotesize
% alignment=mixed
% style=fancy
% wrap-text
\caption{\textbf{
Detailed Feature Comparison
}
\smallskip
\\
Comprehensive comparison of features across different software packages.
}
% width=0.95\textwidth
```

### Landscape Table with Custom Column Specification

```latex
% orientation=landscape
% column-spec=l>{\centering\arraybackslash}p{2cm}>{\centering\arraybackslash}p{2cm}r
% tabcolsep=6pt
\caption{\textbf{
Wide Dataset Summary
}
\smallskip
\\
Summary statistics for the complete dataset with multiple variables.
}
% width=0.9\textwidth
```

### Table with Smart Alignment and No Colors

```latex
% alignment=smart
% no-color
% header-style=plain
\caption{\textbf{
Mixed Data Types
}
\smallskip
\\
Dataset containing both text descriptions and numerical measurements.
}
% width=0.85\textwidth
```

## Implementation Notes

These formatting options are processed by the `process_tables.sh` script in the SciTex system. Each option is extracted from comments in the table caption file and applied when generating the LaTeX code for the table.