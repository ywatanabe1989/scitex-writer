---
description: Scientific writing proofreading style — respectful tone, hedging, transitional words, terminology conventions, anti-patterns (AP1-AP9, AP12), placeholder command, and usage.
---

# Scientific Writing Proofreading — Style, Tone, and Anti-Patterns

Continuation of [21_writing-proofreading.md](21_writing-proofreading.md).

## Respectful Tone Toward Prior Work

Maintain professional, respectful language when comparing with other tools or prior work:

| DO NOT | DO |
|--------|-----|
| "achieved negligible adoption" | "seen limited adoption" |
| "X cannot Y" | "X does not yet address Y" or "X was not designed for Y" |
| "X failed to achieve..." | "X has not yet achieved widespread..." |
| "largely does not exist" | "remains limited" |
| "impossible to use" | "requires significant expertise" |

Use "was not designed to X" rather than "does not X" or "cannot X" — this acknowledges design intent rather than implying deficiency.

## Hedging and Evidence-Based Claims

| DO NOT | DO |
|--------|-----|
| "proves reproducibility" | "provides cryptographic evidence for reproducibility" |
| "ensures integrity" | "is designed to ensure integrity" |
| "is the solution" | "provides evidence that" |

- Use "is" only for well-evidenced claims backed by citations; otherwise use "may be" or hedging language
- Use `N+` suffix for numbers that grow (e.g., "300+ MCP tools") to avoid needing manuscript updates

## Transitional Words and Paragraph Cohesion

Use transitional words to signal relationships between paragraphs:

| Relationship | Transitional Words |
|---|---|
| Adding similar points | Similarly, Likewise, In the same vein, Along these lines |
| Contrasting | However, In contrast, Conversely, On the other hand |
| Building on | Beyond X, Furthermore, Moreover, Building on this |
| Temporal/sequence | Meanwhile, Subsequently, In parallel |
| Consequence | These gaps become more consequential as, As a result, Consequently |
| Example/specification | For instance, In particular, Specifically |

Never start a paragraph that feels disconnected from the previous one.

## Terminology Spelling-Out Rule

On first use of any abbreviation or acronym, spell it out in full followed by the abbreviation in parentheses. All subsequent uses should use only the abbreviation.

- First occurrence: "directed acyclic graphs (DAGs)"
- All subsequent: "DAGs" (never spell out again)
- Apply per-document (abstract, main text, supplementary each count as separate documents)
- The abstract is self-contained: spell out abbreviations even if they appear in the main text
- Define acronyms and name origins at first appearance, not later

## Anti-Patterns in Scientific Writing

### AP1: Dismissive Language
See "Respectful Tone" section above.

### AP2: Overclaiming / Missing Hedges
See "Hedging" section above.

### AP3: Numeric Repetition
When the same number appears in multiple sections, vary the context or consolidate to avoid redundancy.

### AP4: Word Repetition Across Paragraph Boundaries
Vary vocabulary across consecutive paragraphs: "failure" → "reason", "shortcoming" → "limitation".

### AP5: Missing Transitions
See "Transitional Words" section above.

### AP6: Restating Abstract in Discussion
Discussion should synthesize, not repeat. Assume the reader has read the abstract.

### AP7: Overusing Signature Terms
If a distinctive term (e.g., "meta-demonstration") appears 4+ times, reduce to 2 occurrences.

### AP8: Em-Dash Overuse
Mix punctuation variety — do not use 4+ em-dashes in one sentence:
- Em-dash (`---`): dramatic pause, strong aside, interruption (spaced: `word --- word`)
- Comma: light parenthetical, natural flow
- Colon: introduces explanation or list
- Parentheses: truly supplementary info

### AP9: Future-Proofing Counts
Use `N+` suffix for numbers that grow (e.g., "300+ MCP tools", "187+ built-in Skills").

### AP12: Repeating Key Expressions Across Sections

When a concept is central to the paper, the same word or phrase tends to appear in every section. This weakens the prose and makes it feel formulaic.

**Rule.** Key expressions should appear at most 2–3 times in the full manuscript. Establish the concept in one section (usually Introduction), then vary the expression elsewhere.

**Example: "byproduct"**

*Before (5 uses):* Introduction "a byproduct of productive work", Introduction "a byproduct of convenience", Abstract "building verification as a byproduct", Discussion "embedded as a byproduct of", Discussion "building...as a byproduct".

*After (2 uses, both in Introduction):* "a byproduct of productive work" (establishes concept), "a byproduct of convenience" (reinforces for Clew). Abstract → "generating verification automatically". Discussion → "emerges naturally from" / "simultaneously constructing".

**Substitution patterns.**

| Overused | Alternatives |
|---|---|
| "as a byproduct" | "emerges naturally from", "generating X automatically", "simultaneously constructing", "without additional effort" |
| "was not designed to" | "does not yet", "targets X rather than Y", "focuses on X" |
| "hash-based verification" | "cryptographic integrity checks", "content-addressable tracking", "SHA-256 chains" |
| "human-navigable" | "reviewer-accessible", "structured audit trail", "inspectable" |

**How to apply.**
1. After drafting, grep for key terms and count occurrences.
2. Keep 2 uses maximum per distinctive phrase across the full manuscript.
3. Vary at section boundaries (intro → methods → results → discussion).
4. The Introduction establishes terminology; other sections can paraphrase.

**Relation to other APs.** Extends AP4 (word repetition at paragraph boundaries) to manuscript-wide scope. Complements AP7 (overusing signature terms like "meta-demonstration").

## Placeholder Command for Draft Content

Use `\placeholder{text}` (or short alias `\ph{text}`) for content not yet finalized. Renders as red bold on yellow background in the compiled PDF.

| DO NOT | DO |
|--------|-----|
| `[IRB details to be added]` | `\placeholder{IRB details to be added}` |
| `[citation needed]` | `\ph{citation needed}` |
| `approximately N participants` | `approximately \ph{N} participants` |

Before submission, run `grep placeholder` to find all unresolved items.

## Usage

Provide your manuscript text for proofreading. The revision will be returned in a LaTeX code block.

``` tex
YOUR REVISED TEXT
```

## Related

- [21_writing-proofreading.md](21_writing-proofreading.md) — role, general rules, formatting, language rules, common corrections, section-specific guidelines
