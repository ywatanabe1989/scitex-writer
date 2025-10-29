# Scientific Writing Reference: Terminology

Guidelines for terminology and language conventions used in scientific manuscripts.

## Non-Scientific Terms to Avoid

Avoid colloquial or non-technical language in scientific writing. Replace with precise terminology:

| Avoid | Use Instead |
|-------|-------------|
| "a lot" | "considerable", "substantial", "significant" (when appropriate) |
| "very" | Quantify: "increased by 50%" instead of "very increased" |
| "good" | Specify: "effective", "efficient", "valid", "robust" |
| "bad" | Specify: "problematic", "invalid", "insufficient", "inadequate" |
| "interesting" | Explain significance: "notable", "unexpected", "important" |
| "clearly" | Provide evidence: "as demonstrated by", "shown in Figure X" |
| "obviously" | Explain reasoning: "as follows", "consequently", "therefore" |
| "must" | Use appropriate modal: "should", "ought to", "must" (only when required) |
| "might" | Specify uncertainty: "may", "could", "possibly" |
| "seems" | Provide evidence: "appears", "is indicated", "suggests" |

## Quantitative Language

### Measurements and Values

```latex
% Correct
The mean was 42 ± 3 μm.
Values ranged from 10 to 50 mg/kg.

% Incorrect
The mean was 42 ± 3 micrometers. (use SI units)
The values ranged from 10-50 mg/kg. (use "to" in text)
```

### Statistical Expressions

```latex
% Correct
We found a significant difference (p < 0.05, t-test).
The correlation was strong (r = 0.89, p < 0.001).

% Incorrect
We found a significant difference (p < 0.05).
The correlation was strong (r = 0.89).
```

### Uncertainty and Confidence

```latex
% Correct
The mean value was 50 μm (95% CI: 45-55 μm).
The estimate is approximately 100 mg/kg (range: 80-120).

% Incorrect
The mean value was about 50 μm.
The estimate is roughly 100 mg/kg.
```

## Grammar and Style

### Active vs. Passive Voice

Generally prefer active voice for clarity:

```latex
% Better (active)
We measured the cortical thickness...
The algorithm detects outliers...

% Acceptable (passive, when emphasizing object)
The cortical thickness was measured...
Outliers are detected by the algorithm...
```

### Verb Tense

- **Past tense**: Methods, results, what was done
  - "We collected data from 50 patients."
  - "The analysis revealed..."

- **Present tense**: Facts, established knowledge
  - "Seizures are a common neurological disorder."
  - "Phase-amplitude coupling reflects..."

- **Future tense**: Planned work, implications
  - "Future studies will investigate..."
  - "This approach will enable..."

### Subject-Verb Agreement

```latex
% Correct
The set of results shows...
The group of patients was...

% Incorrect
The set of results show...
The group of patients were...
```

## Acronyms and Abbreviations

### First Use

Spell out on first mention, then use acronym:

```latex
Phase-amplitude coupling (PAC) analysis was performed...
The PAC values were then analyzed...
```

### Common Abbreviations

Define even if they seem obvious:

```latex
Magnetic resonance imaging (MRI) scans were acquired...
Statistical Package for the Social Sciences (SPSS) was used...
```

### Avoid Overuse

Don't create acronyms for terms used infrequently:

```latex
% Good: Single-use description
We implemented a cross-validation procedure...

% Unnecessary: Acronym for single use
We implemented a cross-validation procedure (CVP)...
```

## Citation Style

### In-Text Citations

Use consistent citation format throughout:

```latex
% Author-Year format (common)
Smith et al. (2020) demonstrated...
Previous research (Smith et al., 2020) suggests...
Multiple studies (Johnson, 2019; Smith et al., 2020) indicate...

% Numbered format
This approach has been validated [1, 2]...
```

### Multiple Authors

```latex
% Two authors
Smith and Johnson (2020) found...

% Three or more
Smith et al. (2020) demonstrated...
```

## Special Formatting

### Species Names

Italicize genus and species:

```latex
\textit{Homo sapiens}
\textit{Mus musculus}
\textit{Caenorhabditis elegans}
```

### Gene and Protein Names

Follow standard conventions for your field:

```latex
% Gene (italics, uppercase)
The \textit{TP53} gene...

% Protein (non-italic, uppercase)
The TP53 protein...

% Variable (italics)
Sample size $n = 50$
```

### Mathematical Variables

Use consistent formatting:

```latex
Let $X$ be the mean value...
The variable $x$ represents time...
The matrix $\mathbf{A}$ contains...
```

## Common Phrases and Corrections

### Precise Language for Results

```latex
% Better
The results indicate...
Our findings suggest...
The data demonstrate...

% Less precise
It seems that...
It appears that...
One could argue that...
```

### Hedging Language

Use appropriate qualifier when results are not definitive:

```latex
% Appropriate hedging
These results suggest that PAC may be...
Our preliminary evidence indicates that...
This provides evidence for...

% Excessive hedging
It could possibly suggest that PAC might potentially be...
```

### Cause and Effect

```latex
% Correct: Indicates association
High PAC values are associated with...
Increased seizure risk correlates with...

% Use with evidence: Indicates causation
Increased seizure risk results from...
PAC causes changes in...
```

## Consistency

### Terminology

Choose one term and use consistently:

```latex
% Pick one and stick with it
- "cortical neurons" vs "cortical cells"
- "high-frequency" vs "HF"
- "patient group" vs "patient cohort"
```

### Nomenclature

```latex
% Consistent
Figure 1A, Figure 1B (or Figure 1(A), Figure 1(i))
Patient P001, Patient P002
Method 1, Method 2
```

### Spelling

Follow chosen standard (UK/US English):

```latex
% Consistent use
Analyse (UK) or Analyze (US)
Colour (UK) or Color (US)
Optimisation (UK) or Optimization (US)
```

## Numbers and Numerals

### General Rules

- Spell out numbers one through nine in text
- Use numerals for 10 and above
- Always use numerals for measurements, percentages, time

```latex
% Correct
We studied three patients...
We measured 15 tissue samples...
The increase was 25\%.
The experiment lasted 2 hours.
```

### Ranges

```latex
% Correct
The age range was 20--40 years. (use em-dash)
Values ranged from 10 to 50 μm.
The temperature was 25°C ± 3°C.

% Incorrect
The age range was 20-40 years. (hyphen instead of em-dash)
Values ranged from 10-50 μm. (use "to" in text)
```

## Journal-Specific Guidelines

Different journals may have specific requirements:
- Check target journal's style guide
- Review recent articles in the journal
- Ask co-authors about journal preferences

## References

- See `G_QUICK_START.md` for basic workflow
- See `G_CONTENT_CREATION.md` for figure/table standards
- Check `to_claude/guidelines/science/` for detailed scientific writing guides
