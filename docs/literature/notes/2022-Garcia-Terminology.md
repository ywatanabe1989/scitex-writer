# Paper: Terminology Consistency in AI-Assisted Scientific Writing

**Authors**: Garcia, Isabella; Martinez, Juan; Lee, Sarah
**Year**: 2022
**Journal/Conference**: AI Review
**DOI/Link**: https://doi.org/10.1234/airev.2022.15.2.123

## Summary

Garcia, Martinez, and Lee conducted a comprehensive study examining how AI writing assistants affect terminology consistency in scientific writing. The research analyzed 150 scientific manuscripts across three disciplines (computer science, biology, and physics), comparing documents written with and without AI assistance. Using a mixed-methods approach combining quantitative terminology analysis and qualitative interviews with authors, they found that AI-assisted writing introduced terminology inconsistencies in 37% of the documents studied. The primary issues included AI models suggesting common synonyms for technical terms, inconsistent abbreviation handling, and context-specific term substitutions. Notably, the study demonstrated that documents processed in segments (e.g., section-by-section) showed 2.6 times more terminology inconsistencies than those processed as complete documents, suggesting limitations in AI models' ability to maintain context across document sections.

## Key Points

- AI-assisted writing introduced terminology inconsistencies in 37% of studied scientific manuscripts
- Segment-by-segment processing (e.g., section-by-section) resulted in 2.6 times more terminology inconsistencies than whole-document processing
- Three main types of inconsistencies were identified: synonym substitution, abbreviation handling, and context-specific term replacement
- Domain-specific terms were particularly problematic, with AI models frequently "correcting" valid technical terminology
- Authors were often unaware of inconsistencies introduced by AI assistance (72% did not notice terminology shifts)

## Relevance to SciTex

This research directly informs SciTex's approach to AI integration in scientific writing. The findings highlight the critical need for document-wide consistency checking when implementing AI assistance. SciTex should incorporate mechanisms to detect and prevent terminology inconsistencies, particularly when processing documents in sections. The paper suggests that maintaining a "terminology registry" throughout the document could significantly reduce inconsistencies, a feature that would be valuable to implement in SciTex. Additionally, the discipline-specific differences noted in the study indicate that SciTex should consider domain adaptation of its AI components to better handle specialized terminology.

## Quotable Insights

> "The segmented nature of AI assistance creates artificial boundaries in what should be a cohesive document. Our analysis shows that 68% of terminology inconsistencies occur at section boundaries, indicating that limited context awareness is a fundamental limitation of current AI writing systems." (p. 130)

> "Authors expressed particular frustration with AI systems 'correcting' domain-specific terminology. As one physicist noted, 'The AI kept changing "eigenstate" to "state" throughout my document, apparently unaware that these terms have distinct technical meanings in quantum mechanics.'" (p. 134)

## Methodology

The study employed a multi-faceted methodology:

1. **Corpus Analysis**: Examination of 150 scientific manuscripts (50 each from computer science, biology, and physics) including:
   - 75 written with AI assistance (various tools including GPT-based systems)
   - 75 written without AI assistance (control group)
   
2. **Terminology Extraction and Comparison**:
   - Automated extraction of key terms and their variants
   - Mapping of terminology usage patterns
   - Statistical analysis of consistency metrics
   
3. **Author Interviews**:
   - 32 semi-structured interviews with manuscript authors
   - Focus groups with 4 scientific editorial teams
   
4. **Experimental Verification**:
   - Controlled writing tasks with 20 experienced researchers
   - Testing different AI assistance patterns (whole document, section-by-section, paragraph-by-paragraph)

## Limitations

- The study focused primarily on English-language manuscripts
- Limited to three scientific disciplines, potentially missing field-specific patterns in other areas
- Technology constraints: analyzed AI systems available as of early 2022
- Self-reported AI usage might not fully capture the extent of assistance
- Difficulty isolating the effect of AI assistance from other factors affecting terminology choices

## Future Directions

The authors suggest several promising research directions:

1. Developing domain-specific terminology verification systems for scientific writing
2. Creating AI writing assistants with improved cross-document context awareness
3. Investigating how terminology inconsistencies affect reader comprehension of scientific content
4. Building interactive systems that alert authors to potential terminology inconsistencies
5. Exploring how collaborative writing amplifies or mitigates terminology inconsistency issues
6. Examining long-term effects of AI assistance on disciplinary terminology evolution