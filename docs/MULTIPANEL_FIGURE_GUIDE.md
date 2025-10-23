# Multi-Panel Figure Guide for SciTex

This comprehensive guide explains how to create, manage, and reference multi-panel figures in the SciTex system, covering various approaches and best practices.

## Overview

Multi-panel figures are essential in scientific papers for presenting related data or concepts in a unified visual presentation. They allow you to:

- Present multiple related experiments in a single figure
- Show different aspects or analyses of the same dataset
- Illustrate sequential processes or workflows
- Compare results across different conditions or treatments
- Combine raw data with analytical visualizations

SciTex provides robust support for creating, formatting, and referencing complex figures with multiple panels (labeled A, B, C, etc.).

## Creating Multi-Panel Figures

SciTex supports three main approaches for creating multi-panel figures, each with specific advantages depending on your needs.

### Approach 1: Pre-assembled Image (Recommended for Complex Layouts)

This approach uses a single pre-assembled image containing all panels with embedded panel labels:

1. Use your preferred graphics software (PowerPoint, Illustrator, Python, etc.) to create a figure with multiple panels
2. Add panel labels (A, B, C, etc.) directly in the image, typically in the upper-left corner of each panel
3. Export as a high-resolution PNG file (300 DPI recommended)
4. Place in `manuscript/contents/figures/contents/`
5. Create a caption file explaining each panel

**Advantages:**
- Full control over panel placement and alignment
- Consistent styling across all panels
- Simple to implement in LaTeX
- Best for complex layouts that don't follow a grid structure

**Example Files:**
```
manuscript/contents/figures/contents/.01_multipanel.png   # Image with all panels
manuscript/contents/figures/contents/.01_multipanel.tex   # Caption file
```

**Recommended Tools:**
- **PowerPoint**: Excellent for quick creation with easy alignment tools
- **Adobe Illustrator/Inkscape**: For professional-quality vector-based figures
- **Python (Matplotlib)**: For programmatically generated data figures
- **R (ggplot2)**: For statistical visualizations

### Approach 2: LaTeX Subfigure Environment (Best for Grid Layouts)

For simple grid layouts, use the subfigure environment to combine individual panel images:

```latex
% In your figure caption file (e.g., .02_comparison.tex)
% This will be automatically processed into a proper figure environment

\begin{figure*}[htbp]
  \centering
  \begin{subfigure}[b]{0.48\textwidth}
    \includegraphics[width=\textwidth]{./contents/figures/contents/panel_a_data.png}
    \caption{}
    \label{fig:02A}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \includegraphics[width=\textwidth]{./contents/figures/contents/panel_b_model.png}
    \caption{}
    \label{fig:02B}
  \end{subfigure}
  
  \vspace{1em}
  
  \begin{subfigure}[b]{0.48\textwidth}
    \includegraphics[width=\textwidth]{./contents/figures/contents/panel_c_analysis.png}
    \caption{}
    \label{fig:02C}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \includegraphics[width=\textwidth]{./contents/figures/contents/panel_d_results.png}
    \caption{}
    \label{fig:02D}
  \end{subfigure}
  
  % Your main caption here
  \caption{\textbf{
  Comparison of experimental data with model predictions.
  }
  \smallskip
  \\
  \textbf{\textit{A.}} Raw experimental data from three independent trials. 
  \textbf{\textit{B.}} Computational model predictions under the same conditions.
  \textbf{\textit{C.}} Statistical analysis showing correlation between data and model.
  \textbf{\textit{D.}} Quantification of error rates across different parameter settings.
  }
  \label{fig:02}
\end{figure*}
```

**Advantages:**
- Individual panels can be easily updated without recreating the entire figure
- Automatic panel labeling
- Consistent spacing and alignment
- Perfect for grid-based layouts (2×2, 3×3, etc.)

### Approach 3: TikZ for Vector-Based Panels (Best for Diagrams)

For diagrams, flowcharts, and conceptual figures, use TikZ to create vector-based multi-panel figures directly in LaTeX:

```latex
\begin{tikzpicture}[
  panel/.style={draw=black!30, rounded corners, fill=white, inner sep=10pt},
  label/.style={font=\bfseries, anchor=north west, text=black}
]
  % First panel
  \begin{scope}[local bounding box=panel-a]
    \node[panel] at (0,0) {
      % Panel A content
      \begin{tikzpicture}
        \draw[-Stealth, thick] (0,0) -- (2,0) node[right] {Time};
        \draw[-Stealth, thick] (0,0) -- (0,2) node[above] {Response};
        \draw[blue, thick] plot[smooth] coordinates {(0,0) (0.5,0.8) (1,1.2) (1.5,1.6) (2,1.8)};
      \end{tikzpicture}
    };
  \end{scope}
  
  % Second panel
  \begin{scope}[local bounding box=panel-b, shift={(5,0)}]
    \node[panel] at (0,0) {
      % Panel B content
      \begin{tikzpicture}
        \node[circle, draw, fill=gray!20] (A) at (0,0) {A};
        \node[circle, draw, fill=gray!20] (B) at (2,0) {B};
        \draw[-Stealth, thick] (A) -- (B) node[midway, above] {Process};
      \end{tikzpicture}
    };
  \end{scope}
  
  % Panel labels
  \node[label] at (panel-a.north west) {A};
  \node[label] at (panel-b.north west) {B};
\end{tikzpicture}
```

**Advantages:**
- Resolution-independent vector graphics
- Perfect for diagrams, flowcharts, and conceptual figures
- Can include annotations, arrows, and connectors between panels
- Consistent with LaTeX fonts and styling

## Writing Captions for Multi-Panel Figures

Captions for multi-panel figures should:

1. Start with a bold title describing the overall figure
2. Include a detailed description of each panel, using bold italic formatting for panel labels

Example caption file structure:

```latex
\caption{\textbf{
Multi-panel figure showing different aspects of SciTex performance
}
\smallskip
\\
\textbf{\textit{A.}} Workflow diagram showing how figures are processed in SciTex. 
\textbf{\textit{B.}} Performance comparison between traditional LaTeX and SciTex.
\textbf{\textit{C.}} User satisfaction ratings from 50 researchers using SciTex for manuscript preparation.
\textbf{\textit{D.}} Time required for compilation with and without figures enabled.
}
% width=1\textwidth
```

## Referencing Multi-Panel Figures

To reference the entire figure:

```latex
Figure~\ref{fig:01} shows the complete SciTex workflow and performance metrics.
```

To reference specific panels:

```latex
Figure~\ref{fig:01}A illustrates the workflow diagram.
Figure~\ref{fig:01}B,C presents the performance and satisfaction data.
Figure~\ref{fig:01}B--D shows the quantitative performance metrics.
```

## Panel Labeling Conventions

Follow these conventions for panel labels:

1. **Uppercase Letters**: Use "A, B, C, ..." for main panels
   ```
   \textbf{\textit{A.}} Panel description...
   ```

2. **Lowercase Roman Numerals**: Use "i, ii, iii, ..." for sub-panels
   ```
   \textbf{\textit{A.}} Main panel description... \textbf{\textit{(i)}} Sub-panel description...
   ```

3. **Lowercase Letters**: Use "a, b, c, ..." for another level of sub-panels
   ```
   \textbf{\textit{A.}} \textbf{\textit{(i)}} \textbf{\textit{a.}} Tertiary panel description...
   ```

## Examples

### Example 1: Caption for a 2×2 Panel Figure

```latex
\caption{\textbf{
SciTex enhances scientific writing workflow and productivity
}
\smallskip
\\
\textbf{\textit{A.}} The SciTex workflow diagram shows integration of manuscript preparation, 
figure processing, and LaTeX compilation stages.
\textbf{\textit{B.}} Compilation times comparison between traditional LaTeX workflows (gray) 
and SciTex (blue), showing 45% improved performance.
\textbf{\textit{C.}} Error rates in final manuscripts decreased by 72% with SciTex compared 
to manual formatting methods (n=50 manuscripts).
\textbf{\textit{D.}} User satisfaction survey results from 30 researchers, with ratings across 
five dimensions: ease of use, time savings, figure handling, table handling, and citation management.
}
% width=1\textwidth
```

### Example 2: Multi-Level Panel Caption

```latex
\caption{\textbf{
Hierarchical analysis of SciTex performance metrics
}
\smallskip
\\
\textbf{\textit{A.}} System performance metrics. \textbf{\textit{(i)}} Compilation time across 
different manuscript sizes. \textbf{\textit{(ii)}} Memory usage during processing stages.
\textbf{\textit{B.}} User experience evaluation. \textbf{\textit{(i)}} Novice users (n=15). 
\textbf{\textit{(ii)}} Experienced LaTeX users (n=12). \textbf{\textit{(iii)}} Technical editors (n=8).
}
% width=1\textwidth
```

## Best Practices

1. **Consistency**: Use the same panel labeling style throughout your manuscript
2. **Visual Hierarchy**: Make panel labels visually distinct from the content
3. **Logical Ordering**: Arrange panels in a logical sequence (typically left-to-right, top-to-bottom)
4. **Clear References**: When referencing panels in the text, always include the main figure number
5. **Caption Detail**: Each panel should have a concise but informative description in the caption

## Advanced Techniques

### Using Subfigures Package

For more control over multi-panel layout, you can use the `subcaption` package in your custom LaTeX templates:

```latex
\usepackage{subcaption}

% In your figure environment:
\begin{figure*}
  \centering
  \begin{subfigure}[b]{0.45\textwidth}
    \includegraphics[width=\textwidth]{panel_a.png}
    \caption{}
    \label{fig:1a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.45\textwidth}
    \includegraphics[width=\textwidth]{panel_b.png}
    \caption{}
    \label{fig:1b}
  \end{subfigure}
  
  \vspace{1em}
  
  \begin{subfigure}[b]{0.45\textwidth}
    \includegraphics[width=\textwidth]{panel_c.png}
    \caption{}
    \label{fig:1c}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.45\textwidth}
    \includegraphics[width=\textwidth]{panel_d.png}
    \caption{}
    \label{fig:1d}
  \end{subfigure}
  
  \caption{A four-panel figure example. \textbf{(a)} Description of panel A. 
  \textbf{(b)} Description of panel B. \textbf{(c)} Description of panel C. 
  \textbf{(d)} Description of panel D.}
  \label{fig:multipanel}
\end{figure*}
```

This technique allows for more precise control over panel layout but requires customizing your LaTeX template.

## Troubleshooting

### Common Issues with Multi-Panel Figures

#### Panel Layout and Formatting Issues

1. **Inconsistent Panel Labels**
   - **Problem**: Panel labels have inconsistent formatting or placement
   - **Solution**: Use a template for consistent label placement (typically upper-left corner)
   - **Prevention**: Create a label style guide for your figures (font, size, position, etc.)

2. **Poor Resolution**
   - **Problem**: Panels appear pixelated or blurry in the compiled PDF
   - **Solution**: Export source images at 300-600 DPI, PNG format recommended
   - **Prevention**: Check figure appearance at 100% zoom and at print size before final export

3. **Unbalanced Panel Sizes**
   - **Problem**: Panels of equal importance have very different sizes
   - **Solution**: Standardize dimensions for similar content types
   - **Prevention**: Create a grid template in your graphics software with predefined panel sizes

4. **Cramped Layout**
   - **Problem**: Too many panels in one figure makes each one hard to read
   - **Solution**: Split into multiple figures or use a larger format
   - **Prevention**: Limit complex figures to 4-6 panels; use hierarchical labeling for subpanels

#### Compilation Problems

5. **Figure Not Appearing**
   - **Problem**: The multi-panel figure doesn't appear in the compiled PDF
   - **Solution**: Check the file paths in your LaTeX code, ensure files exist
   - **Debugging**: Examine the log files in `manuscript/contents/figures/compiled/debug/`

6. **Missing or Duplicate Labels**
   - **Problem**: Panel labels are missing or duplicated in the compiled figure
   - **Solution**: Check for label conflicts in your LaTeX code
   - **Prevention**: Use a consistent labeling system (e.g., `fig:XXA`, `fig:XXB`)

7. **Cropping Issues**
   - **Problem**: Parts of panels are cut off in the compiled figure
   - **Solution**: Add padding around your panels or reduce the figure width
   - **Fix**: Modify the width parameter or adjust margins in the source image

#### Integration with Caption

8. **Mismatched Panel Descriptions**
   - **Problem**: Caption panel descriptions don't match the actual panels
   - **Solution**: Systematically review caption text against the figure
   - **Prevention**: Create caption text simultaneously with figure assembly

9. **Inconsistent Caption Style**
   - **Problem**: Panel descriptions have inconsistent formatting
   - **Solution**: Follow a consistent format: `\textbf{\textit{A.}} Panel description.`
   - **Prevention**: Use the same styling for all panel labels in captions

### Image Size and Orientation Considerations

#### Controlling Figure Width

For complex multi-panel figures, you can adjust the width to optimize readability:

```latex
% width=1\textwidth    # Full page width (default)
% width=0.9\textwidth  # 90% of page width (reduces margins)
% width=0.8\textwidth  # 80% of page width (adds larger margins)
% width=0.75\textwidth # 75% of page width (good for 2-column journals)
```

Add this comment to the end of your caption file to control the figure width.

#### Using Landscape Orientation

For very wide figures (e.g., time series data, large comparisons), use landscape orientation:

```latex
% orientation=landscape
```

This comment in your caption file will rotate the figure to landscape orientation in the final PDF.

#### Handling Very Large Figures

For extremely detailed figures:

1. Create a high-resolution main figure for online supplementary materials
2. Create a simplified version for the main manuscript
3. Consider splitting complex figures into multiple related figures

### Testing Your Multi-Panel Figures

Before finalizing your figures:

1. Compile with the `--figs` flag: `./compile --figs`
2. Check the PDF output at both 100% zoom and fit-to-page
3. Print a test page to ensure readability on paper
4. Have a colleague review the figure for clarity and completeness

## Conclusion

Multi-panel figures are powerful tools for presenting complex information in scientific manuscripts. By following these guidelines, you can create clear, informative, and professionally formatted multi-panel figures in SciTex.

For more information, see the main [Figure and Table Guide](FIGURE_TABLE_GUIDE.md).