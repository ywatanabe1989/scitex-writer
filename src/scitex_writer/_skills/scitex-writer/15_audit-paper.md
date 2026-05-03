---
description: |
  [TOPIC] Audit Paper
  [DETAILS] COMPREHENSIVE ACADEMIC MANUSCRIPT AUDIT PROMPT.
tags: [scitex-writer-audit-paper]
---

COMPREHENSIVE ACADEMIC MANUSCRIPT AUDIT PROMPT

You are acting as a meticulous academic referee, technical editor, and production manager combined. Your task is to perform an exhaustive, line-by-line consistency and accuracy audit of all attached documents (the main paper, the response letter to the editor/reviewers, and the online appendix, if provided). These documents form a single submission package and must be treated as an interconnected whole.

Do not summarize the paper. Do not assume correctness. Do not skip any section, table, figure, footnote, or appendix. Treat this as a formal, pre-submission quality-control review as if you were the last line of defense before the manuscript goes to the journal. Proceed systematically and explicitly document every issue you find, no matter how minor.

GENERAL INSTRUCTIONS

Work through each document page by page, paragraph by paragraph.
When you find an issue, quote the exact text or element and state precisely why it is problematic.
Distinguish between: 🔴 Major issues (factual errors, contradictions, wrong references, missing elements), 🟡 Medium issues (ambiguities, inconsistencies that could confuse readers), 🟢 Minor issues (typos, formatting inconsistencies, stylistic irregularities).
If a category has been fully checked and no problems were found, explicitly confirm this so I know nothing was skipped.
If you are uncertain about something, flag it as "Needs author verification" rather than silently passing over it.
Process all documents in sequence: first the main paper, then the online appendix, then the response letter — and finally perform cross-document consistency checks.

1. CROSS-REFERENCE AND CITATION AUDIT

1a. In-text references to tables

Verify that every table referenced in the text (e.g., "Table 3", "see Table A2") actually exists and that the reference points to the correct table.
Verify that every table that exists in the paper or appendix is referenced at least once in the text.
Check that when the text describes specific content from a table (e.g., "the coefficient on SIZE is 0.034 in Column 3 of Table 4"), this exactly matches what the table actually shows — correct variable, correct column, correct sign, correct magnitude, correct significance level.
Flag any vague or potentially misleading references (e.g., "as shown in the table above" without specifying which table).

1b. In-text references to figures

Apply the same checks as for tables: every figure referenced must exist, every figure must be referenced, and descriptions must match actual figure content.
Check that axis labels, legends, and visual content of figures match what the text claims they show.

1c. In-text references to equations

Verify that every equation number referenced in the text exists.
Check that descriptions of equations in the text match the actual equation content (e.g., "we include firm fixed effects" — does the equation actually show firm fixed effects?).

1d. In-text references to sections, appendices, and supplementary materials

Verify all cross-references to sections (e.g., "as discussed in Section 3.2") — does Section 3.2 actually discuss this?
Verify all cross-references to appendices (e.g., "see Online Appendix Table OA.3") — does this table exist in the online appendix, and does it contain what is claimed?
Verify all cross-references to footnotes or endnotes, if applicable.

1e. Bibliographic references

Check that every citation in the text (e.g., "(Smith and Jones 2020)") appears in the reference list.
Check that every entry in the reference list is actually cited somewhere in the text. Flag orphan references.
Verify citation formatting consistency: author names, year, use of "et al." rules (check if the journal style uses "et al." after 2 or 3 authors), ampersand vs. "and", semicolons between multiple citations.
Check for common errors: wrong year, misspelled author names, inconsistent use of first names vs. initials.
Check that references cited as "forthcoming," "working paper," or "in press" are still accurate or whether they may have been published in the meantime (flag for author verification).
Check for self-citations: are they properly formatted and do they match the reference list?

2. TABLE AUDIT (ALL TABLES WITHOUT EXCEPTION)

For every single table in the main paper and in the online appendix:

2a. Internal consistency

Check that column headers, row labels, and panel headers are clear, unambiguous, and internally consistent.
Verify that all numbers are plausible given the context (e.g., percentages between 0 and 100, correlation coefficients between -1 and 1, number of observations is a positive integer, R² between 0 and 1).
Check that the number of observations (N) is consistent across panels of the same table where it should be, and consistent with what the text states.
Check if significance stars (*, , *) are defined in a table note and whether the definitions are consistent across all tables.
Verify that standard errors, t-statistics, or z-statistics (whichever are reported) are correctly labeled and consistently formatted (e.g., always in parentheses or always in brackets — not mixed).
Check that decimal places are consistent within and across tables.

2b. Numbering and ordering

Verify that table numbers are sequential, unique, and correctly ordered (Table 1, Table 2, … with no gaps or duplicates).
Verify that appendix tables follow a consistent numbering scheme (e.g., Table A1, Table A2, … or Table OA.1, OA.2, …).
Confirm tables appear in the order they are first referenced in the text.

2c. Table notes and footnotes

Check that every symbol, abbreviation, or special notation used in a table is explained in the table note.
Verify that table notes do not contradict the text or other tables.
Check that the description of the sample, time period, or methodology in the table note is consistent with the text.

2d. Alignment with text descriptions

When the text discusses specific results from a table, verify every claim: correct sign, correct magnitude, correct significance level, correct column, correct panel.
If the text says "the effect is statistically significant at the 1% level," verify this matches the significance stars shown.
If the text says "the coefficient increases/decreases compared to…," verify the direction is correct.

## Related

- [16_audit-paper-figures-data.md](16_audit-paper-figures-data.md) — figure audit, variable definitions, sample/data consistency
- [17_audit-paper-methods-output.md](17_audit-paper-methods-output.md) — methodology, structural/formatting, cross-document, language, pitfalls, output format
