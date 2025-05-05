# Literature Review Directory

This directory contains literature references and notes for the SciTex project. The purpose is to maintain an organized collection of relevant research papers, identify gaps in the literature, and inform the development of SciTex.

## Directory Structure

```
literature/
├── README.md          # This file
├── papers/            # PDF files of research papers
├── notes/             # Notes on specific papers
├── summaries/         # Thematic summaries
├── gaps.md            # Identified research gaps
└── bibliography.bib   # BibTeX entries for all papers
```

## Paper Categories

Papers are organized into the following categories:

1. **Scientific Writing**: Research on scientific writing practices and challenges
2. **LaTeX Systems**: Papers about LaTeX and document preparation systems
3. **AI in Writing**: Research on AI assistance in writing processes
4. **Document Workflows**: Studies on scientific document workflows
5. **Figure and Table Management**: Research on handling visual elements in documents

## How to Add a New Paper

1. Save the PDF in the `papers/` directory with a descriptive filename:
   ```
   YYYY-AuthorLastName-KeywordFromTitle.pdf
   ```
   Example: `2023-Smith-AIWritingAssistance.pdf`

2. Create a note file in the `notes/` directory with the same base name:
   ```
   YYYY-AuthorLastName-KeywordFromTitle.md
   ```

3. Add the BibTeX entry to `bibliography.bib`

4. Update relevant thematic summaries in the `summaries/` directory

## Paper Notes Template

Each paper note should follow this template:

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

## Research Gap Analysis

The `gaps.md` file maintains a living document of identified research gaps that SciTex could address. When you discover a potential gap in the literature, add it to this file with:

1. A clear description of the gap
2. Supporting evidence from the literature
3. How SciTex might address this gap
4. Potential research questions to explore

## Literature Review Process

1. **Initial Scan**: Broad search of relevant literature using key terms
2. **Selection**: Filter papers based on relevance to SciTex
3. **Analysis**: Read and annotate selected papers
4. **Synthesis**: Identify themes, patterns, and gaps
5. **Application**: Apply insights to SciTex development

## Recommended Search Terms

When searching for relevant literature, consider these keywords:

- Scientific writing workflow
- LaTeX document preparation
- AI-assisted writing
- Figure management in documents
- Scientific manuscript templates
- Citation management systems
- Document compilation automation
- Collaborative scientific writing