# Cross-Referencing Between Documents

## How It Works

The `\link` command in `base.tex` enables cross-references between manuscript and supplementary materials.

```latex
\link[supple-]{../02_supplementary/main}
```

This command:
1. Reads the supplementary's `.aux` file for labels
2. Adds prefix `supple-` to all supplementary labels
3. Makes them available in the manuscript

## Usage Examples

### From Manuscript → Supplementary

```latex
% In manuscript text:
See Supplementary Figure~\ref{supple-fig:01_extra_analysis} for additional data.

The full dataset is provided in Supplementary Table~\ref{supple-tab:01_all_patients}.

Detailed methods are described in Supplementary Section~\ref{supple-sec:detailed_methods}.
```

### From Supplementary → Manuscript

```latex
% In supplementary text (if you add reverse link):
As shown in the main text (Figure~\ref{main-fig:01_primary_result})...
```

## Label Format

| Document | File | Label | Reference from Manuscript |
|----------|------|-------|---------------------------|
| Main | `.01_result.png` | `fig:01_result` | `\ref{fig:01_result}` |
| Supplementary | `.01_extra.png` | `fig:01_extra` | `\ref{supple-fig:01_extra}` |

## Setting Up Reverse Links

To reference manuscript from supplementary, add to `02_supplementary/main.tex`:

```latex
\link[main-]{../01_manuscript/manuscript}
```

## Common Issues

1. **"Undefined reference"**: Compile supplementary first, then manuscript
2. **Missing .aux file**: Both documents must be compiled at least once
3. **Path errors**: Ensure paths in `\link` match actual directory structure

## Compilation Order

For cross-references to work:
1. Compile supplementary: `./compile_supplementary`
2. Compile manuscript: `./compile_manuscript`
3. Compile manuscript again (to resolve references)

<!-- EOF -->