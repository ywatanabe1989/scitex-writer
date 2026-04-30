---
name: audit-paper-methods-output
description: COMPREHENSIVE ACADEMIC MANUSCRIPT AUDIT — METHODS, STRUCTURE, CROSS-DOCUMENT, PITFALLS, OUTPUT
tags: [scitex-writer, scitex-package]
---

COMPREHENSIVE ACADEMIC MANUSCRIPT AUDIT — METHODS, STRUCTURE, CROSS-DOCUMENT, PITFALLS, OUTPUT

Continuation of [15_audit-paper.md](15_audit-paper.md). Sections 6–10 of the audit plus the output format.

6. METHODOLOGY AND ECONOMETRIC CONSISTENCY

Verify that the empirical model described in the text matches what is shown in equation form.
Check that the control variables mentioned in the text match those listed in the tables.
Verify that fixed effects described in the text (e.g., "we include industry and year fixed effects") match what is reported in the tables (e.g., a row saying "Industry FE: Yes, Year FE: Yes").
If the paper mentions clustering of standard errors (e.g., "clustered at the firm level"), verify this is stated consistently in all relevant table notes.
Check that robustness tests described in the text actually appear in the tables and vice versa.

7. STRUCTURAL AND FORMATTING CHECKS

7a. Section and heading structure

Verify that section numbering is sequential and consistent (no gaps, no duplicates).
Check that the structure described in any "roadmap" paragraph (e.g., "Section 2 reviews the literature…") matches the actual section structure.

7b. Footnotes and endnotes

Verify that footnote numbers are sequential and unique.
Check that footnotes do not contain critical information that should be in the main text (flag for author consideration).
Verify that footnotes do not contradict the main text.

7c. Formatting consistency

Check for consistent use of fonts, bold, italics, and spacing in tables and text.
Verify consistent number formatting (e.g., thousands separator, decimal separator).
Check for consistent use of abbreviations (e.g., "e.g.," vs. "for example"; "i.e.," vs. "that is").
Check that all parenthetical asides, quotation marks, and brackets are properly closed.

7d. Page and line references

If the document uses page numbers or line numbers, verify they are sequential and not missing.

8. CROSS-DOCUMENT CONSISTENCY (CRITICAL)

This section applies when multiple documents are provided (main paper, online appendix, response letter).

8a. Main paper ↔ Online appendix

Verify that every reference from the main paper to the online appendix (e.g., "see Online Appendix Table OA.5") points to an element that actually exists in the online appendix.
Verify that every element in the online appendix is referenced from the main paper (flag orphan appendix items).
Check that variable definitions, sample descriptions, and methodology descriptions are consistent between the main paper and the appendix.
Verify that results discussed in both documents are consistent (e.g., if the main paper says "results are robust as shown in the Online Appendix," verify this is actually the case).

8b. Main paper ↔ Response letter

If the response letter promises specific changes (e.g., "We now include an additional control for firm size in Table 5"), verify that these changes are actually reflected in the current version of the paper.
If the response letter references specific tables, figures, or sections in the revised paper, verify that these references are correct.
Flag any promises in the response letter that do not appear to have been implemented in the paper.
Check that any new analyses or tables added in response to reviewer comments are properly integrated (numbered, referenced, noted).

8c. Online appendix ↔ Response letter

If the response letter references new appendix items (e.g., "We provide this analysis in the new Online Appendix Table OA.7"), verify that these items exist in the online appendix.

9. LANGUAGE AND CLARITY CHECKS (ACCOUNTING-SPECIFIC)

Check for correct use of accounting and finance terminology (e.g., "earnings management" vs. "earnings manipulation," "accruals" vs. "accrual," "discretionary" vs. "non-discretionary").
Verify consistency in how accounting standards are referenced (e.g., "IFRS" vs. "IAS," "ASC 606" vs. "the new revenue recognition standard").
Flag any claims that appear to overstate or misrepresent results (e.g., claiming causality when the method only supports association).
Check for hedging language consistency: are similar results described with similar levels of certainty throughout?

10. COMMON PITFALLS CHECKLIST

Finally, specifically check for these frequently occurring errors in accounting research papers:

"Table X" references that are off by one (very common after reordering tables during revision)
Copy-paste errors where a paragraph describes Table 3 but was copied from the description of Table 2 and not fully updated
Significance levels described in text that don't match the stars in the table
Sample sizes that don't add up (e.g., subsamples should sum to full sample)
Control variables listed in the text that don't appear in the table, or vice versa
Inconsistent rounding (e.g., "0.034" in text but "0.0341" in table)
Orphan references (cited in text but missing from reference list, or in reference list but never cited)
Mismatched parenthetical citation formats
Tables where the dependent variable is not clearly stated
Appendix items that are referenced with wrong numbering scheme (e.g., "Table A3" in text but "Table A.3" in appendix)

OUTPUT FORMAT

Organize your findings into clearly labeled sections following the structure above (Sections 1–10). Within each section:

Quote or precisely describe the problematic element with its exact location (page, section, table, column, row).
Explain why it is an issue.
Mark severity: 🔴 Major / 🟡 Medium / 🟢 Minor.
If no issue is found in a category, explicitly state: "Checked — no issues detected."

At the end, provide a summary table listing all issues found, sorted by severity (major first), with columns: Issue #, Location, Category, Severity, Description.

Work slowly and carefully. Go through every single element. Precision and completeness are more important than speed. When in doubt, flag it.

## Related

- [15_audit-paper.md](15_audit-paper.md) — general instructions, cross-reference/citation audit, table audit
- [16_audit-paper-figures-data.md](16_audit-paper-figures-data.md) — figure audit, variable definitions, sample/data consistency
