# Proofread Guideline

## Aim of Proofreading
The aim is to correct English while retaining original meaning and conforming to scholarly language standards.

## Rules
Proofreading must:
- Correct the English without including messages or comments.
- Retain the original syntax as much as possible while conforming to scholarly language.
- Not modify linguistically correct sections.
- Minimize revisions to avoid endless paraphrasing.
- Avoid unnecessary adjectives unsuitable for scientific writing (e.g., "somewhat", "in-depth", "various").
- Use proper figure and table references (e.g., Figure~\ref{fig:01}A, Table~\ref{tab:01}).
- Highlight ambiguous parts using fixme tags: [fixme ->] ambiguous sentence [<- fixme].
- Add spaces on either side when using em dash (---).
- Maintain consistent terminology throughout the manuscript.
- Follow title capitalization rules (prepositions in lowercase).
- Use noun forms for figure and table titles and legends.
- Never remove references and LaTeX code.
- Use LaTeX format.

## Common Issues

[1. Grammar and Style]
- Subject-verb agreement
- Article usage (a, an, the)
- Verb tense consistency
- Parallel structure in lists
- Dangling modifiers

[2. Scientific Writing Conventions]
- Passive vs. active voice appropriateness
- Precision in quantitative statements
- Proper use of hedging language
- Consistency in nomenclature

[3. Punctuation]
- Hyphens (-): compound adjectives before nouns
- En dashes (--): ranges (e.g., pages 1--10)
- Em dashes (---): interruptions with spaces
- Minus signs: use proper math mode

[4. LaTeX Specifics]
- Non-breaking spaces before references (~)
- Proper escaping of special characters
- Consistent formatting of units

## Examples

## With tags

[START of 1. Grammar and Style] The data shows that the treatment were effective. [END of 1. Grammar and Style] -> [START of 1. Grammar and Style] The data show that the treatment was effective. [END of 1. Grammar and Style]

[START of 3. Punctuation] The range was 10-20 Hz. [END of 3. Punctuation] -> [START of 3. Punctuation] The range was 10--20~Hz. [END of 3. Punctuation]

## Without tags

The data shows that the treatment were effective. -> The data show that the treatment was effective.

The range was 10-20 Hz. -> The range was 10--20~Hz.
