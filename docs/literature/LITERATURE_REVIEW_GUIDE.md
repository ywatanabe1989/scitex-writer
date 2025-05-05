# SciTex Literature Review Guide

This guide explains how to use and contribute to the SciTex literature review system. The literature review is a structured collection of research papers, notes, and summaries that inform the development of SciTex and identify relevant gaps in scientific document preparation research.

## Table of Contents

1. [Structure Overview](#structure-overview)
2. [Using the Literature Review](#using-the-literature-review)
3. [Contributing to the Literature Review](#contributing-to-the-literature-review)
4. [Creating Paper Notes](#creating-paper-notes)
5. [Updating Thematic Summaries](#updating-thematic-summaries)
6. [Citing Papers in Your Work](#citing-papers-in-your-work)
7. [Gap Analysis](#gap-analysis)

## Structure Overview

The literature review is organized into the following components:

```
literature/
├── README.md                  # General overview and templates
├── index.md                   # Central index of all papers and summaries
├── papers/                    # PDF files of research papers
├── notes/                     # Notes on specific papers
│   └── YYYY-Author-Keyword.md # Individual paper note files
├── summaries/                 # Thematic summaries
│   └── Theme_Summary.md       # Summary documents on specific themes
├── gaps.md                    # Identified research gaps
└── bibliography.bib           # BibTeX entries for all papers
```

## Using the Literature Review

### Finding Relevant Papers

1. Start with the [index.md](./index.md) file, which categorizes papers by topic
2. Look for papers with the ✅ symbol, which indicates complete notes are available
3. Explore thematic summaries to understand trends across multiple papers
4. Check the [gaps.md](./gaps.md) file to understand research opportunities

### Accessing Paper Information

1. **Paper Notes**: Detailed notes on individual papers in the `notes/` directory
2. **PDFs**: Original papers in the `papers/` directory (when available)
3. **BibTeX Entries**: Citation information in the `bibliography.bib` file
4. **Thematic Summaries**: Synthesis of multiple papers in the `summaries/` directory

## Contributing to the Literature Review

### Adding a New Paper

1. **Save the PDF**: Place the paper in the `papers/` directory with the naming format:
   ```
   YYYY-AuthorLastName-KeywordFromTitle.pdf
   ```
   Example: `2023-Chen-AIAssisted.pdf`

2. **Create a Note File**: Create a markdown file in the `notes/` directory with the same base name:
   ```
   YYYY-AuthorLastName-KeywordFromTitle.md
   ```
   Example: `2023-Chen-AIAssisted.md`

3. **Add BibTeX Entry**: Add the citation to `bibliography.bib`

4. **Update Index**: Add the paper to the appropriate section in `index.md`

5. **Update Thematic Summaries**: If relevant, incorporate insights into thematic summaries

### Updating Reading Lists

The reading list in `index.md` tracks priority papers for review. To update it:

1. Add new papers with the 🔍 symbol to indicate they're on the reading list
2. Update papers to ✅ symbol when notes are completed
3. Remove papers from the list when they're no longer priorities

## Creating Paper Notes

Paper notes should follow this template:

```markdown
# Paper: [Full Title]

**Authors**: [Author Names]
**Year**: [Publication Year]
**Journal/Conference**: [Publication Venue]
**DOI/Link**: [DOI or URL]

## Summary

[1-2 paragraph summary of the paper]

## Key Points

- [Point 1]
- [Point 2]
- [Point 3]

## Relevance to SciTex

[How this paper relates to the SciTex project]

## Quotable Insights

> [Direct quote from the paper]

## Methodology

[Brief description of the methodology used]

## Limitations

[Noted limitations of the research]

## Future Directions

[Suggested future work from the paper]
```

## Updating Thematic Summaries

Thematic summaries synthesize findings across multiple papers. To update a summary:

1. Review all relevant papers on the theme
2. Identify common patterns, contradictions, and evolving trends
3. Organize insights into meaningful sections
4. Use consistent citation format (Author, Year) throughout
5. Ensure the implications for SciTex are clearly articulated
6. Include a complete reference list at the end

When creating a new thematic summary, follow this structure:

```markdown
# Thematic Summary: [Theme Name]

This summary synthesizes key findings from the literature regarding [theme], with particular focus on implications for the SciTex project.

## [Section 1]

[Content with citations (Author, Year)]

## [Section 2]

[Content with citations (Author, Year)]

...

## Implications for SciTex

[How these findings inform SciTex development]

## Future Research Directions

[Promising areas for further investigation]

## Conclusion

[Brief synthesis of key takeaways]

---

## References

- Full references in consistent format
```

## Citing Papers in Your Work

The `bibliography.bib` file contains BibTeX entries for all papers in the literature review. To cite these papers in your LaTeX documents:

1. Import the bibliography:
   ```latex
   \bibliography{/path/to/bibliography.bib}
   ```

2. Cite papers using standard LaTeX citation commands:
   ```latex
   \cite{authorYear}
   \citep{authorYear}
   \citet{authorYear}
   ```

3. Use the year and author's last name as the citation key:
   ```
   chen2023ai
   johnson2021figure
   ```

## Gap Analysis

The `gaps.md` file tracks identified research gaps that SciTex could address. When you identify a new gap:

1. Add a new section to the gap analysis document
2. Clearly describe the gap and provide supporting evidence
3. Explain how SciTex might address this gap
4. Suggest potential research questions to explore

Format for new gap entries:

```markdown
## Gap X: [Brief Title]

**Description**: [Clear description of the gap]

**Evidence**:
- [Citation 1] found that "..."
- [Citation 2] noted that "..."

**SciTex Approach**:
- [How SciTex could address this gap]
- [Specific features or approaches]

**Research Questions**:
- [Question 1]
- [Question 2]
```

---

*Last updated: 2025-05-05*