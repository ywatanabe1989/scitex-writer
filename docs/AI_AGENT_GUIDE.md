<!-- ---
!-- Timestamp: 2025-09-26 23:00:00
!-- Author: ywatanabe
!-- File: AI_AGENT_GUIDE.md
!-- --- -->

# AI Agent Guide for SciTeX Writer

This guide helps AI agents create scientific manuscripts from research projects using SciTeX Writer.

## Quick Reference

```bash
# Initialize manuscript
export STXW_DOC_TYPE=manuscript
./compile_manuscript

# Output locations
manuscript: 01_manuscript/manuscript.pdf
changes: 01_manuscript/diff.pdf
```

## Project → Manuscript Workflow

### 1. Link Research Assets

Instead of copying files, use symlinks to maintain single source of truth:

```bash
# Link figures from analysis
ln -s ~/proj/neurovista/scripts/analysis/output/fig1.png \
      01_manuscript/contents/figures/caption_and_media/.01_seizure_prediction.png

# Link tables from results
ln -s ~/proj/neurovista/data/results/performance.csv \
      01_manuscript/contents/tables/caption_and_media/.01_performance.csv

# Link Mermaid diagrams
ln -s ~/proj/neurovista/docs/workflow.mmd \
      01_manuscript/contents/figures/caption_and_media/.02_workflow.mmd
```

### 2. Write Content

Edit section files in `01_manuscript/contents/`:

```latex
% introduction.tex
\section{Introduction}
Neural interactions through phase-amplitude coupling...

% Reference to linked figure
As shown in Figure~\ref{fig:01_seizure_prediction}...

% Citation (from shared/bibliography.bib)
Previous work \cite{Tort2010} demonstrated...
```

**Note**: Bibliography is shared across all documents:
- Edit: `shared/bibliography.bib` 
- Automatically used by: manuscript, supplementary, and revision

### 3. Add Figure Captions

Create `01_manuscript/contents/figures/caption_and_media/.01_seizure_prediction.tex`:

```latex
\textbf{Seizure prediction performance.}
(A) ROC curves across patients. 
(B) Feature importance analysis.
(C) Temporal dynamics of prediction confidence.
```

### 4. Compile

```bash
./compile_manuscript  # Everything handled automatically
```

## File Naming Conventions

### CRITICAL: Naming Rules

**Figures**: `.XX_descriptive_name.{jpg|png|tif|mmd}`
- Must start with `.`
- XX = two-digit number (01, 02, 03...)
- descriptive_name = lowercase with underscores
- Example: `.01_seizure_prediction.png`

**Tables**: `.XX_descriptive_name.csv`
- Must start with `.`
- XX = two-digit number (01, 02, 03...)
- descriptive_name = lowercase with underscores
- Example: `.01_patient_demographics.csv`

**Captions**: Same name but with `.tex` extension
- `.01_seizure_prediction.tex` (caption for the figure)
- `.01_patient_demographics.tex` (caption for the table)

### LaTeX Citation Syntax

The naming convention automatically generates LaTeX labels:

**Figures**:
```latex
% File: .01_seizure_prediction.png
% LaTeX label generated: fig:01_seizure_prediction

% How to cite:
Figure~\ref{fig:01_seizure_prediction}        % "Figure 1"
\autoref{fig:01_seizure_prediction}           % "Figure 1" (automatic)
As shown in Figure~\ref{fig:01_seizure_prediction}, the results...
(Figure~\ref{fig:01_seizure_prediction}A)     % Subfigure reference
```

**Tables**:
```latex
% File: .02_performance_metrics.csv
% LaTeX label generated: tab:02_performance_metrics

% How to cite:
Table~\ref{tab:02_performance_metrics}        % "Table 2"
\autoref{tab:02_performance_metrics}          % "Table 2" (automatic)
The results (Table~\ref{tab:02_performance_metrics}) show...
```

### Label Generation Pattern

```
Filename:                        → LaTeX label:
.01_pac_analysis.png   → fig:01_pac_analysis
.02_workflow.mmd        → fig:02_workflow
.01_statistics.csv      → tab:01_statistics
.03_parameters.csv      → tab:03_parameters
```

### Citations
```latex
\cite{Author2024}                    % Single citation
\cite{Author2024,Smith2023}          % Multiple citations
\citep{Author2024}                   % Parenthetical citation
\citet{Author2024}                   % Textual citation
```

### Sections
```latex
\section{Methods}
\subsection{Data Collection}
\subsubsection{Patient Selection}
```

## Converting Research Code to Manuscript

### Example: neurovista project → paper

```bash
# 1. Identify key results
ls ~/proj/neurovista/scripts/pac/visualization/*_out/
ls ~/proj/neurovista/scripts/analysis/results/

# 2. Create symlinks for best figures
for fig in ~/proj/neurovista/scripts/pac/visualization/*_out/*.png; do
    name=$(basename $fig .png)
    id=$(printf "%02d" $counter)
    ln -s $fig 01_manuscript/contents/figures/caption_and_media/.${id}_${name}.png
    ((counter++))
done

# 3. Extract methods from code docstrings
grep -h "^\"\"\"" ~/proj/neurovista/scripts/pac/*.py | \
    sed 's/"""//g' > methods_draft.txt

# 4. Generate bibliography from code
grep -h "doi\.org" ~/proj/neurovista/scripts/**/*.py | \
    sed 's/.*doi.org\///' > dois_to_cite.txt
```

## File Organization Pattern

```
Research Project                    SciTeX Writer
----------------                    -------------
scripts/analysis/
  ├── compute_pac.py        →      (methods.tex describes)
  └── output/
      ├── pac_results.png    →      .03_pac.png (symlink)
      └── statistics.csv     →      .02_stats.csv (symlink)

data/processed/
  └── patient_data.csv       →      (referenced in methods.tex)

docs/
  └── workflow.mmd           →      .01_workflow.mmd (symlink)
```

## Best Practices for AI Agents

### DO:
- Use symlinks to maintain data provenance
- Follow naming convention: `{Figure|Table}_ID_XX_descriptive_name`
- Keep IDs sequential (01, 02, 03...)
- Auto-convert .mmd → .png → .jpg for diagrams
- Let containers handle missing tools

### DON'T:
- Copy files (use symlinks instead)
- Hardcode paths (use relative paths)
- Include data in repo (link to data directory)
- Worry about LaTeX installation (containers handle it)

## Complete Example: Research to Manuscript

### Step 1: Link Assets with Proper Names

```bash
# Link a PAC analysis result
ln -s ~/proj/neurovista/scripts/pac/visualization/pac_duration_out/summary.png \
      01_manuscript/contents/figures/caption_and_media/.03_pac_duration.png

# Link performance metrics table  
ln -s ~/proj/neurovista/data/results/classifier_performance.csv \
      01_manuscript/contents/tables/caption_and_media/.01_classifier_performance.csv

# Link workflow diagram
ln -s ~/proj/neurovista/docs/analysis_pipeline.mmd \
      01_manuscript/contents/figures/caption_and_media/.01_analysis_pipeline.mmd
```

### Step 2: Write Captions

`01_manuscript/contents/figures/caption_and_media/.03_pac_duration.tex`:
```latex
\textbf{Phase-amplitude coupling duration analysis.}
Distribution of PAC burst durations across (A) preictal and (B) interictal periods.
Violin plots show patient-specific variations with median (white dot) and IQR (thick bar).
Statistical significance: ***p<0.001, **p<0.01, *p<0.05 (Wilcoxon signed-rank test).
```

### Step 3: Reference in Manuscript

`01_manuscript/contents/results.tex`:
```latex
\section{Results}

\subsection{PAC Duration Analysis}
We analyzed the duration of PAC bursts across different seizure states 
(Figure~\ref{fig:03_pac_duration}). The results revealed significantly 
longer PAC durations during preictal periods compared to interictal 
baseline (p<0.001, Table~\ref{tab:01_classifier_performance}).

Our analysis pipeline (Figure~\ref{fig:01_analysis_pipeline}) processed
continuous iEEG recordings through multiple stages...
```

### Step 4: Compile

```bash
export STXW_DOC_TYPE=manuscript
./compile_manuscript
```

## Automation Example

```python
#!/usr/bin/env python3
"""Generate manuscript from research outputs."""

import os
from pathlib import Path
import subprocess

def link_figures(source_dir, manuscript_dir):
    """Create symlinks for all figures."""
    fig_dir = Path(manuscript_dir) / "01_manuscript/contents/figures/caption_and_media"
    
    for i, fig_path in enumerate(Path(source_dir).glob("**/*.png"), 1):
        target = fig_dir / f".{i:02d}_{fig_path.stem}.png"
        if not target.exists():
            target.symlink_to(fig_path.resolve())
            print(f"Linked: {fig_path.name} → {target.name}")

def generate_methods(code_dir, output_file):
    """Extract methods from code documentation."""
    methods = []
    for py_file in Path(code_dir).glob("**/*.py"):
        with open(py_file) as f:
            # Extract docstrings and comments
            # Convert to LaTeX format
            pass
    
    with open(output_file, 'w') as f:
        f.write("\\section{Methods}\n")
        f.write('\n'.join(methods))

def compile_manuscript():
    """Run SciTeX Writer compilation."""
    env = os.environ.copy()
    env['STXW_DOC_TYPE'] = 'manuscript'
    subprocess.run(['./compile_manuscript'], env=env)

if __name__ == "__main__":
    link_figures("~/proj/neurovista/scripts", ".")
    generate_methods("~/proj/neurovista/scripts", "01_manuscript/contents/methods.tex")
    compile_manuscript()
```

## Quick Checklist

- [ ] Symlinks created for all figures/tables
- [ ] Figure/Table IDs are sequential
- [ ] Captions written for all figures
- [ ] All sections have content
- [ ] Bibliography entries added
- [ ] `./compile_manuscript` runs without errors
- [ ] PDF generated successfully

## Common Naming Mistakes to Avoid

❌ **WRONG**:
- `figure1.png` (missing . prefix)
- `Figure_1_results.png` (single digit, should be 01)
- `.01-results.png` (hyphen not allowed, use underscore)
- `.01_Results.png` (uppercase in description)
- `fig_01_analysis.png` (wrong prefix)

✅ **CORRECT**:
- `.01_results.png`
- `.02_patient_data.csv`
- `.03_pac_analysis.mmd`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Undefined reference" | Check filename follows `.XX_name` pattern |
| Figure not appearing | Verify symlink target exists and is readable |
| Wrong figure number | ID in filename must match citation (01 → fig:01_name) |
| Citation undefined | Add entry to bibliography.bib |
| Mermaid not rendering | .mmd file will auto-convert on compile |
| LaTeX errors | Check 01_manuscript/logs/global.log |

## Support

For AI agents using this system:
- Follow this guide for consistent results
- Containers handle all dependencies automatically
- Focus on content, not compilation details

<!-- EOF -->