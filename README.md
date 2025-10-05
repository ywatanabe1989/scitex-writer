<!-- ---
!-- Timestamp: 2025-09-30 22:06:02
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/README.md
!-- --- -->

# SciTeX Writer

LaTeX compilation system with predefined project structure

## Usage

### Main Files for Writing Your Manuscript

1. **Text**: Edit `.tex` files in `01_manuscript/contents/`
   - `abstract.tex`, `introduction.tex`, `methods.tex`, `results.tex`, `discussion.tex`
2. **Figures**: Place images in `01_manuscript/contents/figures/caption_and_media/`
   - Supports: `.jpg`, `.png`, `.tif`, `.mmd` (Mermaid diagrams)
   - Auto-converts to required formats during compilation
3. **Tables**: Place `.xlsx` or `.csv` files in `01_manuscript/contents/tables/caption_and_media/`
   - Auto-converts to LaTeX tables during compilation
4. **References**: Update `shared/bib_files/bibliography.bib` (shared across all documents)
5. **Metadata**: Edit `shared/title.tex`, `shared/authors.tex`, `shared/keywords.tex`

### Compilation

```bash
# Compile manuscript (default)
./compile

# Or explicitly specify document type
./compile -m                    # manuscript
./compile -s                    # supplementary materials
./compile -r                    # revision responses

# Watch mode (auto-recompile on file changes)
./compile -m -w

# Output:
# - 01_manuscript/manuscript.pdf (main document)
# - 01_manuscript/manuscript_diff.pdf (tracked changes)
```

## Installation

```bash
# Check requirements
$ ./scripts/installation/check_requirements.sh

# Optional: Download all containers upfront (~3.2GB total)
$ ./scripts/installation/download_containers.sh
```

## Project Structure

```
paper/
├── compile                         # Unified compilation interface
├── config/                         # YAML configurations
├── shared/                         # Common files (single source of truth)
│   ├── bib_files/                  # Bibliography files
│   │   └── bibliography.bib        # References
│   ├── authors.tex                 # Author list
│   ├── title.tex                   # Paper title
│   ├── journal_name.tex            # Target journal
│   ├── keywords.tex                # Keywords
│   └── latex_styles/               # LaTeX formatting
├── scripts/
│   ├── installation/               # Setup scripts
│   ├── python/                     # Python tools
│   │   └── explore_bibtex.py       # Bibliography analysis
│   └── shell/                      # Shell scripts
│       ├── compile_manuscript      # Manuscript compiler
│       ├── compile_supplementary   # Supplementary compiler
│       ├── compile_revision        # Revision compiler
│       └── modules/                # Compilation modules
├── 01_manuscript/
│   ├── contents/                   # Document-specific content
│   │   ├── abstract.tex            # Abstract
│   │   ├── introduction.tex        # Introduction
│   │   ├── methods.tex             # Methods
│   │   ├── results.tex             # Results
│   │   ├── discussion.tex          # Discussion
│   │   ├── figures/                # Figure files
│   │   ├── tables/                 # Table files
│   │   └── [symlinks to shared/]   # Metadata & styles
│   ├── manuscript.pdf              # Output PDF
│   ├── manuscript_diff.pdf         # Changes tracking
│   └── logs/                       # Compilation logs
├── 02_supplementary/               # Supplementary materials
└── .cache/containers/              # Auto-downloaded containers
```

## Features

- **Container-based**: Consistent compilation across systems
- **Auto-fallback**: Native → Container → Module system
- **Version tracking**: Automatic versioning with diff generation
- **Mermaid support**: `.mmd` files auto-convert to images
- **Image processing**: Automatic format conversion via ImageMagick
- **HPC-ready**: Project-local containers for compute clusters
- **Bibliography analysis**: Identify high-impact papers to cite with `explore_bibtex.py`

<details>
<summary>Reference Tips</summary>

### 1. Get BibTeX file from AI2
Access [AI2 Asta](https://asta.allen.ai/chat/) and download BibTeX file for your query by clicking `Export All Citations`.

### 2. Find related articles published by co-authors

``` bash
python ./scripts/python/generate_ai2_prompt.py --type coauthors

# Reading manuscript files...
#  
# ================================================================================AI2 ASTA PROMPT
# ================================================================================
# We are currently writing a paper manuscript with the information below. Please find related papers published by the authors of our manuscript, particularly focusing on their work related to the topics covered in this manuscript.
#  
# Title: \title{
# Phase-amplitude coupling for detection and prediction of epileptic seizures in long-term intracranial electroencephalogram data
# }
#  
# Keywords: \begin{keyword}
# epilepsy \sep seizure detection \sep seizure prediction \sep NeuroVista dataset \sep phase-amplitude coupling 
# \end{keyword}
#  
# Authors: \author[1]{Yusuke Watanabe}
# \author[2,3]{Takufumi Yanagisawa}
# \author[1]{David B. Grayden\corref{cor1}}
#  
#  
# \address[1]{NeuroEngineering Research Laboratory, Department of Biomedical Engineering, The University of Melbourne, Parkville VIC 3010, Australia}
# \address[2]{Institute for Advanced Cocreation studies, Osaka University, 2-2 Yamadaoka, Suita, 565-0871, Osaka, Japan}
# \address[3]{Department of Neurosurgery, Osaka University Graduate School of Medicine, 2-2 Yamadaoka, Osaka, 565-0871, Japan}
#  
# \cortext[cor1]{Corresponding author. Tel: +XX-X-XXXX-XXXX Email: grayden@unimelb.edu.au}
#  
# Abstract: \begin{abstract}
#   \pdfbookmark[1]{Abstract}{abstract}
#  
#  
# Neural oscillations exhibit cross-frequency interactions that coordinate information processing across temporal and spatial scales, with disruptions implicated in neurological disorders including epilepsy. Phase-amplitude coupling (PAC), quantifying how low-frequency phase modulates high-frequency amplitude, has emerged as a promising biomarker for epileptic state transitions, reflecting fundamental cross-frequency neural communication mechanisms. While recent studies demonstrate systematic PAC alterations surrounding seizure events, comprehensive characterization across extended timescales has been limited by computational constraints and scarcity of long-term continuous recordings. The inability to efficiently process large-scale datasets has hindered development of reliable seizure prediction systems. Here we address these challenges through GPU-accelerated PAC computation applied to the NeuroVista dataset—comprising 4.1 TB of continuous intracranial electroencephalogram recordings from 15 patients with drug-resistant focal epilepsy monitored over 6 months to 2 years, encompassing 1,539 Type 1 clinical seizures. We computed PAC between 25 phase bands (2-30 Hz) and 25 amplitude bands (60-180 Hz) across 16 channels, extracting 17 statistical features from resulting PAC distributions at 127 temporal sampling points spanning 24 hours before to 10 minutes after seizure onset. \hl{We identified systematic preictal PAC modulation beginning 5-60 minutes before seizure onset, with theta-to-beta phase and gamma amplitude coupling showing the strongest discriminative power}. Pseudo-prospective seizure prediction achieved balanced accuracy of \hl{[XX.X±XX.X]\%} and ROC-AUC of \hl{[0.XX±0.XX]} for discriminating preictal from interictal states, with patient-specific variability reflecting individual seizure dynamics. Our GPU-accelerated implementation achieved approximately \hl{100-fold} speed improvements over conventional CPU methods, reducing processing time from years to months and enabling near-real-time analysis with \hl{<2-minute} latency per data segment. These findings establish PAC as a computationally tractable and physiologically interpretable biomarker for seizure prediction, providing a foundation for next-generation implantable seizure advisory systems that could transform epilepsy management from reactive to predictive care.
#  
# \end{abstract}
#  
# ================================================================================
# Next steps:
# 1. Visit https://asta.allen.ai/chat/
# 2. Copy and paste the prompt above
# 3. Click 'Export All Citations' to download BibTeX file
```


## Bibliography Analysis Tool

The `explore_bibtex.py` script helps analyze and filter BibTeX files enriched with citation counts and journal impact factors:

```bash
# Find high-impact uncited papers (score = citations + IF×10)
./scripts/python/explore_bibtex.py \
	shared/bib_files/bibliography.bib \
    --uncited --min-score 150 --limit 10

# Filter by keyword and metrics
./scripts/python/explore_bibtex.py \
	shared/bib_files/bibliography.bib \
    --keyword "seizure prediction" --min-citations 100 --year-min 2015

# Show statistics about your bibliography
./scripts/python/explore_bibtex.py \
	shared/bib_files/bibliography.bib --stats

# Find recent high-impact papers (2020+, IF > 5.0)
./scripts/python/explore_bibtex.py \
	shared/bib_files/bibliography.bib \
    --year-min 2020 --min-if 5.0 --limit 10

# Compare against cited papers in manuscript
./scripts/python/explore_bibtex.py \
	shared/bib_files/bibliography.bib \
    --cited --sort citation_count --reverse

# Export filtered subset to new .bib file
./scripts/python/explore_bibtex.py \
	shared/bib_files/bibliography.bib \
    --min-if 5.0 --min-citations 50 --output high_impact.bib
```

**Available filters:**
- `--min-citations N` / `--max-citations N` - Citation count range
- `--min-if X` / `--max-if X` - Journal impact factor range
- `--min-score X` - Minimum composite score (citations + IF×10)
- `--year-min Y` / `--year-max Y` - Publication year range
- `--keyword "text"` - Search in title/abstract/keywords
- `--journal "name"` - Filter by journal (partial match)
- `--author "name"` - Filter by author (partial match)
- `--cited` / `--uncited` - Compare with manuscript citations
- `--sort FIELD` - Sort by: citation_count, journal_impact_factor, year, title, score
- `--reverse` - Sort descending
- `--stats` - Show summary statistics
- `--limit N` - Maximum papers to display
- `--output FILE` - Export filtered results to .bib file

</details>

## Troubleshooting

| Issue                   | Solution                                |
|-------------------------|-----------------------------------------|
| "command not found"     | Containers will handle it automatically |
| Chrome/Puppeteer errors | Mermaid container includes Chromium     |
| First run slow          | Downloading containers (~3GB one-time)  |

## Configuration

The system uses YAML configuration files in `config/`:
- `config_manuscript.yaml` - Manuscript compilation settings
- `config_supplementary.yaml` - Supplementary materials settings
- `config_revision.yaml` - Revision response settings

## For AI Agents

See [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md) for automated manuscript generation from research projects.

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->