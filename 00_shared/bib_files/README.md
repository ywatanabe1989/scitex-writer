# Bibliography Files - SciTeX Writer Project

## 🎯 Quick Start

**For LaTeX/BibTeX use:**
```latex
\bibliography{enriched_all}
```

## 📁 Files Overview

### Primary Bibliography (USE THIS)
- **`enriched_all.bib`** (97 KB, 102 entries)
  - Fully enriched with DOIs, abstracts, citations, impact factors
  - Ready for publication use
  - Updated: 2025-11-12

### Source Files (Individual collections)
- `bibliography.bib` - Main collection (17 KB)
- `related_work.bib` - Related work papers (13 KB)
- `by_grok.bib`, `by_claude.bib`, `by_gpt5.bib`, `by_gemini.bib` - AI-curated
- `field_background.bib` - Domain background papers
- `methods_refs.bib` - Methodology references
- `my_papers.bib` - Your publications
- `scitex-system.bib` - SciTeX system reference

### Processing Outputs
- `merged_all.bib` - Deduplicated merge (66 KB)
- `enriched_all_v2.bib` - Second-pass attempt (95 KB)
- `enrichment_summary.txt` - Statistics
- `enrichment_v2_summary.txt` - Second-pass statistics
- `FINAL_REPORT.md` - Comprehensive analysis

## 📊 Quality Metrics

| Metric | Value |
|--------|-------|
| Total unique papers | 102 |
| With DOI | 53 (52%) |
| With abstract | 44 (43%) |
| With citations | 21 (21%) |
| Deduplication rate | 48% |

## 🔄 Maintenance

To update enrichment (e.g., refresh citation counts):
```bash
cd /home/ywatanabe/proj/scitex-writer/00_shared/bib_files
python3 /home/ywatanabe/proj/scitex-writer/.tmp/enrich_second_pass.py
```

## 📝 Adding New Papers

1. Add to appropriate source file (e.g., `related_work.bib`)
2. Run merge and enrichment:
```bash
python3 /home/ywatanabe/proj/scitex-writer/.tmp/merge_and_enrich_bibtex.py
```

## 🏆 Top Journals by Impact Factor

- Trends in Cognitive Sciences: 16.7 (Q1)
- Genome Biology: 10.1 (Q1)
- Research Integrity and Peer Review: 7.2 (Q1)
- Patterns (Elsevier): 6.7
- Electrochimica Acta: 5.5

---
Generated: 2025-11-12 | Tool: scitex.scholar v2.0
